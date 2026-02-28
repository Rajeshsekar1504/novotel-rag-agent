"""
core/exceptions.py
------------------
Custom exception classes for the application.
Raising domain-specific exceptions makes error handling
clean and predictable across all layers.
"""
class NovaTelBaseException(Exception):
    """
    Base exception for all NovaTel errors.
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class VectorStoreNotReadyError(NovaTelBaseException):
    """Raised when ChromaDB is not initialized or Unreachable."""
    def __init__(self):
        super().__init__(
            message="Vector store is not ready. Run the ingestion pipeline first.",
            status_code=503
        )
class DocumentIngestionError(NovaTelBaseException):
    """Raised when document loading or chunking fails."""
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"Failed to ingest document '{filename}': {reason}",
            status_code=500
        )

class AgentInvocationError(NovaTelBaseException):
    """Raised when the langgraph agent fails to produce a response."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Agent failed to process query: {reason}",
            status_code=500
        )
    
class SessionNotFoundError(NovaTelBaseException):
    """Raised when a session_id is not found in the store."""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session '{session_id}' not found.",
            status_code=404
        )

class InvalidQueryError(NovaTelBaseException):
    """Raised when the user query is empty or invalid. """
    def __init__(self):
        super().__init__(
            message="Query must be a non-empty string under 2000 characters.",
            status_code=422
        )

    
        