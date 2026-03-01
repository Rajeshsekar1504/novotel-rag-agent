"""
config.py
---------
Centralized configuration using Pydantic BaseSettings.
All environment variables are loaded from .env file.
Single source of truth for the entire backend.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache


# ── Directory References ──────────────────────────────────────────────────────
# config.py lives at: novotel-rag-agent/backend/config.py
# parents[0] = backend/
# parents[1] = novotel-rag-agent/   ← PROJECT ROOT

BACKEND_DIR  = Path(__file__).resolve().parent        # backend/
PROJECT_ROOT = Path(__file__).resolve().parents[1]    # novotel-rag-agent/


class Settings(BaseSettings):

    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str
    CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1024

    # ── Paths (all relative to PROJECT ROOT) ──────────────────────────────────
    # config.py — find these 3 lines and fix them


    import os
    CHROMA_PATH: str        = os.getenv("CHROMA_PATH", "chroma_db")
    DOCS_PATH: str          = os.getenv("DOCS_PATH", "documents")
    HASH_REGISTRY_PATH: str = os.getenv("HASH_REGISTRY_PATH", "hash_registry.json")

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    COLLECTION_NAME: str = "telecom_support"

    # ── Retrieval ─────────────────────────────────────────────────────────────
    RETRIEVER_K: int        = 5
    RETRIEVER_FETCH_K: int  = 15
    RETRIEVER_LAMBDA: float = 0.7
    RERANKER_TOP_N: int     = 3

    # ── API ───────────────────────────────────────────────────────────────────
    API_HOST: str   = "0.0.0.0"
    API_PORT: int   = 8000
    API_RELOAD: bool = True
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # ── Session ───────────────────────────────────────────────────────────────
    MAX_HISTORY_TURNS: int = 10

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str    = "NovaTel AI Support Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool      = False

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    lru_cache ensures .env is read only once.
    Import this function everywhere instead of instantiating Settings directly.
    """
    return Settings()