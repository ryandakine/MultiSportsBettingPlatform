import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.config import settings

logger = logging.getLogger(__name__)

class RealSportsService:
    """
    Service to fetch REAL sports data using public ESPN endpoints and The Odds API.
    """
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"
    
    # Mapping for ESPN endpoints
    ENDPOINTS = {
        "nfl": "/football/nfl/scoreboard",
        "mlb": "/baseball/mlb/scoreboard",
        "nhl": "/hockey/nhl/scoreboard",
        "ncaaf": "/football/college-football/scoreboard",
        "ncaab": "/basketball/mens-college-basketball/scoreboard",
        "ncaaw": "/basketball/womens-college-basketball/scoreboard",
        "wnba": "/basketball/wnba/scoreboard"
    }

    # Mapping for The Odds API sport keys
    ODDS_API_SPORTS = {
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "nhl": "icehockey_nhl",
        "ncaaf": "americanfootball_ncaaf",
        "ncaab": "basketball_ncaab",
        "wnba": "basketball_wnba",
        "ncaaw": "basketball_ncaaw" # Assuming this key, may degrade gracefully if invalid
    }
    
    async def get_live_games(self, sport: str, date: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
        """
        Fetch games for a specific sport from ESPN and enrich with Odds API data if available.
        
        Args:
            sport: Sport code (nfl, nhl, etc.)
            date: Optional date to fetch games for (defaults to today)
        """
        sport_code = sport.lower()
        if sport_code not in self.ENDPOINTS:
            logger.warning(f"Unsupported sport for real data: {sport}")
            return []
            
        # 1. Fetch Games from ESPN
        url = f"{self.BASE_URL}{self.ENDPOINTS[sport_code]}"
        
        # Add date parameter if specified (ESPN API format: dates=YYYYMMDD)
        params = {}
        if date:
            date_str = date.strftime('%Y%m%d')
            params['dates'] = date_str
            logger.info(f"Fetching games for {sport} on {date} (ESPN date: {date_str})")
        
        games = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                games = self._parse_espn_response(data, sport_code)
                
        except Exception as e:
            logger.error(f"Failed to fetch real data for {sport}: {e}")
            return []

        # 2. Fetch Odds from The Odds API (if key matches)
        # Only fetch if we have games and an API key
        if games and settings.the_odds_api_key:
             odds_data = await self._fetch_live_odds(sport_code)
             if odds_data:
                 self._merge_odds_data(games, odds_data)

        return games

    async def _fetch_live_odds(self, sport_code: str) -> List[Dict[str, Any]]:
        """Fetch live odds from The Odds API."""
        if sport_code not in self.ODDS_API_SPORTS:
            return []
            
        sport_key = self.ODDS_API_SPORTS[sport_code]
        url = f"{self.ODDS_API_URL}/{sport_key}/odds"
        
        params = {
            "apiKey": settings.the_odds_api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Odds API error: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to fetch odds from API: {e}")
            return []

    def _merge_odds_data(self, games: List[Dict[str, Any]], odds_data: List[Dict[str, Any]]):
        """Merge Odds API data into ESPN games list based on team names."""
        from src.services.team_normalization import normalization_service
        
        # Create lookup map for games based on home team name
        # We index by home team because usually that's sufficient to identify the game within a sport/day
        games_map = normalization_service.create_lookup_map(games, 'home_team')
        
        for odd_event in odds_data:
            odd_home = odd_event.get('home_team', '')
            
            # Find matching game efficiently
            game = normalization_service.find_match(odd_home, games_map)
            
            if game:
                # Extract best bookmaker odds
                bookmakers = odd_event.get('bookmakers', [])
                if bookmakers:
                    # Just take the first one (usually low latency one) or widely available
                    book = bookmakers[0]
                    game['real_odds'] = {
                        "provider": book['title'],
                        "markets": book['markets'],
                        "last_update": book['last_update']
                    }

    def _parse_espn_response(self, data: Dict[str, Any], sport: str) -> List[Dict[str, Any]]:
        """Parse raw ESPN response into unified game format."""
        games = []
        
        try:
            events = data.get('events', [])
            
            for event in events:
                competition = event['competitions'][0]
                competitors = competition['competitors']
                
                home_team = next((team for team in competitors if team['homeAway'] == 'home'), None)
                away_team = next((team for team in competitors if team['homeAway'] == 'away'), None)
                
                if not home_team or not away_team:
                    continue
                    
                status_type = event['status']['type']
                
                game = {
                    "id": event['id'],
                    "sport": sport.upper(),
                    "date": event['date'],
                    "name": event['name'],
                    "shortName": event['shortName'],
                    "status": status_type['description'],
                    "period": event['status'].get('period', 0),
                    "clock": event['status'].get('displayClock', "0:00"),
                    "venue": competition.get('venue', {}).get('fullName', "Unknown Venue"),
                    
                    "home_team": home_team['team']['displayName'],
                    "home_score": int(home_team.get('score', 0)),
                    "home_logo": home_team['team'].get('logo'),
                    "home_id": home_team['team']['id'],
                    
                    "away_team": away_team['team']['displayName'],
                    "away_score": int(away_team.get('score', 0)),
                    "away_logo": away_team['team'].get('logo'),
                    "away_id": away_team['team']['id'],
                    
                    "odds": self._extract_odds(competition)
                }
                
                games.append(game)
                
        except Exception as e:
            logger.error(f"Error parsing ESPN data: {e}")
            
        return games
    
    def _extract_odds(self, competition: Dict[str, Any]) -> Dict[str, Any]:
        """Extract odds if available."""
        odds = {}
        if 'odds' in competition:
            try:
                # Provide the first available line
                line = competition['odds'][0]
                odds['details'] = line.get('details') # e.g. "DET -3.0"
                odds['overUnder'] = line.get('overUnder')
            except (IndexError, KeyError):
                pass
        return odds

# Global instance
real_sports_service = RealSportsService()
