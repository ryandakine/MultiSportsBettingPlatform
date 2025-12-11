"""
Caching Service
===============
Redis-based caching layer for predictions, schedules, and expensive queries.
"""

import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import hashlib

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis-based caching service with automatic TTL and invalidation.
    
    Features:
    - Automatic serialization/deserialization
    - Configurable TTL per cache type
    - Cache invalidation
    - Cache hit/miss metrics
    - Graceful degradation without Redis
    """
    
    def __init__(self, redis_url: str = None):
        from src.config import settings
        self.redis_url = redis_url or settings.redis_url
        self.redis_client = None
        
        # Cache TTL configurations (seconds)
        self.ttls = {
            "predictions": 300,  # 5 minutes
            "game_schedules": 3600,  # 1 hour
            "team_stats": 1800,  # 30 minutes
            "odds": 60,  # 1 minute (real-time)
            "user_profile": 600,  # 10 minutes
        }
        
        # Metrics
        self.hits = 0
        self.misses = 0
    
    async def _get_redis(self):
        """Lazy-initialize Redis connection."""
        if self.redis_client is None:
            try:
                import redis.asyncio as redis
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("✅ Cache: Redis connected")
            except Exception as e:
                logger.warning(f"⚠️ Cache: Redis unavailable: {e}")
                self.redis_client = False
        
        return self.redis_client if self.redis_client is not False else None
    
    async def get(
        self,
        key: str,
        cache_type: str = "default"
    ) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache (for TTL lookup)
        
        Returns:
            Cached value or None if not found
        """
        redis = await self._get_redis()
        if not redis:
            self.misses += 1
            return None
        
        try:
            cache_key = self._build_key(key, cache_type)
            value = await redis.get(cache_key)
            
            if value is None:
                self.misses += 1
                return None
            
            self.hits += 1
            logger.debug(f"Cache HIT: {cache_key}")
            
            # Deserialize JSON
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.misses += 1
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        cache_type: str = "default",
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            cache_type: Type of cache (for TTL lookup)
            ttl: Optional custom TTL in seconds
        
        Returns:
            True if successful, False otherwise
        """
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = self._build_key(key, cache_type)
            
            # Serialize to JSON
            serialized = json.dumps(value)
            
            # Get TTL
            ttl_seconds = ttl or self.ttls.get(cache_type, 300)
            
            # Set with TTL
            await redis.setex(cache_key, ttl_seconds, serialized)
            
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete value from cache."""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = self._build_key(key, cache_type)
            await redis.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "predictions:*")
        
        Returns:
            Number of keys deleted
        """
        redis = await self._get_redis()
        if not redis:
            return 0
        
        try:
            deleted = 0
            cursor = 0
            
            while True:
                cursor, keys = await redis.scan(
                    cursor,
                    match=f"cache:{pattern}",
                    count=100
                )
                
                if keys:
                    await redis.delete(*keys)
                    deleted += len(keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"Cache invalidated: {deleted} keys matching {pattern}")
            return deleted
            
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0
    
    def _build_key(self, key: str, cache_type: str) -> str:
        """Build full cache key with namespace."""
        return f"cache:{cache_type}:{key}"
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total
        }


def cached(
    cache_type: str = "default",
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(cache_type="predictions", ttl=300)
        async def get_prediction(user_id: str, game_id: str):
            # Expensive operation
            return prediction
    
    Args:
        cache_type: Type of cache
        ttl: Optional TTL override
        key_func: Optional function to generate cache key from args
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash function name + args
                key_parts = [func.__name__] + [str(arg) for arg in args]
                cache_key = hashlib.md5(
                    ":".join(key_parts).encode()
                ).hexdigest()
            
            # Try to get from cache
            cached_value = await cache_service.get(cache_key, cache_type)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, cache_type, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache service instance
cache_service = CacheService()
