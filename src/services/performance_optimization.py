#!/usr/bin/env python3
"""
Performance Optimization and Reliability System
==============================================
Comprehensive performance optimizations and system reliability improvements
for the WebSocket communication system.
"""

import asyncio
import json
import gzip
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from collections import defaultdict, deque
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

# Configure logging
logger = logging.getLogger(__name__)

class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CompressionType(str, Enum):
    """Compression types."""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    connection_count: int
    message_count: int
    avg_response_time: float
    error_rate: float
    memory_usage: float
    cpu_usage: float
    compression_ratio: float
    circuit_breaker_state: str
    active_channels: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "connection_count": self.connection_count,
            "message_count": self.message_count,
            "avg_response_time": self.avg_response_time,
            "error_rate": self.error_rate,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "compression_ratio": self.compression_ratio,
            "circuit_breaker_state": self.circuit_breaker_state,
            "active_channels": self.active_channels
        }

class PayloadCompressor:
    """Handle payload compression and decompression."""
    
    def __init__(self, compression_threshold: int = 1024):
        self.compression_threshold = compression_threshold
        self.compression_stats = defaultdict(int)
    
    def compress_payload(self, payload: Union[str, bytes], compression_type: CompressionType = CompressionType.GZIP) -> Dict[str, Any]:
        """Compress payload if it exceeds threshold."""
        try:
            if isinstance(payload, str):
                payload_bytes = payload.encode('utf-8')
            else:
                payload_bytes = payload
            
            original_size = len(payload_bytes)
            
            # Only compress if payload is large enough
            if original_size < self.compression_threshold:
                return {
                    "compressed": False,
                    "data": payload,
                    "original_size": original_size,
                    "compressed_size": original_size,
                    "compression_ratio": 1.0,
                    "compression_type": CompressionType.NONE.value
                }
            
            if compression_type == CompressionType.GZIP:
                compressed_data = gzip.compress(payload_bytes)
                compressed_size = len(compressed_data)
                compression_ratio = compressed_size / original_size
                
                self.compression_stats["gzip_compressions"] += 1
                
                return {
                    "compressed": True,
                    "data": compressed_data,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "compression_type": compression_type.value
                }
            
            # Fallback to no compression
            return {
                "compressed": False,
                "data": payload,
                "original_size": original_size,
                "compressed_size": original_size,
                "compression_ratio": 1.0,
                "compression_type": CompressionType.NONE.value
            }
            
        except Exception as e:
            logger.error(f"❌ Compression failed: {e}")
            return {
                "compressed": False,
                "data": payload,
                "original_size": len(payload_bytes) if 'payload_bytes' in locals() else len(payload),
                "compressed_size": len(payload_bytes) if 'payload_bytes' in locals() else len(payload),
                "compression_ratio": 1.0,
                "compression_type": CompressionType.NONE.value
            }
    
    def decompress_payload(self, compressed_data: Dict[str, Any]) -> Union[str, bytes]:
        """Decompress payload."""
        try:
            if not compressed_data.get("compressed", False):
                return compressed_data["data"]
            
            if compressed_data["compression_type"] == CompressionType.GZIP.value:
                # Handle both string and bytes input
                data = compressed_data["data"]
                if isinstance(data, str):
                    # If data is string, encode to bytes first
                    data = data.encode('utf-8')
                
                decompressed = gzip.decompress(data)
                
                # Try to decode back to string if original was string
                try:
                    return decompressed.decode('utf-8')
                except UnicodeDecodeError:
                    return decompressed
            
            return compressed_data["data"]
            
        except Exception as e:
            logger.error(f"❌ Decompression failed: {e}")
            return compressed_data["data"]
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return dict(self.compression_stats)

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.total_requests = 0
        
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._can_execute():
            raise Exception(f"Circuit breaker is {self.state.value}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection."""
        if not self._can_execute():
            raise Exception(f"Circuit breaker is {self.state.value}")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _can_execute(self) -> bool:
        """Check if function can be executed."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                return True
            
            return False
    
    def _on_success(self):
        """Handle successful execution."""
        with self._lock:
            self.total_requests += 1
            self.success_count += 1
            self.failure_count = 0
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("✅ Circuit breaker closed - service recovered")
    
    def _on_failure(self):
        """Handle failed execution."""
        with self._lock:
            self.total_requests += 1
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"⚠️ Circuit breaker opened after {self.failure_count} failures")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("⚠️ Circuit breaker reopened after failed half-open test")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_requests": self.total_requests,
                "failure_rate": self.failure_count / max(self.total_requests, 1),
                "last_failure_time": datetime.fromtimestamp(self.last_failure_time).isoformat() if self.last_failure_time else None
            }

class SystemMonitor:
    """Monitor system performance and health."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.metrics_history = deque(maxlen=1000)
        self.monitoring_active = False
        self.monitor_task = None
        
        # Performance tracking
        self.response_times = deque(maxlen=100)
        self.error_counts = defaultdict(int)
        self.message_counts = defaultdict(int)
        
        # System metrics
        self.process = psutil.Process()
    
    async def start_monitoring(self, interval: int = 30):
        """Start system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info("🚀 System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 System monitoring stopped")
    
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Store in Redis
                await self._store_metrics(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics."""
        try:
            # Connection and message metrics
            connection_count = await self._get_connection_count()
            message_count = sum(self.message_counts.values())
            
            # Response time metrics
            avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
            
            # Error rate
            total_requests = sum(self.message_counts.values())
            total_errors = sum(self.error_counts.values())
            error_rate = total_errors / max(total_requests, 1)
            
            # System metrics
            memory_usage = self.process.memory_percent()
            cpu_usage = self.process.cpu_percent()
            
            # Compression metrics
            compression_ratio = 1.0  # Will be updated by compressor
            
            # Circuit breaker state
            circuit_breaker_state = "closed"  # Will be updated by circuit breakers
            
            # Active channels
            active_channels = await self._get_active_channels()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                connection_count=connection_count,
                message_count=message_count,
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                compression_ratio=compression_ratio,
                circuit_breaker_state=circuit_breaker_state,
                active_channels=active_channels
            )
            
        except Exception as e:
            logger.error(f"❌ Metrics collection failed: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                connection_count=0,
                message_count=0,
                avg_response_time=0,
                error_rate=0,
                memory_usage=0,
                cpu_usage=0,
                compression_ratio=1.0,
                circuit_breaker_state="unknown",
                active_channels=0
            )
    
    async def _get_connection_count(self) -> int:
        """Get current connection count."""
        try:
            return await self.redis_client.llen("websocket:connections")
        except:
            return 0
    
    async def _get_active_channels(self) -> int:
        """Get active channel count."""
        try:
            channels = await self.redis_client.smembers("websocket:channels")
            return len(channels)
        except:
            return 0
    
    async def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in Redis."""
        try:
            metrics_key = f"metrics:{datetime.now().strftime('%Y%m%d:%H%M')}"
            await self.redis_client.setex(
                metrics_key,
                3600,  # 1 hour TTL
                json.dumps(metrics.to_dict())
            )
        except Exception as e:
            logger.error(f"❌ Failed to store metrics: {e}")
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts."""
        alerts = []
        
        # High error rate alert
        if metrics.error_rate > 0.1:  # 10% error rate
            alerts.append(f"High error rate: {metrics.error_rate:.1%}")
        
        # High memory usage alert
        if metrics.memory_usage > 80:  # 80% memory usage
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        # High CPU usage alert
        if metrics.cpu_usage > 80:  # 80% CPU usage
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        # High response time alert
        if metrics.avg_response_time > 1000:  # 1 second
            alerts.append(f"High response time: {metrics.avg_response_time:.0f}ms")
        
        # Send alerts
        for alert in alerts:
            logger.warning(f"⚠️ Performance Alert: {alert}")
            await self._send_alert(alert)
    
    async def _send_alert(self, alert: str):
        """Send performance alert."""
        try:
            alert_data = {
                "type": "performance_alert",
                "message": alert,
                "timestamp": datetime.now().isoformat(),
                "severity": "warning"
            }
            await self.redis_client.publish("alerts", json.dumps(alert_data))
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
    
    def record_response_time(self, response_time: float):
        """Record response time for metrics."""
        self.response_times.append(response_time)
    
    def record_error(self, error_type: str):
        """Record error for metrics."""
        self.error_counts[error_type] += 1
    
    def record_message(self, message_type: str):
        """Record message for metrics."""
        self.message_counts[message_type] += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 metrics
        
        return {
            "total_metrics": len(self.metrics_history),
            "avg_connection_count": statistics.mean([m.connection_count for m in recent_metrics]),
            "avg_message_count": statistics.mean([m.message_count for m in recent_metrics]),
            "avg_response_time": statistics.mean([m.avg_response_time for m in recent_metrics]),
            "avg_error_rate": statistics.mean([m.error_rate for m in recent_metrics]),
            "avg_memory_usage": statistics.mean([m.memory_usage for m in recent_metrics]),
            "avg_cpu_usage": statistics.mean([m.cpu_usage for m in recent_metrics]),
            "latest_metrics": recent_metrics[-1].to_dict() if recent_metrics else None
        }

class FallbackManager:
    """Manage fallback mechanisms for system reliability."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.fallback_handlers = {}
        self.circuit_breakers = {}
    
    def register_fallback(self, service_name: str, fallback_func: Callable, circuit_breaker: CircuitBreaker = None):
        """Register a fallback handler for a service."""
        self.fallback_handlers[service_name] = fallback_func
        if circuit_breaker:
            self.circuit_breakers[service_name] = circuit_breaker
    
    async def execute_with_fallback(self, service_name: str, primary_func: Callable, *args, **kwargs) -> Any:
        """Execute function with fallback mechanism."""
        try:
            # Check if circuit breaker is open
            if service_name in self.circuit_breakers:
                cb = self.circuit_breakers[service_name]
                if cb.state == CircuitBreakerState.OPEN:
                    logger.warning(f"⚠️ Circuit breaker open for {service_name}, using fallback")
                    return await self._execute_fallback(service_name, *args, **kwargs)
            
            # Try primary function
            if service_name in self.circuit_breakers:
                result = await self.circuit_breakers[service_name].call_async(primary_func, *args, **kwargs)
            else:
                result = await primary_func(*args, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Primary function failed for {service_name}: {e}")
            return await self._execute_fallback(service_name, *args, **kwargs)
    
    async def _execute_fallback(self, service_name: str, *args, **kwargs) -> Any:
        """Execute fallback function."""
        if service_name not in self.fallback_handlers:
            raise Exception(f"No fallback handler registered for {service_name}")
        
        try:
            fallback_func = self.fallback_handlers[service_name]
            if asyncio.iscoroutinefunction(fallback_func):
                result = await fallback_func(*args, **kwargs)
            else:
                result = fallback_func(*args, **kwargs)
            
            logger.info(f"✅ Fallback executed successfully for {service_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Fallback also failed for {service_name}: {e}")
            raise e
    
    async def get_fallback_status(self) -> Dict[str, Any]:
        """Get fallback system status."""
        status = {}
        
        for service_name, cb in self.circuit_breakers.items():
            status[service_name] = {
                "circuit_breaker_state": cb.state.value,
                "has_fallback": service_name in self.fallback_handlers,
                "stats": cb.get_stats()
            }
        
        return status

class PerformanceOptimizer:
    """Main performance optimization orchestrator."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
        # Initialize components
        self.compressor = PayloadCompressor()
        self.monitor = SystemMonitor(redis_client)
        self.fallback_manager = FallbackManager(redis_client)
        
        # Performance tracking
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.optimization_active = False
    
    async def start_optimization(self):
        """Start performance optimization."""
        if self.optimization_active:
            return
        
        self.optimization_active = True
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        # Register default fallbacks
        self._register_default_fallbacks()
        
        logger.info("🚀 Performance optimization started")
    
    async def stop_optimization(self):
        """Stop performance optimization."""
        self.optimization_active = False
        await self.monitor.stop_monitoring()
        self.executor.shutdown(wait=True)
        logger.info("🛑 Performance optimization stopped")
    
    def _register_default_fallbacks(self):
        """Register default fallback handlers."""
        # Redis fallback
        redis_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        self.fallback_manager.register_fallback(
            "redis",
            self._redis_fallback,
            redis_cb
        )
        
        # WebSocket fallback
        websocket_cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        self.fallback_manager.register_fallback(
            "websocket",
            self._websocket_fallback,
            websocket_cb
        )
    
    async def _redis_fallback(self, *args, **kwargs):
        """Redis fallback mechanism."""
        logger.warning("⚠️ Using Redis fallback - in-memory storage")
        # Implement in-memory storage fallback
        return {"status": "fallback", "storage": "memory"}
    
    async def _websocket_fallback(self, *args, **kwargs):
        """WebSocket fallback mechanism."""
        logger.warning("⚠️ Using WebSocket fallback - HTTP polling")
        # Implement HTTP polling fallback
        return {"status": "fallback", "communication": "http_polling"}
    
    def optimize_payload(self, payload: Union[str, bytes]) -> Dict[str, Any]:
        """Optimize payload with compression."""
        return self.compressor.compress_payload(payload)
    
    def decompress_payload(self, compressed_data: Dict[str, Any]) -> Union[str, bytes]:
        """Decompress payload."""
        return self.compressor.decompress_payload(compressed_data)
    
    async def execute_with_fallback(self, service_name: str, primary_func: Callable, *args, **kwargs) -> Any:
        """Execute function with fallback protection."""
        return await self.fallback_manager.execute_with_fallback(service_name, primary_func, *args, **kwargs)
    
    def record_metrics(self, response_time: float = None, error_type: str = None, message_type: str = None):
        """Record performance metrics."""
        if response_time is not None:
            self.monitor.record_response_time(response_time)
        if error_type is not None:
            self.monitor.record_error(error_type)
        if message_type is not None:
            self.monitor.record_message(message_type)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "optimization_active": self.optimization_active,
            "compression_stats": self.compressor.get_compression_stats(),
            "metrics_summary": self.monitor.get_metrics_summary(),
            "fallback_status": {},  # Will be populated when needed
            "system_info": {
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent(),
                "disk_usage": psutil.disk_usage('/').percent
            }
        }
    
    async def get_async_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary with async data."""
        summary = self.get_performance_summary()
        summary["fallback_status"] = await self.fallback_manager.get_fallback_status()
        return summary

async def initialize_performance_optimizer(redis_client: redis.Redis) -> PerformanceOptimizer:
    """Initialize the performance optimization system."""
    optimizer = PerformanceOptimizer(redis_client)
    await optimizer.start_optimization()
    return optimizer 