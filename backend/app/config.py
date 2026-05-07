from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    API_URL: str

    LLM_MODEL: str
    EMBEDDING_MODEL: str

    DIMENSIONS: int

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