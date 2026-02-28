"""
models/schemas.py
-----------------
Pydantic v2 request/response schemas for all API endpoints.

WHY Pydantic schemas:
      - Validates every incoming request before it touches agent logic
      - Guarantees every outgoing response has the exact same shape
      - Auto-generates OPENAI docs  at /docs
      - Frontend always knows what shape to expect - no surprises
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ── Enums ─────────────────────────────────────────────────────────────────────

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class IntentCategory(str, Enum):
    PLANS_PRICING = "plans_pricing"
    BILLING = "billing"
    NETWORK = "network"
    SIM_ACTIVATION = "sim_activation"
    ROAMING = "roaming"
    REFUND_CANCELLATION = "refund_cancellation"
    GENERAL = "general"

# ── Sub-models ────────────────────────────────────────────────────────────────

class Message(BaseModel):
    """Single turn in a conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SourceDocument(BaseModel):
    """A retrieved document chunk shown as citation in the UI."""
    content: str = Field(..., description="Chunk text snippet (max 300 chars)")
    source_file: str = Field(..., description="Original .docx filename")
    category: str = Field(..., description="Inferred telecom category")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)

# ── Request Schemas ─────────────────────────────────────────────────────────── 
class ChatRequest(BaseModel):
    """
    Incoming chat request from the frontend.

    session_id: Unique ID per browser tab/user session
    message: The user's current query
    """ 
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique session identifier"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's query"
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blanks(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be blank or whitespace only.")
        return v.strip()
    
# ── Response Schemas ──────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    """
    Full response returned to fronend after agent processing.
    """ 
    session_id: str
    answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    intent: Optional[IntentCategory] = None
    needs_escalation: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_time_ms: int = Field(default=0, ge=0)

class HealthResponse(BaseModel):
    """Response from GET /health endpoint."""
    status: str
    app_name: str
    version: str
    vector_store_ready: bool
    documents_indexed: int
    model: str

class SessionClearResponse(BaseModel):
    """Response from DELETE /session/{id} endpoint."""
    session_id: str
    message: str

class AdminStatsResponse(BaseModel):
    """Response from GET /admin/stats endpoint."""
    total_chunks: int
    collection_name: str
    embedding_model: str
    chat_model: str
    active_sessions: int
    