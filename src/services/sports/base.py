from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from src.config import settings

class SportService(ABC):
    """Abstract Base Class for Sport Services."""
    
    def __init__(self, sport_key: str):
        self.sport_key = sport_key
        self.api_key = settings.the_odds_api_key
        self.base_url = "https://api.the-odds-api.com/v4/sports"

    @abstractmethod
    async def fetch_odds(self, markets: str = "h2h,spreads,totals") -> List[Dict[str, Any]]:
        """Fetch odds from The Odds API."""
        pass

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Helper to make async HTTP requests."""
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
