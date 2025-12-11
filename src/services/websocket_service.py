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
import uuid
from src.config import settings

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
    session_id: str
    client_id: str
    instance_id: str  # ID of the server instance holding this connection
    connected_at: datetime
    last_activity: datetime
    status: ConnectionStatus
    subscriptions: Set[str]
    user_preferences: Dict[str, Any]
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "client_id": self.client_id,
            "instance_id": self.instance_id,
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
        self.secret_key = settings.secret_key
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
    """Redis-based WebSocket connection management."""
    
    def __init__(self, redis_url: str = settings.redis_url):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub = None
        
    async def connect_redis(self):
        """Connect to Redis."""
        self.redis_client = redis.from_url(
            self.redis_url, 
            decode_responses=True,
            retry_on_timeout=True
        )
        await self.redis_client.ping()
        logger.info("✅ Redis connected")

    async def get_redis(self) -> redis.Redis:
        if not self.redis_client:
            await self.connect_redis()
        return self.redis_client

class EnhancedWebSocketManager:
    """Enhanced WebSocket connection manager with authentication and Redis integration."""
    
    def __init__(self):
        # Local connections map: session_id -> ConnectionInfo
        # This keeps the ACTUAL open WebSocket objects (which can't be stored in Redis)
        self.local_connections: Dict[str, ConnectionInfo] = {}
        
        self.auth_service = WebSocketAuthenticationService()
        self.redis_manager = RedisWebSocketManager()
        
        # Unique ID for this server instance
        self.instance_id = str(uuid.uuid4())
        
        self.connection_counter = 0
        self.max_connections = 10000
        self.heartbeat_interval = 30
        
    async def initialize(self):
        """Initialize the WebSocket manager and start Redis listener."""
        await self.redis_manager.connect_redis()
        redis_client = await self.redis_manager.get_redis()
        
        # Subscribe to instance-specific channel AND broadcast channel
        self.pubsub = redis_client.pubsub()
        await self.pubsub.subscribe(f"instance:{self.instance_id}", "broadcast:all")
        
        # Start listening task
        asyncio.create_task(self._redis_listener())
        logger.info(f"🚀 WebSocket Manager initialized (Instance: {self.instance_id})")
    
    async def _redis_listener(self):
        """Listen for messages from Redis and relay to local connections."""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    target_type = data.get("target_type")
                    
                    if target_type == "broadcast":
                        await self._local_broadcast(data["payload"])
                    elif target_type == "direct":
                        # Direct message to specific session on this instance
                        session_id = data.get("session_id")
                        if session_id in self.local_connections:
                            await self.send_local_message(
                                self.local_connections[session_id], 
                                WebSocketMessage(**data["payload"])
                            )
                except Exception as e:
                    logger.error(f"❌ Error processing Redis message: {e}")

    async def connect(self, websocket: WebSocket, client_data: Dict[str, Any]) -> ConnectionInfo:
        """Connect a new WebSocket client."""
        await websocket.accept()
        
        session_id = f"session_{int(datetime.now().timestamp())}_{self.connection_counter}"
        self.connection_counter += 1
        
        connection_info = ConnectionInfo(
            websocket=websocket,
            session_id=session_id,
            client_id=client_data.get("client_id", f"client_{session_id}"),
            instance_id=self.instance_id,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            status=ConnectionStatus.CONNECTED,
            subscriptions=set(),
            user_preferences=client_data.get("preferences", {})
        )
        
        # Store locally
        self.local_connections[session_id] = connection_info
        
        # Register in Redis (Global Registry)
        r = await self.redis_manager.get_redis()
        await r.hset(f"websocket:session:{session_id}", mapping={
            "instance_id": self.instance_id,
            "user_id": "",
            "connected_at": datetime.now().isoformat()
        })
        await r.expire(f"websocket:session:{session_id}", 3600*24)
        
        logger.info(f"🔌 New WebSocket connection: {session_id}")
        return connection_info

    async def disconnect(self, session_id: str):
        """Disconnect a client."""
        if session_id in self.local_connections:
            del self.local_connections[session_id]
            
            # Remove from Redis
            r = await self.redis_manager.get_redis()
            await r.delete(f"websocket:session:{session_id}")
            
            logger.info(f"🔌 WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: WebSocketMessage):
        """Send message to a session (local or remote)."""
        if session_id in self.local_connections:
            # Optimized local send
            await self.send_local_message(self.local_connections[session_id], message)
        else:
            # Remote send via Redis
            r = await self.redis_manager.get_redis()
            session_data = await r.hgetall(f"websocket:session:{session_id}")
            
            if session_data:
                target_instance = session_data.get("instance_id")
                await r.publish(f"instance:{target_instance}", json.dumps({
                    "target_type": "direct",
                    "session_id": session_id,
                    "payload": message.to_dict()
                }))

    async def send_local_message(self, connection_info: ConnectionInfo, message: WebSocketMessage):
        """Send message directly to local socket."""
        try:
            await connection_info.websocket.send_text(json.dumps(message.to_dict()))
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            await self.disconnect(connection_info.session_id)

    async def _local_broadcast(self, message_dict: Dict[str, Any]):
        """Broadcast message to all *local* connections."""
        message = WebSocketMessage(**message_dict)
        for conn in self.local_connections.values():
            await self.send_local_message(conn, message)

    async def broadcast_message(self, message: WebSocketMessage):
        """Broadcast to ALL users across ALL instances."""
        r = await self.redis_manager.get_redis()
        await r.publish("broadcast:all", json.dumps({
            "target_type": "broadcast",
            "payload": message.to_dict()
        }))

# Global Instance
websocket_manager = EnhancedWebSocketManager()