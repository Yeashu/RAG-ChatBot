from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int

class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1)

class SourceChunk(BaseModel):
    text: str
    chunk_index: int
    score: float
    page_number: int 

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
