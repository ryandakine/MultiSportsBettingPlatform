"""
Enhanced WebSocket Service for Real-Time Communication
====================================================
Advanced WebSocket management with authentication, Redis integration, and comprehensive error handling.
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import HTTPBearer
import jwt
from src.config import settings
from src.services.message_broadcasting import initialize_message_broadcaster, MessageBroadcaster
from src.services.notification_service import initialize_notification_service, NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStatus(str, Enum):
    """WebSocket connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"

class MessageType(str, Enum):
    """WebSocket message types."""
    AUTHENTICATION = "authentication"
    PREDICTION_UPDATE = "prediction_update"
    NOTIFICATION = "notification"
    SYSTEM_ALERT = "system_alert"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    WELCOME = "welcome"
    CONNECTION_STATUS = "connection_status"

@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id
        }

@dataclass
class ConnectionInfo:
    """Connection information for a WebSocket client."""
    websocket: WebSocket
    user_id: Optional[str] = None
    session_id: str
    client_id: str
    connected_at: datetime
    last_activity: datetime
    status: ConnectionStatus
    subscriptions: Set[str]
    user_preferences: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "client_id": self.client_id,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "subscriptions": list(self.subscriptions),
            "user_preferences": self.user_preferences
        }

class WebSocketAuthenticationService:
    """Handle WebSocket authentication using JWT tokens."""
    
    def __init__(self):
        self.security = HTTPBearer()
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
    
    async def authenticate_websocket(self, token: str) -> Optional[str]:
        """Authenticate WebSocket connection using JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id:
                logger.info(f"✅ WebSocket authenticated for user: {user_id}")
                return user_id
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ JWT token expired for WebSocket authentication")
        except jwt.InvalidTokenError as e:
            logger.error(f"❌ Invalid JWT token for WebSocket: {e}")
        except Exception as e:
            logger.error(f"❌ WebSocket authentication error: {e}")
        
        return None

class RedisWebSocketManager:
    """Redis-based WebSocket connection management with connection pool and health monitoring."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.connection_prefix = "websocket:connection:"
        self.channel_prefix = "websocket:channel:"
        self.health_check_interval = 30  # seconds
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1  # seconds, will be exponential
        self.connection_pool_size = 10
        self.active_connections = 0
        self.health_status = "unknown"
        self.last_health_check = None
    
    async def connect_redis(self):
        """Connect to Redis with retry logic and health monitoring."""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                # Create Redis connection with connection pool
                self.redis_client = redis.from_url(
                    self.redis_url, 
                    decode_responses=True,
                    max_connections=self.connection_pool_size,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30
                )
                
                # Test connection
                await self.redis_client.ping()
                self.health_status = "healthy"
                self.last_health_check = datetime.now()
                self.reconnect_attempts = 0
                
                logger.info(f"✅ Redis connected successfully (pool size: {self.connection_pool_size})")
                
                # Start health monitoring
                asyncio.create_task(self._health_monitor())
                
                return True
                
            except Exception as e:
                self.reconnect_attempts += 1
                self.health_status = "unhealthy"
                delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # Exponential backoff
                
                logger.error(f"❌ Redis connection attempt {self.reconnect_attempts} failed: {e}")
                logger.info(f"⏳ Retrying in {delay} seconds...")
                
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ Failed to connect to Redis after {self.max_reconnect_attempts} attempts")
                    return False
        
        return False
    
    async def _health_monitor(self):
        """Monitor Redis connection health."""
        while True:
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    self.health_status = "healthy"
                    self.last_health_check = datetime.now()
                    
                    # Reset reconnect attempts on successful health check
                    if self.reconnect_attempts > 0:
                        self.reconnect_attempts = 0
                        logger.info("✅ Redis connection recovered")
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.health_status = "unhealthy"
                logger.warning(f"⚠️ Redis health check failed: {e}")
                
                # Attempt reconnection if connection is lost
                if not self.redis_client:
                    logger.info("🔄 Attempting Redis reconnection...")
                    await self.connect_redis()
                
                await asyncio.sleep(self.health_check_interval)
    
    async def _ensure_connection(self):
        """Ensure Redis connection is available."""
        if not self.redis_client or self.health_status != "healthy":
            logger.warning("⚠️ Redis connection not healthy, attempting reconnection...")
            await self.connect_redis()
        
        return self.redis_client is not None and self.health_status == "healthy"
    
    async def store_connection(self, connection_info: ConnectionInfo):
        """Store connection information in Redis with connection pool management."""
        if not await self._ensure_connection():
            logger.warning("⚠️ Redis not available, skipping connection storage")
            return
        
        try:
            key = f"{self.connection_prefix}{connection_info.session_id}"
            
            # Store connection data with TTL
            await self.redis_client.hset(key, mapping=connection_info.to_dict())
            await self.redis_client.expire(key, 3600)  # 1 hour TTL
            
            # Update connection pool stats
            self.active_connections += 1
            
            # Store in connection index for quick lookup
            await self.redis_client.sadd("websocket:active_connections", connection_info.session_id)
            
            logger.info(f"✅ Connection stored in Redis: {connection_info.session_id} (pool: {self.active_connections})")
            
        except Exception as e:
            logger.error(f"❌ Failed to store connection in Redis: {e}")
            # Attempt reconnection on failure
            await self._ensure_connection()
    
    async def remove_connection(self, session_id: str):
        """Remove connection from Redis with connection pool management."""
        if not await self._ensure_connection():
            logger.warning("⚠️ Redis not available, skipping connection removal")
            return
        
        try:
            key = f"{self.connection_prefix}{session_id}"
            
            # Remove connection data
            await self.redis_client.delete(key)
            
            # Remove from connection index
            await self.redis_client.srem("websocket:active_connections", session_id)
            
            # Update connection pool stats
            self.active_connections = max(0, self.active_connections - 1)
            
            logger.info(f"✅ Connection removed from Redis: {session_id} (pool: {self.active_connections})")
            
        except Exception as e:
            logger.error(f"❌ Failed to remove connection from Redis: {e}")
            # Attempt reconnection on failure
            await self._ensure_connection()
    
    async def publish_message(self, channel: str, message: WebSocketMessage):
        """Publish message to Redis channel with connection pool management."""
        if not await self._ensure_connection():
            logger.warning("⚠️ Redis not available, skipping message publish")
            return
        
        try:
            channel_key = f"{self.channel_prefix}{channel}"
            message_data = json.dumps(message.to_dict())
            
            # Publish with retry logic
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    await self.redis_client.publish(channel_key, message_data)
                    logger.debug(f"✅ Message published to channel: {channel}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"⚠️ Publish retry {retry_count}/{max_retries} for channel {channel}: {e}")
                        await asyncio.sleep(0.1 * retry_count)  # Small delay before retry
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"❌ Failed to publish message to Redis: {e}")
            # Attempt reconnection on failure
            await self._ensure_connection()
    
    async def subscribe_to_channel(self, channel: str, callback):
        """Subscribe to Redis channel with connection pool management."""
        if not await self._ensure_connection():
            logger.warning("⚠️ Redis not available, skipping subscription")
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            channel_key = f"{self.channel_prefix}{channel}"
            
            # Subscribe with retry logic
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    await pubsub.subscribe(channel_key)
                    logger.info(f"✅ Subscribed to channel: {channel}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"⚠️ Subscription retry {retry_count}/{max_retries} for channel {channel}: {e}")
                        await asyncio.sleep(0.1 * retry_count)
                    else:
                        raise e
            
            # Listen for messages with error handling
            async for message in pubsub.listen():
                try:
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        await callback(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in Redis message: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing Redis message: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Redis subscription error: {e}")
            # Attempt reconnection on failure
            await self._ensure_connection()
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get Redis connection pool statistics."""
        if not await self._ensure_connection():
            return {
                "redis_status": "unavailable",
                "active_connections": 0,
                "pool_size": self.connection_pool_size,
                "health_status": self.health_status,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
            }
        
        try:
            # Get active connections from Redis
            active_connections = await self.redis_client.scard("websocket:active_connections")
            
            return {
                "redis_status": "healthy",
                "active_connections": active_connections,
                "pool_size": self.connection_pool_size,
                "pool_utilization": round((active_connections / self.connection_pool_size) * 100, 2),
                "health_status": self.health_status,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "reconnect_attempts": self.reconnect_attempts
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get Redis stats: {e}")
            return {
                "redis_status": "error",
                "active_connections": 0,
                "pool_size": self.connection_pool_size,
                "health_status": self.health_status,
                "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
                "error": str(e)
            }

class EnhancedWebSocketManager:
    """Enhanced WebSocket connection manager with authentication and Redis integration."""
    
    def __init__(self):
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.auth_service = WebSocketAuthenticationService()
        self.redis_manager = RedisWebSocketManager()
        self.message_broadcaster: Optional[MessageBroadcaster] = None
        self.notification_service: Optional[NotificationService] = None
        self.connection_counter = 0
        self.max_connections = 10000
        self.heartbeat_interval = 30  # seconds
        
    async def initialize(self):
        """Initialize the WebSocket manager."""
        await self.redis_manager.connect_redis()
        
        # Initialize message broadcaster
        if self.redis_manager.redis_client:
            self.message_broadcaster = await initialize_message_broadcaster(
                self.redis_manager.redis_client, 
                self
            )
            
            # Initialize notification service
            self.notification_service = await initialize_notification_service(
                self.redis_manager.redis_client,
                self
            )
        
        logger.info("🚀 Enhanced WebSocket Manager initialized with message broadcasting and notifications")
    
    async def connect(self, websocket: WebSocket, client_data: Dict[str, Any]) -> ConnectionInfo:
        """Connect a new WebSocket client with authentication."""
        try:
            await websocket.accept()
            
            # Generate session ID
            session_id = f"session_{int(datetime.now().timestamp())}_{self.connection_counter}"
            self.connection_counter += 1
            
            # Create connection info
            connection_info = ConnectionInfo(
                websocket=websocket,
                session_id=session_id,
                client_id=client_data.get("client_id", f"client_{session_id}"),
                connected_at=datetime.now(),
                last_activity=datetime.now(),
                status=ConnectionStatus.CONNECTED,
                subscriptions=set(),
                user_preferences=client_data.get("preferences", {})
            )
            
            # Store in memory
            self.active_connections[session_id] = connection_info
            
            # Store in Redis
            await self.redis_manager.store_connection(connection_info)
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                type=MessageType.WELCOME,
                data={
                    "message": "Welcome to MultiSportsBettingPlatform! 🚀",
                    "session_id": session_id,
                    "client_id": connection_info.client_id,
                    "features": ["real-time_predictions", "notifications", "live_updates"]
                },
                timestamp=datetime.now(),
                session_id=session_id
            )
            
            await self.send_message(connection_info, welcome_message)
            
            logger.info(f"🔌 New WebSocket connection: {session_id}")
            return connection_info
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            raise
    
    async def authenticate_connection(self, connection_info: ConnectionInfo, token: str):
        """Authenticate an existing connection."""
        try:
            user_id = await self.auth_service.authenticate_websocket(token)
            if user_id:
                connection_info.user_id = user_id
                connection_info.status = ConnectionStatus.AUTHENTICATED
                
                # Update in Redis
                await self.redis_manager.store_connection(connection_info)
                
                # Send authentication success message
                auth_message = WebSocketMessage(
                    type=MessageType.AUTHENTICATION,
                    data={
                        "status": "authenticated",
                        "user_id": user_id,
                        "message": "Authentication successful! 🎉"
                    },
                    timestamp=datetime.now(),
                    user_id=user_id,
                    session_id=connection_info.session_id
                )
                
                await self.send_message(connection_info, auth_message)
                logger.info(f"✅ Connection authenticated: {user_id}")
                return True
            else:
                connection_info.status = ConnectionStatus.UNAUTHENTICATED
                await self.redis_manager.store_connection(connection_info)
                logger.warning(f"⚠️ Authentication failed for session: {connection_info.session_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def disconnect(self, session_id: str):
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            connection_info = self.active_connections[session_id]
            
            # Update status
            connection_info.status = ConnectionStatus.DISCONNECTED
            
            # Remove from memory
            del self.active_connections[session_id]
            
            # Remove from Redis
            await self.redis_manager.remove_connection(session_id)
            
            logger.info(f"🔌 WebSocket disconnected: {session_id}")
    
    async def send_message(self, connection_info: ConnectionInfo, message: WebSocketMessage):
        """Send a message to a specific client."""
        try:
            connection_info.last_activity = datetime.now()
            await connection_info.websocket.send_text(json.dumps(message.to_dict()))
            logger.debug(f"📤 Message sent to {connection_info.session_id}: {message.type.value}")
        except Exception as e:
            logger.error(f"❌ Failed to send message to {connection_info.session_id}: {e}")
            await self.disconnect(connection_info.session_id)
    
    async def broadcast_message(self, message: WebSocketMessage, filter_func=None):
        """Broadcast a message to all connected clients."""
        disconnected = []
        
        for session_id, connection_info in self.active_connections.items():
            try:
                # Apply filter if provided
                if filter_func and not filter_func(connection_info):
                    continue
                
                await self.send_message(connection_info, message)
                
            except Exception as e:
                logger.error(f"❌ Broadcast error for {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected clients
        for session_id in disconnected:
            await self.disconnect(session_id)
        
        logger.info(f"📡 Broadcasted message to {len(self.active_connections) - len(disconnected)} clients")
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send a message to all connections of a specific user."""
        user_connections = [
            conn for conn in self.active_connections.values()
            if conn.user_id == user_id
        ]
        
        for connection_info in user_connections:
            await self.send_message(connection_info, message)
        
        logger.info(f"📤 Sent message to user {user_id} ({len(user_connections)} connections)")
    
    async def subscribe_to_channel(self, connection_info: ConnectionInfo, channel: str):
        """Subscribe a connection to a specific channel."""
        connection_info.subscriptions.add(channel)
        await self.redis_manager.store_connection(connection_info)
        
        # Send subscription confirmation
        sub_message = WebSocketMessage(
            type=MessageType.CONNECTION_STATUS,
            data={
                "action": "subscribed",
                "channel": channel,
                "subscriptions": list(connection_info.subscriptions)
            },
            timestamp=datetime.now(),
            user_id=connection_info.user_id,
            session_id=connection_info.session_id
        )
        
        await self.send_message(connection_info, sub_message)
        logger.info(f"📡 {connection_info.session_id} subscribed to {channel}")
    
    async def unsubscribe_from_channel(self, connection_info: ConnectionInfo, channel: str):
        """Unsubscribe a connection from a specific channel."""
        connection_info.subscriptions.discard(channel)
        await self.redis_manager.store_connection(connection_info)
        
        # Send unsubscription confirmation
        unsub_message = WebSocketMessage(
            type=MessageType.CONNECTION_STATUS,
            data={
                "action": "unsubscribed",
                "channel": channel,
                "subscriptions": list(connection_info.subscriptions)
            },
            timestamp=datetime.now(),
            user_id=connection_info.user_id,
            session_id=connection_info.session_id
        )
        
        await self.send_message(connection_info, unsub_message)
        logger.info(f"📡 {connection_info.session_id} unsubscribed from {channel}")
    
    async def handle_heartbeat(self, connection_info: ConnectionInfo):
        """Handle client heartbeat/ping."""
        connection_info.last_activity = datetime.now()
        
        pong_message = WebSocketMessage(
            type=MessageType.PONG,
            data={"timestamp": datetime.now().isoformat()},
            timestamp=datetime.now(),
            user_id=connection_info.user_id,
            session_id=connection_info.session_id
        )
        
        await self.send_message(connection_info, pong_message)
        logger.debug(f"💓 Heartbeat from {connection_info.session_id}")
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections."""
        current_time = datetime.now()
        inactive_threshold = timedelta(minutes=5)
        inactive_connections = []
        
        for session_id, connection_info in self.active_connections.items():
            if current_time - connection_info.last_activity > inactive_threshold:
                inactive_connections.append(session_id)
        
        for session_id in inactive_connections:
            await self.disconnect(session_id)
        
        if inactive_connections:
            logger.info(f"🧹 Cleaned up {len(inactive_connections)} inactive connections")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics with Redis pool information."""
        total_connections = len(self.active_connections)
        authenticated_connections = len([
            conn for conn in self.active_connections.values()
            if conn.status == ConnectionStatus.AUTHENTICATED
        ])
        
        # Get Redis pool stats
        redis_stats = asyncio.create_task(self.redis_manager.get_connection_stats())
        
        return {
            "total_connections": total_connections,
            "authenticated_connections": authenticated_connections,
            "unauthenticated_connections": total_connections - authenticated_connections,
            "max_connections": self.max_connections,
            "connection_utilization": round((total_connections / self.max_connections) * 100, 2),
            "redis_pool": redis_stats
        }
    
    async def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics including Redis pool."""
        total_connections = len(self.active_connections)
        authenticated_connections = len([
            conn for conn in self.active_connections.values()
            if conn.status == ConnectionStatus.AUTHENTICATED
        ])
        
        # Get Redis pool stats
        redis_stats = await self.redis_manager.get_connection_stats()
        
        # Get subscription statistics
        subscription_stats = {}
        for conn in self.active_connections.values():
            for subscription in conn.subscriptions:
                if subscription not in subscription_stats:
                    subscription_stats[subscription] = 0
                subscription_stats[subscription] += 1
        
        return {
            "websocket_stats": {
                "total_connections": total_connections,
                "authenticated_connections": authenticated_connections,
                "unauthenticated_connections": total_connections - authenticated_connections,
                "max_connections": self.max_connections,
                "connection_utilization": round((total_connections / self.max_connections) * 100, 2)
            },
            "redis_pool": redis_stats,
            "subscription_stats": subscription_stats,
            "timestamp": datetime.now().isoformat()
        }

# Global WebSocket manager instance
websocket_manager = EnhancedWebSocketManager() 