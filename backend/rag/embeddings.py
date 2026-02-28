"""
rag/embeddings.py
-----------------
Centralized embedding model configuration.

WHY this file exists:
  Single source of truth for the embedding model.
  Every module imports get_embedding_model() from here.
  Change the model in ONE place — entire system updates.
"""

import sys
from pathlib import Path

# Path bootstrap — allows direct execution and imports
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from langchain_openai import OpenAIEmbeddings
from config import get_settings
from core.logging import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Returns a configured OpenAI embedding model instance.

    Model: text-embedding-3-small
      - 1536 dimensions
      - Best cost/performance ratio for RAG
      - $0.02 per million tokens

    Usage:
        from rag.embeddings import get_embedding_model
        embeddings = get_embedding_model()
    """
    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")

    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )