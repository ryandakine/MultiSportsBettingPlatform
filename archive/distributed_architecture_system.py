#!/usr/bin/env python3
"""
Distributed Architecture System - YOLO MODE!
===========================================
Microservices, message queues, service discovery, circuit breakers,
and distributed caching for enterprise-scale sports betting platform
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
from collections import defaultdict, deque
import uuid
import threading
import enum
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    STARTING = "starting"
    STOPPING = "stopping"

class CircuitBreakerState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceInfo:
    """Service registration information"""
    service_id: str
    service_name: str
    version: str
    host: str
    port: int
    health_check_url: str
    status: ServiceStatus
    last_heartbeat: str
    metadata: Dict[str, Any]
    tags: List[str]
    region: str = "us-east-1"

@dataclass
class MessageQueueMessage:
    """Message queue message structure"""
    message_id: str
    queue_name: str
    payload: Dict[str, Any]
    priority: int
    retry_count: int
    max_retries: int
    created_at: str
    scheduled_for: str = ""
    dead_letter: bool = False

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    service_name: str
    failure_threshold: int
    recovery_timeout: int
    request_timeout: int
    half_open_max_calls: int
    sliding_window_size: int

@dataclass
class DistributedCacheNode:
    """Distributed cache node information"""
    node_id: str
    host: str
    port: int
    memory_limit: int
    current_memory: int
    key_count: int
    status: ServiceStatus
    last_sync: str

class ServiceDiscovery:
    """Service discovery and registration system"""
    
    def __init__(self):
        self.services = {}
        self.service_instances = defaultdict(list)
        self.health_check_interval = 30
        self.lock = threading.Lock()
        
        logger.info("🚀 Service Discovery initialized - YOLO MODE!")
    
    def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a service instance"""
        with self.lock:
            self.services[service_info.service_id] = service_info
            self.service_instances[service_info.service_name].append(service_info)
            
            logger.info(f"✅ Registered service: {service_info.service_name} "
                       f"({service_info.service_id}) at {service_info.host}:{service_info.port}")
            return True
    
    def deregister_service(self, service_id: str) -> bool:
        """Deregister a service instance"""
        with self.lock:
            if service_id in self.services:
                service_info = self.services[service_id]
                
                # Remove from services
                del self.services[service_id]
                
                # Remove from service instances
                instances = self.service_instances[service_info.service_name]
                self.service_instances[service_info.service_name] = [
                    s for s in instances if s.service_id != service_id
                ]
                
                logger.info(f"❌ Deregistered service: {service_info.service_name} ({service_id})")
                return True
            
            return False
    
    def discover_service(self, service_name: str, region: str = None) -> List[ServiceInfo]:
        """Discover healthy instances of a service"""
        instances = self.service_instances.get(service_name, [])
        
        # Filter by region if specified
        if region:
            instances = [s for s in instances if s.region == region]
        
        # Filter by health status
        healthy_instances = [s for s in instances if s.status == ServiceStatus.HEALTHY]
        
        return healthy_instances
    
    def get_service_instance(self, service_name: str, load_balancing: str = "round_robin") -> Optional[ServiceInfo]:
        """Get a single service instance using load balancing"""
        instances = self.discover_service(service_name)
        
        if not instances:
            return None
        
        if load_balancing == "round_robin":
            return instances[int(time.time()) % len(instances)]
        elif load_balancing == "random":
            return random.choice(instances)
        else:
            return instances[0]
    
    def update_service_health(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service health status"""
        with self.lock:
            if service_id in self.services:
                self.services[service_id].status = status
                self.services[service_id].last_heartbeat = datetime.now().isoformat()
                return True
            return False
    
    def get_all_services(self) -> Dict[str, List[ServiceInfo]]:
        """Get all registered services"""
        return dict(self.service_instances)

class MessageQueue:
    """Distributed message queue system"""
    
    def __init__(self):
        self.queues = defaultdict(deque)
        self.dead_letter_queue = deque()
        self.subscribers = defaultdict(list)
        self.processing_messages = {}
        self.lock = threading.Lock()
        
        logger.info("🚀 Message Queue initialized - YOLO MODE!")
    
    def publish(self, queue_name: str, payload: Dict[str, Any], 
                priority: int = 5, delay_seconds: int = 0) -> str:
        """Publish message to queue"""
        message_id = str(uuid.uuid4())
        
        scheduled_for = ""
        if delay_seconds > 0:
            scheduled_for = (datetime.now() + timedelta(seconds=delay_seconds)).isoformat()
        
        message = MessageQueueMessage(
            message_id=message_id,
            queue_name=queue_name,
            payload=payload,
            priority=priority,
            retry_count=0,
            max_retries=3,
            created_at=datetime.now().isoformat(),
            scheduled_for=scheduled_for
        )
        
        with self.lock:
            self.queues[queue_name].append(message)
            
        logger.debug(f"📤 Published message {message_id} to queue {queue_name}")
        return message_id
    
    def subscribe(self, queue_name: str, callback) -> str:
        """Subscribe to queue messages"""
        subscriber_id = str(uuid.uuid4())
        
        with self.lock:
            self.subscribers[queue_name].append({
                "id": subscriber_id,
                "callback": callback
            })
        
        logger.info(f"📥 Subscribed to queue {queue_name} (subscriber: {subscriber_id})")
        return subscriber_id
    
    def consume(self, queue_name: str, count: int = 1) -> List[MessageQueueMessage]:
        """Consume messages from queue"""
        messages = []
        
        with self.lock:
            queue = self.queues[queue_name]
            current_time = datetime.now()
            
            for _ in range(min(count, len(queue))):
                if not queue:
                    break
                
                message = queue.popleft()
                
                # Check if message is scheduled for future
                if message.scheduled_for:
                    scheduled_time = datetime.fromisoformat(message.scheduled_for)
                    if current_time < scheduled_time:
                        # Put back in queue
                        queue.appendleft(message)
                        break
                
                # Mark as processing
                self.processing_messages[message.message_id] = message
                messages.append(message)
        
        return messages
    
    def acknowledge(self, message_id: str) -> bool:
        """Acknowledge message processing"""
        with self.lock:
            if message_id in self.processing_messages:
                del self.processing_messages[message_id]
                logger.debug(f"✅ Acknowledged message {message_id}")
                return True
            return False
    
    def reject(self, message_id: str, requeue: bool = True) -> bool:
        """Reject message and optionally requeue"""
        with self.lock:
            if message_id not in self.processing_messages:
                return False
            
            message = self.processing_messages[message_id]
            del self.processing_messages[message_id]
            
            if requeue and message.retry_count < message.max_retries:
                message.retry_count += 1
                self.queues[message.queue_name].append(message)
                logger.debug(f"🔄 Requeued message {message_id} (retry {message.retry_count})")
            else:
                # Send to dead letter queue
                message.dead_letter = True
                self.dead_letter_queue.append(message)
                logger.warning(f"💀 Message {message_id} sent to dead letter queue")
            
            return True
    
    def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            queue = self.queues[queue_name]
            processing_count = len([m for m in self.processing_messages.values() 
                                  if m.queue_name == queue_name])
            
            return {
                "queue_name": queue_name,
                "pending_messages": len(queue),
                "processing_messages": processing_count,
                "subscribers": len(self.subscribers[queue_name]),
                "dead_letter_messages": len([m for m in self.dead_letter_queue 
                                           if m.queue_name == queue_name])
            }

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.request_history = deque(maxlen=config.sliding_window_size)
        self.lock = threading.Lock()
        
        logger.info(f"🚀 Circuit Breaker initialized for {config.service_name}")
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if not self._can_execute():
            raise Exception(f"Circuit breaker is OPEN for {self.config.service_name}")
        
        try:
            # Set timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.request_timeout
            )
            
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _can_execute(self) -> bool:
        """Check if request can be executed"""
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            elif self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if (self.last_failure_time and 
                    time.time() - self.last_failure_time > self.config.recovery_timeout):
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info(f"🔄 Circuit breaker for {self.config.service_name} moved to HALF_OPEN")
                    return True
                return False
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return self.half_open_calls < self.config.half_open_max_calls
            
            return False
    
    def _on_success(self):
        """Handle successful request"""
        with self.lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls >= self.config.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info(f"✅ Circuit breaker for {self.config.service_name} moved to CLOSED")
            
            self.request_history.append({"success": True, "timestamp": time.time()})
    
    def _on_failure(self):
        """Handle failed request"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            self.request_history.append({"success": False, "timestamp": time.time()})
            
            if self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.warning(f"⚠️ Circuit breaker for {self.config.service_name} moved to OPEN")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"⚠️ Circuit breaker for {self.config.service_name} back to OPEN")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        success_count = len([r for r in self.request_history if r["success"]])
        total_count = len(self.request_history)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "service_name": self.config.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_rate": success_rate,
            "total_requests": total_count,
            "half_open_calls": self.half_open_calls if self.state == CircuitBreakerState.HALF_OPEN else 0
        }

class DistributedCache:
    """Distributed caching system with consistent hashing"""
    
    def __init__(self):
        self.nodes = {}
        self.hash_ring = {}
        self.replication_factor = 2
        self.lock = threading.Lock()
        
        logger.info("🚀 Distributed Cache initialized - YOLO MODE!")
    
    def add_node(self, node: DistributedCacheNode):
        """Add cache node to cluster"""
        with self.lock:
            self.nodes[node.node_id] = node
            self._rebuild_hash_ring()
            logger.info(f"✅ Added cache node {node.node_id} ({node.host}:{node.port})")
    
    def remove_node(self, node_id: str):
        """Remove cache node from cluster"""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                self._rebuild_hash_ring()
                logger.info(f"❌ Removed cache node {node_id}")
    
    def _rebuild_hash_ring(self):
        """Rebuild consistent hash ring"""
        self.hash_ring = {}
        
        for node_id in self.nodes.keys():
            for i in range(100):  # Virtual nodes for better distribution
                hash_key = hash(f"{node_id}:{i}")
                self.hash_ring[hash_key] = node_id
    
    def _get_nodes_for_key(self, key: str) -> List[str]:
        """Get nodes responsible for a key"""
        if not self.hash_ring:
            return []
        
        key_hash = hash(key)
        sorted_hashes = sorted(self.hash_ring.keys())
        
        # Find the first node
        idx = 0
        for i, h in enumerate(sorted_hashes):
            if h >= key_hash:
                idx = i
                break
        
        # Get nodes for replication
        nodes = []
        used_nodes = set()
        
        for i in range(len(sorted_hashes)):
            node_id = self.hash_ring[sorted_hashes[(idx + i) % len(sorted_hashes)]]
            if node_id not in used_nodes:
                nodes.append(node_id)
                used_nodes.add(node_id)
                if len(nodes) >= self.replication_factor:
                    break
        
        return nodes
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        nodes = self._get_nodes_for_key(key)
        
        for node_id in nodes:
            node = self.nodes.get(node_id)
            if node and node.status == ServiceStatus.HEALTHY:
                # Simulate cache get
                await asyncio.sleep(0.001)
                
                # Simulate cache hit/miss
                if random.random() > 0.2:  # 80% hit rate
                    return f"cached_value_for_{key}"
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in distributed cache"""
        nodes = self._get_nodes_for_key(key)
        success_count = 0
        
        for node_id in nodes:
            node = self.nodes.get(node_id)
            if node and node.status == ServiceStatus.HEALTHY:
                try:
                    # Simulate cache set
                    await asyncio.sleep(0.001)
                    
                    # Update node statistics
                    node.key_count += 1
                    node.current_memory += len(str(value))
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to set key {key} on node {node_id}: {e}")
        
        # Require majority success
        return success_count >= (len(nodes) + 1) // 2
    
    async def delete(self, key: str) -> bool:
        """Delete value from distributed cache"""
        nodes = self._get_nodes_for_key(key)
        success_count = 0
        
        for node_id in nodes:
            node = self.nodes.get(node_id)
            if node and node.status == ServiceStatus.HEALTHY:
                try:
                    # Simulate cache delete
                    await asyncio.sleep(0.001)
                    
                    # Update node statistics
                    node.key_count = max(0, node.key_count - 1)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to delete key {key} on node {node_id}: {e}")
        
        return success_count > 0
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get distributed cache cluster statistics"""
        total_nodes = len(self.nodes)
        healthy_nodes = len([n for n in self.nodes.values() if n.status == ServiceStatus.HEALTHY])
        total_keys = sum(n.key_count for n in self.nodes.values())
        total_memory = sum(n.current_memory for n in self.nodes.values())
        
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "total_keys": total_keys,
            "total_memory_bytes": total_memory,
            "replication_factor": self.replication_factor,
            "node_details": [
                {
                    "node_id": node.node_id,
                    "status": node.status.value,
                    "keys": node.key_count,
                    "memory_usage": f"{node.current_memory}/{node.memory_limit}"
                }
                for node in self.nodes.values()
            ]
        }

class MicroserviceOrchestrator:
    """Microservice orchestration and management"""
    
    def __init__(self):
        self.service_discovery = ServiceDiscovery()
        self.message_queue = MessageQueue()
        self.circuit_breakers = {}
        self.distributed_cache = DistributedCache()
        
        logger.info("🚀 Microservice Orchestrator initialized - YOLO MODE!")
    
    def register_service(self, service_info: ServiceInfo) -> bool:
        """Register microservice"""
        return self.service_discovery.register_service(service_info)
    
    def create_circuit_breaker(self, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create circuit breaker for service"""
        circuit_breaker = CircuitBreaker(config)
        self.circuit_breakers[config.service_name] = circuit_breaker
        return circuit_breaker
    
    async def call_service(self, service_name: str, method: str, 
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call microservice with circuit breaker protection"""
        # Get service instance
        service_instance = self.service_discovery.get_service_instance(service_name)
        if not service_instance:
            raise Exception(f"No healthy instances found for service {service_name}")
        
        # Get circuit breaker
        circuit_breaker = self.circuit_breakers.get(service_name)
        
        async def service_call():
            # Simulate service call
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            # Simulate occasional failures
            if random.random() < 0.1:  # 10% failure rate
                raise Exception(f"Service {service_name} call failed")
            
            return {
                "service": service_name,
                "method": method,
                "params": params,
                "instance": service_instance.service_id,
                "timestamp": datetime.now().isoformat()
            }
        
        if circuit_breaker:
            return await circuit_breaker.call(service_call)
        else:
            return await service_call()
    
    async def publish_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        """Publish event to message queue"""
        return self.message_queue.publish(f"events.{event_type}", payload)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        all_services = self.service_discovery.get_all_services()
        
        total_services = sum(len(instances) for instances in all_services.values())
        healthy_services = sum(
            len([s for s in instances if s.status == ServiceStatus.HEALTHY])
            for instances in all_services.values()
        )
        
        # Circuit breaker stats
        circuit_breaker_stats = {
            name: cb.get_stats() 
            for name, cb in self.circuit_breakers.items()
        }
        
        # Cache stats
        cache_stats = self.distributed_cache.get_cluster_stats()
        
        return {
            "overall_health": "healthy" if healthy_services >= total_services * 0.8 else "degraded",
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0
            },
            "circuit_breakers": circuit_breaker_stats,
            "distributed_cache": cache_stats,
            "message_queues": {
                queue_name: self.message_queue.get_queue_stats(queue_name)
                for queue_name in self.message_queue.queues.keys()
            }
        }

async def main():
    """Test the distributed architecture system"""
    print("🚀 Testing Distributed Architecture System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = MicroserviceOrchestrator()
    
    try:
        # Test service discovery
        print("\n🔍 Testing Service Discovery:")
        print("-" * 40)
        
        # Register test services
        services = [
            ServiceInfo(
                service_id="auth-service-1", service_name="auth-service", version="1.0.0",
                host="10.0.1.10", port=8001, health_check_url="/health",
                status=ServiceStatus.HEALTHY, last_heartbeat=datetime.now().isoformat(),
                metadata={"region": "us-east-1"}, tags=["authentication", "security"]
            ),
            ServiceInfo(
                service_id="betting-service-1", service_name="betting-service", version="1.0.0",
                host="10.0.1.11", port=8002, health_check_url="/health",
                status=ServiceStatus.HEALTHY, last_heartbeat=datetime.now().isoformat(),
                metadata={"region": "us-east-1"}, tags=["betting", "core"]
            ),
            ServiceInfo(
                service_id="analytics-service-1", service_name="analytics-service", version="1.0.0",
                host="10.0.1.12", port=8003, health_check_url="/health",
                status=ServiceStatus.HEALTHY, last_heartbeat=datetime.now().isoformat(),
                metadata={"region": "us-west-1"}, tags=["analytics", "ml"]
            )
        ]
        
        for service in services:
            orchestrator.register_service(service)
            print(f"✅ Registered {service.service_name} ({service.service_id})")
        
        # Test service discovery
        auth_instances = orchestrator.service_discovery.discover_service("auth-service")
        print(f"✅ Found {len(auth_instances)} auth-service instances")
        
        # Test circuit breakers
        print("\n⚡ Testing Circuit Breakers:")
        print("-" * 40)
        
        # Create circuit breakers
        for service_name in ["auth-service", "betting-service", "analytics-service"]:
            config = CircuitBreakerConfig(
                service_name=service_name,
                failure_threshold=3,
                recovery_timeout=10,
                request_timeout=5,
                half_open_max_calls=2,
                sliding_window_size=10
            )
            orchestrator.create_circuit_breaker(config)
            print(f"✅ Created circuit breaker for {service_name}")
        
        # Test service calls
        print("\n📞 Testing Service Calls:")
        print("-" * 40)
        
        successful_calls = 0
        failed_calls = 0
        
        for i in range(10):
            try:
                response = await orchestrator.call_service(
                    "auth-service", 
                    "authenticate", 
                    {"token": f"test_token_{i}"}
                )
                successful_calls += 1
                print(f"✅ Call {i+1}: Success - {response['instance']}")
                
            except Exception as e:
                failed_calls += 1
                print(f"❌ Call {i+1}: Failed - {str(e)}")
        
        print(f"✅ Service calls: {successful_calls} successful, {failed_calls} failed")
        
        # Test distributed cache
        print("\n💾 Testing Distributed Cache:")
        print("-" * 40)
        
        # Add cache nodes
        cache_nodes = [
            DistributedCacheNode(
                node_id="cache-1", host="10.0.2.10", port=6379,
                memory_limit=1024*1024*1024, current_memory=0, key_count=0,
                status=ServiceStatus.HEALTHY, last_sync=datetime.now().isoformat()
            ),
            DistributedCacheNode(
                node_id="cache-2", host="10.0.2.11", port=6379,
                memory_limit=1024*1024*1024, current_memory=0, key_count=0,
                status=ServiceStatus.HEALTHY, last_sync=datetime.now().isoformat()
            ),
            DistributedCacheNode(
                node_id="cache-3", host="10.0.2.12", port=6379,
                memory_limit=1024*1024*1024, current_memory=0, key_count=0,
                status=ServiceStatus.HEALTHY, last_sync=datetime.now().isoformat()
            )
        ]
        
        for node in cache_nodes:
            orchestrator.distributed_cache.add_node(node)
        
        # Test cache operations
        cache_operations = []
        for i in range(20):
            key = f"test_key_{i}"
            value = f"test_value_{i}"
            
            # Set value
            success = await orchestrator.distributed_cache.set(key, value)
            cache_operations.append(success)
            
            # Get value
            cached_value = await orchestrator.distributed_cache.get(key)
            if cached_value:
                print(f"✅ Cache {i+1}: SET/GET successful")
            else:
                print(f"❌ Cache {i+1}: GET failed")
        
        successful_cache_ops = sum(cache_operations)
        print(f"✅ Cache operations: {successful_cache_ops}/20 successful")
        
        # Test message queue
        print("\n📨 Testing Message Queue:")
        print("-" * 40)
        
        # Publish messages
        message_ids = []
        for i in range(5):
            message_id = orchestrator.message_queue.publish(
                "test-queue",
                {"event": f"test_event_{i}", "data": f"test_data_{i}"},
                priority=i % 3
            )
            message_ids.append(message_id)
            print(f"✅ Published message {i+1}: {message_id}")
        
        # Consume messages
        consumed_messages = orchestrator.message_queue.consume("test-queue", count=3)
        print(f"✅ Consumed {len(consumed_messages)} messages")
        
        # Acknowledge messages
        for message in consumed_messages:
            orchestrator.message_queue.acknowledge(message.message_id)
            print(f"✅ Acknowledged message: {message.message_id}")
        
        # Test system health
        print("\n🏥 Testing System Health:")
        print("-" * 40)
        
        health_status = orchestrator.get_system_health()
        print(f"✅ Overall health: {health_status['overall_health']}")
        print(f"✅ Services: {health_status['services']['healthy']}/{health_status['services']['total']} healthy")
        print(f"✅ Cache nodes: {health_status['distributed_cache']['healthy_nodes']}/{health_status['distributed_cache']['total_nodes']}")
        print(f"✅ Circuit breakers: {len(health_status['circuit_breakers'])} active")
        
        # Show circuit breaker stats
        print(f"\n⚡ Circuit Breaker Status:")
        for service_name, stats in health_status['circuit_breakers'].items():
            print(f"   {service_name}: {stats['state']} (success rate: {stats['success_rate']:.1f}%)")
        
        # Show cache cluster stats
        cache_stats = health_status['distributed_cache']
        print(f"\n💾 Distributed Cache Status:")
        print(f"   Total keys: {cache_stats['total_keys']}")
        print(f"   Memory usage: {cache_stats['total_memory_bytes']} bytes")
        print(f"   Replication factor: {cache_stats['replication_factor']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Distributed Architecture System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 