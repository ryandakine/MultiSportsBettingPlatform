"""
Unit Tests for FeatureFlagService
=================================
Tests feature flag functionality including global flags, user overrides, and graceful degradation.
"""

import pytest
import pytest_asyncio
from src.services.feature_flags import FeatureFlagService


@pytest_asyncio.fixture
async def flag_service():
    """Provide a test FeatureFlagService instance."""
    service = FeatureFlagService()
    yield service
    
    # Cleanup
    redis_client = await service._get_redis()
    if redis_client:
        await redis_client.flushdb()


@pytest_asyncio.fixture
async def clean_redis(flag_service):
    """Clean Redis before each test."""
    redis_client = await flag_service._get_redis()
    if redis_client:
        await redis_client.flushdb()
    yield
    if redis_client:
        await redis_client.flushdb()


@pytest.mark.asyncio
class TestDefaultFlags:
    """Test default feature flag behavior."""
    
    async def test_default_flag_enabled(self, flag_service, clean_redis):
        """Test that default enabled flags return True."""
        enabled = await flag_service.is_enabled("autonomous_scanning")
        assert enabled is True
    
    async def test_default_flag_disabled(self, flag_service, clean_redis):
        """Test that default disabled flags return False."""
        enabled = await flag_service.is_enabled("advanced_ai")
        assert enabled is False
    
    async def test_unknown_flag_defaults_false(self, flag_service, clean_redis):
        """Test that unknown flags default to False."""
        enabled = await flag_service.is_enabled("unknown_feature")
        assert enabled is False
    
    async def test_custom_default_value(self, flag_service, clean_redis):
        """Test providing custom default value."""
        enabled = await flag_service.is_enabled("custom_flag", default=True)
        assert enabled is True


@pytest.mark.asyncio
class TestGlobalFlags:
    """Test global feature flag management."""
    
    async def test_set_global_flag(self, flag_service, clean_redis):
        """Test setting a global flag."""
        success = await flag_service.set_global_flag("test_feature", True)
        assert success is True
        
        enabled = await flag_service.is_enabled("test_feature")
        assert enabled is True
    
    async def test_override_default_flag(self, flag_service, clean_redis):
        """Test overriding a default flag value."""
        # Default is True
        assert await flag_service.is_enabled("autonomous_scanning") is True
        
        # Override to False
        await flag_service.set_global_flag("autonomous_scanning", False)
        assert await flag_service.is_enabled("autonomous_scanning") is False
    
    async def test_get_all_global_flags(self, flag_service, clean_redis):
        """Test getting all global flags."""
        await flag_service.set_global_flag("feature1", True)
        await flag_service.set_global_flag("feature2", False)
        
        all_flags = await flag_service.get_all_flags()
        
        # Should include defaults + custom flags
        assert "autonomous_scanning" in all_flags
        assert "feature1" in all_flags
        assert all_flags["feature1"] is True
        assert all_flags["feature2"] is False


@pytest.mark.asyncio
class TestUserSpecificFlags:
    """Test user-specific flag overrides."""
    
    async def test_set_user_flag(self, flag_service, clean_redis):
        """Test setting a user-specific flag."""
        success = await flag_service.set_user_flag("user123", "test_feature", True)
        assert success is True
        
        enabled = await flag_service.is_enabled("test_feature", user_id="user123")
        assert enabled is True
    
    async def test_user_override_global_flag(self, flag_service, clean_redis):
        """Test that user flags override global flags."""
        # Set global flag to False
        await flag_service.set_global_flag("advanced_ai", False)
        
        # Enable for specific user
        await flag_service.set_user_flag("premium_user", "advanced_ai", True)
        
        # Regular user sees False
        assert await flag_service.is_enabled("advanced_ai") is False
        
        # Premium user sees True
        assert await flag_service.is_enabled("advanced_ai", user_id="premium_user") is True
    
    async def test_delete_user_flag(self, flag_service, clean_redis):
        """Test deleting a user-specific flag override."""
        # Set user override
        await flag_service.set_user_flag("user123", "feature", True)
        assert await flag_service.is_enabled("feature", user_id="user123") is True
        
        # Delete override
        success = await flag_service.delete_user_flag("user123", "feature")
        assert success is True
        
        # Should revert to default/global
        assert await flag_service.is_enabled("feature", user_id="user123") is False
    
    async def test_get_all_user_flags(self, flag_service, clean_redis):
        """Test getting all flags for a specific user."""
        # Set global and user-specific flags
        await flag_service.set_global_flag("global_feature", True)
        await flag_service.set_user_flag("user123", "user_feature", True)
        
        user_flags = await flag_service.get_all_flags(user_id="user123")
        
        assert user_flags["global_feature"] is True
        assert user_flags["user_feature"] is True


@pytest.mark.asyncio
class TestFlagPriority:
    """Test feature flag priority: user > global > default."""
    
    async def test_priority_user_beats_global(self, flag_service, clean_redis):
        """Test that user flags override global flags."""
        await flag_service.set_global_flag("feature", False)
        await flag_service.set_user_flag("user1", "feature", True)
        
        assert await flag_service.is_enabled("feature") is False
        assert await flag_service.is_enabled("feature", user_id="user1") is True
    
    async def test_priority_global_beats_default(self, flag_service, clean_redis):
        """Test that global flags override defaults."""
        # Default for advanced_ai is False
        assert await flag_service.is_enabled("advanced_ai") is False
        
        # Set global to True
        await flag_service.set_global_flag("advanced_ai", True)
        assert await flag_service.is_enabled("advanced_ai") is True
    
    async def test_priority_custom_default(self, flag_service, clean_redis):
        """Test custom default is lowest priority."""
        # Custom default
        assert await flag_service.is_enabled("new_feature", default=True) is True
        
        # Global overrides custom default
        await flag_service.set_global_flag("new_feature", False)
        assert await flag_service.is_enabled("new_feature", default=True) is False
        
        # User overrides global
        await flag_service.set_user_flag("user1", "new_feature", True)
        assert await flag_service.is_enabled("new_feature", user_id="user1", default=False) is True


@pytest.mark.asyncio
class TestRedisFailure:
    """Test graceful degradation when Redis is unavailable."""
    
    async def test_is_enabled_redis_unavailable(self):
        """Test that flags fall back to defaults without Redis."""
        service = FeatureFlagService(redis_url="redis://invalid:9999")
        
        # Should use default values
        enabled = await service.is_enabled("autonomous_scanning")
        assert enabled is True  # Default value
    
    async def test_set_flag_redis_unavailable(self):
        """Test that setting flag fails gracefully without Redis."""
        service = FeatureFlagService(redis_url="redis://invalid:9999")
        
        success = await service.set_global_flag("feature", True)
        assert success is False
    
    async def test_get_all_flags_redis_unavailable(self):
        """Test that get_all_flags returns defaults without Redis."""
        service = FeatureFlagService(redis_url="redis://invalid:9999")
        
        flags = await service.get_all_flags()
        # Should return DEFAULT_FLAGS
        assert "autonomous_scanning" in flags
        assert flags["autonomous_scanning"] is True


@pytest.mark.asyncio
class TestMultiUser:
    """Test feature flags with multiple users."""
    
    async def test_different_users_different_flags(self, flag_service, clean_redis):
        """Test that different users can have different flag values."""
        await flag_service.set_user_flag("user1", "feature", True)
        await flag_service.set_user_flag("user2", "feature", False)
        
        assert await flag_service.is_enabled("feature", user_id="user1") is True
        assert await flag_service.is_enabled("feature", user_id="user2") is False
    
    async def test_ab_testing_scenario(self, flag_service, clean_redis):
        """Test A/B testing scenario with control and treatment groups."""
        # Global default: False (control group)
        await flag_service.set_global_flag("new_ui", False)
        
        # Treatment group
        await flag_service.set_user_flag("test_user_1", "new_ui", True)
        await flag_service.set_user_flag("test_user_2", "new_ui", True)
        
        # Control sees old UI
        assert await flag_service.is_enabled("new_ui") is False
        assert await flag_service.is_enabled("new_ui", user_id="control_user") is False
        
        # Treatment sees new UI
        assert await flag_service.is_enabled("new_ui", user_id="test_user_1") is True
        assert await flag_service.is_enabled("new_ui", user_id="test_user_2") is True
