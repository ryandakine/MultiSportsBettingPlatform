"""
Notification Service
===================
Comprehensive notification management system with filtering, routing, and persistence.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Types of notifications."""
    SYSTEM_ALERT = "system_alert"
    PREDICTION_UPDATE = "prediction_update"
    BETTING_ALERT = "betting_alert"
    SPORT_UPDATE = "sport_update"
    USER_ACTIVITY = "user_activity"
    SOCIAL_INTERACTION = "social_interaction"
    MARKETING = "marketing"
    SECURITY = "security"

class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"

class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

@dataclass
class Notification:
    """Notification data structure."""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    timestamp: datetime
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    channels: List[NotificationChannel] = None
    data: Dict[str, Any] = None
    expires_at: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    read_at: Optional[datetime] = None
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = [NotificationChannel.IN_APP]
        if self.data is None:
            self.data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "channels": [c.value for c in self.channels],
            "data": self.data,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "delivery_attempts": self.delivery_attempts,
            "max_delivery_attempts": self.max_delivery_attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            title=data["title"],
            message=data["message"],
            priority=NotificationPriority(data["priority"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sender_id=data.get("sender_id"),
            recipient_id=data.get("recipient_id"),
            channels=[NotificationChannel(c) for c in data.get("channels", ["in_app"])],
            data=data.get("data", {}),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            status=NotificationStatus(data.get("status", "pending")),
            read_at=datetime.fromisoformat(data["read_at"]) if data.get("read_at") else None,
            delivery_attempts=data.get("delivery_attempts", 0),
            max_delivery_attempts=data.get("max_delivery_attempts", 3)
        )

@dataclass
class NotificationPreference:
    """User notification preferences."""
    user_id: str
    notification_types: Dict[NotificationType, bool]
    channels: Dict[NotificationChannel, bool]
    priority_levels: Dict[NotificationPriority, bool]
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    timezone: str = "UTC"
    marketing_enabled: bool = False
    frequency_limit: Optional[int] = None  # max notifications per hour
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "notification_types": {k.value: v for k, v in self.notification_types.items()},
            "channels": {k.value: v for k, v in self.channels.items()},
            "priority_levels": {k.value: v for k, v in self.priority_levels.items()},
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "timezone": self.timezone,
            "marketing_enabled": self.marketing_enabled,
            "frequency_limit": self.frequency_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationPreference':
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            notification_types={NotificationType(k): v for k, v in data.get("notification_types", {}).items()},
            channels={NotificationChannel(k): v for k, v in data.get("channels", {}).items()},
            priority_levels={NotificationPriority(k): v for k, v in data.get("priority_levels", {}).items()},
            quiet_hours_start=data.get("quiet_hours_start"),
            quiet_hours_end=data.get("quiet_hours_end"),
            timezone=data.get("timezone", "UTC"),
            marketing_enabled=data.get("marketing_enabled", False),
            frequency_limit=data.get("frequency_limit")
        )

class NotificationFilter:
    """Filter notifications based on user preferences and rules."""
    
    def __init__(self):
        self.default_preferences = NotificationPreference(
            user_id="default",
            notification_types={
                NotificationType.SYSTEM_ALERT: True,
                NotificationType.PREDICTION_UPDATE: True,
                NotificationType.BETTING_ALERT: True,
                NotificationType.SPORT_UPDATE: True,
                NotificationType.USER_ACTIVITY: True,
                NotificationType.SOCIAL_INTERACTION: True,
                NotificationType.MARKETING: False,
                NotificationType.SECURITY: True
            },
            channels={
                NotificationChannel.WEBSOCKET: True,
                NotificationChannel.EMAIL: False,
                NotificationChannel.PUSH: False,
                NotificationChannel.SMS: False,
                NotificationChannel.IN_APP: True
            },
            priority_levels={
                NotificationPriority.LOW: True,
                NotificationPriority.NORMAL: True,
                NotificationPriority.HIGH: True,
                NotificationPriority.URGENT: True
            }
        )
    
    def should_deliver_notification(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Determine if notification should be delivered based on preferences."""
        # Check if notification type is enabled
        if not preferences.notification_types.get(notification.type, False):
            logger.debug(f"❌ Notification type {notification.type.value} disabled for user {preferences.user_id}")
            return False
        
        # Check if priority level is enabled
        if not preferences.priority_levels.get(notification.priority, False):
            logger.debug(f"❌ Priority level {notification.priority.value} disabled for user {preferences.user_id}")
            return False
        
        # Check quiet hours
        if self._is_in_quiet_hours(preferences):
            # Allow urgent notifications during quiet hours
            if notification.priority != NotificationPriority.URGENT:
                logger.debug(f"❌ Quiet hours active for user {preferences.user_id}")
                return False
        
        # Check marketing preferences
        if notification.type == NotificationType.MARKETING and not preferences.marketing_enabled:
            logger.debug(f"❌ Marketing notifications disabled for user {preferences.user_id}")
            return False
        
        return True
    
    def get_delivery_channels(self, notification: Notification, preferences: NotificationPreference) -> List[NotificationChannel]:
        """Get allowed delivery channels for notification."""
        allowed_channels = []
        
        for channel in notification.channels:
            if preferences.channels.get(channel, False):
                allowed_channels.append(channel)
        
        return allowed_channels
    
    def _is_in_quiet_hours(self, preferences: NotificationPreference) -> bool:
        """Check if current time is within quiet hours."""
        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False
        
        try:
            from datetime import time
            
            current_time = datetime.now().time()
            start_time = time.fromisoformat(preferences.quiet_hours_start)
            end_time = time.fromisoformat(preferences.quiet_hours_end)
            
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:  # Quiet hours span midnight
                return current_time >= start_time or current_time <= end_time
                
        except Exception as e:
            logger.error(f"❌ Error checking quiet hours: {e}")
            return False

class NotificationRouter:
    """Route notifications to appropriate delivery channels."""
    
    def __init__(self, websocket_manager, redis_client: redis.Redis):
        self.websocket_manager = websocket_manager
        self.redis_client = redis_client
        self.filter = NotificationFilter()
        self.delivery_handlers = {
            NotificationChannel.WEBSOCKET: self._deliver_websocket,
            NotificationChannel.EMAIL: self._deliver_email,
            NotificationChannel.PUSH: self._deliver_push,
            NotificationChannel.SMS: self._deliver_sms,
            NotificationChannel.IN_APP: self._deliver_in_app
        }
    
    async def route_notification(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Route notification to appropriate channels."""
        try:
            # Check if notification should be delivered
            if not self.filter.should_deliver_notification(notification, preferences):
                return False
            
            # Get allowed delivery channels
            allowed_channels = self.filter.get_delivery_channels(notification, preferences)
            
            if not allowed_channels:
                logger.warning(f"⚠️ No allowed delivery channels for notification {notification.id}")
                return False
            
            # Deliver to each allowed channel
            delivery_results = []
            for channel in allowed_channels:
                handler = self.delivery_handlers.get(channel)
                if handler:
                    try:
                        result = await handler(notification, preferences)
                        delivery_results.append((channel, result))
                    except Exception as e:
                        logger.error(f"❌ Failed to deliver notification {notification.id} via {channel.value}: {e}")
                        delivery_results.append((channel, False))
                else:
                    logger.warning(f"⚠️ No handler for channel {channel.value}")
                    delivery_results.append((channel, False))
            
            # Update notification status
            successful_deliveries = [r for r in delivery_results if r[1]]
            if successful_deliveries:
                notification.status = NotificationStatus.SENT
                logger.info(f"✅ Notification {notification.id} delivered via {len(successful_deliveries)} channels")
                return True
            else:
                notification.status = NotificationStatus.FAILED
                logger.error(f"❌ Notification {notification.id} failed to deliver via any channel")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error routing notification {notification.id}: {e}")
            return False
    
    async def _deliver_websocket(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Deliver notification via WebSocket."""
        try:
            if notification.recipient_id:
                # Send to specific user
                from src.services.websocket_service import WebSocketMessage, MessageType
                
                ws_message = WebSocketMessage(
                    type=MessageType.NOTIFICATION,
                    data={
                        "notification": notification.to_dict()
                    },
                    timestamp=datetime.now(),
                    user_id=notification.recipient_id
                )
                
                await self.websocket_manager.send_to_user(notification.recipient_id, ws_message)
                return True
            else:
                # Broadcast to all users
                from src.services.websocket_service import WebSocketMessage, MessageType
                
                ws_message = WebSocketMessage(
                    type=MessageType.NOTIFICATION,
                    data={
                        "notification": notification.to_dict()
                    },
                    timestamp=datetime.now()
                )
                
                await self.websocket_manager.broadcast_message(ws_message)
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket delivery failed: {e}")
            return False
    
    async def _deliver_email(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Deliver notification via email."""
        # TODO: Implement email delivery
        logger.info(f"📧 Email delivery not implemented for notification {notification.id}")
        return False
    
    async def _deliver_push(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Deliver notification via push notification."""
        # TODO: Implement push notification delivery
        logger.info(f"📱 Push notification delivery not implemented for notification {notification.id}")
        return False
    
    async def _deliver_sms(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Deliver notification via SMS."""
        # TODO: Implement SMS delivery
        logger.info(f"📱 SMS delivery not implemented for notification {notification.id}")
        return False
    
    async def _deliver_in_app(self, notification: Notification, preferences: NotificationPreference) -> bool:
        """Deliver notification in-app (same as WebSocket for now)."""
        return await self._deliver_websocket(notification, preferences)

class NotificationPersistence:
    """Persist notifications in Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.notification_prefix = "notification:"
        self.user_notifications_prefix = "user_notifications:"
        self.preferences_prefix = "notification_preferences:"
    
    async def store_notification(self, notification: Notification) -> bool:
        """Store notification in Redis."""
        try:
            # Store notification data
            notification_key = f"{self.notification_prefix}{notification.id}"
            await self.redis_client.hset(notification_key, mapping=notification.to_dict())
            await self.redis_client.expire(notification_key, 86400 * 30)  # 30 days TTL
            
            # Add to user's notification list if recipient specified
            if notification.recipient_id:
                user_key = f"{self.user_notifications_prefix}{notification.recipient_id}"
                await self.redis_client.lpush(user_key, notification.id)
                await self.redis_client.ltrim(user_key, 0, 999)  # Keep last 1000 notifications
                await self.redis_client.expire(user_key, 86400 * 90)  # 90 days TTL
            
            logger.info(f"✅ Notification {notification.id} stored in Redis")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store notification {notification.id}: {e}")
            return False
    
    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Retrieve notification from Redis."""
        try:
            notification_key = f"{self.notification_prefix}{notification_id}"
            data = await self.redis_client.hgetall(notification_key)
            
            if data:
                return Notification.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification {notification_id}: {e}")
            return None
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a specific user."""
        try:
            user_key = f"{self.user_notifications_prefix}{user_id}"
            notification_ids = await self.redis_client.lrange(user_key, offset, offset + limit - 1)
            
            notifications = []
            for notification_id in notification_ids:
                notification = await self.get_notification(notification_id)
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Failed to get notifications for user {user_id}: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read."""
        try:
            notification = await self.get_notification(notification_id)
            if notification:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now()
                await self.store_notification(notification)
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to mark notification {notification_id} as read: {e}")
            return False
    
    async def store_preferences(self, preferences: NotificationPreference) -> bool:
        """Store user notification preferences."""
        try:
            preferences_key = f"{self.preferences_prefix}{preferences.user_id}"
            await self.redis_client.hset(preferences_key, mapping=preferences.to_dict())
            await self.redis_client.expire(preferences_key, 86400 * 365)  # 1 year TTL
            
            logger.info(f"✅ Preferences stored for user {preferences.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store preferences for user {preferences.user_id}: {e}")
            return False
    
    async def get_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        """Get user notification preferences."""
        try:
            preferences_key = f"{self.preferences_prefix}{user_id}"
            data = await self.redis_client.hgetall(preferences_key)
            
            if data:
                return NotificationPreference.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get preferences for user {user_id}: {e}")
            return None

class NotificationService:
    """Main notification service."""
    
    def __init__(self, redis_client: redis.Redis, websocket_manager):
        self.redis_client = redis_client
        self.websocket_manager = websocket_manager
        self.persistence = NotificationPersistence(redis_client)
        self.router = NotificationRouter(websocket_manager, redis_client)
        self.filter = NotificationFilter()
        self.notification_counter = 0
    
    async def send_notification(self, notification: Notification, user_id: Optional[str] = None) -> str:
        """Send a notification."""
        try:
            # Generate notification ID if not provided
            if not notification.id:
                self.notification_counter += 1
                notification.id = f"notif_{int(datetime.now().timestamp())}_{self.notification_counter}"
            
            # Set recipient if specified
            if user_id:
                notification.recipient_id = user_id
            
            # Get user preferences
            preferences = await self.persistence.get_preferences(user_id) if user_id else self.filter.default_preferences
            
            # Store notification
            await self.persistence.store_notification(notification)
            
            # Route notification
            delivery_success = await self.router.route_notification(notification, preferences)
            
            if delivery_success:
                logger.info(f"✅ Notification {notification.id} sent successfully")
            else:
                logger.warning(f"⚠️ Notification {notification.id} delivery failed")
            
            return notification.id
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
            raise
    
    async def send_bulk_notification(self, notification: Notification, user_ids: List[str]) -> Dict[str, Any]:
        """Send notification to multiple users."""
        results = {
            "successful": [],
            "failed": [],
            "total": len(user_ids)
        }
        
        for user_id in user_ids:
            try:
                notification_id = await self.send_notification(notification, user_id)
                results["successful"].append({"user_id": user_id, "notification_id": notification_id})
            except Exception as e:
                results["failed"].append({"user_id": user_id, "error": str(e)})
        
        logger.info(f"📡 Bulk notification sent: {len(results['successful'])}/{results['total']} successful")
        return results
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a user."""
        return await self.persistence.get_user_notifications(user_id, limit, offset)
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read."""
        return await self.persistence.mark_notification_read(notification_id, user_id)
    
    async def update_preferences(self, user_id: str, preferences: NotificationPreference) -> bool:
        """Update user notification preferences."""
        preferences.user_id = user_id
        return await self.persistence.store_preferences(preferences)
    
    async def get_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        """Get user notification preferences."""
        return await self.persistence.get_preferences(user_id)
    
    async def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics for a user."""
        try:
            notifications = await self.get_user_notifications(user_id, limit=1000)
            
            total_notifications = len(notifications)
            unread_notifications = len([n for n in notifications if n.status == NotificationStatus.SENT])
            read_notifications = len([n for n in notifications if n.status == NotificationStatus.READ])
            
            # Count by type
            type_counts = defaultdict(int)
            for notification in notifications:
                type_counts[notification.type.value] += 1
            
            # Count by priority
            priority_counts = defaultdict(int)
            for notification in notifications:
                priority_counts[notification.priority.value] += 1
            
            return {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "read_notifications": read_notifications,
                "read_rate": round((read_notifications / total_notifications) * 100, 2) if total_notifications > 0 else 0,
                "type_distribution": dict(type_counts),
                "priority_distribution": dict(priority_counts)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification stats for user {user_id}: {e}")
            return {}

# Global notification service instance
notification_service = None

async def initialize_notification_service(redis_client: redis.Redis, websocket_manager):
    """Initialize the global notification service."""
    global notification_service
    notification_service = NotificationService(redis_client, websocket_manager)
    logger.info("🚀 Notification service initialized")
    return notification_service 