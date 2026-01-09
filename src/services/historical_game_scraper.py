"""
Historical Game Scraper
=======================
Scrapes historical game results from ESPN when the API doesn't return complete data.
Uses multiple strategies to ensure we can settle old bets.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import re

logger = logging.getLogger(__name__)


class HistoricalGameScraper:
    """
    Scraper for historical game results from ESPN.
    
    Strategies:
    1. Try ESPN scoreboard API with date parameter
    2. Try individual game detail endpoints
    3. Parse HTML if necessary
    """
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    ENDPOINTS = {
        "nfl": "/football/nfl",
        "mlb": "/baseball/mlb",
        "nhl": "/hockey/nhl",
        "ncaaf": "/football/college-football",
        "ncaab": "/basketball/mens-college-basketball",
        "ncaaw": "/basketball/womens-college-basketball",
        "wnba": "/basketball/wnba"
    }
    
    async def get_historical_games(self, sport: str, game_date: date) -> List[Dict[str, Any]]:
        """
        Get historical games for a specific date.
        
        Args:
            sport: Sport code (nfl, nhl, etc.)
            game_date: Date to fetch games for
            
        Returns:
            List of game dictionaries with scores and status
        """
        sport_code = sport.lower()
        if sport_code not in self.ENDPOINTS:
            logger.warning(f"⚠️ Unsupported sport: {sport}")
            return []
        
        logger.info(f"🔍 Fetching historical games for {sport} on {game_date}")
        
        # Strategy 1: Try scoreboard API
        games = await self._fetch_from_scoreboard(sport_code, game_date)
        if games:
            logger.info(f"✅ Found {len(games)} games from scoreboard API")
            return games
        
        # Strategy 2: Try scraping the scoreboard page
        logger.info(f"📄 Scoreboard API returned no games, trying HTML scrape...")
        games = await self._scrape_scoreboard_page(sport_code, game_date)
        if games:
            logger.info(f"✅ Found {len(games)} games from HTML scrape")
            return games
        
        logger.warning(f"⚠️ No games found for {sport} on {game_date}")
        return []
    
    async def _fetch_from_scoreboard(self, sport_code: str, game_date: date) -> List[Dict[str, Any]]:
        """Fetch games from ESPN scoreboard API."""
        endpoint = self.ENDPOINTS[sport_code]
        url = f"{self.BASE_URL}{endpoint}/scoreboard"
        
        date_str = game_date.strftime('%Y%m%d')
        params = {'dates': date_str}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                games = self._parse_scoreboard_response(data, sport_code, game_date)
                return games
                
        except Exception as e:
            logger.error(f"❌ Error fetching scoreboard for {sport_code} on {game_date}: {e}")
            return []
    
    def _parse_scoreboard_response(self, data: Dict[str, Any], sport: str, target_date: date) -> List[Dict[str, Any]]:
        """Parse ESPN scoreboard API response."""
        games = []
        
        try:
            events = data.get('events', [])
            
            for event in events:
                try:
                    competition = event.get('competitions', [{}])[0]
                    competitors = competition.get('competitors', [])
                    
                    if len(competitors) < 2:
                        continue
                    
                    home_team_obj = next((t for t in competitors if t.get('homeAway') == 'home'), None)
                    away_team_obj = next((t for t in competitors if t.get('homeAway') == 'away'), None)
                    
                    if not home_team_obj or not away_team_obj:
                        continue
                    
                    status_type = event.get('status', {}).get('type', {})
                    status_desc = status_type.get('description', '')
                    
                    # Extract scores
                    home_score = int(home_team_obj.get('score', 0) or 0)
                    away_score = int(away_team_obj.get('score', 0) or 0)
                    
                    # Parse game date
                    event_date_str = event.get('date', '')
                    event_date = None
                    if event_date_str:
                        try:
                            event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    game = {
                        "id": str(event.get('id', '')),
                        "sport": sport.upper(),
                        "date": event_date_str,
                        "game_date": event_date.date() if event_date else target_date,
                        "name": event.get('name', ''),
                        "status": status_desc,
                        "home_team": home_team_obj['team'].get('displayName', ''),
                        "home_score": home_score,
                        "away_team": away_team_obj['team'].get('displayName', ''),
                        "away_score": away_score,
                        "venue": competition.get('venue', {}).get('fullName', 'Unknown')
                    }
                    
                    games.append(game)
                    
                except Exception as e:
                    logger.debug(f"⚠️ Error parsing event: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error parsing scoreboard response: {e}")
        
        return games
    
    async def _scrape_scoreboard_page(self, sport_code: str, game_date: date) -> List[Dict[str, Any]]:
        """
        Scrape the HTML scoreboard page as fallback.
        ESPN's scoreboard pages are usually available even for historical dates.
        """
        endpoint = self.ENDPOINTS[sport_code]
        # ESPN uses different URL format for HTML pages
        date_str = game_date.strftime('%Y%m%d')
        url = f"https://www.espn.com{endpoint}/scoreboard/_/date/{date_str}"
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ HTML page returned {response.status_code}")
                    return []
                
                # Try to parse HTML - look for embedded JSON data
                html = response.text
                
                # ESPN often embeds JSON data in script tags
                json_match = re.search(r'window\.__espnfitt__=({.+?});', html)
                if json_match:
                    import json
                    try:
                        data = json.loads(json_match.group(1))
                        # Navigate the nested structure to find games
                        games = self._extract_games_from_embedded_json(data, sport_code, game_date)
                        if games:
                            return games
                    except Exception as e:
                        logger.debug(f"Could not parse embedded JSON: {e}")
                
                # Alternative: Try to extract from page props
                page_props_match = re.search(r'__NEXT_DATA__.*?"props":({.+?}),"page"', html)
                if page_props_match:
                    import json
                    try:
                        data = json.loads(page_props_match.group(1))
                        games = self._extract_games_from_page_props(data, sport_code, game_date)
                        if games:
                            return games
                    except Exception as e:
                        logger.debug(f"Could not parse page props: {e}")
                
                logger.debug(f"Could not extract games from HTML for {sport_code} on {game_date}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error scraping HTML page: {e}")
            return []
    
    def _extract_games_from_embedded_json(self, data: Dict[str, Any], sport: str, target_date: date) -> List[Dict[str, Any]]:
        """Extract games from ESPN's embedded JSON structure."""
        games = []
        
        # Navigate through various possible JSON structures
        # This is a best-effort extraction
        try:
            # Try different paths in the JSON structure
            events = None
            
            # Common paths in ESPN JSON
            if 'page' in data and 'content' in data['page']:
                events = data['page']['content'].get('events', [])
            elif 'scoreboard' in data:
                events = data['scoreboard'].get('events', [])
            elif 'events' in data:
                events = data['events']
            
            if not events:
                return games
            
            for event in events:
                try:
                    # Extract game data similar to API response
                    competition = event.get('competitions', [{}])[0]
                    competitors = competition.get('competitors', [])
                    
                    if len(competitors) < 2:
                        continue
                    
                    home_team_obj = next((t for t in competitors if t.get('homeAway') == 'home'), None)
                    away_team_obj = next((t for t in competitors if t.get('homeAway') == 'away'), None)
                    
                    if not home_team_obj or not away_team_obj:
                        continue
                    
                    home_score = int(home_team_obj.get('score', 0) or 0)
                    away_score = int(away_team_obj.get('score', 0) or 0)
                    status_desc = event.get('status', {}).get('type', {}).get('description', 'Final')
                    
                    game = {
                        "id": str(event.get('id', '')),
                        "sport": sport.upper(),
                        "game_date": target_date,
                        "name": event.get('name', ''),
                        "status": status_desc,
                        "home_team": home_team_obj.get('team', {}).get('displayName', ''),
                        "home_score": home_score,
                        "away_team": away_team_obj.get('team', {}).get('displayName', ''),
                        "away_score": away_score
                    }
                    
                    games.append(game)
                    
                except Exception as e:
                    logger.debug(f"Error extracting game from embedded JSON: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error navigating embedded JSON: {e}")
        
        return games
    
    def _extract_games_from_page_props(self, data: Dict[str, Any], sport: str, target_date: date) -> List[Dict[str, Any]]:
        """Extract games from Next.js page props."""
        # Similar structure to embedded JSON
        return self._extract_games_from_embedded_json(data, sport, target_date)
    
    async def get_game_by_id(self, sport: str, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific game by ID from ESPN.
        Useful when we have a game_id but need the final score.
        """
        sport_code = sport.lower()
        if sport_code not in self.ENDPOINTS:
            return None
        
        endpoint = self.ENDPOINTS[sport_code]
        url = f"{self.BASE_URL}{endpoint}/summary"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params={'event': game_id})
                response.raise_for_status()
                data = response.json()
                
                # Parse the summary response
                game = self._parse_game_summary(data, sport_code, game_id)
                return game
                
        except Exception as e:
            logger.error(f"❌ Error fetching game {game_id}: {e}")
            return None
    
    def _parse_game_summary(self, data: Dict[str, Any], sport: str, game_id: str) -> Optional[Dict[str, Any]]:
        """Parse ESPN game summary response."""
        try:
            competition = data.get('header', {}).get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) < 2:
                return None
            
            home_team_obj = next((t for t in competitors if t.get('homeAway') == 'home'), None)
            away_team_obj = next((t for t in competitors if t.get('homeAway') == 'away'), None)
            
            if not home_team_obj or not away_team_obj:
                return None
            
            status_type = data.get('header', {}).get('competitions', [{}])[0].get('status', {}).get('type', {})
            
            game = {
                "id": game_id,
                "sport": sport.upper(),
                "name": data.get('header', {}).get('competitions', [{}])[0].get('name', ''),
                "status": status_type.get('description', ''),
                "home_team": home_team_obj['team'].get('displayName', ''),
                "home_score": int(home_team_obj.get('score', 0) or 0),
                "away_team": away_team_obj['team'].get('displayName', ''),
                "away_score": int(away_team_obj.get('score', 0) or 0)
            }
            
            return game
            
        except Exception as e:
            logger.error(f"❌ Error parsing game summary: {e}")
            return None


# Global instance
historical_game_scraper = HistoricalGameScraper()


