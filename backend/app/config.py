from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenRouter / OpenAI-compatible LLM
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    OPENAI_MODEL: str

    # Embedding model (separate — OpenRouter doesn't support embeddings)
    EMBEDDING_MODEL: str
    DIMENSIONS: int

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str

    TOP_K: int

    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    MAX_FILE_SIZE_MB: int

    SYSTEM_PROMPT: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings() # type: ignore