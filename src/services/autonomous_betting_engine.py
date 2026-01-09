"""
Autonomous Betting Engine
==========================
Makes automated betting decisions based on AI predictions and risk management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from src.services.bet_tracker import bet_tracker
from src.services.parlay_builder import parlay_builder
from src.services.data_validation import data_validator, DataValidationError
from src.services.playoff_detector import playoff_detector

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
        """
        Main betting loop - runs continuously.
        
        Strategy:
        - Check once per day for new predictions and place bets
        - After placing daily picks and parlays, wait until next day
        - This ensures we place bets once per day automatically
        """
        import time
        from datetime import datetime, timedelta
        
        logger.info(f"🤖 Autonomous betting loop started for user {user_id}")
        logger.info(f"   Daily execution mode: Checking once per day at scheduled time")
        
        while self.enabled:
            try:
                # Get latest predictions
                predictions = await self._get_predictions(user_id)
                
                if not predictions:
                    logger.info("⏳ No predictions available, waiting 1 hour before checking again")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                # Check bankroll and limits
                bankroll = await bet_tracker.get_bankroll(user_id)
                if not bankroll:
                    logger.warning("⚠️ No bankroll found, waiting 1 hour before retrying")
                    await asyncio.sleep(3600)
                    continue
                
                # Check if we've already placed bets today
                todays_parlays = await self._get_todays_parlays(user_id)
                from src.db.database import AsyncSessionLocal
                from src.db.models.bet import Bet
                from sqlalchemy import select, and_, func
                from datetime import datetime
                
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        select(func.count(Bet.id)).where(
                            and_(
                                Bet.user_id == user_id,
                                Bet.placed_at >= today_start
                            )
                        )
                    )
                    bets_today = result.scalar()
                
                # If we've already placed bets today, wait until tomorrow
                if bets_today > 0:
                    # Calculate seconds until midnight
                    now = datetime.utcnow()
                    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    seconds_until_midnight = (tomorrow - now).total_seconds()
                    
                    logger.info(
                        f"✅ Already placed {bets_today} bets today. "
                        f"Waiting until tomorrow ({seconds_until_midnight/3600:.1f} hours)"
                    )
                    await asyncio.sleep(min(seconds_until_midnight, 86400))  # Max 24 hours
                    continue
                
                # Check daily loss limit
                if await self._hit_daily_loss_limit(user_id, bankroll):
                    logger.warning("⚠️ Daily loss limit hit, stopping for today")
                    await asyncio.sleep(3600)  # Wait 1 hour before checking again
                    continue
                
                # Process predictions for betting opportunities (place daily picks and parlays)
                logger.info(f"🎯 Processing {len(predictions)} predictions for today's bets...")
                bets_placed = await self._process_predictions(
                    user_id, predictions, bankroll
                )
                
                logger.info(f"✅ Daily betting complete: Placed {bets_placed} bets today")
                
                # Calculate seconds until midnight to wait until next day
                now = datetime.utcnow()
                tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_until_midnight = (tomorrow - now).total_seconds()
                
                logger.info(f"⏳ Waiting {seconds_until_midnight/3600:.1f} hours until next betting cycle")
                await asyncio.sleep(min(seconds_until_midnight, 86400))  # Max 24 hours
                
            except Exception as e:
                logger.error(f"❌ Error in betting loop: {e}", exc_info=True)
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _process_predictions(
        self,
        user_id: str,
        predictions: List[Dict],
        bankroll: Dict
    ) -> int:
        """
        Process predictions and place bets.
        
        Daily strategy (PRIORITY ORDER):
        1. Place daily picks (straight bets) FIRST - these are the best individual picks
        2. Then build parlays from the remaining top picks - parlays benefit from seeing
           which picks were identified as the best straight bets
        
        This order makes sense because:
        - Straight bets have better individual odds and win rates
        - By identifying best picks first, we can then intelligently combine them into parlays
        - Ensures daily picks get priority over parlay construction
        
        Returns:
            Number of bets placed
        """
        bets_placed = 0
        eligible_predictions = []
        
        # Filter predictions by edge, confidence, AND game date (only today's games)
        now = datetime.utcnow()
        today_date = now.replace(hour=0, minute=0, second=0, microsecond=0).date()
        tomorrow_date = today_date + timedelta(days=1)
        allow_tomorrow = now.hour >= 22  # After 10 PM UTC, allow early tomorrow games
        
        skipped_future = 0
        for pred in predictions:
            # Check edge and confidence
            edge = pred.get("edge", 0)
            confidence = pred.get("confidence", 0)
            
            if edge < self.min_edge_threshold or confidence < self.min_confidence:
                continue
            
            # CRITICAL: Only include games happening TODAY (not future dates where lines can change)
            game_date_str = pred.get("game_date") or pred.get("date")
            if game_date_str:
                try:
                    from dateutil import parser
                    if isinstance(game_date_str, str):
                        game_date = parser.parse(game_date_str)
                    else:
                        game_date = game_date_str
                    
                    game_date_only = game_date.date()
                    
                    # Only include today's games
                    include = False
                    if game_date_only == today_date:
                        include = True
                    elif allow_tomorrow and game_date_only == tomorrow_date:
                        # Only early morning tomorrow games (before 6 AM)
                        game_hour = game_date.hour if hasattr(game_date, 'hour') else 0
                        if game_hour < 6:
                            include = True
                    
                    if not include:
                        skipped_future += 1
                        continue  # Skip future games - lines/odds can change
                except Exception:
                    # If we can't parse date, skip it
                    continue
            else:
                # No game_date means we can't verify it's for today - skip it
                continue
            
            eligible_predictions.append(pred)
        
        if skipped_future > 0:
            logger.info(f"⏭️ Skipped {skipped_future} predictions for future dates (lines can change before game)")
        
        if not eligible_predictions:
            return 0
        
        # Sort by quality (confidence * edge) to get best picks first
        eligible_predictions.sort(
            key=lambda x: x.get("confidence", 0) * x.get("edge", 0),
            reverse=True
        )
        
        logger.info(f"📊 Found {len(eligible_predictions)} eligible predictions for betting")
        
        # Store for potential relaxed parlay building (ensuring daily 6-leg placement)
        self._last_eligible_predictions = eligible_predictions
        
        # STEP 1: Place daily picks (straight bets) FIRST
        # This identifies and locks in the best individual picks
        daily_picks_placed = 0
        for pred in eligible_predictions[:10]:  # Take top 10 for daily picks
            if bets_placed >= self.max_daily_bets:
                break
            
            bet_placed = await self._place_single_bet(
                user_id, pred, bankroll
            )
            
            if bet_placed:
                bets_placed += 1
                daily_picks_placed += 1
                logger.info(f"✅ Daily pick #{daily_picks_placed} placed")
        
        logger.info(f"📊 Placed {daily_picks_placed} daily picks (straight bets)")
        
        # STEP 2: Now build parlays from the eligible predictions
        # These can use the same predictions, but we've already identified the best ones above
        # The parlay builder will intelligently select which ones to combine
        if self.enable_parlays:
            # Check what parlays we've already placed today
            todays_parlays = await self._get_todays_parlays(user_id)
            placed_2leg = any(p['num_legs'] == 2 for p in todays_parlays)
            placed_3leg = any(p['num_legs'] == 3 for p in todays_parlays)
            placed_6leg = any(p['num_legs'] == 6 for p in todays_parlays)
            
            logger.info(
                f"📊 Daily parlay status: 2-leg={'✅' if placed_2leg else '❌'}, "
                f"3-leg={'✅' if placed_3leg else '❌'}, "
                f"6-leg={'✅' if placed_6leg else '❌'}"
            )
            
            # Place 2-leg parlay if not already placed today
            if not placed_2leg and len(eligible_predictions) >= 2:
                logger.info("🎯 Building 2-leg parlay (after daily picks)")
                parlay_placed = await self._place_parlay(
                    user_id, eligible_predictions, bankroll, num_legs=2
                )
                if parlay_placed:
                    bets_placed += 1
                    logger.info("✅ Daily 2-leg parlay placed successfully")
                else:
                    logger.warning("⚠️ Failed to place 2-leg parlay - insufficient predictions or build failed")
            
            # Place 3-leg parlay if not already placed today
            if not placed_3leg and len(eligible_predictions) >= 3:
                logger.info("🎯 Building 3-leg parlay (after daily picks)")
                parlay_placed = await self._place_parlay(
                    user_id, eligible_predictions, bankroll, num_legs=3
                )
                if parlay_placed:
                    bets_placed += 1
                    logger.info("✅ Daily 3-leg parlay placed successfully")
                else:
                    logger.warning("⚠️ Failed to place 3-leg parlay - insufficient predictions or build failed")
            
            # Place 6-leg parlay if not already placed today
            # CRITICAL: Always attempt to place 6-leg parlay daily (user requirement)
            if not placed_6leg:
                if len(eligible_predictions) >= 6:
                    logger.info("🎯 Building 6-leg parlay (after daily picks)")
                    parlay_placed = await self._place_parlay(
                        user_id, eligible_predictions, bankroll, num_legs=6
                    )
                    if parlay_placed:
                        bets_placed += 1
                        logger.info("✅ Daily 6-leg parlay placed successfully")
                    else:
                        logger.warning(
                            f"⚠️ Failed to place 6-leg parlay with standard thresholds. "
                            f"Available predictions: {len(eligible_predictions)}. "
                            f"Retrying with ALL predictions (relaxed filtering)..."
                        )
                        # RETRY with ALL predictions (no filtering) - ensures we ALWAYS place a 6-leg parlay daily
                        # Use all predictions from the original list, just filtered by date
                        all_predictions = [p for p in predictions if self._is_today_or_tomorrow(p)]
                        if len(all_predictions) >= 6:
                            logger.info(f"🔄 Retrying 6-leg parlay with {len(all_predictions)} total predictions (relaxed filtering)")
                            parlay_placed = await self._place_parlay(
                                user_id, all_predictions, bankroll, num_legs=6
                            )
                            if parlay_placed:
                                bets_placed += 1
                                logger.info("✅ Daily 6-leg parlay placed (with relaxed filtering - ensuring daily placement)")
                            else:
                                logger.error("❌ CRITICAL: Failed to place 6-leg parlay even with relaxed filtering")
                        else:
                            logger.error(f"❌ CRITICAL: Only {len(all_predictions)} predictions available (need 6+ for parlay)")
                else:
                    logger.warning(f"⚠️ Only {len(eligible_predictions)} eligible predictions (need 6+). Trying with ALL predictions...")
                    # Try with all predictions if we don't have enough eligible ones
                    all_predictions = [p for p in predictions if self._is_today_or_tomorrow(p)]
                    if len(all_predictions) >= 6:
                        logger.info(f"🔄 Attempting 6-leg parlay with {len(all_predictions)} total predictions (relaxed filtering)")
                        parlay_placed = await self._place_parlay(
                            user_id, all_predictions, bankroll, num_legs=6
                        )
                        if parlay_placed:
                            bets_placed += 1
                            logger.info("✅ Daily 6-leg parlay placed (with relaxed filtering)")
                        else:
                            logger.error("❌ CRITICAL: Failed to place 6-leg parlay even with relaxed filtering")
                    else:
                        logger.error(f"❌ CRITICAL: Only {len(all_predictions)} total predictions available (need 6+ for parlay)")
        
        logger.info(f"📊 Total bets placed: {bets_placed} ({daily_picks_placed} straight + {bets_placed - daily_picks_placed} parlays)")
        return bets_placed
    
    def _is_today_or_tomorrow(self, pred: Dict) -> bool:
        """Helper to check if prediction is for today or tomorrow."""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        today_date = now.replace(hour=0, minute=0, second=0, microsecond=0).date()
        tomorrow_date = today_date + timedelta(days=1)
        allow_tomorrow = now.hour >= 22
        
        game_date_str = pred.get("game_date") or pred.get("date")
        if not game_date_str:
            return False
        
        try:
            from dateutil import parser
            if isinstance(game_date_str, str):
                game_date = parser.parse(game_date_str)
            else:
                game_date = game_date_str
            
            game_date_only = game_date.date()
            
            if game_date_only == today_date:
                return True
            elif allow_tomorrow and game_date_only == tomorrow_date:
                game_hour = game_date.hour if hasattr(game_date, 'hour') else 0
                if game_hour < 6:
                    return True
        except Exception:
            pass
        
        return False
    
    async def _get_todays_parlays(self, user_id: str) -> List[Dict]:
        """Get parlays placed today for this user."""
        from src.db.database import AsyncSessionLocal
        from src.db.models.bet import Bet, BetType
        from sqlalchemy import select, and_, func
        from datetime import datetime, timedelta
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Bet).where(
                    and_(
                        Bet.user_id == user_id,
                        Bet.bet_type == BetType.PARLAY,
                        Bet.placed_at >= today_start
                    )
                )
            )
            parlay_bets = result.scalars().all()
            
            # Get leg counts for each parlay
            parlays_info = []
            from src.services.parlay_tracker import parlay_tracker
            for bet in parlay_bets:
                legs = await parlay_tracker.get_parlay_legs(bet.id)
                parlays_info.append({
                    'bet_id': bet.id,
                    'num_legs': len(legs),
                    'placed_at': bet.placed_at
                })
            
            return parlays_info
    
    async def _place_single_bet(
        self,
        user_id: str,
        prediction: Dict,
        bankroll: Dict
    ) -> bool:
        """
        Place a single bet based on prediction.
        
        CRITICAL: Validates all data is real - never uses synthetic/mocked data.
        For playoff games, applies playoff-specific adjustments to find edge.
        """
        try:
            # VALIDATION: Ensure data is real and verified (NO synthetic data)
            # Missing data = CRITICAL alert (recorded in validation)
            is_valid, error = await data_validator.validate_prediction_for_betting(prediction)
            if not is_valid:
                logger.warning(f"⚠️ Skipping bet due to validation failure: {error}")
                return False
            
            # Verify data came from API
            if not data_validator.require_api_verification(prediction):
                logger.warning(f"⚠️ Skipping bet: Data source not verified - may contain synthetic data")
                return False
            
            # Check if this is a playoff game and apply playoff-specific adjustments
            bet_type = prediction.get("bet_type", "moneyline")
            sport = prediction.get("sport", "")
            game_data = {
                'name': prediction.get('game_name') or prediction.get('name', ''),
                'date': prediction.get('game_date') or prediction.get('date'),
                'game_id': prediction.get('game_id', '')
            }
            
            is_playoff = playoff_detector.is_playoff_game(game_data, sport)
            if is_playoff:
                # Get playoff adjustments
                adjustments = playoff_detector.get_playoff_adjustments(game_data, sport)
                playoff_round = adjustments.get('round', 'Playoff')
                
                logger.info(f"🏆 Playoff game detected ({playoff_round}) - applying playoff-specific logic")
                
                # For playoff games, moneyline and over/under have less edge (everyone bets them)
                # Adjust confidence/edge requirements for these bet types
                if bet_type in ["moneyline", "over_under", "total"]:
                    # These are the "public" bets - require higher edge
                    original_edge = prediction.get("edge", 0)
                    original_confidence = prediction.get("confidence", 0)
                    
                    # Playoff games: moneyline/over-under bets need MORE edge (harder to find value)
                    # But other bet types might have more edge
                    adjusted_edge = original_edge - 0.02  # Require 2% more edge for public bets
                    adjusted_confidence = original_confidence - 0.05  # Require 5% more confidence
                    
                    if adjusted_edge < self.min_edge_threshold or adjusted_confidence < self.min_confidence:
                        logger.info(
                            f"⚠️ Playoff {bet_type} bet doesn't meet adjusted thresholds "
                            f"(edge: {original_edge:.3f} -> {adjusted_edge:.3f}, "
                            f"conf: {original_confidence:.3f} -> {adjusted_confidence:.3f}) - "
                            f"considering alternative bet types for edge"
                        )
                        # TODO: Try to find alternative bet types with more edge (props, first half, etc.)
                        # For now, skip this bet but log that we should look for alternatives
                        return False
                    
                    # Update prediction with adjusted values
                    prediction = prediction.copy()
                    prediction['edge'] = adjusted_edge
                    prediction['confidence'] = adjusted_confidence
                    prediction['playoff_adjustment_applied'] = True
                    prediction['playoff_round'] = playoff_round
            
            # Calculate bet amount using Kelly Criterion
            bet_amount = self._calculate_bet_size(
                prediction, bankroll["available_balance"]
            )
            
            logger.info(f"💰 Calculated bet size: ${bet_amount:.2f} for {prediction.get('team', 'TBD')}")
            
            if bet_amount < 1:  # Minimum $1 bet
                logger.warning(f"⚠️ Bet amount too small: ${bet_amount:.2f} < $1 minimum")
                return False
            
            # Validate bet data before placing
            bet_type = prediction.get("bet_type", "moneyline")
            
            # VALIDATION: Over/under bets must have valid data
            if bet_type in ["over_under", "total"]:
                line = prediction.get("line")
                team = prediction.get("team", "").lower() if prediction.get("team") else ""
                
                # Must have a positive line (totals are always positive)
                if line is None:
                    logger.warning(f"⚠️ Skipping over/under bet: Missing line value")
                    return False
                
                if line < 0:
                    logger.warning(f"⚠️ Skipping over/under bet: Negative line ({line}) indicates this is a spread bet, not a total")
                    return False
                
                # Must have Over/Under direction
                if team not in ['over', 'under', 'o', 'u']:
                    logger.warning(f"⚠️ Skipping over/under bet: Team field has '{prediction.get('team')}' instead of Over/Under")
                    return False
            
            # VALIDATION: Spread bets must have a line
            if bet_type == "spread" and prediction.get("line") is None:
                logger.warning(f"⚠️ Skipping spread bet: Missing line value")
                return False
            
            # Prepare bet data with game information for settlement
            bet_data = {
                "sportsbook": "paper_trading" if self.paper_trading else "draftkings",
                "sport": prediction.get("sport"),
                "game_id": prediction.get("game_id"),
                "game_date": prediction.get("game_date") or prediction.get("date"),
                "home_team": prediction.get("home_team"),
                "away_team": prediction.get("away_team"),
                "bet_type": bet_type,
                "team": prediction.get("team"),
                "line": prediction.get("line"),
                "amount": bet_amount,
                "odds": prediction.get("odds", -110),
                "predicted_probability": prediction.get("probability"),
                "predicted_edge": prediction.get("edge"),
                "model_confidence": prediction.get("confidence")
            }
            
            # Place bet (store in database even for paper trading for tracking)
            bet_id = await bet_tracker.place_bet(
                user_id, bet_data, is_autonomous=True
            )
            
            if self.paper_trading:
                logger.info(f"📄 PAPER TRADE: Bet ${bet_amount} on {bet_data.get('team', 'TBD')} | ID: {bet_id}")
            else:
                logger.info(f"✅ Auto-bet placed: {bet_id} | ${bet_amount} on {bet_data.get('team', 'TBD')}")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Error placing bet: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return False
    
    async def _place_parlay(
        self,
        user_id: str,
        predictions: List[Dict],
        bankroll: Dict,
        num_legs: Optional[int] = None
    ) -> bool:
        """Build and place a parlay bet."""
        try:
            from src.services.parlay_tracker import parlay_tracker
            
            # Determine risk level based on number of legs
            if num_legs == 2:
                risk_level = "conservative"
            elif num_legs == 3:
                risk_level = "moderate"
            elif num_legs == 6:
                risk_level = "aggressive"
            else:
                risk_level = "moderate"
            
            # Build parlay with specific number of legs
            parlay = parlay_builder.build_parlay(predictions, risk_level, num_legs=num_legs)
            
            if not parlay:
                return False
            
            # Calculate bet amount (smaller for parlays due to higher risk)
            max_parlay_bet = bankroll["available_balance"] * 0.02  # 2% max for parlays
            bet_amount = min(max_parlay_bet, 50)  # Cap at $50
            
            # Prepare leg data for storage
            legs = []
            earliest_game_date = None
            
            for leg_prediction in parlay.get("legs", []):
                # Find the original prediction for this leg to get game info
                leg_pred = next(
                    (p for p in predictions if p.get("game_id") == leg_prediction.get("game_id")),
                    leg_prediction
                )
                
                # Track earliest game date
                leg_game_date = leg_pred.get("game_date") or leg_pred.get("date")
                if leg_game_date:
                    try:
                        from dateutil import parser
                        leg_date = parser.parse(leg_game_date) if isinstance(leg_game_date, str) else leg_game_date
                        if not earliest_game_date or leg_date < earliest_game_date:
                            earliest_game_date = leg_date
                    except Exception:
                        pass
                
                # Store game_date as datetime object (not string) for proper storage
                legs.append({
                    "sport": leg_pred.get("sport", "unknown"),
                    "game_id": leg_pred.get("game_id", ""),
                    "home_team": leg_pred.get("home_team"),
                    "away_team": leg_pred.get("away_team"),
                    "bet_type": leg_prediction.get("bet_type", "moneyline"),
                    "team": leg_prediction.get("team"),
                    "line": leg_prediction.get("line"),
                    "odds": leg_prediction.get("odds", -110),
                    "probability": leg_prediction.get("probability"),
                    "edge": leg_prediction.get("edge"),
                    "game_date": leg_game_date  # Store as datetime object
                })
            
            # Store parlay in database
            parlay_data = {
                "legs": legs,
                "amount": bet_amount,
                "combined_odds": parlay.get("combined_odds", 0),
                "combined_probability": parlay.get("combined_probability"),
                "expected_edge": parlay.get("expected_edge"),
                "combined_confidence": parlay.get("combined_confidence"),
                "sportsbook": "paper_trading" if self.paper_trading else "draftkings",
                "game_date": earliest_game_date
            }
            
            parlay_bet_id = await parlay_tracker.place_parlay(
                user_id, parlay_data, is_autonomous=True
            )
            
            confidence = parlay.get('confidence_level', 'UNKNOWN')
            reasoning = parlay.get('reasoning', 'No reasoning provided')
            
            if self.paper_trading:
                logger.info(
                    f"📄 PAPER PARLAY: {parlay['num_legs']} legs | "
                    f"${bet_amount} @ {parlay['combined_odds']} | "
                    f"Confidence: {confidence} | ID: {parlay_bet_id}"
                )
                logger.info(f"   Reasoning: {reasoning}")
            else:
                logger.info(
                    f"✅ Auto-parlay placed: {parlay['num_legs']} legs | "
                    f"${bet_amount} @ {parlay['combined_odds']} | "
                    f"Confidence: {confidence} | ID: {parlay_bet_id}"
                )
                logger.info(f"   Reasoning: {reasoning}")
            
            return True
                
        except Exception as e:
            logger.error(f"Error placing parlay: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _calculate_bet_size(self, prediction: Dict, bankroll: float) -> float:
        """
        Calculate optimal bet size using Kelly Criterion.
        
        Formula: f = (bp - q) / b
        Where:
        - f = fraction of bankroll to bet
        - b = odds in decimal - 1
        - p = probability of winning (from model)
        - q = probability of losing (1 - p)
        
        If edge is provided, we use it to adjust the probability to reflect our model's advantage.
        """
        edge = prediction.get("edge", 0)
        probability = prediction.get("probability", 0.5)
        american_odds = prediction.get("odds", -110)
        
        # Convert American odds to implied probability
        if american_odds > 0:
            implied_prob = 100 / (american_odds + 100)
            decimal_odds = (american_odds / 100) + 1
        else:
            implied_prob = abs(american_odds) / (abs(american_odds) + 100)
            decimal_odds = (100 / abs(american_odds)) + 1
        
        # Use model probability if it's meaningfully different from implied prob
        # Otherwise, calculate it from implied prob + edge
        if edge > 0:
            # Model thinks probability is implied_prob + edge
            model_prob = implied_prob + edge
            # Cap at reasonable bounds
            model_prob = max(0.01, min(0.99, model_prob))
        else:
            # Use the provided probability, but ensure it reflects an edge
            model_prob = probability
        
        b = decimal_odds - 1
        p = model_prob
        q = 1 - p
        
        # Kelly Criterion: f = (bp - q) / b
        # Only bet if we have positive expected value (bp > q)
        if b * p - q <= 0:
            # No positive expected value, don't bet
            return 0.0
        
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
        """
        Get current predictions for betting.
        
        Fetches recent predictions from database and converts them to betting format.
        In the future, this could also query HeadAgent for fresh predictions.
        
        Returns:
            List of prediction dicts with format:
            {
                "sport": str,
                "game_id": str,
                "home_team": str,
                "away_team": str,
                "team": str,  # Team to bet on
                "bet_type": str,  # moneyline, spread, total
                "line": float,  # Spread or total line
                "odds": float,  # American odds
                "probability": float,  # 0-1
                "confidence": float,  # 0-1
                "edge": float,  # Expected edge %
                "game_date": datetime or str
            }
        """
        try:
            # Try to get predictions from database
            from src.db.database import AsyncSessionLocal
            from src.db.models.prediction import Prediction as PredictionModel
            from sqlalchemy import select
            from datetime import datetime, timedelta
            
            # Get today's date for filtering (only games happening TODAY)
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_date = today_start.date()
            # Also allow early tomorrow games if it's late at night (after 10 PM UTC)
            # This handles games that start just after midnight
            tomorrow_date = today_date + timedelta(days=1)
            cutoff_hour = 22  # 10 PM UTC - after this, allow tomorrow's early games
            allow_tomorrow = now.hour >= cutoff_hour
            
            from dateutil import parser
            
            async with AsyncSessionLocal() as session:
                # Get recent predictions (last 48 hours to ensure we catch games from late yesterday)
                cutoff = datetime.utcnow() - timedelta(hours=48)
                
                result = await session.execute(
                    select(PredictionModel)
                    .where(PredictionModel.timestamp >= cutoff)
                    .order_by(PredictionModel.timestamp.desc())
                )
                all_predictions = result.scalars().all()
                
                if not all_predictions:
                    logger.warning("⚠️ No recent predictions found in database")
                    return []
                
                # Convert to betting format and filter by game_date (ONLY TODAY, or early tomorrow if late at night)
                betting_predictions = []
                for pred in all_predictions:
                    # Extract metadata
                    metadata = pred.metadata_json or {}
                    game_date_str = metadata.get("game_date") or metadata.get("date")
                    
                    # Filter to only predictions for games scheduled today (or early tomorrow if late)
                    game_date = None
                    if game_date_str:
                        try:
                            if isinstance(game_date_str, str):
                                game_date = parser.parse(game_date_str)
                            else:
                                game_date = game_date_str
                            
                            game_date_only = game_date.date()
                            
                            # Only include games happening TODAY
                            # Optionally include tomorrow's early games (before 6 AM) if it's late at night
                            include_prediction = False
                            if game_date_only == today_date:
                                include_prediction = True
                            elif allow_tomorrow and game_date_only == tomorrow_date:
                                # Only include tomorrow's games if they're early morning (before 6 AM)
                                game_hour = game_date.hour if hasattr(game_date, 'hour') else 0
                                if game_hour < 6:  # Early morning games (before 6 AM)
                                    include_prediction = True
                            
                            if not include_prediction:
                                continue  # Skip predictions not for today's (or early tomorrow's) games
                        except Exception:
                            # If we can't parse the date, skip this prediction
                            logger.debug(f"Could not parse game_date for prediction {pred.id}: {game_date_str}")
                            continue
                    else:
                        # If no game_date in metadata, skip it (we need game dates for betting)
                        continue
                    
                    # Convert confidence string to float if needed
                    confidence_value = pred.confidence
                    if isinstance(confidence_value, str):
                        confidence_map = {"low": 0.5, "medium": 0.65, "high": 0.85}
                        confidence_value = confidence_map.get(confidence_value.lower(), 0.65)
                    elif isinstance(confidence_value, (int, float)):
                        confidence_value = float(confidence_value) / 100.0 if confidence_value > 1 else float(confidence_value)
                    else:
                        confidence_value = 0.65
                    
                    # Extract betting info from metadata or prediction text
                    game_id = metadata.get("game_id", f"game_{pred.id}")
                    home_team = metadata.get("home_team")
                    away_team = metadata.get("away_team")
                    team = metadata.get("team") or home_team  # Default to home team
                    bet_type = metadata.get("bet_type", "moneyline")
                    line = metadata.get("line")
                    odds = metadata.get("odds", -110)  # Default -110
                    probability = metadata.get("probability", confidence_value)
                    edge = metadata.get("edge", 0.05)  # Default 5% edge
                    
                    # Map bet_type to enum values
                    bet_type_mapping = {
                        "total": "over_under",
                        "over_under": "over_under",
                        "moneyline": "moneyline",
                        "spread": "spread"
                    }
                    mapped_bet_type = bet_type_mapping.get(bet_type.lower(), bet_type.lower())
                    
                    betting_predictions.append({
                        "sport": pred.sport,
                        "game_id": game_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "team": team,
                        "bet_type": mapped_bet_type,
                        "line": line,
                        "odds": float(odds),
                        "probability": float(probability),
                        "confidence": float(confidence_value),
                        "edge": float(edge),
                        "game_date": game_date.isoformat() if hasattr(game_date, 'isoformat') else str(game_date),
                        "date": game_date.isoformat() if hasattr(game_date, 'isoformat') else str(game_date),
                        "prediction_id": pred.id
                    })
                
                logger.info(f"✅ Fetched {len(betting_predictions)} predictions from database")
                return betting_predictions
                
        except Exception as e:
            logger.error(f"❌ Error fetching predictions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _hit_daily_loss_limit(self, user_id: str, bankroll: Dict) -> bool:
        """Check if daily loss limit has been hit."""
        from src.db.database import AsyncSessionLocal
        from src.db.models.bet import Bet, BetStatus
        from sqlalchemy import select, and_, func
        from datetime import datetime, timedelta
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate today's actual losses from settled bets
        async with AsyncSessionLocal() as session:
            # Sum losses from today's settled bets
            result = await session.execute(
                select(func.coalesce(func.sum(Bet.amount), 0))
                .where(
                    and_(
                        Bet.user_id == user_id,
                        Bet.status == BetStatus.LOST,
                        Bet.settled_at >= today_start
                    )
                )
            )
            daily_loss = result.scalar() or 0.0
        
        max_loss = bankroll["current_balance"] * self.max_daily_loss_percentage
        
        logger.info(f"💰 Daily loss check: ${daily_loss:.2f} lost today, limit: ${max_loss:.2f}")
        
        return daily_loss >= max_loss


# Global autonomous betting engine
autonomous_engine = AutonomousBettingEngine()
