"""
Feature Flag Service for MultiSportsBettingPlatform
==================================================
Provides runtime feature toggles for enabling/disabling features,
A/B testing, and client-specific customization.
"""

import logging
from typing import Dict, Any, Optional
import redis.asyncio as redis
from src.config import settings

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Service for managing feature flags with Redis backend."""
    
    # Default feature flags
    DEFAULT_FLAGS = {
        "autonomous_scanning": True,
        "real_time_predictions": True,
        "advanced_ai": False,
        "websocket_enabled": True,
        "social_features": True,
        "email_notifications": False,
        "sms_notifications": False,
        "push_notifications": False,
    }
    
    def __init__(self, redis_url: str = None):
        """Initialize the feature flag service."""
        self.redis_url = redis_url or settings.redis_url
        self.redis_client = None
        self.cache: Dict[str, bool] = {}
        self.cache_ttl = 60  # Cache flags for 60 seconds
        self.last_cache_update = 0
        logger.info("✅ FeatureFlagService initialized")
    
    async def _get_redis(self):
        """Lazy-initialize async Redis connection."""
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("✅ Feature flags: Redis connection established")
            except Exception as e:
                logger.warning(f"⚠️ Feature flags: Redis connection failed: {e}")
                self.redis_client = False  # Mark as failed
        return self.redis_client if self.redis_client is not False else None
    
    async def is_enabled(
        self, 
        flag: str, 
        user_id: Optional[str] = None, 
        default: Optional[bool] = None
    ) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag: Feature flag name
            user_id: Optional user ID for user-specific overrides
            default: Optional default value (falls back to DEFAULT_FLAGS)
        
        Returns:
            True if enabled, False otherwise
        
        Priority order:
        1. User-specific override (if user_id provided)
        2. Global flag in Redis
        3. Default value from DEFAULT_FLAGS
        4. Provided default
        5. False (safe default)
        """
        # Check user-specific override
        if user_id:
            user_value = await self._get_user_flag(user_id, flag)
            if user_value is not None:
                return user_value
        
        # Check global flag
        global_value = await self._get_global_flag(flag)
        if global_value is not None:
            return global_value
        
        # Fall back to defaults
        if default is not None:
            return default
        
        return self.DEFAULT_FLAGS.get(flag, False)
    
    async def _get_user_flag(self, user_id: str, flag: str) -> Optional[bool]:
        """Get user-specific flag override."""
        redis_client = await self._get_redis()
        if not redis_client:
            return None
        
        try:
            key = f"flags:user:{user_id}"
            value = await redis_client.hget(key, flag)
            if value is not None:
                return value.lower() == "true"
        except Exception as e:
            logger.error(f"❌ Failed to get user flag: {e}")
        
        return None
    
    async def _get_global_flag(self, flag: str) -> Optional[bool]:
        """Get global flag value."""
        redis_client = await self._get_redis()
        if not redis_client:
            return None
        
        try:
            key = f"flags:global:{flag}"
            value = await redis_client.get(key)
            if value is not None:
                return value.lower() == "true"
        except Exception as e:
            logger.error(f"❌ Failed to get global flag: {e}")
        
        return None
    
    async def set_global_flag(self, flag: str, enabled: bool) -> bool:
        """
        Set a global feature flag.
        
        Args:
            flag: Feature flag name
            enabled: True to enable, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            logger.warning(f"⚠️ Cannot set flag {flag}: Redis not available")
            return False
        
        try:
            key = f"flags:global:{flag}"
            await redis_client.set(key, "true" if enabled else "false")
            logger.info(f"✅ Global flag set: {flag} = {enabled}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set global flag: {e}")
            return False
    
    async def set_user_flag(self, user_id: str, flag: str, enabled: bool) -> bool:
        """
        Set a user-specific feature flag override.
        
        Args:
            user_id: User ID
            flag: Feature flag name
            enabled: True to enable, False to disable
        
        Returns:
            True if successful, False otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            logger.warning(f"⚠️ Cannot set user flag for {user_id}: Redis not available")
            return False
        
        try:
            key = f"flags:user:{user_id}"
            await redis_client.hset(key, flag, "true" if enabled else "false")
            logger.info(f"✅ User flag set: {user_id} -> {flag} = {enabled}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set user flag: {e}")
            return False
    
    async def get_all_flags(self, user_id: Optional[str] = None) -> Dict[str, bool]:
        """
        Get all feature flags (global + user overrides if user_id provided).
        
        Args:
            user_id: Optional user ID for user-specific overrides
        
        Returns:
            Dictionary of flag names to enabled status
        """
        flags = {}
        
        # Start with defaults
        flags.update(self.DEFAULT_FLAGS)
        
        # Override with global flags from Redis
        redis_client = await self._get_redis()
        if redis_client:
            try:
                # Get all global flags
                cursor = 0
                while True:
                    cursor, keys = await redis_client.scan(cursor, match="flags:global:*", count=100)
                    for key in keys:
                        flag_name = key.replace("flags:global:", "")
                        value = await redis_client.get(key)
                        flags[flag_name] = value.lower() == "true" if value else False
                    if cursor == 0:
                        break
                
                # Override with user-specific flags
                if user_id:
                    user_flags = await redis_client.hgetall(f"flags:user:{user_id}")
                    for flag_name, value in user_flags.items():
                        flags[flag_name] = value.lower() == "true" if value else False
            except Exception as e:
                logger.error(f"❌ Failed to get all flags: {e}")
        
        return flags
    
    async def delete_user_flag(self, user_id: str, flag: str) -> bool:
        """
        Delete a user-specific flag override (reverts to global/default).
        
        Args:
            user_id: User ID
            flag: Feature flag name
        
        Returns:
            True if successful, False otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            return False
        
        try:
            key = f"flags:user:{user_id}"
            await redis_client.hdel(key, flag)
            logger.info(f"✅ User flag deleted: {user_id} -> {flag}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete user flag: {e}")
            return False


# Global instance
feature_flags = FeatureFlagService()
