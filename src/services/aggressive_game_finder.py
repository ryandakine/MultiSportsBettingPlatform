"""
Aggressive Game Finder
======================
Find games by ANY means necessary - team names, dates, fuzzy matching, multiple sources.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import re

logger = logging.getLogger(__name__)


class AggressiveGameFinder:
    """
    Aggressively find games using multiple strategies:
    1. Search by team names + date across all relevant sport codes
    2. Fuzzy match team names
    3. Try date variations (±1 day)
    4. Search multiple endpoints
    """
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    SPORT_CODES = {
        "football": ["ncaaf", "nfl"],
        "basketball": ["ncaab", "nba", "ncaaw", "wnba"],
        "baseball": ["mlb"],
        "hockey": ["nhl"],
    }
    
    ENDPOINTS = {
        "nfl": "/football/nfl/scoreboard",
        "ncaaf": "/football/college-football/scoreboard",
        "mlb": "/baseball/mlb/scoreboard",
        "nhl": "/hockey/nhl/scoreboard",
        "ncaab": "/basketball/mens-college-basketball/scoreboard",
        "ncaaw": "/basketball/womens-college-basketball/scoreboard",
        "nba": "/basketball/nba/scoreboard",
        "wnba": "/basketball/wnba/scoreboard"
    }
    
    async def find_game_by_teams_and_date(
        self,
        team1: str,
        team2: Optional[str],
        bet_date: date,
        sport_hint: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a game by team names and date.
        Tries all relevant sport codes and date variations.
        """
        if not team1:
            return None
        
        # Normalize team names
        team1_norm = self._normalize_team(team1)
        team2_norm = self._normalize_team(team2) if team2 else None
        
        # Determine which sport codes to try
        sport_codes = []
        if sport_hint:
            sport_codes = self.SPORT_CODES.get(sport_hint.lower(), [sport_hint.lower()])
        else:
            # Try all sports if no hint
            sport_codes = ["ncaaf", "nfl", "ncaab", "nba", "mlb", "nhl"]
        
        # Try date ± 1 day for late games
        dates_to_try = [bet_date, bet_date - timedelta(days=1), bet_date + timedelta(days=1)]
        
        for try_date in dates_to_try:
            for sport_code in sport_codes:
                if sport_code not in self.ENDPOINTS:
                    continue
                
                try:
                    games = await self._fetch_games_for_sport_date(sport_code, try_date)
                    
                    for game in games:
                        if self._match_teams(game, team1_norm, team2_norm):
                            logger.info(f"✅ Found game: {game.get('home_team')} vs {game.get('away_team')} on {try_date}")
                            return game
                            
                except Exception as e:
                    logger.debug(f"Error searching {sport_code} on {try_date}: {e}")
                    continue
        
        return None
    
    async def _fetch_games_for_sport_date(self, sport_code: str, game_date: date) -> List[Dict[str, Any]]:
        """Fetch games for a specific sport and date."""
        endpoint = self.ENDPOINTS[sport_code]
        url = f"{self.BASE_URL}{endpoint}"
        date_str = game_date.strftime('%Y%m%d')
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params={'dates': date_str})
                response.raise_for_status()
                data = response.json()
                return self._parse_games(data)
        except Exception as e:
            logger.debug(f"Error fetching {sport_code} on {game_date}: {e}")
            return []
    
    def _parse_games(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse ESPN API response."""
        games = []
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
                
                game = {
                    "id": str(event.get('id', '')),
                    "home_team": home_team_obj['team'].get('displayName', ''),
                    "home_score": int(home_team_obj.get('score', 0) or 0),
                    "away_team": away_team_obj['team'].get('displayName', ''),
                    "away_score": int(away_team_obj.get('score', 0) or 0),
                    "status": status_type.get('description', ''),
                    "date": event.get('date', '')
                }
                games.append(game)
                
            except Exception as e:
                logger.debug(f"Error parsing event: {e}")
                continue
        
        return games
    
    def _normalize_team(self, team_name: str) -> str:
        """Normalize team name for matching."""
        if not team_name:
            return ""
        
        # Remove common prefixes/suffixes
        normalized = team_name.lower()
        normalized = re.sub(r'\b(over|under|o\s+|u\s+)\b', '', normalized)  # Remove over/under indicators
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        
        # Remove common words
        words_to_remove = ['the', 'university', 'state', 'college']
        words = normalized.split()
        words = [w for w in words if w not in words_to_remove]
        
        return ' '.join(words).strip()
    
    def _match_teams(self, game: Dict[str, Any], team1_norm: str, team2_norm: Optional[str]) -> bool:
        """Check if game matches the teams."""
        home_norm = self._normalize_team(game.get('home_team', ''))
        away_norm = self._normalize_team(game.get('away_team', ''))
        
        # Check if team1 matches either side
        team1_in_home = team1_norm in home_norm or home_norm in team1_norm
        team1_in_away = team1_norm in away_norm or away_norm in team1_norm
        
        if not (team1_in_home or team1_in_away):
            return False
        
        # If we only have one team, that's enough
        if not team2_norm:
            return True
        
        # Check if team2 matches the other side
        if team1_in_home:
            return team2_norm in away_norm or away_norm in team2_norm
        else:
            return team2_norm in home_norm or home_norm in team2_norm


# Global instance
aggressive_game_finder = AggressiveGameFinder()

