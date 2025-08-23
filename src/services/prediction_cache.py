#!/usr/bin/env python3
"""
Prediction Caching System for MultiSportsBettingPlatform
Improves performance by caching predictions and reducing redundant API calls.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
import asyncio
from collections import OrderedDict

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for predictions."""
    key: str
    data: Any
    timestamp: datetime
    ttl: int  # Time to live in seconds
    access_count: int = 0
    last_accessed: datetime = None
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)
    
    def update_access(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now()

class PredictionCache:
    """LRU cache for predictions with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def _generate_key(self, query: str, sports: List[str], user_id: str = None) -> str:
        """Generate a unique cache key for the query."""
        key_data = {
            'query': query.lower().strip(),
            'sports': sorted(sports),
            'user_id': user_id
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, sports: List[str], user_id: str = None) -> Optional[Any]:
        """Get cached prediction if available and not expired."""
        key = self._generate_key(query, sports, user_id)
        
        if key in self.cache:
            entry = self.cache[key]
            
            if entry.is_expired():
                # Remove expired entry
                del self.cache[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                logger.debug(f"Cache miss (expired): {key}")
                return None
            
            # Update access statistics
            entry.update_access()
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            
            self.stats['hits'] += 1
            logger.debug(f"Cache hit: {key}")
            return entry.data
        
        self.stats['misses'] += 1
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(self, query: str, sports: List[str], data: Any, 
            ttl: int = None, user_id: str = None) -> str:
        """Cache a prediction with TTL."""
        key = self._generate_key(query, sports, user_id)
        ttl = ttl or self.default_ttl
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            data=data,
            timestamp=datetime.now(),
            ttl=ttl
        )
        
        # Check if cache is full
        if len(self.cache) >= self.max_size:
            # Remove least recently used entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
            logger.debug(f"Cache eviction: {oldest_key}")
        
        # Add new entry
        self.cache[key] = entry
        logger.debug(f"Cached prediction: {key}")
        
        return key
    
    def invalidate(self, query: str = None, sports: List[str] = None, 
                   user_id: str = None) -> int:
        """Invalidate cache entries matching criteria."""
        invalidated_count = 0
        
        if query is None and sports is None and user_id is None:
            # Clear all cache
            invalidated_count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cleared entire cache ({invalidated_count} entries)")
            return invalidated_count
        
        # Invalidate matching entries
        keys_to_remove = []
        
        for key, entry in self.cache.items():
            should_remove = False
            
            if query and query.lower().strip() in entry.data.get('query', '').lower():
                should_remove = True
            
            if sports and any(sport in entry.data.get('sports', []) for sport in sports):
                should_remove = True
            
            if user_id and entry.data.get('user_id') == user_id:
                should_remove = True
            
            if should_remove:
                keys_to_remove.append(key)
        
        # Remove matching entries
        for key in keys_to_remove:
            del self.cache[key]
            invalidated_count += 1
        
        logger.info(f"Invalidated {invalidated_count} cache entries")
        return invalidated_count
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries from cache."""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            self.stats['expirations'] += 1
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = 0
        if self.stats['hits'] + self.stats['misses'] > 0:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': hit_rate,
            'evictions': self.stats['evictions'],
            'expirations': self.stats['expirations'],
            'utilization': len(self.cache) / self.max_size
        }
    
    def get_popular_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed queries."""
        query_counts = {}
        
        for entry in self.cache.values():
            query = entry.data.get('query', '')
            query_counts[query] = query_counts.get(query, 0) + entry.access_count
        
        # Sort by access count
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:limit]

class SportSpecificCache:
    """Cache optimized for sport-specific predictions."""
    
    def __init__(self, max_size_per_sport: int = 200):
        self.max_size_per_sport = max_size_per_sport
        self.sport_caches = {}
        self.sport_stats = {}
    
    def _get_sport_cache(self, sport: str) -> PredictionCache:
        """Get or create cache for a specific sport."""
        if sport not in self.sport_caches:
            self.sport_caches[sport] = PredictionCache(
                max_size=self.max_size_per_sport,
                default_ttl=600  # 10 minutes for sport-specific cache
            )
            self.sport_stats[sport] = {
                'hits': 0,
                'misses': 0,
                'total_queries': 0
            }
        
        return self.sport_caches[sport]
    
    def get(self, sport: str, query: str, user_id: str = None) -> Optional[Any]:
        """Get cached prediction for a specific sport."""
        cache = self._get_sport_cache(sport)
        result = cache.get(query, [sport], user_id)
        
        if result:
            self.sport_stats[sport]['hits'] += 1
        else:
            self.sport_stats[sport]['misses'] += 1
        
        self.sport_stats[sport]['total_queries'] += 1
        return result
    
    def set(self, sport: str, query: str, data: Any, 
            ttl: int = None, user_id: str = None) -> str:
        """Cache prediction for a specific sport."""
        cache = self._get_sport_cache(sport)
        return cache.set(query, [sport], data, ttl, user_id)
    
    def invalidate_sport(self, sport: str) -> int:
        """Invalidate all cache entries for a specific sport."""
        if sport in self.sport_caches:
            cache = self.sport_caches[sport]
            return cache.invalidate(sports=[sport])
        return 0
    
    def get_sport_stats(self, sport: str = None) -> Dict[str, Any]:
        """Get statistics for a specific sport or all sports."""
        if sport:
            if sport in self.sport_stats:
                stats = self.sport_stats[sport]
                cache = self.sport_caches[sport]
                cache_stats = cache.get_stats()
                return {**stats, **cache_stats}
            return {}
        
        # Return stats for all sports
        all_stats = {}
        for sport_name in self.sport_stats:
            all_stats[sport_name] = self.get_sport_stats(sport_name)
        
        return all_stats

class CacheManager:
    """Manages multiple cache instances."""
    
    def __init__(self):
        self.main_cache = PredictionCache(max_size=1000, default_ttl=300)
        self.sport_cache = SportSpecificCache(max_size_per_sport=200)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    async def get_cached_prediction(self, query: str, sports: List[str], 
                                   user_id: str = None) -> Optional[Any]:
        """Get prediction from appropriate cache."""
        # Try main cache first
        result = self.main_cache.get(query, sports, user_id)
        if result:
            return result
        
        # Try sport-specific caches
        for sport in sports:
            result = self.sport_cache.get(sport, query, user_id)
            if result:
                return result
        
        return None
    
    async def cache_prediction(self, query: str, sports: List[str], data: Any,
                              ttl: int = None, user_id: str = None):
        """Cache prediction in appropriate caches."""
        # Cache in main cache
        self.main_cache.set(query, sports, data, ttl, user_id)
        
        # Cache in sport-specific caches
        for sport in sports:
            self.sport_cache.set(sport, query, data, ttl, user_id)
    
    def cleanup(self):
        """Clean up expired entries from all caches."""
        current_time = time.time()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            # Clean main cache
            self.main_cache.cleanup_expired()
            
            # Clean sport-specific caches
            for sport_cache in self.sport_cache.sport_caches.values():
                sport_cache.cleanup_expired()
            
            self.last_cleanup = current_time
            logger.info("Cache cleanup completed")
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get statistics from all caches."""
        main_stats = self.main_cache.get_stats()
        sport_stats = self.sport_cache.get_sport_stats()
        
        return {
            'main_cache': main_stats,
            'sport_caches': sport_stats,
            'total_entries': main_stats['size'] + sum(
                stats.get('size', 0) for stats in sport_stats.values()
            )
        } 