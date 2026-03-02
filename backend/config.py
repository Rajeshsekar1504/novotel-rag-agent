from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):

    # OpenAI
    OPENAI_API_KEY: str

    CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1024

    # Paths
    CHROMA_PATH: str = str(PROJECT_ROOT / "chroma_db")
    DOCS_PATH: str = str(PROJECT_ROOT / "documents")
    HASH_REGISTRY_PATH: str = str(PROJECT_ROOT / "hash_registry.json")

    COLLECTION_NAME: str = "telecom_support"

    # Retrieval
    RETRIEVER_K: int = 5
    RETRIEVER_FETCH_K: int = 15
    RETRIEVER_LAMBDA: float = 0.7
    RERANKER_TOP_N: int = 3

    # Session  ✅ FIX
    MAX_HISTORY_TURNS: int = 10

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # ✅ REQUIRED for logging
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost:3000",
    ]

    APP_NAME: str = "NovaTel AI Support Agent"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()