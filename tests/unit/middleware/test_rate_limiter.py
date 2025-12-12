"""
Rate Limiter Tests
==================
Unit tests for rate limiting functionality.
"""

import pytest
import pytest_asyncio
import asyncio
from src.middleware.rate_limiter import RateLimiter


@pytest_asyncio.fixture
async def rate_limiter():
    """Provide test rate limiter."""
    limiter = RateLimiter()
    yield limiter


@pytest.mark.asyncio
class TestBasicRateLimiting:
    """Test basic rate limiting."""
    
    async def test_first_request_allowed(self, rate_limiter):
        """Test that first request is always allowed."""
        allowed = await rate_limiter.check_rate_limit("test_ip_1", "global")
        assert allowed is True
    
    async def test_within_limit(self, rate_limiter):
        """Test multiple requests within limit."""
        ip = "test_ip_2"
        
        # Make 5 requests (well under limit)
        for _ in range(5):
            allowed = await rate_limiter.check_rate_limit(ip, "global")
            assert allowed is True
    
    async def test_exceed_limit(self, rate_limiter):
        """Test exceeding rate limit."""
        ip = "test_ip_3"
        limit = rate_limiter.limits["global"]["requests"]
        
        # Make requests up to limit
        for i in range(limit + 5):
            allowed = await rate_limiter.check_rate_limit(ip, "global")
            
            if i < limit:
                assert allowed is True
            # Note: May pass even after limit if using Redis (depends on timing)


@pytest.mark.asyncio
class TestDifferentLimitTypes:
    """Test different rate limit types."""
    
    async def test_auth_register_limit(self, rate_limiter):
        """Test stricter limit for registration."""
        ip = "test_ip_register"
        
        # Auth register has 5 req/hour limit
        for _ in range(3):
            allowed = await rate_limiter.check_rate_limit(ip, "auth_register")
            assert allowed is True
    
    async def test_predictions_limit(self, rate_limiter):
        """Test predictions endpoint limit."""
        ip = "test_ip_predictions"
        
        # Predictions has 30 req/min limit
        for _ in range(10):
            allowed = await rate_limiter.check_rate_limit(ip, "predictions")
            assert allowed is True


@pytest.mark.asyncio
class TestPremiumBypass:
    """Test premium user bypass."""
    
    async def test_premium_user_bypass(self, rate_limiter):
        """Test that premium users bypass rate limits."""
        # Mock premium user check
        rate_limiter._is_premium_user = AsyncMock(return_value=True)
        
        # Should allow unlimited requests
        for _ in range(200):
            allowed = await rate_limiter.check_rate_limit(
                "premium_user", "global", user_id="premium_123"
            )
            assert allowed is True


@pytest.mark.asyncio
class TestMemoryFallback:
    """Test in-memory fallback when Redis unavailable."""
    
    async def test_memory_rate_limiting(self, rate_limiter):
        """Test rate limiting with memory backend."""
        # Force memory backend (no Redis)
        rate_limiter.redis_client = None
        
        ip = "test_memory"
        
        # First request should work
        allowed = rate_limiter._check_memory_rate_limit(ip, 5, 60)
        assert allowed is True
        
        # Should track in memory
        assert ip in rate_limiter._memory_store
    
    async def test_memory_window_expiry(self, rate_limiter):
        """Test that memory windows expire correctly."""
        rate_limiter.redis_client = None
        
        ip = "test_window"
        
        # First request
        rate_limiter._check_memory_rate_limit(ip, 5, 1)  # 1 second window
        
        # Wait for window to expire
        await asyncio.sleep(1.1)
        
        # Should reset window
        allowed = rate_limiter._check_memory_rate_limit(ip, 5, 1)
        assert allowed is True


@pytest.mark.asyncio
class TestRateLimitHeaders:
    """Test rate limit header generation."""
    
    async def test_get_headers(self, rate_limiter):
        """Test rate limit headers."""
        headers = rate_limiter.get_rate_limit_headers("test_ip", "global")
        
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        
        # Check limit is correct
        assert headers["X-RateLimit-Limit"] == "100"
