#!/usr/bin/env python3
"""
Data Integration System - YOLO MODE!
===================================
Comprehensive sports data integration with multiple APIs
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TeamStats:
    """Team statistics data structure"""
    team_id: str
    team_name: str
    sport: str
    wins: int
    losses: int
    ties: int = 0
    win_percentage: float = 0.0
    points_for: int = 0
    points_against: int = 0
    streak: str = ""
    last_updated: str = ""

@dataclass
class PlayerStats:
    """Player statistics data structure"""
    player_id: str
    player_name: str
    team: str
    sport: str
    position: str
    games_played: int
    stats: Dict[str, Any]
    last_updated: str = ""

@dataclass
class GameData:
    """Game/match data structure"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    game_date: str
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    odds: Dict[str, float] = None
    weather: Optional[Dict[str, Any]] = None

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    api_key: str
    base_url: str
    rate_limit: int  # requests per minute
    last_request: float = 0.0
    requests_made: int = 0

class DataIntegrationSystem:
    """Comprehensive sports data integration system"""
    
    def __init__(self):
        self.sources = {
            "sportradar": DataSource(
                name="Sportradar",
                api_key="your_sportradar_api_key_here",
                base_url="https://api.sportradar.us",
                rate_limit=60
            ),
            "espn": DataSource(
                name="ESPN",
                api_key="your_espn_api_key_here", 
                base_url="https://site.api.espn.com",
                rate_limit=100
            ),
            "the_odds_api": DataSource(
                name="The Odds API",
                api_key="your_odds_api_key_here",
                base_url="https://api.the-odds-api.com",
                rate_limit=500
            ),
            "api_football": DataSource(
                name="API-Football",
                api_key="your_api_football_key_here",
                base_url="https://v3.football.api-sports.io",
                rate_limit=100
            )
        }
        
        # Cache for storing data
        self.cache = {
            "team_stats": {},
            "player_stats": {},
            "games": {},
            "odds": {}
        }
        
        # Cache expiration (in seconds)
        self.cache_expiry = {
            "team_stats": 3600,  # 1 hour
            "player_stats": 1800,  # 30 minutes
            "games": 300,  # 5 minutes
            "odds": 60  # 1 minute
        }
        
        logger.info("🚀 Data Integration System initialized - YOLO MODE!")

    async def rate_limit_check(self, source_name: str) -> bool:
        """Check and enforce rate limits"""
        source = self.sources.get(source_name)
        if not source:
            return False
            
        current_time = time.time()
        time_diff = current_time - source.last_request
        
        # Reset counter if more than 1 minute has passed
        if time_diff >= 60:
            source.requests_made = 0
            source.last_request = current_time
            
        # Check if we're within rate limit
        if source.requests_made >= source.rate_limit:
            wait_time = 60 - time_diff
            if wait_time > 0:
                logger.warning(f"⚠️ Rate limit reached for {source_name}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                source.requests_made = 0
                source.last_request = time.time()
                
        source.requests_made += 1
        return True

    async def fetch_team_stats(self, sport: str, team_id: str = None) -> List[TeamStats]:
        """Fetch team statistics from multiple sources"""
        cache_key = f"{sport}_teams"
        
        # Check cache first
        if cache_key in self.cache["team_stats"]:
            cached_data = self.cache["team_stats"][cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_expiry["team_stats"]:
                logger.info(f"✅ Using cached team stats for {sport}")
                return cached_data["data"]
        
        logger.info(f"🔄 Fetching fresh team stats for {sport}")
        
        # Fetch from multiple sources for redundancy
        all_stats = []
        
        # ESPN API (free tier available)
        try:
            if await self.rate_limit_check("espn"):
                espn_stats = await self._fetch_espn_team_stats(sport)
                all_stats.extend(espn_stats)
                logger.info(f"✅ ESPN data fetched for {sport}: {len(espn_stats)} teams")
        except Exception as e:
            logger.error(f"❌ ESPN API error: {e}")
        
        # Sportradar API (paid, more comprehensive)
        try:
            if await self.rate_limit_check("sportradar"):
                sportradar_stats = await self._fetch_sportradar_team_stats(sport)
                all_stats.extend(sportradar_stats)
                logger.info(f"✅ Sportradar data fetched for {sport}: {len(sportradar_stats)} teams")
        except Exception as e:
            logger.error(f"❌ Sportradar API error: {e}")
        
        # Cache the results
        self.cache["team_stats"][cache_key] = {
            "data": all_stats,
            "timestamp": time.time()
        }
        
        return all_stats

    async def fetch_player_stats(self, sport: str, team_id: str = None) -> List[PlayerStats]:
        """Fetch player statistics"""
        cache_key = f"{sport}_players_{team_id or 'all'}"
        
        # Check cache first
        if cache_key in self.cache["player_stats"]:
            cached_data = self.cache["player_stats"][cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_expiry["player_stats"]:
                logger.info(f"✅ Using cached player stats for {sport}")
                return cached_data["data"]
        
        logger.info(f"🔄 Fetching fresh player stats for {sport}")
        
        all_stats = []
        
        # ESPN API for player stats
        try:
            if await self.rate_limit_check("espn"):
                espn_stats = await self._fetch_espn_player_stats(sport, team_id)
                all_stats.extend(espn_stats)
                logger.info(f"✅ ESPN player data fetched: {len(espn_stats)} players")
        except Exception as e:
            logger.error(f"❌ ESPN player API error: {e}")
        
        # Cache the results
        self.cache["player_stats"][cache_key] = {
            "data": all_stats,
            "timestamp": time.time()
        }
        
        return all_stats

    async def fetch_game_odds(self, sport: str, game_id: str = None) -> Dict[str, Any]:
        """Fetch betting odds for games"""
        cache_key = f"{sport}_odds_{game_id or 'current'}"
        
        # Check cache first
        if cache_key in self.cache["odds"]:
            cached_data = self.cache["odds"][cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_expiry["odds"]:
                logger.info(f"✅ Using cached odds for {sport}")
                return cached_data["data"]
        
        logger.info(f"🔄 Fetching fresh odds for {sport}")
        
        odds_data = {}
        
        # The Odds API
        try:
            if await self.rate_limit_check("the_odds_api"):
                odds_data = await self._fetch_odds_api(sport)
                logger.info(f"✅ Odds API data fetched for {sport}")
        except Exception as e:
            logger.error(f"❌ Odds API error: {e}")
        
        # Cache the results
        self.cache["odds"][cache_key] = {
            "data": odds_data,
            "timestamp": time.time()
        }
        
        return odds_data

    async def fetch_upcoming_games(self, sport: str, days_ahead: int = 7) -> List[GameData]:
        """Fetch upcoming games"""
        cache_key = f"{sport}_games_{days_ahead}"
        
        # Check cache first
        if cache_key in self.cache["games"]:
            cached_data = self.cache["games"][cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_expiry["games"]:
                logger.info(f"✅ Using cached games for {sport}")
                return cached_data["data"]
        
        logger.info(f"🔄 Fetching upcoming games for {sport}")
        
        games = []
        
        # ESPN API for upcoming games
        try:
            if await self.rate_limit_check("espn"):
                espn_games = await self._fetch_espn_upcoming_games(sport, days_ahead)
                games.extend(espn_games)
                logger.info(f"✅ ESPN games fetched: {len(espn_games)} games")
        except Exception as e:
            logger.error(f"❌ ESPN games API error: {e}")
        
        # Cache the results
        self.cache["games"][cache_key] = {
            "data": games,
            "timestamp": time.time()
        }
        
        return games

    async def _fetch_espn_team_stats(self, sport: str) -> List[TeamStats]:
        """Fetch team stats from ESPN API"""
        sport_mapping = {
            "basketball": "basketball/nba",
            "football": "football/nfl", 
            "baseball": "baseball/mlb",
            "hockey": "hockey/nhl"
        }
        
        sport_path = sport_mapping.get(sport, sport)
        url = f"{self.sources['espn'].base_url}/apis/site/v2/sports/{sport_path}/teams"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    teams = []
                    
                    for team in data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", []):
                        team_info = team.get("team", {})
                        stats = team.get("stats", [])
                        
                        # Extract basic stats
                        wins = 0
                        losses = 0
                        ties = 0
                        
                        for stat in stats:
                            if stat.get("name") == "wins":
                                wins = stat.get("value", 0)
                            elif stat.get("name") == "losses":
                                losses = stat.get("value", 0)
                            elif stat.get("name") == "ties":
                                ties = stat.get("value", 0)
                        
                        win_percentage = wins / (wins + losses + ties) if (wins + losses + ties) > 0 else 0
                        
                        teams.append(TeamStats(
                            team_id=team_info.get("id", ""),
                            team_name=team_info.get("name", ""),
                            sport=sport,
                            wins=wins,
                            losses=losses,
                            ties=ties,
                            win_percentage=win_percentage,
                            last_updated=datetime.now().isoformat()
                        ))
                    
                    return teams
                else:
                    logger.error(f"❌ ESPN API error: {response.status}")
                    return []

    async def _fetch_espn_player_stats(self, sport: str, team_id: str = None) -> List[PlayerStats]:
        """Fetch player stats from ESPN API"""
        sport_mapping = {
            "basketball": "basketball/nba",
            "football": "football/nfl",
            "baseball": "baseball/mlb", 
            "hockey": "hockey/nhl"
        }
        
        sport_path = sport_mapping.get(sport, sport)
        url = f"{self.sources['espn'].base_url}/apis/site/v2/sports/{sport_path}/athletes"
        
        if team_id:
            url += f"?team={team_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    players = []
                    
                    for athlete in data.get("athletes", []):
                        stats = athlete.get("stats", {})
                        
                        players.append(PlayerStats(
                            player_id=athlete.get("id", ""),
                            player_name=athlete.get("fullName", ""),
                            team=athlete.get("team", {}).get("name", ""),
                            sport=sport,
                            position=athlete.get("position", {}).get("abbreviation", ""),
                            games_played=stats.get("gamesPlayed", 0),
                            stats=stats,
                            last_updated=datetime.now().isoformat()
                        ))
                    
                    return players
                else:
                    logger.error(f"❌ ESPN player API error: {response.status}")
                    return []

    async def _fetch_odds_api(self, sport: str) -> Dict[str, Any]:
        """Fetch odds from The Odds API"""
        sport_mapping = {
            "basketball": "basketball_nba",
            "football": "americanfootball_nfl",
            "baseball": "baseball_mlb",
            "hockey": "icehockey_nhl"
        }
        
        sport_key = sport_mapping.get(sport, sport)
        url = f"{self.sources['the_odds_api'].base_url}/v4/sports/{sport_key}/odds"
        
        params = {
            "apiKey": self.sources["the_odds_api"].api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "sport": sport,
                        "odds": data,
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"❌ Odds API error: {response.status}")
                    return {}

    async def _fetch_espn_upcoming_games(self, sport: str, days_ahead: int) -> List[GameData]:
        """Fetch upcoming games from ESPN API"""
        sport_mapping = {
            "basketball": "basketball/nba",
            "football": "football/nfl",
            "baseball": "baseball/mlb",
            "hockey": "hockey/nhl"
        }
        
        sport_path = sport_mapping.get(sport, sport)
        url = f"{self.sources['espn'].base_url}/apis/site/v2/sports/{sport_path}/scoreboard"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    games = []
                    
                    for event in data.get("events", []):
                        game_date = event.get("date", "")
                        status = event.get("status", {}).get("type", {}).get("name", "")
                        
                        home_team = event.get("competitions", [{}])[0].get("competitors", [{}])[0].get("team", {}).get("name", "")
                        away_team = event.get("competitions", [{}])[0].get("competitors", [{}])[1].get("team", {}).get("name", "")
                        
                        games.append(GameData(
                            game_id=event.get("id", ""),
                            sport=sport,
                            home_team=home_team,
                            away_team=away_team,
                            game_date=game_date,
                            status=status,
                            last_updated=datetime.now().isoformat()
                        ))
                    
                    return games
                else:
                    logger.error(f"❌ ESPN games API error: {response.status}")
                    return []

    async def _fetch_sportradar_team_stats(self, sport: str) -> List[TeamStats]:
        """Fetch team stats from Sportradar API (placeholder for paid API)"""
        # This would be implemented with actual Sportradar API calls
        # For now, return empty list as placeholder
        logger.info(f"📝 Sportradar API integration placeholder for {sport}")
        return []

    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status and statistics"""
        status = {
            "cache_size": {},
            "cache_hits": {},
            "last_updated": {}
        }
        
        for cache_type, cache_data in self.cache.items():
            status["cache_size"][cache_type] = len(cache_data)
            status["last_updated"][cache_type] = {
                key: datetime.fromtimestamp(data["timestamp"]).isoformat() 
                for key, data in cache_data.items()
            }
        
        return status

    async def refresh_all_data(self, sports: List[str] = None) -> Dict[str, Any]:
        """Refresh all cached data"""
        if sports is None:
            sports = ["basketball", "football", "baseball", "hockey"]
        
        results = {}
        
        for sport in sports:
            logger.info(f"🔄 Refreshing data for {sport}")
            
            try:
                # Fetch all data types
                team_stats = await self.fetch_team_stats(sport)
                player_stats = await self.fetch_player_stats(sport)
                odds = await self.fetch_game_odds(sport)
                games = await self.fetch_upcoming_games(sport)
                
                results[sport] = {
                    "teams": len(team_stats),
                    "players": len(player_stats),
                    "odds_available": bool(odds),
                    "upcoming_games": len(games),
                    "status": "success"
                }
                
                logger.info(f"✅ {sport} data refreshed successfully")
                
            except Exception as e:
                logger.error(f"❌ Error refreshing {sport} data: {e}")
                results[sport] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results

async def main():
    """Main function to test the data integration system"""
    data_system = DataIntegrationSystem()
    
    print("🚀 Testing Data Integration System - YOLO MODE!")
    print("=" * 60)
    
    # Test fetching data for basketball
    print("\n🏀 Testing Basketball Data Integration:")
    print("-" * 40)
    
    try:
        # Fetch team stats
        team_stats = await data_system.fetch_team_stats("basketball")
        print(f"✅ Team stats fetched: {len(team_stats)} teams")
        
        if team_stats:
            print("Sample teams:")
            for team in team_stats[:3]:
                print(f"  - {team.team_name}: {team.wins}-{team.losses} ({team.win_percentage:.3f})")
        
        # Fetch player stats
        player_stats = await data_system.fetch_player_stats("basketball")
        print(f"✅ Player stats fetched: {len(player_stats)} players")
        
        # Fetch odds
        odds = await data_system.fetch_game_odds("basketball")
        print(f"✅ Odds data fetched: {'Yes' if odds else 'No'}")
        
        # Fetch upcoming games
        games = await data_system.fetch_upcoming_games("basketball")
        print(f"✅ Upcoming games fetched: {len(games)} games")
        
        # Show cache status
        cache_status = data_system.get_cache_status()
        print(f"✅ Cache status: {len(cache_status['cache_size'])} cache types")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Data Integration System Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 