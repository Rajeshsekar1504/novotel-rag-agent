"""
api/middleware/rate_limit.py
----------------------------
Simple in-memory rate limiter middleware.

Limits: 30 requests per minute per IP address.
Production upgrade: Use Redis-backed rate limiting (slowapi + redis).

WHY rate limiting:
    Prevents abuse and runaway OpenAI API costs.
    Each chat request costs ~$0.02 in tokens - 1000 requests = $2.
    A single bad actor could drain you API quota in minutes.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Per-IP request timestamps
_request_log: dict[str, list] = defaultdict(list)

WINDOW_SECONDS = 60
MAX_REQUESTS = 30

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter.
    Allows MAX_REQUESTS per IP per WINDOW_SECONDS.
    """
    async def dispatch(self, request: Request, call_next):
        # Only rate limit the /chat endpoint
        if request.url.path != "/chat":
            return await call_next(request)
        
        client_ip = request.client.host
        now = time.time()
        
        # Remove timestamps outside the window
        _request_log[client_ip] = [
            ts for ts in _request_log[client_ip]
            if now - ts < WINDOW_SECONDS
        ]
        if len(_request_log[client_ip]) >= MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {MAX_REQUESTS} requests per minute."
            )
        _request_log[client_ip].append(now)
        return await call_next(request)