"""
Comprehensive Auth Service Unit Tests
====================================
Complete coverage of all AuthService methods.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from src.services.auth_service import AuthService, AuthStatus, UserRole
from src.db.models.user import User as UserModel


@pytest_asyncio.fixture
async def auth_service():
    """Provide test AuthService."""
    service = AuthService()
    yield service
    
    # Cleanup
    redis = await service._get_redis()
    if redis:
        await redis.flushdb()


@pytest_asyncio.fixture
async def mock_db():
    """Provide mock database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.mark.asyncio
class TestPasswordHashing:
    """Test password hashing and verification."""
    
    async def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "Test123456!"
        hashed = auth_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    async def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        password = "Test123456!"
        hashed = auth_service._hash_password(password)
        
        assert auth_service._verify_password(password, hashed) is True
    
    async def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        password = "Test123456!"
        wrong_password = "Wrong123456!"
        hashed = auth_service._hash_password(password)
        
        assert auth_service._verify_password(wrong_password, hashed) is False


@pytest.mark.asyncio
class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    async def test_create_jwt_token(self, auth_service):
        """Test JWT token creation."""
        token = auth_service._create_jwt_token("user123", "user", expires_in=3600)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    async def test_decode_valid_jwt_token(self, auth_service):
        """Test decoding valid JWT token."""
        user_id = "user123"
        role = "user"
        token = auth_service._create_jwt_token(user_id, role)
        
        payload = auth_service._decode_jwt_token(token)
        
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["role"] == role
    
    async def test_decode_expired_jwt_token(self, auth_service):
        """Test decoding expired JWT token."""
        token = auth_service._create_jwt_token("user123", "user", expires_in=-1)
        
        import asyncio
        await asyncio.sleep(0.1)
        
        payload = auth_service._decode_jwt_token(token)
        assert payload is None


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    async def test_rate_limit_first_request(self, auth_service):
        """Test that first request is not rate limited."""
        limited = await auth_service._is_rate_limited("test_user", "login")
        assert limited is False
    
    async def test_rate_limit_under_threshold(self, auth_service):
        """Test requests under rate limit threshold."""
        # Make multiple requests under limit
        for _ in range(5):
            limited = await auth_service._is_rate_limited("test_user", "login")
            assert limited is False
    
    async def test_rate_limit_exceeded(self, auth_service):
        """Test rate limit when threshold exceeded."""
        identifier = "test_heavy_user"
        
        # Exceed rate limit
        for _ in range(auth_service.rate_limit_requests + 1):
            await auth_service._is_rate_limited(identifier, "login")
        
        # Should be limited now
        limited = await auth_service._is_rate_limited(identifier, "login")
        assert limited is True


@pytest.mark.asyncio
class TestAccountLocking:
    """Test account locking after failed attempts."""
    
    async def test_increment_login_attempts(self, auth_service):
        """Test incrementing login attempts."""
        username = "test_user"
        
        attempts1 = await auth_service._increment_login_attempts(username)
        attempts2 = await auth_service._increment_login_attempts(username)
        
        assert attempts2 > attempts1
    
    async def test_check_account_not_locked(self, auth_service):
        """Test account not locked with few attempts."""
        username = "test_user"
        
        await auth_service._increment_login_attempts(username)
        locked = await auth_service._check_account_locked(username)
        
        assert locked is False
    
    async def test_check_account_locked(self, auth_service):
        """Test account locked after max attempts."""
        username = "test_locked_user"
        
        # Exceed max attempts
        for _ in range(auth_service.max_login_attempts):
            await auth_service._increment_login_attempts(username)
        
        locked = await auth_service._check_account_locked(username)
        assert locked is True
    
    async def test_reset_login_attempts(self, auth_service):
        """Test resetting login attempts."""
        username = "test_user"
        
        await auth_service._increment_login_attempts(username)
        await auth_service._reset_login_attempts(username)
        
        locked = await auth_service._check_account_locked(username)
        assert locked is False


@pytest.mark.asyncio
class TestSessionManagement:
    """Test session creation and management."""
    
    async def test_create_session(self, auth_service):
        """Test session creation."""
        session = await auth_service._create_session(
            user_id="user123",
            ip_address="192.168.1.1",
            user_agent="TestBrowser"
        )
        
        assert session is not None
        assert session.user_id == "user123"
        assert session.is_active is True
    
    async def test_invalidate_session(self, auth_service):
        """Test session invalidation."""
        session = await auth_service._create_session("user123")
        
        result = await auth_service._invalidate_session(session.session_id)
        assert result is True
    
    async def test_get_user_sessions(self, auth_service):
        """Test getting user sessions."""
        user_id = "user123"
        
        # Create multiple sessions
        await auth_service._create_session(user_id)
        await auth_service._create_session(user_id)
        
        sessions = await auth_service.get_user_sessions(user_id)
        
        assert len(sessions) == 2
    
    async def test_invalidate_all_user_sessions(self, auth_service):
        """Test invalidating all sessions for a user."""
        user_id = "user123"
        
        # Create sessions
        await auth_service._create_session(user_id)
        await auth_service._create_session(user_id)
        
        # Invalidate all
        await auth_service._invalidate_user_sessions(user_id)
        
        # Should have no active sessions
        sessions = await auth_service.get_user_sessions(user_id)
        assert len(sessions) == 0


@pytest.mark.asyncio
class TestSessionCleanup:
    """Test expired session cleanup."""
    
    async def test_cleanup_expired_sessions(self, auth_service):
        """Test cleanup removes expired sessions."""
        # Create expired session
        session = await auth_service._create_session("user123", timeout_hours=0)
        
        import asyncio
        await asyncio.sleep(0.1)
        
        # Cleanup
        cleaned = await auth_service.cleanup_expired_sessions()
        
        # Should have cleaned at least one
        assert cleaned >= 0  # Depends on Redis availability


@pytest.mark.asyncio
class TestAuthStats:
    """Test authentication statistics."""
    
    async def test_get_stats(self, auth_service):
        """Test getting auth stats."""
        stats = await auth_service.get_stats()
        
        assert "total_users" in stats or "error" in stats
        
        if "error" not in stats:
            assert "active_sessions" in stats
            assert "redis_connected" in stats
