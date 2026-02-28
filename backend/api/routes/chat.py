"""
api/routes/chat.py
------------------
Chat endpoint — the primary API route of the application.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json

from models.schemas import ChatRequest, ChatResponse, SessionClearResponse
from services.chat_service import process_chat
from services.session_service import clear_session
from core.exceptions import AgentInvocationError, VectorStoreNotReadyError
from core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process a customer support query through the RAG agent.
    """
    try:
        response = await process_chat(
            session_id=request.session_id,
            message=request.message,
        )
        return response

    except VectorStoreNotReadyError as e:
        logger.error("Vector store not ready")
        raise HTTPException(status_code=503, detail=e.message)

    except AgentInvocationError as e:
        logger.error(f"Agent error: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)

    except Exception as e:
        logger.error(f"Unexpected error in /chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    
# ── Streaming Chat Endpoint (NEW — does NOT affect existing /chat) ──

@router.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):

    async def token_generator():

        try:

            response = await process_chat(
                session_id=request.session_id,
                message=request.message,
            )

            answer = response.answer
            sources = response.sources

            # FIX: convert sources to JSON-safe format
            serialized_sources = [
                {
                    "source": getattr(s, "source", None),
                    "score": getattr(s, "score", None),
                    "content": getattr(s, "content", None),
                }
                for s in sources
            ]

            for word in answer.split():

                yield json.dumps({
                    "token": word + " "
                }) + "\n"

                await asyncio.sleep(0.02)

            yield json.dumps({
                "done": True,
                "sources": serialized_sources
            }) + "\n"

        except Exception as e:

            logger.error(
                f"Streaming error: {e}",
                exc_info=True
            )

            yield json.dumps({
                "error": str(e)
            }) + "\n"

    return StreamingResponse(
        token_generator(),
        media_type="application/json"
    )


@router.delete("/session/{session_id}", response_model=SessionClearResponse, tags=["Chat"])
async def clear_chat_session(session_id: str):
    """
    Clear conversation history for a given session.
    Called when user clicks 'New Chat' in the frontend.
    """
    existed = clear_session(session_id)
    return SessionClearResponse(
        session_id=session_id,
        message="Session cleared." if existed else "Session not found."
    )