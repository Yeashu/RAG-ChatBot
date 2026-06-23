import uuid
import asyncio
import fitz
from openai import AsyncOpenAI
from pinecone import Pinecone

from app.config import settings


def extract_text_from_pdf(pdf_bytes: bytes) -> list[str]:
    document = fitz.open(stream=pdf_bytes, filetype='pdf')
    page_texts = []
    for page in document:
        page_texts.append(page.get_text())
    return page_texts

def chunk_text(
        text: str,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
) -> list[str]:
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

async def get_embeddings(
    openai_client: AsyncOpenAI,
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []
    response = await openai_client.embeddings.create(
        input=texts,
        model=settings.EMBEDDING_MODEL,
        dimensions=settings.DIMENSIONS,
    )
    return [data.embedding for data in response.data]

async def process_and_upsert_document(
    openai_client: AsyncOpenAI,
    pinecone_index,
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> tuple[str, int]:
    document_id = str(uuid.uuid4())
    
    if content_type == "application/pdf":
        page_texts = extract_text_from_pdf(file_bytes)
    elif content_type in ["text/plain", "text/csv"]:
        # For plain text or CSV, we treat the whole content as one "page" for simplicity
        page_texts = [file_bytes.decode('utf-8', errors='ignore')]
    else:
        page_texts = []
    
    # Collect all chunks across pages first
    chunks_to_embed = []  # List of tuples: (page_num, chunk_index_in_page, chunk_text)
    for page_num, page_text in enumerate(page_texts, start=1):
        if not page_text.strip():
            continue
        chunks = chunk_text(page_text)
        for i, chunk in enumerate(chunks):
            chunks_to_embed.append((page_num, i, chunk))
            
    if not chunks_to_embed:
        return document_id, 0

    # Batch embeddings creation
    # Embed in batches of 64 to avoid HTTP request overhead or payload limits
    batch_size = 64
    batches = [chunks_to_embed[i:i + batch_size] for i in range(0, len(chunks_to_embed), batch_size)]
    
    # Limit concurrency of OpenRouter embedding calls using Semaphore
    sem = asyncio.Semaphore(5)
    
    async def embed_with_semaphore(batch):
        async with sem:
            texts = [item[2] for item in batch]
            return await get_embeddings(openai_client, texts)
            
    # Run batches concurrently
    tasks = [embed_with_semaphore(b) for b in batches]
    embeddings_list = await asyncio.gather(*tasks)
    
    # Flatten results and map to original chunks
    all_embeddings = []
    for emb_batch in embeddings_list:
        all_embeddings.extend(emb_batch)
        
    vectors = []
    for chunk_count, (page_num, chunk_index_in_page, chunk) in enumerate(chunks_to_embed):
        vector_id = f"{document_id}-p{page_num}-c{chunk_index_in_page}"
        vectors.append({
            "id": vector_id,
            "values": all_embeddings[chunk_count],
            "metadata": {
                "document_id": document_id,
                "text": chunk,
                "page_number": page_num,
                "chunk_index": chunk_count
            }
        })
        
    if vectors:
        upsert_batch_size = 100
        for i in range(0, len(vectors), upsert_batch_size):
            await pinecone_index.upsert(vectors=vectors[i:i + upsert_batch_size])
            
    return document_id, len(vectors)

async def query_and_generate_answer(
    openai_client: AsyncOpenAI,
    pinecone_index,
    document_id: str,
    question: str,
) -> dict:
    q_embedding = (await get_embeddings(openai_client, [question]))[0]
    
    query_response = await pinecone_index.query(
        vector=q_embedding,
        top_k=settings.TOP_K,
        filter={"document_id": {"$eq": document_id}},
        include_metadata=True
    )
    
    sources = []
    contexts = []
    for match in query_response.matches:
        meta = match.metadata
        sources.append({
            "text": meta.get("text", ""),
            "chunk_index": meta.get("chunk_index", 0),
            "score": match.score,
            "page_number": meta.get("page_number", 0)
        })
        contexts.append(meta.get("text", ""))
        
    context_str = "\n\n---\n\n".join(contexts)
    
    messages = [
        {"role": "system", "content": settings.SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion:\n{question}"}
    ]
    
    completion = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources
    }
