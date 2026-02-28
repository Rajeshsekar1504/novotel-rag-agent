"""
services/session_service.py
----------------------------
Manages conversation history per user session.
Storage: In-memory dict (swap to Redis in production).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typing import List
from langchain_core.messages import BaseMessage
from config import get_settings
from core.logging import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

# In-memory session store — keyed by session_id
_store: dict = {}


def get_history(session_id: str) -> List[BaseMessage]:
    """Retrieve conversation history for a session."""
    history = _store.get(session_id, [])
    logger.debug(f"Session {session_id}: loaded {len(history)} messages")
    return history


def save_history(session_id: str, messages: List[BaseMessage]) -> None:
    """Persist updated conversation history. Trims to MAX_HISTORY_TURNS."""
    max_messages = settings.MAX_HISTORY_TURNS * 2
    trimmed = messages[-max_messages:] if len(messages) > max_messages else messages
    _store[session_id] = trimmed
    logger.debug(f"Session {session_id}: saved {len(trimmed)} messages")


def clear_session(session_id: str) -> bool:
    """Delete session history. Returns True if existed."""
    existed = session_id in _store
    _store.pop(session_id, None)
    logger.info(f"Session {session_id}: {'cleared' if existed else 'not found'}")
    return existed


def get_active_session_count() -> int:
    """Returns total number of active sessions."""
    return len(_store)