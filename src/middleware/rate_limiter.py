"""
Rate Limiting Middleware
========================
Prevents abuse and DDoS attacks with configurable rate limits.
"""

import time
import logging
from fastapi import Request, HTTPException, status
from typing import Dict, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with Redis backend for distributed rate limiting.
    
    Features:
    - Per-IP rate limiting
    - Per-user rate limiting
    - Per-endpoint rate limiting
    - Premium user bypass
    - Distributed across instances via Redis
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        
        # In-memory fallback if Redis unavailable
        self._memory_store: Dict[str, Dict] = defaultdict(dict)
        
        # Rate limit configurations
        self.limits = {
            "global": {"requests": 100, "window": 60},  # 100 req/min
            "auth_register": {"requests": 5, "window": 3600},  # 5/hour
            "auth_login": {"requests": 10, "window": 300},  # 10/5min
            "predictions": {"requests": 30, "window": 60},  # 30/min
            "websocket": {"requests": 50, "window": 60},  # 50/min
        }
    
    async def check_rate_limit(
        self,
        key: str,
        limit_type: str = "global",
        user_id: Optional[str] = None
    ) -> bool:
        """
        Check if request is within rate limits.
        
        Args:
            key: Unique identifier (IP address, user ID, etc.)
            limit_type: Type of rate limit to apply
            user_id: User ID for premium bypass check
        
        Returns:
            True if allowed, False if rate limited
        """
        # Check if user has premium (bypass rate limits)
        if user_id and await self._is_premium_user(user_id):
            return True
        
        limit_config = self.limits.get(limit_type, self.limits["global"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        
        # Try Redis first
        if self.redis_client:
            try:
                return await self._check_redis_rate_limit(
                    key, max_requests, window_seconds, limit_type
                )
            except Exception as e:
                logger.warning(f"Redis rate limit check failed, using memory: {e}")
        
        # Fallback to memory
        return self._check_memory_rate_limit(key, max_requests, window_seconds)
    
    async def _check_redis_rate_limit(
        self, key: str, max_requests: int, window: int, limit_type: str
    ) -> bool:
        """Check rate limit using Redis."""
        redis_key = f"rate_limit:{limit_type}:{key}"
        
        try:
            # Use Redis INCR for atomic increment
            current = await self.redis_client.incr(redis_key)
            
            # Set expiry on first request
            if current == 1:
                await self.redis_client.expire(redis_key, window)
            
            if current > max_requests:
                # Log rate limit hit
                logger.warning(
                    f"Rate limit exceeded | Key: {key} | Type: {limit_type} | "
                    f"Count: {current} | Limit: {max_requests}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Allow request on error (fail open)
            return True
    
    def _check_memory_rate_limit(
        self, key: str, max_requests: int, window: int
    ) -> bool:
        """Check rate limit using in-memory store (fallback)."""
        now = time.time()
        
        if key not in self._memory_store:
            self._memory_store[key] = {
                "count": 1,
                "window_start": now
            }
            return True
        
        data = self._memory_store[key]
        
        # Check if window expired
        if now - data["window_start"] > window:
            # Reset window
            data["count"] = 1
            data["window_start"] = now
            return True
        
        # Increment counter
        data["count"] += 1
        
        if data["count"] > max_requests:
            logger.warning(f"Memory rate limit exceeded | Key: {key}")
            return False
        
        return True
    
    async def _is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium subscription (bypass rate limits)."""
        # TODO: Implement actual subscription check
        # For now, return False
        return False
    
    def get_rate_limit_headers(self, key: str, limit_type: str = "global") -> Dict[str, str]:
        """Get rate limit headers for response."""
        limit_config = self.limits.get(limit_type, self.limits["global"])
        
        # TODO: Get actual remaining count from Redis
        return {
            "X-RateLimit-Limit": str(limit_config["requests"]),
            "X-RateLimit-Remaining": "0",  # TODO: Calculate
            "X-RateLimit-Reset": str(int(time.time() + limit_config["window"]))
        }


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        self.app = app
        self.rate_limiter = rate_limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive=receive)
        
        # Determine rate limit type based on path
        limit_type = self._get_limit_type(request.url.path)
        
        # Get identifier (IP or user)
        identifier = self._get_identifier(request)
        
        # Check rate limit
        allowed = await self.rate_limiter.check_rate_limit(
            identifier, limit_type
        )
        
        if not allowed:
            # Return 429 Too Many Requests
            response_body = {
                "error": "Rate Limit Exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": 60
            }
            
            import json
            response = b"HTTP/1.1 429 Too Many Requests\r\n"
            response += b"Content-Type: application/json\r\n"
            response += b"Retry-After: 60\r\n"
            response += b"\r\n"
            response += json.dumps(response_body).encode()
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [[b"content-type", b"application/json"]]
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps(response_body).encode()
            })
            return
        
        # Request allowed, proceed
        await self.app(scope, receive, send)
    
    def _get_limit_type(self, path: str) -> str:
        """Determine rate limit type from path."""
        if "/auth/register" in path:
            return "auth_register"
        elif "/auth/login" in path:
            return "auth_login"
        elif "/predictions" in path:
            return "predictions"
        elif "/ws" in path:
            return "websocket"
        else:
            return "global"
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user ID from auth header
        auth_header = request.headers.get("authorization")
        if auth_header:
            # TODO: Extract user ID from JWT token
            # For now, use IP
            pass
        
        # Use IP address
        if request.client:
            return request.client.host
        
        return "unknown"


# Global rate limiter instance
rate_limiter = RateLimiter()
