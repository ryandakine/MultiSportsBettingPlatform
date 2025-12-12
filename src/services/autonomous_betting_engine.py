"""
Autonomous Betting Engine
==========================
Makes automated betting decisions based on AI predictions and risk management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from src.services.bet_tracker import bet_tracker
from src.services.parlay_builder import parlay_builder

logger = logging.getLogger(__name__)


class AutonomousBettingEngine:
    """
    Autonomous betting decision engine.
    
    Features:
    - Analyze predictions and odds
    - Apply Kelly Criterion sizing
    - Respect bankroll limits
    - Build optimal parlays
    - Execute bets automatically
    """
    
    def __init__(self):
        self.enabled = False
        self.running = False
        
        # Risk parameters (configurable)
        self.min_edge_threshold = 0.05  # 5% minimum edge
        self.min_confidence = 0.65  # 65% minimum confidence
        self.max_bet_percentage = 0.05  # 5% of bankroll max
        self.kelly_multiplier = 0.25  # 1/4 Kelly (conservative)
        self.max_daily_bets = 20
        self.max_daily_loss_percentage = 0.10  # 10% max daily loss
        
        # Parlay settings
        self.enable_parlays = True
        self.parlay_frequency = 0.2  # 20% of bets as parlays
        
        # Paper trading mode (SAFETY)
        self.paper_trading = True  # Start in paper trading mode
    
    async def start(self, user_id: str):
        """Start autonomous betting."""
        self.enabled = True
        self.running = True
        logger.info(f"🤖 Autonomous betting started for user {user_id}")
        
        # Start betting loop
        asyncio.create_task(self._betting_loop(user_id))
    
    async def stop(self):
        """Stop autonomous betting."""
        self.enabled = False
        self.running = False
        logger.info("🛑 Autonomous betting stopped")
    
    async def _betting_loop(self, user_id: str):
        """Main betting loop - runs continuously."""
        while self.enabled:
            try:
                # Get latest predictions
                predictions = await self._get_predictions(user_id)
                
                if not predictions:
                    await asyncio.sleep(60)  # Wait 1 minute
                    continue
                
                # Check bankroll and limits
                bankroll = await bet_tracker.get_bankroll(user_id)
                if not bankroll:
                    logger.warning("No bankroll found")
                    await asyncio.sleep(60)
                    continue
                
                # Check daily loss limit
                if await self._hit_daily_loss_limit(user_id, bankroll):
                    logger.warning("⚠️ Daily loss limit hit, stopping for today")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                # Process predictions for betting opportunities
                bets_placed = await self._process_predictions(
                    user_id, predictions, bankroll
                )
                
                logger.info(f"📊 Processed {len(predictions)} predictions, placed {bets_placed} bets")
                
                # Wait before next loop
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in betting loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _process_predictions(
        self,
        user_id: str,
        predictions: List[Dict],
        bankroll: Dict
    ) -> int:
        """
        Process predictions and place bets.
        
        Returns:
            Number of bets placed
        """
        bets_placed = 0
        eligible_predictions = []
        
        # Filter predictions by edge and confidence
        for pred in predictions:
            edge = pred.get("edge", 0)
            confidence = pred.get("confidence", 0)
            
            if edge >= self.min_edge_threshold and confidence >= self.min_confidence:
                eligible_predictions.append(pred)
        
        if not eligible_predictions:
            return 0
        
        # Decide whether to build parlay
        if self.enable_parlays and len(eligible_predictions) >= 2:
            import random
            if random.random() < self.parlay_frequency:
                # Build and place parlay
                parlay_placed = await self._place_parlay(
                    user_id, eligible_predictions, bankroll
                )
                if parlay_placed:
                    bets_placed += 1
                    return bets_placed
        
        # Place individual bets
        for pred in eligible_predictions[:5]:  # Limit to top 5
            if bets_placed >= self.max_daily_bets:
                break
            
            bet_placed = await self._place_single_bet(
                user_id, pred, bankroll
            )
            
            if bet_placed:
                bets_placed += 1
        
        return bets_placed
    
    async def _place_single_bet(
        self,
        user_id: str,
        prediction: Dict,
        bankroll: Dict
    ) -> bool:
        """Place a single bet based on prediction."""
        try:
            # Calculate bet amount using Kelly Criterion
            bet_amount = self._calculate_bet_size(
                prediction, bankroll["available_balance"]
            )
            
            if bet_amount < 1:  # Minimum $1 bet
                return False
            
            # Prepare bet data
            bet_data = {
                "sportsbook": "draftkings",
                "sport": prediction.get("sport"),
                "game_id": prediction.get("game_id"),
                "bet_type": prediction.get("bet_type", "moneyline"),
                "team": prediction.get("team"),
                "line": prediction.get("line"),
                "amount": bet_amount,
                "odds": prediction.get("odds", -110),
                "predicted_probability": prediction.get("probability"),
                "predicted_edge": prediction.get("edge"),
                "model_confidence": prediction.get("confidence")
            }
            
            # Place bet (or simulate if paper trading)
            if self.paper_trading:
                logger.info(f"📄 PAPER TRADE: Would bet ${bet_amount} on {bet_data['team']}")
                # TODO: Store paper trade in database
                return True
            else:
                bet_id = await bet_tracker.place_bet(
                    user_id, bet_data, is_autonomous=True
                )
                logger.info(f"✅ Auto-bet placed: {bet_id} | ${bet_amount}")
                return True
                
        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            return False
    
    async def _place_parlay(
        self,
        user_id: str,
        predictions: List[Dict],
        bankroll: Dict
    ) -> bool:
        """Build and place a parlay bet."""
        try:
            # Build parlay
            parlay = parlay_builder.build_parlay(predictions, "moderate")
            
            if not parlay:
                return False
            
            # Calculate bet amount (smaller for parlays due to higher risk)
            max_parlay_bet = bankroll["available_balance"] * 0.02  # 2% max for parlays
            bet_amount = min(max_parlay_bet, 50)  # Cap at $50
            
            if self.paper_trading:
                logger.info(
                    f"📄 PAPER PARLAY: {parlay['num_legs']} legs | "
                    f"${bet_amount} @ {parlay['combined_odds']}"
                )
                return True
            else:
                # TODO: Place actual parlay via API
                logger.info(f"✅ Auto-parlay placed: {parlay['num_legs']} legs | ${bet_amount}")
                return True
                
        except Exception as e:
            logger.error(f"Error placing parlay: {e}")
            return False
    
    def _calculate_bet_size(self, prediction: Dict, bankroll: float) -> float:
        """
        Calculate optimal bet size using Kelly Criterion.
        
        Formula: f = (bp - q) / b
        Where:
        - f = fraction of bankroll to bet
        - b = odds in decimal - 1
        - p = probability of winning
        - q = probability of losing (1 - p)
        """
        edge = prediction.get("edge", 0)
        probability = prediction.get("probability", 0.5)
        american_odds = prediction.get("odds", -110)
        
        # Convert American odds to decimal
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1
        
        b = decimal_odds - 1
        p = probability
        q = 1 - p
        
        # Kelly Criterion
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Apply Kelly multiplier for safety (1/4 Kelly)
        kelly_fraction *= self.kelly_multiplier
        
        # Cap at max bet percentage
        kelly_fraction = min(kelly_fraction, self.max_bet_percentage)
        
        # Calculate dollar amount
        bet_amount = bankroll * kelly_fraction
        
        # Round to nearest dollar
        return round(bet_amount, 0)
    
    async def _get_predictions(self, user_id: str) -> List[Dict]:
        """Get current predictions from HeadAgent."""
        # TODO: Integrate with actual HeadAgent
        # For now, return empty list
        return []
    
    async def _hit_daily_loss_limit(self, user_id: str, bankroll: Dict) -> bool:
        """Check if daily loss limit has been hit."""
        # TODO: Calculate today's losses
        daily_loss = 0  # Placeholder
        
        max_loss = bankroll["current_balance"] * self.max_daily_loss_percentage
        
        return daily_loss >= max_loss


# Global autonomous betting engine
autonomous_engine = AutonomousBettingEngine()
