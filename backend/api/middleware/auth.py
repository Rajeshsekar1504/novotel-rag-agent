"""
api/middleware/auth.py
----------------------
API key authentication for admin routes.

Admin routes (/admin/*) require the X-API-Key header.
Chat and health routes are publicly accessible.

Usage in production:
  Set ADMIN_API_KEY in your .env file.
  Pass header: X-API-Key: your-secret-key
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config import get_settings
from core.logging import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

ADMIN_API_KEY = "novotel-admin-secret"  # Move to settings in production

class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    Protects /admin/* routes with a static API key.
    Production: Use JWT tokens or AWS Cognito instead.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/admin"):
            api_key = request.headers.get("X-API-Key")
            if api_key != ADMIN_API_KEY:
                logger.warning(f"Unauthorized admin access attempt from {request.client.host}")
                raise HTTPException(status_code=401, detail="Unauthorized.Provide X-API-Key header.")
            return await call_next(request)
        