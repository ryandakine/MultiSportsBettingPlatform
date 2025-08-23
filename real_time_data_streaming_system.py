#!/usr/bin/env python3
"""
Real-Time Data Streaming System - YOLO MODE!
============================================
Live data feeds, validation, caching, and streaming analytics
for ultra-fast sports betting data integration
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
from collections import defaultdict, deque
import hashlib
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiveDataStream:
    """Live data stream configuration"""
    stream_id: str
    source: str
    data_type: str  # 'odds', 'scores', 'stats', 'news', 'sentiment'
    update_frequency: int  # seconds
    is_active: bool = True
    last_update: Optional[str] = None
    error_count: int = 0
    success_count: int = 0

@dataclass
class DataValidationRule:
    """Data validation rule"""
    field_name: str
    rule_type: str  # 'range', 'format', 'required', 'custom'
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = True
    custom_validator: Optional[Callable] = None
    error_message: str = "Validation failed"

@dataclass
class StreamedDataPoint:
    """Individual data point from stream"""
    timestamp: str
    source: str
    data_type: str
    data: Dict[str, Any]
    validation_status: str  # 'valid', 'invalid', 'warning'
    confidence_score: float
    processing_time_ms: int

@dataclass
class DataStreamMetrics:
    """Stream performance metrics"""
    stream_id: str
    total_messages: int
    valid_messages: int
    invalid_messages: int
    average_latency_ms: float
    throughput_messages_per_second: float
    uptime_percentage: float
    last_error: Optional[str] = None

@dataclass
class RealTimeAlert:
    """Real-time alert for data anomalies"""
    alert_id: str
    alert_type: str  # 'data_anomaly', 'stream_down', 'validation_error', 'performance_issue'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: str
    data_context: Dict[str, Any]
    actionable: bool = True

class DataValidator:
    """Advanced data validation engine"""
    
    def __init__(self):
        self.validation_rules = {
            "odds": [
                DataValidationRule("home_odds", "range", min_value=1.0, max_value=100.0),
                DataValidationRule("away_odds", "range", min_value=1.0, max_value=100.0),
                DataValidationRule("draw_odds", "range", min_value=1.0, max_value=100.0, required=False),
                DataValidationRule("timestamp", "required"),
                DataValidationRule("bookmaker", "required")
            ],
            "scores": [
                DataValidationRule("home_score", "range", min_value=0, max_value=200),
                DataValidationRule("away_score", "range", min_value=0, max_value=200),
                DataValidationRule("period", "range", min_value=1, max_value=10),
                DataValidationRule("time_remaining", "range", min_value=0, max_value=3600),
                DataValidationRule("game_id", "required")
            ],
            "stats": [
                DataValidationRule("team_id", "required"),
                DataValidationRule("points", "range", min_value=0, max_value=200),
                DataValidationRule("rebounds", "range", min_value=0, max_value=50),
                DataValidationRule("assists", "range", min_value=0, max_value=30),
                DataValidationRule("timestamp", "required")
            ]
        }
        
        self.custom_validators = {
            "odds_consistency": self._validate_odds_consistency,
            "score_plausibility": self._validate_score_plausibility,
            "timestamp_freshness": self._validate_timestamp_freshness
        }
    
    def validate_data(self, data: Dict[str, Any], data_type: str) -> Tuple[bool, List[str], float]:
        """Validate data against rules"""
        start_time = time.time()
        errors = []
        warnings = []
        
        if data_type not in self.validation_rules:
            return True, [], 1.0
        
        rules = self.validation_rules[data_type]
        
        for rule in rules:
            field_value = data.get(rule.field_name)
            
            # Check if required field is present
            if rule.required and field_value is None:
                errors.append(f"Required field '{rule.field_name}' is missing")
                continue
            
            if field_value is not None:
                # Range validation
                if rule.rule_type == "range":
                    if rule.min_value is not None and field_value < rule.min_value:
                        errors.append(f"Field '{rule.field_name}' value {field_value} is below minimum {rule.min_value}")
                    if rule.max_value is not None and field_value > rule.max_value:
                        errors.append(f"Field '{rule.field_name}' value {field_value} is above maximum {rule.max_value}")
                
                # Format validation
                elif rule.rule_type == "format":
                    if not self._validate_format(field_value, rule.field_name):
                        errors.append(f"Field '{rule.field_name}' has invalid format")
                
                # Custom validation
                elif rule.rule_type == "custom" and rule.custom_validator:
                    try:
                        if not rule.custom_validator(field_value, data):
                            errors.append(rule.error_message)
                    except Exception as e:
                        errors.append(f"Custom validation error for '{rule.field_name}': {str(e)}")
        
        # Run custom validators
        for validator_name, validator_func in self.custom_validators.items():
            try:
                if not validator_func(data):
                    warnings.append(f"Custom validation '{validator_name}' failed")
            except Exception as e:
                warnings.append(f"Custom validation '{validator_name}' error: {str(e)}")
        
        # Calculate confidence score
        confidence = self._calculate_confidence(data, errors, warnings)
        
        processing_time = (time.time() - start_time) * 1000
        
        return len(errors) == 0, errors + warnings, confidence
    
    def _validate_odds_consistency(self, data: Dict[str, Any]) -> bool:
        """Validate odds consistency"""
        home_odds = data.get("home_odds")
        away_odds = data.get("away_odds")
        
        if home_odds and away_odds:
            # Check if odds are reasonable (not too far apart)
            ratio = max(home_odds, away_odds) / min(home_odds, away_odds)
            return ratio < 10.0  # Odds shouldn't be more than 10x different
        
        return True
    
    def _validate_score_plausibility(self, data: Dict[str, Any]) -> bool:
        """Validate score plausibility"""
        home_score = data.get("home_score", 0)
        away_score = data.get("away_score", 0)
        
        # Check for reasonable score ranges
        if home_score > 200 or away_score > 200:
            return False
        
        # Check for reasonable score differences
        score_diff = abs(home_score - away_score)
        return score_diff <= 100  # Unlikely to have 100+ point difference
    
    def _validate_timestamp_freshness(self, data: Dict[str, Any]) -> bool:
        """Validate timestamp freshness"""
        timestamp_str = data.get("timestamp")
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timestamp.tzinfo)
            age_seconds = (now - timestamp).total_seconds()
            
            # Data should be no older than 5 minutes
            return age_seconds <= 300
        except:
            return False
    
    def _validate_format(self, value: Any, field_name: str) -> bool:
        """Validate field format"""
        if field_name == "timestamp":
            try:
                datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                return True
            except:
                return False
        elif field_name == "game_id":
            return isinstance(value, str) and len(value) > 0
        elif field_name == "bookmaker":
            return isinstance(value, str) and len(value) > 0
        
        return True
    
    def _calculate_confidence(self, data: Dict[str, Any], errors: List[str], warnings: List[str]) -> float:
        """Calculate confidence score based on validation results"""
        base_confidence = 1.0
        
        # Reduce confidence for errors
        base_confidence -= len(errors) * 0.3
        
        # Reduce confidence for warnings
        base_confidence -= len(warnings) * 0.1
        
        # Boost confidence for complete data
        if len(data) >= 5:
            base_confidence += 0.1
        
        # Boost confidence for recent data
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(str(data["timestamp"]).replace('Z', '+00:00'))
                now = datetime.now(timestamp.tzinfo)
                age_seconds = (now - timestamp).total_seconds()
                if age_seconds <= 60:  # Very recent data
                    base_confidence += 0.2
                elif age_seconds <= 300:  # Recent data
                    base_confidence += 0.1
            except:
                pass
        
        return max(0.0, min(1.0, base_confidence))

class DataCache:
    """High-performance data cache with TTL"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        self.access_counts = defaultdict(int)
        self.ttl_default = 300  # 5 minutes default TTL
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cache value with TTL"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        ttl = ttl or self.ttl_default
        expiry_time = time.time() + ttl
        
        self.cache[key] = value
        self.timestamps[key] = expiry_time
        self.access_counts[key] = 0
        
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() > self.timestamps[key]:
            self.delete(key)
            return None
        
        # Update access count
        self.access_counts[key] += 1
        
        return self.cache[key]
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            del self.access_counts[key]
            return True
        return False
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self.timestamps.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def _evict_oldest(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find least accessed entry
        least_accessed = min(self.access_counts.items(), key=lambda x: x[1])
        self.delete(least_accessed[0])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        expired_count = sum(1 for expiry_time in self.timestamps.values() if current_time > expiry_time)
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "active_entries": len(self.cache) - expired_count,
            "max_size": self.max_size,
            "utilization_percentage": (len(self.cache) / self.max_size) * 100
        }

class LiveDataStreamer:
    """Real-time data streaming engine"""
    
    def __init__(self):
        self.streams = {}
        self.subscribers = defaultdict(list)
        self.validator = DataValidator()
        self.cache = DataCache()
        self.metrics = {}
        self.alerts = []
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Stream configurations
        self.stream_configs = {
            "odds_stream": LiveDataStream("odds_stream", "api", "odds", 30),
            "scores_stream": LiveDataStream("scores_stream", "api", "scores", 15),
            "stats_stream": LiveDataStream("stats_stream", "api", "stats", 60),
            "news_stream": LiveDataStream("news_stream", "api", "news", 120),
            "sentiment_stream": LiveDataStream("sentiment_stream", "api", "sentiment", 45)
        }
        
        logger.info("🚀 Live Data Streamer initialized - YOLO MODE!")
    
    async def start_streaming(self):
        """Start all data streams"""
        self.is_running = True
        logger.info("🔄 Starting all data streams...")
        
        # Start each stream
        for stream_id, config in self.stream_configs.items():
            if config.is_active:
                asyncio.create_task(self._run_stream(stream_id, config))
        
        # Start cache cleanup task
        asyncio.create_task(self._cache_cleanup_task())
        
        # Start metrics collection task
        asyncio.create_task(self._metrics_collection_task())
        
        logger.info("✅ All data streams started")
    
    async def stop_streaming(self):
        """Stop all data streams"""
        self.is_running = False
        logger.info("🛑 Stopping all data streams...")
        
        # Wait for streams to stop
        await asyncio.sleep(2)
        logger.info("✅ All data streams stopped")
    
    async def _run_stream(self, stream_id: str, config: LiveDataStream):
        """Run individual data stream"""
        logger.info(f"🔄 Starting stream: {stream_id}")
        
        while self.is_running and config.is_active:
            try:
                start_time = time.time()
                
                # Generate mock data (replace with real API calls)
                data = await self._fetch_stream_data(stream_id, config)
                
                # Validate data
                is_valid, errors, confidence = self.validator.validate_data(data, config.data_type)
                
                # Create data point
                data_point = StreamedDataPoint(
                    timestamp=datetime.now().isoformat(),
                    source=config.source,
                    data_type=config.data_type,
                    data=data,
                    validation_status="valid" if is_valid else "invalid",
                    confidence_score=confidence,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
                
                # Cache data
                cache_key = f"{stream_id}_{data_point.timestamp}"
                self.cache.set(cache_key, asdict(data_point), ttl=config.update_frequency * 2)
                
                # Update metrics
                self._update_stream_metrics(stream_id, data_point, errors)
                
                # Notify subscribers
                await self._notify_subscribers(stream_id, data_point)
                
                # Generate alerts if needed
                if not is_valid or confidence < 0.5:
                    await self._generate_alert(stream_id, data_point, errors)
                
                config.last_update = data_point.timestamp
                config.success_count += 1
                
                logger.info(f"✅ {stream_id}: Data processed (confidence: {confidence:.3f})")
                
            except Exception as e:
                config.error_count += 1
                logger.error(f"❌ {stream_id}: Error - {str(e)}")
                await self._generate_alert(stream_id, None, [str(e)])
            
            # Wait for next update
            await asyncio.sleep(config.update_frequency)
    
    async def _fetch_stream_data(self, stream_id: str, config: LiveDataStream) -> Dict[str, Any]:
        """Fetch data from stream source (mock implementation)"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        if config.data_type == "odds":
            return {
                "game_id": f"game_{random.randint(1000, 9999)}",
                "home_odds": round(random.uniform(1.5, 3.0), 2),
                "away_odds": round(random.uniform(1.5, 3.0), 2),
                "draw_odds": round(random.uniform(3.0, 5.0), 2),
                "bookmaker": random.choice(["Bet365", "William Hill", "DraftKings"]),
                "timestamp": datetime.now().isoformat()
            }
        elif config.data_type == "scores":
            return {
                "game_id": f"game_{random.randint(1000, 9999)}",
                "home_score": random.randint(0, 120),
                "away_score": random.randint(0, 120),
                "period": random.randint(1, 4),
                "time_remaining": random.randint(0, 720),
                "timestamp": datetime.now().isoformat()
            }
        elif config.data_type == "stats":
            return {
                "team_id": f"team_{random.randint(1, 30)}",
                "points": random.randint(80, 130),
                "rebounds": random.randint(30, 50),
                "assists": random.randint(15, 30),
                "timestamp": datetime.now().isoformat()
            }
        elif config.data_type == "news":
            return {
                "headline": f"Breaking news {random.randint(1, 100)}",
                "content": f"News content {random.randint(1, 1000)}",
                "source": random.choice(["ESPN", "SportsCenter", "Bleacher Report"]),
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "timestamp": datetime.now().isoformat()
            }
        else:  # sentiment
            return {
                "team_id": f"team_{random.randint(1, 30)}",
                "sentiment_score": random.uniform(-1.0, 1.0),
                "volume": random.randint(100, 10000),
                "source": random.choice(["twitter", "reddit", "news"]),
                "timestamp": datetime.now().isoformat()
            }
    
    def _update_stream_metrics(self, stream_id: str, data_point: StreamedDataPoint, errors: List[str]):
        """Update stream performance metrics"""
        if stream_id not in self.metrics:
            self.metrics[stream_id] = DataStreamMetrics(
                stream_id=stream_id,
                total_messages=0,
                valid_messages=0,
                invalid_messages=0,
                average_latency_ms=0.0,
                throughput_messages_per_second=0.0,
                uptime_percentage=100.0
            )
        
        metrics = self.metrics[stream_id]
        metrics.total_messages += 1
        
        if data_point.validation_status == "valid":
            metrics.valid_messages += 1
        else:
            metrics.invalid_messages += 1
            metrics.last_error = "; ".join(errors) if errors else "Unknown error"
        
        # Update average latency
        total_latency = metrics.average_latency_ms * (metrics.total_messages - 1) + data_point.processing_time_ms
        metrics.average_latency_ms = total_latency / metrics.total_messages
    
    async def _notify_subscribers(self, stream_id: str, data_point: StreamedDataPoint):
        """Notify all subscribers of new data"""
        if stream_id in self.subscribers:
            for callback in self.subscribers[stream_id]:
                try:
                    await callback(data_point)
                except Exception as e:
                    logger.error(f"❌ Subscriber callback error: {str(e)}")
    
    async def _generate_alert(self, stream_id: str, data_point: Optional[StreamedDataPoint], errors: List[str]):
        """Generate real-time alert"""
        alert = RealTimeAlert(
            alert_id=f"alert_{len(self.alerts) + 1}",
            alert_type="validation_error" if data_point else "stream_down",
            severity="high" if len(errors) > 2 else "medium",
            message=f"Stream {stream_id}: {'; '.join(errors)}",
            timestamp=datetime.now().isoformat(),
            data_context={
                "stream_id": stream_id,
                "data_point": asdict(data_point) if data_point else None,
                "errors": errors
            }
        )
        
        self.alerts.append(alert)
        logger.warning(f"⚠️ Alert generated: {alert.message}")
    
    async def _cache_cleanup_task(self):
        """Periodic cache cleanup task"""
        while self.is_running:
            try:
                expired_count = self.cache.clear_expired()
                if expired_count > 0:
                    logger.info(f"🧹 Cache cleanup: {expired_count} expired entries removed")
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {str(e)}")
            
            await asyncio.sleep(60)  # Cleanup every minute
    
    async def _metrics_collection_task(self):
        """Periodic metrics collection task"""
        while self.is_running:
            try:
                for stream_id, metrics in self.metrics.items():
                    # Calculate throughput (simplified)
                    metrics.throughput_messages_per_second = metrics.total_messages / 60.0
                    
                    # Calculate uptime percentage
                    total_attempts = metrics.valid_messages + metrics.invalid_messages
                    if total_attempts > 0:
                        metrics.uptime_percentage = (metrics.valid_messages / total_attempts) * 100
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {str(e)}")
            
            await asyncio.sleep(60)  # Update metrics every minute
    
    def subscribe(self, stream_id: str, callback: Callable):
        """Subscribe to data stream"""
        self.subscribers[stream_id].append(callback)
        logger.info(f"✅ Subscribed to stream: {stream_id}")
    
    def unsubscribe(self, stream_id: str, callback: Callable):
        """Unsubscribe from data stream"""
        if stream_id in self.subscribers and callback in self.subscribers[stream_id]:
            self.subscribers[stream_id].remove(callback)
            logger.info(f"✅ Unsubscribed from stream: {stream_id}")
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all streams"""
        status = {}
        for stream_id, config in self.stream_configs.items():
            metrics = self.metrics.get(stream_id)
            status[stream_id] = {
                "active": config.is_active,
                "last_update": config.last_update,
                "success_count": config.success_count,
                "error_count": config.error_count,
                "metrics": asdict(metrics) if metrics else None
            }
        return status
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return [asdict(alert) for alert in self.alerts[-limit:]]

async def main():
    """Test the real-time data streaming system"""
    print("🚀 Testing Real-Time Data Streaming System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize streaming system
    streamer = LiveDataStreamer()
    
    # Test subscriber callback
    async def test_subscriber(data_point: StreamedDataPoint):
        print(f"📡 Received {data_point.data_type} data: {data_point.validation_status} (confidence: {data_point.confidence_score:.3f})")
    
    # Subscribe to streams
    streamer.subscribe("odds_stream", test_subscriber)
    streamer.subscribe("scores_stream", test_subscriber)
    
    try:
        # Start streaming
        print("\n🔄 Starting Data Streams:")
        print("-" * 40)
        await streamer.start_streaming()
        
        # Let it run for a bit
        print("\n⏱️ Running streams for 30 seconds...")
        await asyncio.sleep(30)
        
        # Get status
        print("\n📊 Stream Status:")
        print("-" * 40)
        status = streamer.get_stream_status()
        for stream_id, stream_status in status.items():
            print(f"✅ {stream_id}:")
            print(f"   Active: {stream_status['active']}")
            print(f"   Success: {stream_status['success_count']}")
            print(f"   Errors: {stream_status['error_count']}")
            if stream_status['metrics']:
                metrics = stream_status['metrics']
                print(f"   Valid: {metrics['valid_messages']}/{metrics['total_messages']}")
                print(f"   Latency: {metrics['average_latency_ms']:.1f}ms")
                print(f"   Uptime: {metrics['uptime_percentage']:.1f}%")
        
        # Get cache stats
        print("\n💾 Cache Statistics:")
        print("-" * 40)
        cache_stats = streamer.get_cache_stats()
        for key, value in cache_stats.items():
            print(f"✅ {key}: {value}")
        
        # Get recent alerts
        print("\n⚠️ Recent Alerts:")
        print("-" * 40)
        alerts = streamer.get_recent_alerts(5)
        for alert in alerts:
            print(f"⚠️ {alert['alert_type']}: {alert['message']}")
        
        # Stop streaming
        print("\n🛑 Stopping streams...")
        await streamer.stop_streaming()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Real-Time Data Streaming System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 