"""
api/routes/admin.py
-----------------------
Admin/ops endpoints for monitoring and management.

Routes:
    GET  /admin/stats     --System stats (chunks, sessions, models)
    POST /admin/reingest   -- Trigger document re-ingestion
    GET  /admin/documents  -- List indexed document files

In production: protect these routes with API key auth middleware.        
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import AdminStatsResponse
from rag.retriever import get_vectorstore
from services.session_service import get_active_session_count
from core.logging import setup_logger
from config import get_settings

logger = setup_logger(__name__)
router = APIRouter()
settings = get_settings()

@router.get("/admin/stats", response_model=AdminStatsResponse, tags=["Admin"])
async def get_stats():
    """
    Returns current system statistics.
    Useful for monitoring dashboards.
    """
    try:
        vectorstore = get_vectorstore()
        total_chunks = vectorstore._collection.count()
    except Exception:
        total_chunks = 0
    
    return AdminStatsResponse(
        total_chunks=total_chunks,
        collection_name=settings.COLLECTION_NAME,
        embedding_model=settings.EMBEDDING_MODEL,
        chat_model=settings.CHAT_MODEL,
        active_sessions=get_active_session_count(),
    )

@router.post("/admin/reingest", tags=["Admin"])
async def reingest_documents(background_tasks: BackgroundTasks):
    """
    Trigger document re-ingestion in the background.
    Only re-ingests changed or new files (use has registry).
    Returns immediately - ingestion runs asynchronously.
    """
    def run_ingestion():
        try:
            from rag.ingestor import ingest
            logger.info("Background re-ingestion strarted")
            ingest()
            logger.info("Background re-ingestion complete")
        except Exception as e:
            logger.error(f"Re-ingestion failed: {e}", exc_info=True)

    background_tasks.add_task(run_ingestion)
    return {"message": "Re-ingestion started in background. Check server logs for progress."}

@router.get("/admin/documents", tags=["Admin"])
async def list_documents():
    """
    Lists all document files currently tracked in the hash registry.
    """
    import json
    from pathlib import Path

    registry_path = Path(settings.HASH_REGISTRY_PATH)
    if not registry_path.exists():
        return {"documents": [], "message": "No hash registry found. Run ingestion first."}

    with open(registry_path) as f:
        registry = json.load(f)

    return {
        "documents": list(registry.keys()),
        "total": len(registry),
    }        

