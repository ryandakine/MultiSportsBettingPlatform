from typing import List, Dict, Any
from src.services.sports.base import SportService
import random

class TennisService(SportService):
    """Service for ATP/WTA Tennis data and odds."""

    def __init__(self, sport_key: str):
        # sport_key must be 'tennis_atp' or 'tennis_wta'
        super().__init__(sport_key=sport_key)

    async def fetch_odds(self, markets: str = "h2h") -> List[Dict[str, Any]]:
        """Fetch real-time Tennis odds (defaulting to H2H/Moneyline)."""
        # Tennis spreads/totals are less common in basic API tiers, focusing on H2H
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
            print(f"Error fetching Tennis odds ({self.sport_key}): {e}")
            return []

    def process_game_data(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw API data into platform format."""
        processed = []
        for match in matches:
            # Tennis specific normalizing if needed
            processed.append(match)
        return processed

    async def predict_outcome(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a prediction for a Tennis match using ML models.
        """
        from src.services.model_prediction_service import model_prediction_service
        
        # Pass odds=0 for now as we don't have a reliable primary player concept here without logic
        # Model service will likely fallback or use internal logic
        return await model_prediction_service.get_model_prediction(self.sport_key, game_data, 0)
