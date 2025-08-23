"""
Message Broadcasting Service
===========================
Advanced message broadcasting system with queuing, delivery confirmation, and retry logic.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)

class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageStatus(str, Enum):
    """Message delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class BroadcastMessage:
    """Broadcast message structure."""
    id: str
    type: str
    data: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    sender_id: Optional[str] = None
    target_channels: Optional[List[str]] = None
    target_users: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    status: MessageStatus = MessageStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "sender_id": self.sender_id,
            "target_channels": self.target_channels,
            "target_users": self.target_users,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "status": self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BroadcastMessage':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=data["type"],
            data=data["data"],
            priority=MessagePriority(data["priority"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sender_id=data.get("sender_id"),
            target_channels=data.get("target_channels"),
            target_users=data.get("target_users"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            max_retries=data.get("max_retries", 3),
            retry_count=data.get("retry_count", 0),
            status=MessageStatus(data.get("status", "pending"))
        )

@dataclass
class DeliveryReceipt:
    """Message delivery receipt."""
    message_id: str
    recipient_id: str
    delivered_at: datetime
    status: MessageStatus
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "recipient_id": self.recipient_id,
            "delivered_at": self.delivered_at.isoformat(),
            "status": self.status.value,
            "error_message": self.error_message
        }

class MessageQueue:
    """Priority-based message queue with Redis backend."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.queue_prefix = "message_queue:"
        self.priority_queues = {
            MessagePriority.URGENT: f"{self.queue_prefix}urgent",
            MessagePriority.HIGH: f"{self.queue_prefix}high",
            MessagePriority.NORMAL: f"{self.queue_prefix}normal",
            MessagePriority.LOW: f"{self.queue_prefix}low"
        }
    
    async def enqueue_message(self, message: BroadcastMessage) -> bool:
        """Add message to appropriate priority queue."""
        try:
            queue_key = self.priority_queues[message.priority]
            message_data = json.dumps(message.to_dict())
            
            # Add to Redis sorted set with timestamp as score for ordering
            await self.redis_client.zadd(queue_key, {message_data: message.timestamp.timestamp()})
            
            # Set expiration for the message
            if message.expires_at:
                ttl = int((message.expires_at - datetime.now()).total_seconds())
                if ttl > 0:
                    await self.redis_client.expire(queue_key, ttl)
            
            logger.info(f"✅ Message {message.id} enqueued with priority {message.priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue message {message.id}: {e}")
            return False
    
    async def dequeue_message(self, priority: MessagePriority = MessagePriority.URGENT) -> Optional[BroadcastMessage]:
        """Get next message from specified priority queue."""
        try:
            queue_key = self.priority_queues[priority]
            
            # Get message with lowest timestamp (oldest first)
            messages = await self.redis_client.zrange(queue_key, 0, 0, withscores=True)
            
            if messages:
                message_data, score = messages[0]
                message_dict = json.loads(message_data)
                message = BroadcastMessage.from_dict(message_dict)
                
                # Remove from queue
                await self.redis_client.zrem(queue_key, message_data)
                
                logger.debug(f"📤 Dequeued message {message.id} from {priority.value} queue")
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to dequeue message from {priority.value} queue: {e}")
            return None
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all message queues."""
        stats = {}
        
        for priority, queue_key in self.priority_queues.items():
            try:
                count = await self.redis_client.zcard(queue_key)
                stats[priority.value] = count
            except Exception as e:
                logger.error(f"❌ Failed to get stats for {priority.value} queue: {e}")
                stats[priority.value] = 0
        
        return stats

class MessageBroadcaster:
    """Advanced message broadcasting system."""
    
    def __init__(self, redis_client: redis.Redis, websocket_manager):
        self.redis_client = redis_client
        self.websocket_manager = websocket_manager
        self.message_queue = MessageQueue(redis_client)
        self.delivery_receipts: Dict[str, List[DeliveryReceipt]] = defaultdict(list)
        self.batch_size = 50
        self.batch_timeout = 1.0  # seconds
        self.retry_delays = [1, 5, 15, 60]  # seconds
        self.active_batches: Dict[str, asyncio.Task] = {}
        self.message_counter = 0
        
    async def broadcast_message(self, message: BroadcastMessage) -> str:
        """Broadcast a message to all connected clients."""
        try:
            # Generate message ID if not provided
            if not message.id:
                self.message_counter += 1
                message.id = f"broadcast_{int(datetime.now().timestamp())}_{self.message_counter}"
            
            # Add to message queue
            success = await self.message_queue.enqueue_message(message)
            if not success:
                raise Exception("Failed to enqueue message")
            
            # Start batch processing if not already running
            batch_key = f"batch_{message.priority.value}"
            if batch_key not in self.active_batches or self.active_batches[batch_key].done():
                self.active_batches[batch_key] = asyncio.create_task(
                    self._process_message_batch(message.priority)
                )
            
            logger.info(f"📡 Message {message.id} queued for broadcasting")
            return message.id
            
        except Exception as e:
            logger.error(f"❌ Failed to broadcast message: {e}")
            raise
    
    async def broadcast_to_channels(self, message: BroadcastMessage, channels: List[str]) -> str:
        """Broadcast a message to specific channels."""
        message.target_channels = channels
        return await self.broadcast_message(message)
    
    async def broadcast_to_users(self, message: BroadcastMessage, user_ids: List[str]) -> str:
        """Broadcast a message to specific users."""
        message.target_users = user_ids
        return await self.broadcast_message(message)
    
    async def _process_message_batch(self, priority: MessagePriority):
        """Process a batch of messages for the given priority."""
        batch_messages = []
        start_time = datetime.now()
        
        try:
            # Collect messages for batch processing
            while len(batch_messages) < self.batch_size:
                message = await self.message_queue.dequeue_message(priority)
                if not message:
                    break
                
                batch_messages.append(message)
                
                # Check if batch timeout reached
                if (datetime.now() - start_time).total_seconds() >= self.batch_timeout:
                    break
            
            if batch_messages:
                logger.info(f"📦 Processing batch of {len(batch_messages)} {priority.value} priority messages")
                await self._deliver_message_batch(batch_messages)
            
        except Exception as e:
            logger.error(f"❌ Error processing message batch: {e}")
    
    async def _deliver_message_batch(self, messages: List[BroadcastMessage]):
        """Deliver a batch of messages."""
        delivery_tasks = []
        
        for message in messages:
            # Check if message has expired
            if message.expires_at and datetime.now() > message.expires_at:
                logger.warning(f"⚠️ Message {message.id} has expired, skipping delivery")
                continue
            
            # Create delivery task
            task = asyncio.create_task(self._deliver_single_message(message))
            delivery_tasks.append(task)
        
        # Wait for all deliveries to complete
        if delivery_tasks:
            results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                message = messages[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ Failed to deliver message {message.id}: {result}")
                    await self._handle_delivery_failure(message, str(result))
                else:
                    logger.debug(f"✅ Message {message.id} delivered successfully")
    
    async def _deliver_single_message(self, message: BroadcastMessage) -> bool:
        """Deliver a single message with retry logic."""
        try:
            # Determine target connections
            target_connections = await self._get_target_connections(message)
            
            if not target_connections:
                logger.warning(f"⚠️ No target connections found for message {message.id}")
                return True  # Consider it successful if no targets
            
            # Create WebSocket message
            ws_message = self.websocket_manager.WebSocketMessage(
                type=self.websocket_manager.MessageType(message.type),
                data=message.data,
                timestamp=datetime.now(),
                user_id=message.sender_id
            )
            
            # Send to target connections
            delivery_results = []
            for connection_info in target_connections:
                try:
                    await self.websocket_manager.send_message(connection_info, ws_message)
                    delivery_results.append(DeliveryReceipt(
                        message_id=message.id,
                        recipient_id=connection_info.session_id,
                        delivered_at=datetime.now(),
                        status=MessageStatus.DELIVERED
                    ))
                except Exception as e:
                    delivery_results.append(DeliveryReceipt(
                        message_id=message.id,
                        recipient_id=connection_info.session_id,
                        delivered_at=datetime.now(),
                        status=MessageStatus.FAILED,
                        error_message=str(e)
                    ))
            
            # Store delivery receipts
            self.delivery_receipts[message.id].extend(delivery_results)
            
            # Check if any deliveries failed
            failed_deliveries = [r for r in delivery_results if r.status == MessageStatus.FAILED]
            if failed_deliveries and message.retry_count < message.max_retries:
                await self._schedule_retry(message, failed_deliveries)
            
            return len(failed_deliveries) == 0
            
        except Exception as e:
            logger.error(f"❌ Error delivering message {message.id}: {e}")
            await self._handle_delivery_failure(message, str(e))
            return False
    
    async def _get_target_connections(self, message: BroadcastMessage) -> List:
        """Get target connections based on message configuration."""
        target_connections = []
        
        # Get all active connections
        all_connections = list(self.websocket_manager.active_connections.values())
        
        if message.target_channels:
            # Filter by channels
            for connection_info in all_connections:
                if any(channel in connection_info.subscriptions for channel in message.target_channels):
                    target_connections.append(connection_info)
        
        elif message.target_users:
            # Filter by user IDs
            for connection_info in all_connections:
                if connection_info.user_id in message.target_users:
                    target_connections.append(connection_info)
        
        else:
            # Broadcast to all connections
            target_connections = all_connections
        
        return target_connections
    
    async def _schedule_retry(self, message: BroadcastMessage, failed_deliveries: List[DeliveryReceipt]):
        """Schedule message retry with exponential backoff."""
        message.retry_count += 1
        message.status = MessageStatus.RETRYING
        
        if message.retry_count <= len(self.retry_delays):
            delay = self.retry_delays[message.retry_count - 1]
            
            logger.info(f"🔄 Scheduling retry {message.retry_count} for message {message.id} in {delay} seconds")
            
            # Schedule retry
            asyncio.create_task(self._delayed_retry(message, delay))
        else:
            logger.error(f"❌ Message {message.id} exceeded max retries")
            message.status = MessageStatus.FAILED
    
    async def _delayed_retry(self, message: BroadcastMessage, delay: int):
        """Execute delayed retry."""
        await asyncio.sleep(delay)
        
        # Re-queue message for retry
        await self.message_queue.enqueue_message(message)
        
        # Start batch processing for retry
        batch_key = f"retry_batch_{message.priority.value}"
        if batch_key not in self.active_batches or self.active_batches[batch_key].done():
            self.active_batches[batch_key] = asyncio.create_task(
                self._process_message_batch(message.priority)
            )
    
    async def _handle_delivery_failure(self, message: BroadcastMessage, error: str):
        """Handle delivery failure."""
        message.status = MessageStatus.FAILED
        
        # Store failure receipt
        failure_receipt = DeliveryReceipt(
            message_id=message.id,
            recipient_id="system",
            delivered_at=datetime.now(),
            status=MessageStatus.FAILED,
            error_message=error
        )
        self.delivery_receipts[message.id].append(failure_receipt)
        
        logger.error(f"❌ Message {message.id} delivery failed: {error}")
    
    async def get_delivery_stats(self, message_id: str) -> Dict[str, Any]:
        """Get delivery statistics for a specific message."""
        receipts = self.delivery_receipts.get(message_id, [])
        
        if not receipts:
            return {"message_id": message_id, "status": "not_found"}
        
        delivered = len([r for r in receipts if r.status == MessageStatus.DELIVERED])
        failed = len([r for r in receipts if r.status == MessageStatus.FAILED])
        total = len(receipts)
        
        return {
            "message_id": message_id,
            "total_recipients": total,
            "delivered": delivered,
            "failed": failed,
            "success_rate": round((delivered / total) * 100, 2) if total > 0 else 0,
            "receipts": [r.to_dict() for r in receipts]
        }
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get message queue statistics."""
        queue_stats = await self.message_queue.get_queue_stats()
        
        return {
            "queue_stats": queue_stats,
            "active_batches": len(self.active_batches),
            "total_messages_processed": self.message_counter,
            "delivery_receipts_count": sum(len(receipts) for receipts in self.delivery_receipts.values())
        }
    
    async def cleanup_expired_messages(self):
        """Clean up expired messages and old delivery receipts."""
        try:
            # Clean up old delivery receipts (older than 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            expired_receipts = []
            
            for message_id, receipts in self.delivery_receipts.items():
                expired = [r for r in receipts if r.delivered_at < cutoff_time]
                if expired:
                    expired_receipts.append(message_id)
            
            for message_id in expired_receipts:
                del self.delivery_receipts[message_id]
            
            if expired_receipts:
                logger.info(f"🧹 Cleaned up {len(expired_receipts)} expired message receipts")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Global message broadcaster instance
message_broadcaster = None

async def initialize_message_broadcaster(redis_client: redis.Redis, websocket_manager):
    """Initialize the global message broadcaster."""
    global message_broadcaster
    message_broadcaster = MessageBroadcaster(redis_client, websocket_manager)
    logger.info("🚀 Message broadcaster initialized")
    return message_broadcaster 