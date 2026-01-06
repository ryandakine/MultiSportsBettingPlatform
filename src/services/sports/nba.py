from typing import List, Dict, Any
from src.services.sports.base import SportService

class NBAService(SportService):
    """Service for NBA Basketball data and odds."""

    def __init__(self):
        super().__init__(sport_key="basketball_nba")

    async def fetch_odds(self, markets: str = "h2h,spreads,totals") -> List[Dict[str, Any]]:
        """Fetch real-time NBA odds."""
        url = f"{self.base_url}/{self.sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": markets,
            "oddsFormat": "american"
        }
        try:
            return await self._make_request(url, params)
        except Exception as e:
            print(f"Error fetching NBA odds: {e}")
            return []
            
    def process_game_data(self, games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw API data into platform format."""
        processed = []
        for game in games:
            # Add specific NBA processing if needed (e.g., quarter duration checks)
            processed.append(game)
        return processed
