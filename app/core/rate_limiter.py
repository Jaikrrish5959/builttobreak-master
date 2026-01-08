"""
Rate Limiting Middleware for API Security
Prevents brute force attacks on PIN verification and other sensitive endpoints.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Callable
import time

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
PIN_VERIFY_LIMIT = "5/minute"  # 5 PIN attempts per minute per IP
API_GENERAL_LIMIT = "100/minute"  # 100 general API calls per minute
TRANSFER_LIMIT = "10/minute"  # 10 transfers per minute per IP

def get_rate_limit_exceeded_handler():
    """Custom handler for rate limit exceeded errors"""
    async def handler(request: Request, exc: RateLimitExceeded):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": exc.detail
            }
        )
    return handler
