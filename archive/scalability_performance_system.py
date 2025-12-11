#!/usr/bin/env python3
"""
Scalability & Performance System - YOLO MODE!
=============================================
Load balancing, caching, database optimization, auto-scaling,
and performance monitoring for high-traffic sports betting platform
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
import concurrent.futures
import multiprocessing
import psutil
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerNode:
    """Server node configuration"""
    node_id: str
    hostname: str
    ip_address: str
    port: int
    cpu_cores: int
    memory_gb: float
    storage_gb: float
    current_load: float
    max_connections: int
    active_connections: int
    status: str  # 'healthy', 'degraded', 'down'
    last_health_check: str
    region: str

@dataclass
class LoadBalancerRule:
    """Load balancer routing rule"""
    rule_id: str
    name: str
    method: str  # 'round_robin', 'least_connections', 'weighted', 'ip_hash'
    target_nodes: List[str]
    health_check_interval: int
    failover_enabled: bool
    sticky_sessions: bool
    weights: Dict[str, int] = None

@dataclass
class CacheEntry:
    """Cache entry with TTL"""
    key: str
    value: Any
    created_at: float
    ttl: int
    access_count: int
    last_accessed: float
    size_bytes: int

@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics"""
    timestamp: str
    response_time_ms: float
    throughput_rps: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    cache_hit_rate: float
    active_connections: int
    queue_size: int

@dataclass
class AutoScalingRule:
    """Auto-scaling configuration"""
    rule_id: str
    metric_name: str  # 'cpu', 'memory', 'response_time', 'queue_size'
    threshold_up: float
    threshold_down: float
    scale_up_count: int
    scale_down_count: int
    cooldown_minutes: int
    min_instances: int
    max_instances: int
    is_active: bool

@dataclass
class DatabaseConnection:
    """Database connection pool info"""
    connection_id: str
    database_type: str  # 'postgres', 'redis', 'mongodb'
    host: str
    port: int
    pool_size: int
    active_connections: int
    queue_size: int
    avg_query_time: float
    status: str

class HighPerformanceCache:
    """High-performance caching system with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.Lock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info(f"🚀 High-Performance Cache initialized - {max_size} entries max")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if time.time() - entry.created_at > entry.ttl:
                self._remove_entry(key)
                self.misses += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # Update LRU order
            self.access_order.remove(key)
            self.access_order.append(key)
            
            self.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            # Calculate size (approximation)
            size_bytes = len(str(value).encode('utf-8'))
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                ttl=ttl,
                access_count=1,
                last_accessed=time.time(),
                size_bytes=size_bytes
            )
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            # Add/update entry
            if key in self.cache:
                self.access_order.remove(key)
            
            self.cache[key] = entry
            self.access_order.append(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            if lru_key in self.cache:
                del self.cache[lru_key]
                self.evictions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        
        return {
            "entries": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
            "total_size_bytes": total_size,
            "avg_size_bytes": total_size / len(self.cache) if self.cache else 0
        }
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()

class LoadBalancer:
    """Advanced load balancer with multiple algorithms"""
    
    def __init__(self):
        self.nodes = {}
        self.rules = {}
        self.current_node_index = 0
        self.lock = threading.Lock()
        
        logger.info("🚀 Load Balancer initialized - YOLO MODE!")
    
    def add_node(self, node: ServerNode):
        """Add server node to load balancer"""
        with self.lock:
            self.nodes[node.node_id] = node
            logger.info(f"✅ Added node {node.node_id} ({node.hostname}:{node.port})")
    
    def remove_node(self, node_id: str):
        """Remove server node from load balancer"""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                logger.info(f"❌ Removed node {node_id}")
    
    def add_rule(self, rule: LoadBalancerRule):
        """Add load balancing rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"✅ Added load balancing rule: {rule.name} ({rule.method})")
    
    def get_next_node(self, rule_id: str, client_ip: str = None) -> Optional[ServerNode]:
        """Get next available node based on load balancing rule"""
        rule = self.rules.get(rule_id)
        if not rule:
            return None
        
        available_nodes = [
            self.nodes[node_id] for node_id in rule.target_nodes
            if node_id in self.nodes and self.nodes[node_id].status == "healthy"
        ]
        
        if not available_nodes:
            return None
        
        if rule.method == "round_robin":
            return self._round_robin_selection(available_nodes)
        elif rule.method == "least_connections":
            return self._least_connections_selection(available_nodes)
        elif rule.method == "weighted":
            return self._weighted_selection(available_nodes, rule.weights or {})
        elif rule.method == "ip_hash":
            return self._ip_hash_selection(available_nodes, client_ip or "")
        else:
            return available_nodes[0]
    
    def _round_robin_selection(self, nodes: List[ServerNode]) -> ServerNode:
        """Round robin selection"""
        with self.lock:
            node = nodes[self.current_node_index % len(nodes)]
            self.current_node_index += 1
            return node
    
    def _least_connections_selection(self, nodes: List[ServerNode]) -> ServerNode:
        """Least connections selection"""
        return min(nodes, key=lambda n: n.active_connections)
    
    def _weighted_selection(self, nodes: List[ServerNode], weights: Dict[str, int]) -> ServerNode:
        """Weighted selection"""
        weighted_nodes = []
        for node in nodes:
            weight = weights.get(node.node_id, 1)
            weighted_nodes.extend([node] * weight)
        
        return random.choice(weighted_nodes) if weighted_nodes else nodes[0]
    
    def _ip_hash_selection(self, nodes: List[ServerNode], client_ip: str) -> ServerNode:
        """IP hash selection for sticky sessions"""
        hash_value = hash(client_ip)
        return nodes[hash_value % len(nodes)]
    
    def health_check_all_nodes(self):
        """Perform health check on all nodes"""
        for node in self.nodes.values():
            self._health_check_node(node)
    
    def _health_check_node(self, node: ServerNode):
        """Perform health check on single node"""
        try:
            # Simulate health check
            if random.random() > 0.05:  # 95% uptime
                node.status = "healthy"
                node.current_load = random.uniform(0.1, 0.8)
            else:
                node.status = "down"
                node.current_load = 0.0
            
            node.last_health_check = datetime.now().isoformat()
            
        except Exception as e:
            node.status = "down"
            logger.error(f"Health check failed for node {node.node_id}: {e}")

class DatabaseOptimizer:
    """Database optimization and connection pooling"""
    
    def __init__(self):
        self.connections = {}
        self.query_cache = HighPerformanceCache(max_size=5000, default_ttl=60)
        self.connection_pools = {}
        
        logger.info("🚀 Database Optimizer initialized - YOLO MODE!")
    
    def add_database_connection(self, connection: DatabaseConnection):
        """Add database connection to pool"""
        self.connections[connection.connection_id] = connection
        logger.info(f"✅ Added {connection.database_type} connection: {connection.host}:{connection.port}")
    
    async def execute_query(self, connection_id: str, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute optimized database query"""
        start_time = time.time()
        
        # Generate cache key
        cache_key = f"{connection_id}:{hash(query)}:{hash(str(params))}"
        
        # Check cache first
        cached_result = self.query_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return cached_result
        
        # Execute query
        connection = self.connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")
        
        # Simulate query execution
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # Simulate result
        result = {
            "query": query,
            "params": params,
            "rows": random.randint(1, 100),
            "execution_time": time.time() - start_time
        }
        
        # Cache result for SELECT queries
        if query.strip().upper().startswith("SELECT"):
            self.query_cache.set(cache_key, result, ttl=300)
        
        # Update connection stats
        connection.avg_query_time = (connection.avg_query_time + result["execution_time"]) / 2
        
        return result
    
    def optimize_connection_pool(self, connection_id: str):
        """Optimize database connection pool"""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        # Adjust pool size based on load
        if connection.queue_size > connection.pool_size * 0.8:
            # Increase pool size
            new_pool_size = min(connection.pool_size + 2, 50)
            connection.pool_size = new_pool_size
            logger.info(f"📈 Increased pool size for {connection_id} to {new_pool_size}")
        
        elif connection.active_connections < connection.pool_size * 0.3:
            # Decrease pool size
            new_pool_size = max(connection.pool_size - 1, 5)
            connection.pool_size = new_pool_size
            logger.info(f"📉 Decreased pool size for {connection_id} to {new_pool_size}")

class PerformanceMonitor:
    """Real-time performance monitoring and alerting"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.alert_thresholds = {
            "response_time_ms": 1000,
            "error_rate": 5.0,
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "cache_hit_rate": 70.0
        }
        self.alerts = []
        
        logger.info("🚀 Performance Monitor initialized - YOLO MODE!")
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Simulate application metrics
        response_time = random.uniform(50, 500)
        throughput = random.uniform(100, 1000)
        error_rate = random.uniform(0, 10)
        cache_hit_rate = random.uniform(60, 95)
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            response_time_ms=response_time,
            throughput_rps=throughput,
            error_rate=error_rate,
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io=network.bytes_sent + network.bytes_recv,
            cache_hit_rate=cache_hit_rate,
            active_connections=random.randint(50, 500),
            queue_size=random.randint(0, 50)
        )
        
        self.metrics_history.append(metrics)
        self._check_alerts(metrics)
        
        return metrics
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check if metrics exceed alert thresholds"""
        alerts = []
        
        if metrics.response_time_ms > self.alert_thresholds["response_time_ms"]:
            alerts.append(f"High response time: {metrics.response_time_ms:.1f}ms")
        
        if metrics.error_rate > self.alert_thresholds["error_rate"]:
            alerts.append(f"High error rate: {metrics.error_rate:.1f}%")
        
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        if metrics.cache_hit_rate < self.alert_thresholds["cache_hit_rate"]:
            alerts.append(f"Low cache hit rate: {metrics.cache_hit_rate:.1f}%")
        
        for alert in alerts:
            self.alerts.append({
                "timestamp": metrics.timestamp,
                "alert": alert,
                "severity": "warning"
            })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-60:]  # Last 60 measurements
        
        return {
            "avg_response_time": statistics.mean(m.response_time_ms for m in recent_metrics),
            "avg_throughput": statistics.mean(m.throughput_rps for m in recent_metrics),
            "avg_error_rate": statistics.mean(m.error_rate for m in recent_metrics),
            "avg_cpu_usage": statistics.mean(m.cpu_usage for m in recent_metrics),
            "avg_memory_usage": statistics.mean(m.memory_usage for m in recent_metrics),
            "avg_cache_hit_rate": statistics.mean(m.cache_hit_rate for m in recent_metrics),
            "total_alerts": len(self.alerts),
            "recent_alerts": len([a for a in self.alerts if a["timestamp"] > (datetime.now() - timedelta(minutes=10)).isoformat()])
        }

class AutoScaler:
    """Auto-scaling system for dynamic resource allocation"""
    
    def __init__(self):
        self.scaling_rules = {}
        self.scaling_history = []
        self.cooldown_tracker = {}
        
        logger.info("🚀 Auto-Scaler initialized - YOLO MODE!")
    
    def add_scaling_rule(self, rule: AutoScalingRule):
        """Add auto-scaling rule"""
        self.scaling_rules[rule.rule_id] = rule
        logger.info(f"✅ Added scaling rule: {rule.rule_id} ({rule.metric_name})")
    
    def evaluate_scaling(self, metrics: PerformanceMetrics, current_instances: int) -> Dict[str, Any]:
        """Evaluate if scaling is needed based on current metrics"""
        scaling_decision = {
            "action": "none",
            "current_instances": current_instances,
            "target_instances": current_instances,
            "reason": "",
            "rules_triggered": []
        }
        
        for rule in self.scaling_rules.values():
            if not rule.is_active:
                continue
            
            # Check if in cooldown period
            if self._is_in_cooldown(rule.rule_id):
                continue
            
            # Get metric value
            metric_value = self._get_metric_value(metrics, rule.metric_name)
            
            # Check scaling conditions
            if metric_value > rule.threshold_up and current_instances < rule.max_instances:
                # Scale up
                target_instances = min(current_instances + rule.scale_up_count, rule.max_instances)
                scaling_decision.update({
                    "action": "scale_up",
                    "target_instances": target_instances,
                    "reason": f"{rule.metric_name} ({metric_value:.1f}) above threshold ({rule.threshold_up})",
                    "rules_triggered": scaling_decision["rules_triggered"] + [rule.rule_id]
                })
                self._record_scaling_action(rule.rule_id, "scale_up", current_instances, target_instances)
                break
            
            elif metric_value < rule.threshold_down and current_instances > rule.min_instances:
                # Scale down
                target_instances = max(current_instances - rule.scale_down_count, rule.min_instances)
                scaling_decision.update({
                    "action": "scale_down",
                    "target_instances": target_instances,
                    "reason": f"{rule.metric_name} ({metric_value:.1f}) below threshold ({rule.threshold_down})",
                    "rules_triggered": scaling_decision["rules_triggered"] + [rule.rule_id]
                })
                self._record_scaling_action(rule.rule_id, "scale_down", current_instances, target_instances)
                break
        
        return scaling_decision
    
    def _get_metric_value(self, metrics: PerformanceMetrics, metric_name: str) -> float:
        """Get metric value by name"""
        metric_map = {
            "cpu": metrics.cpu_usage,
            "memory": metrics.memory_usage,
            "response_time": metrics.response_time_ms,
            "queue_size": metrics.queue_size,
            "error_rate": metrics.error_rate
        }
        return metric_map.get(metric_name, 0.0)
    
    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_id not in self.cooldown_tracker:
            return False
        
        rule = self.scaling_rules[rule_id]
        last_action_time = self.cooldown_tracker[rule_id]
        cooldown_end = last_action_time + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < cooldown_end
    
    def _record_scaling_action(self, rule_id: str, action: str, from_instances: int, to_instances: int):
        """Record scaling action"""
        self.cooldown_tracker[rule_id] = datetime.now()
        
        self.scaling_history.append({
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_id,
            "action": action,
            "from_instances": from_instances,
            "to_instances": to_instances
        })

class ScalabilityPerformanceSystem:
    """Complete scalability and performance management system"""
    
    def __init__(self):
        self.cache = HighPerformanceCache(max_size=10000, default_ttl=300)
        self.load_balancer = LoadBalancer()
        self.db_optimizer = DatabaseOptimizer()
        self.performance_monitor = PerformanceMonitor()
        self.auto_scaler = AutoScaler()
        
        # Initialize default configurations
        self._initialize_default_setup()
        
        logger.info("🚀 Scalability & Performance System initialized - YOLO MODE!")
    
    def _initialize_default_setup(self):
        """Initialize default system configuration"""
        # Add server nodes
        nodes = [
            ServerNode(
                node_id="node1", hostname="app-server-1", ip_address="10.0.1.10", port=8000,
                cpu_cores=4, memory_gb=16, storage_gb=100, current_load=0.3,
                max_connections=1000, active_connections=150, status="healthy",
                last_health_check=datetime.now().isoformat(), region="us-east-1"
            ),
            ServerNode(
                node_id="node2", hostname="app-server-2", ip_address="10.0.1.11", port=8000,
                cpu_cores=8, memory_gb=32, storage_gb=200, current_load=0.5,
                max_connections=2000, active_connections=300, status="healthy",
                last_health_check=datetime.now().isoformat(), region="us-east-1"
            ),
            ServerNode(
                node_id="node3", hostname="app-server-3", ip_address="10.0.1.12", port=8000,
                cpu_cores=4, memory_gb=16, storage_gb=100, current_load=0.2,
                max_connections=1000, active_connections=100, status="healthy",
                last_health_check=datetime.now().isoformat(), region="us-west-1"
            )
        ]
        
        for node in nodes:
            self.load_balancer.add_node(node)
        
        # Add load balancing rules
        self.load_balancer.add_rule(LoadBalancerRule(
            rule_id="api_traffic",
            name="API Traffic Distribution",
            method="least_connections",
            target_nodes=["node1", "node2", "node3"],
            health_check_interval=30,
            failover_enabled=True,
            sticky_sessions=False
        ))
        
        # Add database connections
        databases = [
            DatabaseConnection(
                connection_id="postgres_main", database_type="postgres",
                host="db-main.internal", port=5432, pool_size=20,
                active_connections=8, queue_size=2, avg_query_time=0.05,
                status="healthy"
            ),
            DatabaseConnection(
                connection_id="redis_cache", database_type="redis",
                host="cache.internal", port=6379, pool_size=10,
                active_connections=3, queue_size=0, avg_query_time=0.001,
                status="healthy"
            )
        ]
        
        for db in databases:
            self.db_optimizer.add_database_connection(db)
        
        # Add auto-scaling rules
        scaling_rules = [
            AutoScalingRule(
                rule_id="cpu_scaling", metric_name="cpu", threshold_up=70.0,
                threshold_down=30.0, scale_up_count=1, scale_down_count=1,
                cooldown_minutes=5, min_instances=2, max_instances=10, is_active=True
            ),
            AutoScalingRule(
                rule_id="response_time_scaling", metric_name="response_time", threshold_up=800.0,
                threshold_down=200.0, scale_up_count=2, scale_down_count=1,
                cooldown_minutes=3, min_instances=2, max_instances=15, is_active=True
            )
        ]
        
        for rule in scaling_rules:
            self.auto_scaler.add_scaling_rule(rule)
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request with full performance optimization"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"request:{hash(str(request_data))}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return {
                "response": cached_response,
                "cached": True,
                "processing_time": time.time() - start_time
            }
        
        # Get optimal server node
        node = self.load_balancer.get_next_node("api_traffic", request_data.get("client_ip"))
        if not node:
            raise Exception("No available server nodes")
        
        # Process request (simulate)
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        response = {
            "status": "success",
            "data": request_data,
            "processed_by": node.node_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache response
        self.cache.set(cache_key, response, ttl=60)
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "cached": False,
            "processing_time": processing_time,
            "node": node.node_id
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Collect current metrics
        current_metrics = self.performance_monitor.collect_metrics()
        performance_summary = self.performance_monitor.get_performance_summary()
        
        # Get cache statistics
        cache_stats = self.cache.get_stats()
        
        # Get load balancer status
        healthy_nodes = [
            node for node in self.load_balancer.nodes.values()
            if node.status == "healthy"
        ]
        
        # Get scaling recommendations
        current_instances = len(healthy_nodes)
        scaling_decision = self.auto_scaler.evaluate_scaling(current_metrics, current_instances)
        
        return {
            "system_health": "healthy" if len(healthy_nodes) >= 2 else "degraded",
            "current_metrics": asdict(current_metrics),
            "performance_summary": performance_summary,
            "cache_statistics": cache_stats,
            "load_balancer": {
                "total_nodes": len(self.load_balancer.nodes),
                "healthy_nodes": len(healthy_nodes),
                "node_status": [
                    {"id": node.node_id, "status": node.status, "load": node.current_load}
                    for node in self.load_balancer.nodes.values()
                ]
            },
            "auto_scaling": scaling_decision,
            "recent_alerts": self.performance_monitor.alerts[-5:] if self.performance_monitor.alerts else []
        }

async def main():
    """Test the scalability and performance system"""
    print("🚀 Testing Scalability & Performance System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize system
    scalability_system = ScalabilityPerformanceSystem()
    
    try:
        # Test cache performance
        print("\n🚀 Testing High-Performance Cache:")
        print("-" * 40)
        
        # Cache performance test
        cache_start = time.time()
        for i in range(1000):
            scalability_system.cache.set(f"key_{i}", f"value_{i}", ttl=60)
        cache_set_time = time.time() - cache_start
        
        cache_start = time.time()
        hits = 0
        for i in range(1000):
            if scalability_system.cache.get(f"key_{i}"):
                hits += 1
        cache_get_time = time.time() - cache_start
        
        print(f"✅ Cache SET: 1000 entries in {cache_set_time:.3f}s ({1000/cache_set_time:.0f} ops/sec)")
        print(f"✅ Cache GET: {hits} hits in {cache_get_time:.3f}s ({1000/cache_get_time:.0f} ops/sec)")
        
        cache_stats = scalability_system.cache.get_stats()
        print(f"✅ Cache stats: {cache_stats['hit_rate']:.1f}% hit rate, {cache_stats['entries']} entries")
        
        # Test load balancing
        print("\n⚖️ Testing Load Balancing:")
        print("-" * 40)
        
        node_requests = defaultdict(int)
        for i in range(50):
            node = scalability_system.load_balancer.get_next_node("api_traffic", f"192.168.1.{i%10}")
            if node:
                node_requests[node.node_id] += 1
        
        print(f"✅ Load distribution across nodes:")
        for node_id, count in node_requests.items():
            print(f"   {node_id}: {count} requests ({count/50*100:.1f}%)")
        
        # Test request handling
        print("\n🔄 Testing Request Handling:")
        print("-" * 40)
        
        request_times = []
        cached_responses = 0
        
        for i in range(20):
            request_data = {"user_id": f"user_{i%5}", "action": "get_predictions"}
            
            response = await scalability_system.handle_request(request_data)
            request_times.append(response["processing_time"])
            
            if response["cached"]:
                cached_responses += 1
            
            print(f"✅ Request {i+1}: {response['processing_time']:.3f}s ({'cached' if response['cached'] else 'processed'})")
        
        avg_response_time = statistics.mean(request_times)
        print(f"✅ Average response time: {avg_response_time:.3f}s")
        print(f"✅ Cache hits: {cached_responses}/20 ({cached_responses/20*100:.1f}%)")
        
        # Test database optimization
        print("\n💾 Testing Database Optimization:")
        print("-" * 40)
        
        query_times = []
        for i in range(10):
            query = f"SELECT * FROM users WHERE id = {i}"
            result = await scalability_system.db_optimizer.execute_query("postgres_main", query, {"id": i})
            query_times.append(result["execution_time"])
            print(f"✅ Query {i+1}: {result['execution_time']:.3f}s ({result['rows']} rows)")
        
        avg_query_time = statistics.mean(query_times)
        print(f"✅ Average query time: {avg_query_time:.3f}s")
        
        # Test performance monitoring
        print("\n📊 Testing Performance Monitoring:")
        print("-" * 40)
        
        # Collect metrics for a few cycles
        for i in range(5):
            metrics = scalability_system.performance_monitor.collect_metrics()
            print(f"✅ Cycle {i+1}: CPU {metrics.cpu_usage:.1f}%, "
                  f"Memory {metrics.memory_usage:.1f}%, "
                  f"Response {metrics.response_time_ms:.1f}ms")
            await asyncio.sleep(0.5)
        
        performance_summary = scalability_system.performance_monitor.get_performance_summary()
        print(f"✅ Performance summary:")
        print(f"   Avg response time: {performance_summary.get('avg_response_time', 0):.1f}ms")
        print(f"   Avg CPU usage: {performance_summary.get('avg_cpu_usage', 0):.1f}%")
        print(f"   Total alerts: {performance_summary.get('total_alerts', 0)}")
        
        # Test system status
        print("\n🎯 Testing System Status:")
        print("-" * 40)
        
        system_status = scalability_system.get_system_status()
        print(f"✅ System health: {system_status['system_health']}")
        print(f"✅ Total nodes: {system_status['load_balancer']['total_nodes']}")
        print(f"✅ Healthy nodes: {system_status['load_balancer']['healthy_nodes']}")
        print(f"✅ Cache hit rate: {system_status['cache_statistics']['hit_rate']:.1f}%")
        print(f"✅ Auto-scaling: {system_status['auto_scaling']['action']}")
        
        if system_status['auto_scaling']['action'] != 'none':
            print(f"   Reason: {system_status['auto_scaling']['reason']}")
            print(f"   Target instances: {system_status['auto_scaling']['target_instances']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Scalability & Performance System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 