from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    CHROMA_PATH: str = str(PROJECT_ROOT / "chroma_db")
    DOCS_PATH: str = str(PROJECT_ROOT / "documents")
    HASH_REGISTRY_PATH: str = str(PROJECT_ROOT / "hash_registry.json")

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()