#!/usr/bin/env python3
"""
Enhanced Data Integration System - YOLO MODE!
=============================================
Real-time sports data integration with streaming, validation, caching, and live odds
"""

import asyncio
import aiohttp
import json
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
import redis
import sqlite3
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiveGameData:
    """Real-time game data"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    quarter: str
    time_remaining: str
    status: str
    last_updated: str
    odds: Dict[str, float]
    weather: Optional[Dict[str, Any]]
    injuries: List[str]
    momentum_score: float

@dataclass
class TeamStats:
    """Enhanced team statistics"""
    team_id: str
    team_name: str
    sport: str
    wins: int
    losses: int
    win_percentage: float
    points_for: float
    points_against: float
    streak: int
    home_record: str
    away_record: str
    last_10_games: List[str]
    injuries: List[str]
    form_rating: float
    strength_of_schedule: float
    rest_days: int
    travel_distance: float

@dataclass
class PlayerStats:
    """Enhanced player statistics"""
    player_id: str
    player_name: str
    team: str
    sport: str
    position: str
    games_played: int
    avg_points: float
    avg_rebounds: float
    avg_assists: float
    shooting_percentage: float
    injury_status: str
    form_rating: float
    matchup_advantage: float
    rest_days: int

@dataclass
class LiveOdds:
    """Real-time betting odds"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    home_odds: float
    away_odds: float
    spread: float
    total: float
    home_ml: int
    away_ml: int
    last_updated: str
    line_movement: List[Dict[str, Any]]
    public_betting: Dict[str, float]

@dataclass
class WeatherData:
    """Weather information for outdoor sports"""
    location: str
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: str
    precipitation_chance: float
    conditions: str
    impact_score: float

class DataValidator:
    """Data validation and quality control"""
    
    def __init__(self):
        self.validation_rules = {
            "score": lambda x: isinstance(x, int) and 0 <= x <= 200,
            "percentage": lambda x: isinstance(x, float) and 0 <= x <= 1,
            "odds": lambda x: isinstance(x, float) and x > 0,
            "temperature": lambda x: isinstance(x, float) and -50 <= x <= 150
        }
    
    def validate_game_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate game data quality"""
        errors = []
        
        # Check required fields
        required_fields = ["game_id", "sport", "home_team", "away_team"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate scores
        if "home_score" in data and not self.validation_rules["score"](data["home_score"]):
            errors.append("Invalid home score")
        if "away_score" in data and not self.validation_rules["score"](data["away_score"]):
            errors.append("Invalid away score")
        
        # Validate percentages
        if "win_percentage" in data and not self.validation_rules["percentage"](data["win_percentage"]):
            errors.append("Invalid win percentage")
        
        return len(errors) == 0, errors
    
    def validate_odds_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate odds data quality"""
        errors = []
        
        # Check required fields
        required_fields = ["game_id", "home_odds", "away_odds"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate odds
        if "home_odds" in data and not self.validation_rules["odds"](data["home_odds"]):
            errors.append("Invalid home odds")
        if "away_odds" in data and not self.validation_rules["odds"](data["away_odds"]):
            errors.append("Invalid away odds")
        
        return len(errors) == 0, errors

class DataCache:
    """Intelligent data caching system"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = {
            "live_games": 30,  # 30 seconds
            "team_stats": 300,  # 5 minutes
            "player_stats": 600,  # 10 minutes
            "odds": 60,  # 1 minute
            "weather": 900,  # 15 minutes
            "historical": 3600  # 1 hour
        }
    
    def get(self, key: str, data_type: str) -> Optional[Any]:
        """Get cached data if still valid"""
        if key not in self.cache:
            return None
        
        if key not in self.cache_timestamps:
            return None
        
        # Check if cache is still valid
        ttl = self.cache_ttl.get(data_type, 300)
        if time.time() - self.cache_timestamps[key] > ttl:
            # Cache expired, remove it
            del self.cache[key]
            del self.cache_timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, data: Any, data_type: str):
        """Cache data with timestamp"""
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()
        logger.info(f"✅ Cached {data_type} data for key: {key}")
    
    def invalidate(self, key: str):
        """Invalidate cached data"""
        if key in self.cache:
            del self.cache[key]
        if key in self.cache_timestamps:
            del self.cache_timestamps[key]
        logger.info(f"🗑️ Invalidated cache for key: {key}")

class LiveDataStreamer:
    """Real-time data streaming system"""
    
    def __init__(self):
        self.active_streams = {}
        self.subscribers = defaultdict(list)
        self.data_buffer = defaultdict(list)
        self.max_buffer_size = 1000
    
    async def start_stream(self, sport: str, game_id: str):
        """Start real-time data stream for a game"""
        stream_key = f"{sport}_{game_id}"
        
        if stream_key in self.active_streams:
            logger.info(f"🔄 Stream already active for {stream_key}")
            return
        
        self.active_streams[stream_key] = True
        logger.info(f"🚀 Started live stream for {stream_key}")
        
        # Start streaming task
        asyncio.create_task(self._stream_data(sport, game_id))
    
    async def _stream_data(self, sport: str, game_id: str):
        """Stream real-time data for a game"""
        stream_key = f"{sport}_{game_id}"
        
        while self.active_streams.get(stream_key, False):
            try:
                # Simulate real-time data updates
                live_data = await self._fetch_live_data(sport, game_id)
                
                if live_data:
                    # Add to buffer
                    self.data_buffer[stream_key].append(live_data)
                    
                    # Keep buffer size manageable
                    if len(self.data_buffer[stream_key]) > self.max_buffer_size:
                        self.data_buffer[stream_key] = self.data_buffer[stream_key][-self.max_buffer_size:]
                    
                    # Notify subscribers
                    await self._notify_subscribers(stream_key, live_data)
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in data stream {stream_key}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _fetch_live_data(self, sport: str, game_id: str) -> Optional[LiveGameData]:
        """Fetch live data from API (simulated)"""
        try:
            # Simulate API call with realistic data
            home_score = random.randint(80, 120)
            away_score = random.randint(80, 120)
            
            # Calculate momentum score based on recent scoring
            momentum_score = (home_score - away_score) / 10.0
            
            return LiveGameData(
                game_id=game_id,
                sport=sport,
                home_team=f"Home Team {game_id}",
                away_team=f"Away Team {game_id}",
                home_score=home_score,
                away_score=away_score,
                quarter="Q4",
                time_remaining="2:30",
                status="Live",
                last_updated=datetime.now().isoformat(),
                odds={"home": 1.85, "away": 2.10},
                weather={"temperature": 72, "conditions": "Clear"},
                injuries=[],
                momentum_score=momentum_score
            )
        except Exception as e:
            logger.error(f"❌ Error fetching live data: {e}")
            return None
    
    async def _notify_subscribers(self, stream_key: str, data: LiveGameData):
        """Notify all subscribers of new data"""
        for callback in self.subscribers[stream_key]:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"❌ Error in subscriber callback: {e}")
    
    def subscribe(self, stream_key: str, callback):
        """Subscribe to a data stream"""
        self.subscribers[stream_key].append(callback)
        logger.info(f"📡 Subscribed to stream: {stream_key}")
    
    def unsubscribe(self, stream_key: str, callback):
        """Unsubscribe from a data stream"""
        if stream_key in self.subscribers and callback in self.subscribers[stream_key]:
            self.subscribers[stream_key].remove(callback)
            logger.info(f"📡 Unsubscribed from stream: {stream_key}")

class EnhancedDataIntegration:
    """Enhanced data integration system - YOLO MODE!"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.cache = DataCache()
        self.streamer = LiveDataStreamer()
        self.session = None
        self.redis_client = None
        
        # API configurations
        self.apis = {
            "sportradar": {
                "base_url": "https://api.sportradar.us",
                "api_key": "your_sportradar_key",
                "rate_limit": 1000  # requests per hour
            },
            "espn": {
                "base_url": "https://site.api.espn.com",
                "rate_limit": 500
            },
            "odds_api": {
                "base_url": "https://api.the-odds-api.com",
                "api_key": "your_odds_api_key",
                "rate_limit": 500
            },
            "weather_api": {
                "base_url": "https://api.openweathermap.org",
                "api_key": "your_weather_api_key",
                "rate_limit": 1000
            }
        }
        
        # Rate limiting
        self.request_counts = defaultdict(int)
        self.last_reset = time.time()
        
        logger.info("🚀 Enhanced Data Integration System initialized - YOLO MODE!")
    
    async def initialize(self):
        """Initialize the data integration system"""
        try:
            # Initialize aiohttp session
            self.session = aiohttp.ClientSession()
            
            # Initialize Redis (if available)
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
                await self.redis_client.ping()
                logger.info("✅ Redis connection established")
            except:
                logger.warning("⚠️ Redis not available, using in-memory cache")
                self.redis_client = None
            
            logger.info("✅ Enhanced Data Integration System ready!")
            
        except Exception as e:
            logger.error(f"❌ Error initializing data integration: {e}")
    
    async def get_live_games(self, sport: str) -> List[LiveGameData]:
        """Get live games with real-time data"""
        cache_key = f"live_games_{sport}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key, "live_games")
        if cached_data:
            return cached_data
        
        try:
            # Fetch live games from multiple sources
            games = []
            
            # ESPN API
            espn_games = await self._fetch_espn_live_games(sport)
            games.extend(espn_games)
            
            # Sportradar API
            sportradar_games = await self._fetch_sportradar_live_games(sport)
            games.extend(sportradar_games)
            
            # Enrich with additional data
            enriched_games = []
            for game in games:
                # Add weather data for outdoor sports
                if sport in ["football", "baseball"]:
                    weather = await self._get_weather_data(game.home_team)
                    game.weather = weather
                
                # Add injury data
                injuries = await self._get_injury_data(game.home_team, game.away_team)
                game.injuries = injuries
                
                # Add live odds
                odds = await self._fetch_live_odds(game.game_id)
                if odds:
                    game.odds = {"home": odds.home_odds, "away": odds.away_odds}
                
                enriched_games.append(game)
            
            # Cache the results
            self.cache.set(cache_key, enriched_games, "live_games")
            
            return enriched_games
            
        except Exception as e:
            logger.error(f"❌ Error fetching live games: {e}")
            return []
    
    async def get_team_stats(self, team_id: str, sport: str) -> Optional[TeamStats]:
        """Get comprehensive team statistics"""
        cache_key = f"team_stats_{team_id}_{sport}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key, "team_stats")
        if cached_data:
            return cached_data
        
        try:
            # Fetch from multiple sources
            stats = await self._fetch_team_stats(team_id, sport)
            
            if stats:
                # Enrich with additional data
                stats.form_rating = await self._calculate_form_rating(team_id, sport)
                stats.strength_of_schedule = await self._calculate_sos(team_id, sport)
                stats.rest_days = await self._get_rest_days(team_id)
                stats.travel_distance = await self._calculate_travel_distance(team_id)
                
                # Cache the results
                self.cache.set(cache_key, stats, "team_stats")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error fetching team stats: {e}")
            return None
    
    async def get_player_stats(self, player_id: str, sport: str) -> Optional[PlayerStats]:
        """Get comprehensive player statistics"""
        cache_key = f"player_stats_{player_id}_{sport}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key, "player_stats")
        if cached_data:
            return cached_data
        
        try:
            # Fetch player stats
            stats = await self._fetch_player_stats(player_id, sport)
            
            if stats:
                # Enrich with additional data
                stats.form_rating = await self._calculate_player_form(player_id, sport)
                stats.matchup_advantage = await self._calculate_matchup_advantage(player_id)
                stats.rest_days = await self._get_player_rest_days(player_id)
                
                # Cache the results
                self.cache.set(cache_key, stats, "player_stats")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error fetching player stats: {e}")
            return None
    
    async def get_live_odds(self, game_id: str) -> Optional[LiveOdds]:
        """Get real-time betting odds"""
        cache_key = f"live_odds_{game_id}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key, "odds")
        if cached_data:
            return cached_data
        
        try:
            # Fetch from multiple odds providers
            odds = await self._fetch_live_odds(game_id)
            
            if odds:
                # Track line movement
                odds.line_movement = await self._get_line_movement(game_id)
                odds.public_betting = await self._get_public_betting(game_id)
                
                # Cache the results
                self.cache.set(cache_key, odds, "odds")
            
            return odds
            
        except Exception as e:
            logger.error(f"❌ Error fetching live odds: {e}")
            return None
    
    async def start_live_stream(self, sport: str, game_id: str):
        """Start live data streaming for a game"""
        await self.streamer.start_stream(sport, game_id)
    
    async def subscribe_to_live_data(self, sport: str, game_id: str, callback):
        """Subscribe to live data updates"""
        stream_key = f"{sport}_{game_id}"
        self.streamer.subscribe(stream_key, callback)
    
    # Helper methods for data fetching (simulated)
    async def _fetch_espn_live_games(self, sport: str) -> List[LiveGameData]:
        """Fetch live games from ESPN API"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        games = []
        for i in range(random.randint(2, 5)):
            game = LiveGameData(
                game_id=f"espn_{sport}_{i}",
                sport=sport,
                home_team=f"ESPN Home {i}",
                away_team=f"ESPN Away {i}",
                home_score=random.randint(80, 120),
                away_score=random.randint(80, 120),
                quarter="Q3",
                time_remaining="5:30",
                status="Live",
                last_updated=datetime.now().isoformat(),
                odds={"home": 1.90, "away": 1.95},
                weather=None,
                injuries=[],
                momentum_score=random.uniform(-2.0, 2.0)
            )
            games.append(game)
        
        return games
    
    async def _fetch_sportradar_live_games(self, sport: str) -> List[LiveGameData]:
        """Fetch live games from Sportradar API"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        games = []
        for i in range(random.randint(1, 3)):
            game = LiveGameData(
                game_id=f"sportradar_{sport}_{i}",
                sport=sport,
                home_team=f"Sportradar Home {i}",
                away_team=f"Sportradar Away {i}",
                home_score=random.randint(80, 120),
                away_score=random.randint(80, 120),
                quarter="Q4",
                time_remaining="1:45",
                status="Live",
                last_updated=datetime.now().isoformat(),
                odds={"home": 1.85, "away": 2.05},
                weather=None,
                injuries=[],
                momentum_score=random.uniform(-2.0, 2.0)
            )
            games.append(game)
        
        return games
    
    async def _fetch_team_stats(self, team_id: str, sport: str) -> Optional[TeamStats]:
        """Fetch team statistics"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        return TeamStats(
            team_id=team_id,
            team_name=f"Team {team_id}",
            sport=sport,
            wins=random.randint(20, 50),
            losses=random.randint(10, 30),
            win_percentage=random.uniform(0.4, 0.8),
            points_for=random.uniform(100, 120),
            points_against=random.uniform(100, 120),
            streak=random.randint(-5, 8),
            home_record=f"{random.randint(10, 25)}-{random.randint(5, 15)}",
            away_record=f"{random.randint(8, 20)}-{random.randint(8, 20)}",
            last_10_games=["W", "L", "W", "W", "L", "W", "L", "W", "W", "L"],
            injuries=[],
            form_rating=0.0,
            strength_of_schedule=0.0,
            rest_days=0,
            travel_distance=0.0
        )
    
    async def _fetch_player_stats(self, player_id: str, sport: str) -> Optional[PlayerStats]:
        """Fetch player statistics"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        return PlayerStats(
            player_id=player_id,
            player_name=f"Player {player_id}",
            team=f"Team {player_id}",
            sport=sport,
            position="PG",
            games_played=random.randint(20, 82),
            avg_points=random.uniform(10, 30),
            avg_rebounds=random.uniform(2, 12),
            avg_assists=random.uniform(2, 10),
            shooting_percentage=random.uniform(0.35, 0.55),
            injury_status="Healthy",
            form_rating=0.0,
            matchup_advantage=0.0,
            rest_days=0
        )
    
    async def _fetch_live_odds(self, game_id: str) -> Optional[LiveOdds]:
        """Fetch live odds"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        return LiveOdds(
            game_id=game_id,
            sport="basketball",
            home_team="Home Team",
            away_team="Away Team",
            home_odds=random.uniform(1.5, 2.5),
            away_odds=random.uniform(1.5, 2.5),
            spread=random.uniform(-10, 10),
            total=random.uniform(200, 240),
            home_ml=random.randint(-200, 200),
            away_ml=random.randint(-200, 200),
            last_updated=datetime.now().isoformat(),
            line_movement=[],
            public_betting={"home": 0.55, "away": 0.45}
        )
    
    async def _get_weather_data(self, team: str) -> Optional[WeatherData]:
        """Get weather data for outdoor sports"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        return WeatherData(
            location=team,
            temperature=random.uniform(50, 90),
            humidity=random.uniform(0.3, 0.8),
            wind_speed=random.uniform(0, 20),
            wind_direction="NE",
            precipitation_chance=random.uniform(0, 0.3),
            conditions="Clear",
            impact_score=random.uniform(0, 1.0)
        )
    
    async def _get_injury_data(self, home_team: str, away_team: str) -> List[str]:
        """Get injury data for teams"""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        injuries = []
        if random.random() < 0.3:  # 30% chance of injuries
            injuries.append(f"Player {random.randint(1, 20)} - Ankle")
        if random.random() < 0.2:  # 20% chance of more injuries
            injuries.append(f"Player {random.randint(21, 40)} - Knee")
        
        return injuries
    
    async def _calculate_form_rating(self, team_id: str, sport: str) -> float:
        """Calculate team form rating"""
        await asyncio.sleep(0.05)
        return random.uniform(0.3, 0.9)
    
    async def _calculate_sos(self, team_id: str, sport: str) -> float:
        """Calculate strength of schedule"""
        await asyncio.sleep(0.05)
        return random.uniform(0.4, 0.8)
    
    async def _get_rest_days(self, team_id: str) -> int:
        """Get days of rest for team"""
        await asyncio.sleep(0.05)
        return random.randint(1, 7)
    
    async def _calculate_travel_distance(self, team_id: str) -> float:
        """Calculate travel distance"""
        await asyncio.sleep(0.05)
        return random.uniform(0, 3000)
    
    async def _calculate_player_form(self, player_id: str, sport: str) -> float:
        """Calculate player form rating"""
        await asyncio.sleep(0.05)
        return random.uniform(0.3, 0.9)
    
    async def _calculate_matchup_advantage(self, player_id: str) -> float:
        """Calculate player matchup advantage"""
        await asyncio.sleep(0.05)
        return random.uniform(-0.5, 0.5)
    
    async def _get_player_rest_days(self, player_id: str) -> int:
        """Get days of rest for player"""
        await asyncio.sleep(0.05)
        return random.randint(1, 5)
    
    async def _get_line_movement(self, game_id: str) -> List[Dict[str, Any]]:
        """Get line movement history"""
        await asyncio.sleep(0.05)
        return [
            {"time": "2 hours ago", "spread": -3.5, "total": 225},
            {"time": "1 hour ago", "spread": -4.0, "total": 224.5},
            {"time": "30 min ago", "spread": -3.5, "total": 225}
        ]
    
    async def _get_public_betting(self, game_id: str) -> Dict[str, float]:
        """Get public betting percentages"""
        await asyncio.sleep(0.05)
        return {"home": random.uniform(0.4, 0.6), "away": random.uniform(0.4, 0.6)}

async def main():
    """Test the enhanced data integration system"""
    print("🚀 Testing Enhanced Data Integration System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize system
    data_system = EnhancedDataIntegration()
    await data_system.initialize()
    
    try:
        # Test live games
        print("\n🎯 Testing Live Games:")
        print("-" * 40)
        live_games = await data_system.get_live_games("basketball")
        print(f"✅ Found {len(live_games)} live basketball games")
        
        for game in live_games[:3]:  # Show first 3 games
            print(f"   🏀 {game.home_team} vs {game.away_team}")
            print(f"      Score: {game.home_score} - {game.away_score}")
            print(f"      Status: {game.status} ({game.quarter}, {game.time_remaining})")
            print(f"      Momentum: {game.momentum_score:.2f}")
        
        # Test team stats
        print("\n📊 Testing Team Statistics:")
        print("-" * 40)
        team_stats = await data_system.get_team_stats("LAL", "basketball")
        if team_stats:
            print(f"✅ Team: {team_stats.team_name}")
            print(f"   Record: {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.3f})")
            print(f"   Streak: {team_stats.streak}")
            print(f"   Form Rating: {team_stats.form_rating:.3f}")
        
        # Test player stats
        print("\n👤 Testing Player Statistics:")
        print("-" * 40)
        player_stats = await data_system.get_player_stats("LBJ", "basketball")
        if player_stats:
            print(f"✅ Player: {player_stats.player_name}")
            print(f"   Position: {player_stats.position}")
            print(f"   PPG: {player_stats.avg_points:.1f}")
            print(f"   Form Rating: {player_stats.form_rating:.3f}")
        
        # Test live odds
        print("\n💰 Testing Live Odds:")
        print("-" * 40)
        odds = await data_system.get_live_odds("game_123")
        if odds:
            print(f"✅ Game: {odds.home_team} vs {odds.away_team}")
            print(f"   Spread: {odds.spread:+.1f}")
            print(f"   Total: {odds.total:.1f}")
            print(f"   Home ML: {odds.home_ml:+d}")
            print(f"   Public Betting: {odds.public_betting['home']:.1%} home")
        
        # Test live streaming
        print("\n📡 Testing Live Data Streaming:")
        print("-" * 40)
        
        async def data_callback(data):
            print(f"   📡 Live Update: {data.home_team} {data.home_score} - {data.away_team} {data.away_score}")
        
        await data_system.subscribe_to_live_data("basketball", "test_game", data_callback)
        await data_system.start_live_stream("basketball", "test_game")
        
        # Let it run for a few seconds
        await asyncio.sleep(5)
        
        print("✅ Live streaming test completed")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Enhanced Data Integration System Test Completed!")
    print("=" * 70)
    
    # Cleanup
    if data_system.session:
        await data_system.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 