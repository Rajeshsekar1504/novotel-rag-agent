"""
api/routes/health.py
--------------------
Health check endpoint.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import chromadb
from chromadb.config import Settings as ChromaSettings
from fastapi import APIRouter
from models.schemas import HealthResponse
from core.logging import setup_logger
from config import get_settings

logger   = setup_logger(__name__)
router   = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """
    System health check.
    Verifies ChromaDB is accessible and returns document count.
    """
    try:
        chroma_path = Path(settings.CHROMA_PATH)
        sqlite_file = chroma_path / "chroma.sqlite3"

        if not chroma_path.exists() or not sqlite_file.exists():
            vector_store_ready = False
            doc_count = 0
        else:
            client     = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            collection = client.get_or_create_collection(settings.COLLECTION_NAME)
            doc_count  = collection.count()
            vector_store_ready = doc_count > 0

    except Exception as e:
        logger.error(f"Health check error: {e}")
        vector_store_ready = False
        doc_count = 0

    return HealthResponse(
        status="healthy" if vector_store_ready else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        vector_store_ready=vector_store_ready,
        documents_indexed=doc_count,
        model=settings.CHAT_MODEL,
    )