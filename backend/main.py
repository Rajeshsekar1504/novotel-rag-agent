"""
main.py
-------
FastAPI application entry point.

Run with:
  uvicorn main:app --reload --port 8000

API docs:
  http://localhost:8000/docs
  http://localhost:8000/redoc
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from config import get_settings
from core.logging import setup_logger
from api.routes import chat, health, admin

settings = get_settings()
logger = setup_logger(__name__)

# ── Create App ────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-powered AI support agent for NovaTel Communications",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware (only this — no custom middleware for now) ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(admin.router)

# ── Startup / Shutdown ────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Chat model    : {settings.CHAT_MODEL}")
    logger.info(f"Embedding     : {settings.EMBEDDING_MODEL}")
    logger.info(f"API docs      : http://localhost:{settings.API_PORT}/docs")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down NovaTel AI Support Agent")

# ── Dev entry point ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )