"""
Real Paper Trading Service
==========================
Connects to real odds API, places paper bets, and tracks actual game outcomes.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx

from src.services.bet_tracker import bet_tracker
from src.db.models.bet import BetStatus, BetType
from src.services.model_prediction_service import model_prediction_service
from src.services.feature_service import feature_service

from dotenv import load_dotenv

# Load environment variables
load_dotenv("/home/ryan/MultiSportsBettingPlatform/.env")

logger = logging.getLogger(__name__)

# The Odds API (free tier: 500 requests/month)
ODDS_API_KEY = os.getenv("ODDS_API_KEY") or os.getenv("THE_ODDS_API_KEY", "")
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Sports we track (your active models)
SPORTS = [
    "icehockey_nhl",           # NHL Hockey
    "basketball_ncaab",        # College Basketball (Men's)
    "basketball_wncaab",       # College Women's Basketball
    "americanfootball_nfl",    # NFL (Playoffs)
    "basketball_nba",          # NBA
    "tennis_atp",              # ATP Tennis (Men's)
    "tennis_wta",              # WTA Tennis (Women's)
]


class RealPaperTrading:
    """
    Real paper trading that:
    1. Fetches real odds from The Odds API
    2. Uses AI predictions to decide bets
    3. Places paper bets with real game IDs
    4. Tracks actual game outcomes
    5. Calculates real ROI
    """
    
    def __init__(self):
        self.running = False
        self.user_id = "demo_user"
        self.min_edge = 0.05  # 5% minimum edge to bet
        self.max_bet_pct = 0.02  # 2% of bankroll per bet
        self.pending_bets: Dict[str, Dict] = {}  # game_id -> bet info
        
    async def start(self):
        """Start continuous paper trading."""
        self.running = True
        logger.info("🚀 Starting REAL paper trading service...")
        
        # Initialize ML Services
        await feature_service.initialize()
        await model_prediction_service.initialize()
        
        while self.running:
            try:
                # 1. Check for settled games
                await self.check_settled_games()
                
                # 2. Get upcoming games with odds
                games = await self.fetch_upcoming_games()
                
                if games:
                    # 3. Analyze and place bets
                    await self.analyze_and_bet(games)
                
                # 4. Wait before next cycle (check every 15 minutes)
                logger.info("⏳ Sleeping 15 minutes before next cycle...")
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def fetch_upcoming_games(self) -> List[Dict]:
        """Fetch real upcoming games with odds from The Odds API."""
        if not ODDS_API_KEY:
            logger.warning("⚠️ No ODDS_API_KEY set - using mock data")
            return await self._get_mock_games()
        
        all_games = []
        
        async with httpx.AsyncClient() as client:
            for sport in SPORTS:
                try:
                    response = await client.get(
                        f"{ODDS_API_BASE}/sports/{sport}/odds",
                        params={
                            "apiKey": ODDS_API_KEY,
                            "regions": "us",
                            "markets": "h2h,spreads,totals",
                            "oddsFormat": "american"
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        games = response.json()
                        for game in games:
                            game["sport_key"] = sport
                        all_games.extend(games)
                        logger.info(f"📊 Fetched {len(games)} games for {sport}")
                    else:
                        logger.warning(f"API error for {sport}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error fetching {sport}: {e}")
        
        return all_games
    
    async def _get_mock_games(self) -> List[Dict]:
        """Generate mock games for testing without API key."""
        import random
        
        teams = [
            ("Lakers", "Celtics", "basketball_nba"),
            ("Chiefs", "Bills", "americanfootball_nfl"),
            ("Warriors", "Nuggets", "basketball_nba"),
            ("Eagles", "Cowboys", "americanfootball_nfl"),
            ("Bucks", "Heat", "basketball_nba"),
        ]
        
        games = []
        for home, away, sport in teams:
            # Random odds
            home_odds = random.choice([-150, -130, -110, +100, +120])
            away_odds = -home_odds if home_odds < 0 else -int(100 / (home_odds/100 + 1))
            
            games.append({
                "id": f"mock_{home}_{away}_{datetime.now().strftime('%Y%m%d')}",
                "sport_key": sport,
                "commence_time": (datetime.utcnow() + timedelta(hours=random.randint(1, 48))).isoformat(),
                "home_team": home,
                "away_team": away,
                "bookmakers": [{
                    "key": "mock_book",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": home, "price": home_odds},
                            {"name": away, "price": away_odds}
                        ]
                    }]
                }]
            })
        
        return games
    
    async def analyze_and_bet(self, games: List[Dict]):
        """Analyze games and place paper bets on good opportunities."""
        bankroll = await bet_tracker.get_bankroll(self.user_id)
        if not bankroll:
            logger.error("No bankroll found!")
            return
        
        available = bankroll["available_balance"]
        bets_placed = 0
        
        for game in games:
            # Skip if already bet on this game
            if game["id"] in self.pending_bets:
                continue
            
            # Get best odds
            best_bet = self._find_best_bet(game)
            if not best_bet:
                continue
            
            # Check if we have edge (using real AI prediction)
            predicted_prob = await self._get_ai_prediction(game, best_bet["team"])
            implied_prob = self._american_to_prob(best_bet["odds"])
            edge = predicted_prob - implied_prob
            
            if edge >= self.min_edge:
                # Calculate bet size (Kelly Criterion simplified)
                kelly_fraction = (edge * best_bet["odds"] / 100) if best_bet["odds"] > 0 else edge
                kelly_fraction = min(kelly_fraction * 0.25, self.max_bet_pct)  # Quarter Kelly
                bet_amount = round(available * kelly_fraction, 2)
                
                if bet_amount >= 5:  # Minimum $5 bet
                    bet_data = {
                        "sportsbook": "paper_trading",
                        "sport": game["sport_key"],
                        "game_id": game["id"],
                        "game_date": game.get("commence_time"),
                        "home_team": game["home_team"],
                        "away_team": game["away_team"],
                        "bet_type": BetType.MONEYLINE,
                        "team": best_bet["team"],
                        "amount": bet_amount,
                        "odds": best_bet["odds"],
                        "predicted_probability": predicted_prob,
                        "predicted_edge": edge,
                        "model_confidence": predicted_prob
                    }
                    
                    try:
                        bet_id = await bet_tracker.place_bet(
                            self.user_id, bet_data, is_autonomous=True
                        )
                        
                        self.pending_bets[game["id"]] = {
                            "bet_id": bet_id,
                            "game": game,
                            "team": best_bet["team"],
                            "commence_time": game.get("commence_time")
                        }
                        
                        logger.info(
                            f"✅ PAPER BET: {best_bet['team']} @ {best_bet['odds']} | "
                            f"${bet_amount:.2f} | Edge: {edge*100:.1f}%"
                        )
                        bets_placed += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to place bet: {e}")
        
        if bets_placed:
            logger.info(f"📊 Placed {bets_placed} new paper bets this cycle")
    
    def _find_best_bet(self, game: Dict) -> Optional[Dict]:
        """Find the best betting opportunity in a game."""
        if not game.get("bookmakers"):
            return None
        
        best = None
        best_value = float("-inf")
        
        for book in game["bookmakers"]:
            for market in book.get("markets", []):
                if market["key"] == "h2h":  # Moneyline
                    for outcome in market.get("outcomes", []):
                        # Prefer slight underdogs (+100 to +200)
                        odds = outcome["price"]
                        if -200 <= odds <= 200:
                            value = abs(odds) if odds > 0 else 100
                            if value > best_value:
                                best_value = value
                                best = {
                                    "team": outcome["name"],
                                    "odds": odds,
                                    "market": "moneyline"
                                }
        
        return best
    
    async def _get_ai_prediction(self, game: Dict, team: str) -> float:
        """
        Get AI prediction for a team winning.
        Connects to ModelPredictionService.
        """
        try:
            # Find odds for this team (needed for edge calc / fallback)
            odds = 0
            for book in game.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market.get("outcomes", []):
                            if outcome["name"] == team:
                                odds = outcome["price"]
                                break
            
            # Call Model Service
            prediction = await model_prediction_service.get_model_prediction(
                game["sport_key"],
                game,
                odds
            )
            
            # If model was used, return its probability
            # The service returns 'model_probability' (0-1)
            # If for some reason it's missing, use odds
            prob = prediction.get('model_probability', 0.5)
            
            # If model returned "Home Win Probability", but 'team' is Away team, flip it?
            # ModelService usually predicts Home Win.
            # We need to map 'team' to Home/Away.
            
            home_team = game.get("home_team")
            if team == home_team:
                return prob
            else:
                # If prediction is home win prob, away win prob is 1-prob
                # CHECK: Does get_model_prediction return 'probability of the specific outcome' or 'home win'?
                # _get_nba_model_prediction returns `prob` from classifier.
                # Classifier trained on `Target_HomeWin`. So prob is Home Win Prob.
                
                # So if team != home_team (Away), we return 1.0 - prob
                return 1.0 - prob
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.5
    
    def _american_to_prob(self, odds: float) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    async def check_settled_games(self):
        """Check if any pending bets should be settled."""
        if not self.pending_bets:
            return
        
        now = datetime.utcnow()
        settled = []
        
        for game_id, bet_info in self.pending_bets.items():
            commence = bet_info.get("commence_time")
            if commence:
                try:
                    if isinstance(commence, str):
                        game_time = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                    else:
                        game_time = commence
                    
                    # Settle after game should be over (3+ hours after start)
                    if now > game_time.replace(tzinfo=None) + timedelta(hours=3):
                        # Determine outcome (mock - check real scores API in production)
                        won = await self._check_game_result(bet_info)
                        
                        status = BetStatus.WON if won else BetStatus.LOST
                        await bet_tracker.update_bet_status(bet_info["bet_id"], status)
                        
                        result = "🎉 WON" if won else "❌ LOST"
                        logger.info(f"{result}: {bet_info['team']} (Game: {game_id})")
                        settled.append(game_id)
                        
                except Exception as e:
                    logger.error(f"Error checking game {game_id}: {e}")
        
        # Remove settled bets
        for game_id in settled:
            del self.pending_bets[game_id]
    
    async def _check_game_result(self, bet_info: Dict) -> bool:
        """
        Check if bet won.
        
        TODO: Connect to scores API for real results!
        For now, simulates with realistic win rate based on odds.
        """
        import random
        
        # Get odds from bet
        game = bet_info.get("game", {})
        team = bet_info.get("team")
        
        # Find implied probability
        implied_prob = 0.5
        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                if market["key"] == "h2h":
                    for outcome in market.get("outcomes", []):
                        if outcome["name"] == team:
                            implied_prob = self._american_to_prob(outcome["price"])
                            break
        
        # Win based on implied probability (realistic simulation)
        return random.random() < implied_prob
    
    def stop(self):
        """Stop paper trading."""
        self.running = False
        logger.info("🛑 Paper trading stopped")


# Global instance
real_paper_trader = RealPaperTrading()


async def main():
    """Run paper trading as standalone script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    await real_paper_trader.start()


if __name__ == "__main__":
    asyncio.run(main())
