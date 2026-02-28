"""
services/chat_service.py
------------------------
Business logic layer between the API route and the Langgraph agent.

WHY a service layer:
    The API route should only handle HTTP concerns (request parsing,
    response formatting, error codes). The agent handles AI logic.
    The Service layer orchestrates between them -- it's the glue.

    This separation means:
    - You can test chat logic without spinning up FastAPI
    - You can call the agent from a CLI, tests, or background jobs
    - The route stays thin and readable
"""

import time
from typing import Tuple, List

from agent.graph import agent
from models.schemas import ChatResponse, SourceDocument
from models.state import AgentState
from services.session_service import get_history, save_history
from core.logging import setup_logger
from core.exceptions import AgentInvocationError
from config import get_settings

logger = setup_logger(__name__)
settings = get_settings()

async def process_chat(session_id: str, message: str) -> ChatResponse:
    """
    Full chat Processing pipeline:
       1. Load session history
       2. Build initial Langgraph state
       3. Invoke agent
       4. Persist updated session history
       5. Format and return ChatResponse
    Args:
         session_id: Unique session identifier from frontend
         message: Current user query
    
    Returns:
        ChatResponse Pydantic model ready for JSON serialization
    """
    start_time = time.time()
    logger.info(f"Processing chat | Session: {session_id} | Query: '{message[:60]}...'")
    # ── Step 1: Load session history ──────────────────────────────────────────
    history = get_history(session_id)

    # ── Step 2: Build initial state ───────────────────────────────────────────
    initial_state: AgentState = {
        "messages": history,
        "session_id": session_id,
        "user_query": message,
        "intent": None,
        "retrieved_docs": [],
        "reranked_docs": [],
        "answer": None,
        "sources": [],
        "needs_escalation": False,
        "iteration_count": 0,
    }
    
    # ── Step 3: Invoke agent ──────────────────────────────────────────────────
    try:
        result: AgentState = agent.invoke(initial_state)
    except Exception as e:
        logger.error(f"Agent invocation failed: {e}", exc_info=True)
        raise AgentInvocationError(str(e))
    
    # ── Step 4: Persist updated history ───────────────────────────────────────
    save_history(session_id, result.get("messages", []))

    # ── Step 5: Format response ───────────────────────────────────────────────
    raw_sources = result.get("sources", [])
    sources = [
        SourceDocument(
            content=doc["content"][:300],   # Truncate for UI display
            source_file=doc["source_file"],
            category=doc["category"],
            relevance_score=0.90,
        )
        for doc in raw_sources[:3]   # Max 3 source citations in UI
    ]

    processing_ms = int((time.time() - start_time) * 1000)
    confidence = 0.90 if raw_sources else 0.40
    
    response = ChatResponse(
        session_id=session_id,
        answer=result.get("answer") or "I'm sorry, I couldn't process your request. Please try again.",
        sources=sources,
        intent=result.get("intent"),
        needs_escalation=result.get("needs_escalation", False),
        confidence=confidence,
        processing_time_ms=processing_ms,
    )

    logger.info(
        f"Chat complete | "
        f"Session: {session_id} | "
        f"Intent: {response.intent} | "
        f"Sources: {len(sources)} | "
        f"Time: {processing_ms}ms"
    )

    return response