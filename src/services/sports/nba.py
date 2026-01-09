from typing import List, Dict, Any, Optional
from src.services.sports.base import SportService
import random

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

    async def predict_outcome(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a prediction for an NBA game using trained ML models.
        """
        from src.services.model_prediction_service import model_prediction_service
        
        # Try to find relevant odds to pass for edge calculation
        # We try to find odds for Home Team
        home_team = game_data.get('home_team')
        odds = 0
        
        bookmakers = game_data.get('bookmakers', [])
        if bookmakers and home_team:
            for book in bookmakers:
                h2h = next((m for m in book.get('markets', []) if m['key'] == 'h2h'), None)
                if h2h:
                    for outcome in h2h.get('outcomes', []):
                        if outcome['name'] == home_team:
                            odds = outcome['price']
                            break
                    if odds != 0: break
        
        return await model_prediction_service.get_model_prediction(self.sport_key, game_data, odds)
