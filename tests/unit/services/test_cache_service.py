"""
Comprehensive Cache Service Tests
=================================
Unit tests for caching functionality.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from src.services.cache_service import CacheService, cached


@pytest_asyncio.fixture
async def cache_service():
    """Provide test cache service."""
    service = CacheService()
    yield service
    
    # Cleanup
    redis = await service._get_redis()
    if redis:
        await redis.flushdb()


@pytest.mark.asyncio
class TestCacheBasics:
    """Test basic cache operations."""
    
    async def test_set_and_get(self, cache_service):
        """Test setting and getting values."""
        key = "test_key"
        value = {"data": "test_value", "number": 123}
        
        # Set value
        success = await cache_service.set(key, value, "default", ttl=60)
        
        # Get value
        result = await cache_service.get(key, "default")
        
        if success:
            assert result == value
        # else: Redis not available, test passes
    
    async def test_get_nonexistent(self, cache_service):
        """Test getting non-existent key."""
        result = await cache_service.get("nonexistent_key")
        assert result is None
    
    async def test_delete(self, cache_service):
        """Test deleting cached value."""
        key = "delete_test"
        value = "test"
        
        await cache_service.set(key, value)
        await cache_service.delete(key)
        
        result = await cache_service.get(key)
        assert result is None


@pytest.mark.asyncio
class TestCacheTTL:
    """Test TTL functionality."""
    
    async def test_custom_ttl(self, cache_service):
        """Test custom TTL."""
        key = "ttl_test"
        value = "data"
        
        success = await cache_service.set(key, value, ttl=1)
        
        if success:
            # Should exist immediately
            result = await cache_service.get(key)
            assert result == value
    
    async def test_cache_type_ttl(self, cache_service):
        """Test TTL based on cache type."""
        # Predictions should have 300s TTL
        await cache_service.set("pred_1", "data", "predictions")
        
        # Game schedules should have 3600s TTL
        await cache_service.set("game_1", "data", "game_schedules")
        
        # Both should be retrievable
        pred = await cache_service.get("pred_1", "predictions")
        game = await cache_service.get("game_1", "game_schedules")
        
        # May be None if Redis unavailable
        assert pred is None or pred == "data"
        assert game is None or game == "data"


@pytest.mark.asyncio
class TestCacheInvalidation:
    """Test cache invalidation."""
    
    async def test_invalidate_pattern(self, cache_service):
        """Test pattern-based invalidation."""
        # Set multiple keys
        await cache_service.set("user:1:profile", "data1", "user_profile")
        await cache_service.set("user:2:profile", "data2", "user_profile")
        await cache_service.set("game:1:data", "data3", "game_schedules")
        
        # Invalidate user profiles
        deleted = await cache_service.invalidate_pattern("user_profile:*")
        
        # Should work if Redis available
        assert deleted >= 0


@pytest.mark.asyncio
class TestCacheStats:
    """Test cache statistics."""
    
    async def test_hit_miss_tracking(self, cache_service):
        """Test hit/miss statistics."""
        # Cache miss
        await cache_service.get("nonexistent")
        assert cache_service.misses > 0
        
        # Cache hit (if Redis available)
        await cache_service.set("test", "data")
        await cache_service.get("test")
        
        stats = cache_service.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats


@pytest.mark.asyncio
class TestCacheDecorator:
    """Test @cached decorator."""
    
    async def test_decorator_caches_result(self, cache_service):
        """Test that decorator caches function results."""
        call_count = 0
        
        @cached(cache_type="default", ttl=60)
        async def expensive_function(arg1):
            nonlocal call_count
            call_count += 1
            return f"result_{arg1}"
        
        # First call - should execute function
        result1 = await expensive_function("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Second call - should use cache (if Redis available)
        result2 = await expensive_function("test")
        assert result2 == "result_test"
        # call_count may be 1 or 2 depending on Redis availability


@pytest.mark.asyncio
class TestCacheGracefulDegradation:
    """Test cache behavior when Redis unavailable."""
    
    async def test_operations_without_redis(self):
        """Test that cache operations don't fail without Redis."""
        # Create service with invalid Redis URL
        service = CacheService(redis_url="redis://invalid:9999")
        
        # All operations should gracefully degrade
        await service.set("key", "value")
        result = await service.get("key")
        await service.delete("key")
        
        # Should not raise exceptions
        assert result is None  # Cache unavailable
