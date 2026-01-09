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

    @abstractmethod
    async def predict_outcome(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a prediction for a game."""
        pass

    def _calculate_implied_prob(self, american_odds: int) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)

    def _find_value_bets(self, game_data: Dict[str, Any], min_edge: float = 0.02) -> Dict[str, Any]:
        """
        Find value bets by comparing individual bookmaker odds against the market average.
        Uses REAL data from available bookmakers.
        """
        bookmakers = game_data.get('bookmakers', [])
        if len(bookmakers) < 2:
            return {"predicted_winner": None, "confidence": 0, "edge": 0}

        # 1. Aggregate market consensus
        # Map: outcome_name -> list of probabilities
        market_probs: Dict[str, List[float]] = {}
        
        for book in bookmakers:
            h2h = next((m for m in book.get('markets', []) if m['key'] == 'h2h'), None)
            if h2h:
                for outcome in h2h.get('outcomes', []):
                    name = outcome['name']
                    price = outcome['price']
                    prob = self._calculate_implied_prob(price)
                    if name not in market_probs:
                        market_probs[name] = []
                    market_probs[name].append(prob)

        # Calculate average prob for each outcome
        avg_probs = {name: sum(probs)/len(probs) for name, probs in market_probs.items()}

        # 2. Find bookmakers offering better odds (lower implied prob) than average
        best_bet = {"predicted_winner": None, "confidence": 0.0, "edge": 0.0}

        for book in bookmakers:
            h2h = next((m for m in book.get('markets', []) if m['key'] == 'h2h'), None)
            if h2h:
                for outcome in h2h.get('outcomes', []):
                    name = outcome['name']
                    price = outcome['price']
                    implied = self._calculate_implied_prob(price)
                    
                    # True probability estimate = Average market probability
                    estimated_true_prob = avg_probs.get(name, 0)
                    
                    if estimated_true_prob > 0:
                        # Edge = (Probability * DecimalOdds) - 1
                        # Wait, simplified: implied < average means value?
                        # Actually: Edge = Estimated_True_Prob - Implied_Prob_of_Bet
                        
                        edge = estimated_true_prob - implied
                        
                        if edge > min_edge and edge > best_bet['edge']:
                            best_bet = {
                                "predicted_winner": name,
                                "confidence": estimated_true_prob,
                                "edge": edge,
                                "odds": price,
                                "bookmaker": book['title'],
                                "type": "moneyline",
                                "details": f"Value found: {book['title']} ({price}) vs Avg Mkt"
                            }
                            
        return best_bet
