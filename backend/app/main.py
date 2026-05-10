from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pinecone import Pinecone

from app.config import settings
from app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SourceChunk,
    UploadResponse,
)
from app.rag import process_and_upsert_document, query_and_generate_answer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create async clients
    app.state.openai = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url=settings.API_URL,
    )
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    app.state.pc = pc
    index_host = pc.describe_index(settings.PINECONE_INDEX_NAME).host
    app.state.index = pc.IndexAsyncio(host=index_host)

    yield

    # Shutdown — close clients
    await app.state.openai.close()
    await app.state.index.close()
    app.state.pc.close()


app = FastAPI(
    title="RAG ChatBot API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


# ── Upload ───────────────────────────────────────────────────────────────────

@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile):
    # Validate content type
    allowed_content_types = [
        "application/pdf",
        "text/plain",
        "text/csv",
    ]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF, TXT, and CSV files are accepted. Received: {file.content_type}",
        )

    # Read and validate file size
    file_bytes = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
        )

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    document_id, chunk_count = await process_and_upsert_document(
        openai_client=app.state.openai,
        pinecone_index=app.state.index,
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        content_type=file.content_type,
    )

    return UploadResponse(
        document_id=document_id,
        filename=file.filename or "unknown",
        chunks=chunk_count,
    )


# ── Chat ─────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    result = await query_and_generate_answer(
        openai_client=app.state.openai,
        pinecone_index=app.state.index,
        document_id=body.document_id,
        question=body.question,
    )

    sources = [SourceChunk(**s) for s in result["sources"]]
    return ChatResponse(answer=result["answer"], sources=sources)
