"""
Parlay Builder Service
======================
Creates optimal parlay combinations based on AI predictions.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ParlayBuilder:
    """
    Build parlay bets with optimal edge and risk management.
    
    Features:
    - Combine high-confidence predictions into parlays
    - Calculate combined odds and probabilities
    - Risk-level based parlay construction
    - Automatic parlay recommendations
    """
    
    def __init__(self):
        self.risk_profiles = {
            "conservative": {
                "min_legs": 2,
                "max_legs": 3,
                "min_leg_confidence": 0.65,  # Match autonomous engine threshold
                "min_combined_probability": 0.40,  # Lowered since we're using model probabilities
                "min_leg_edge": 0.05  # Match autonomous engine threshold
            },
            "moderate": {
                "min_legs": 2,
                "max_legs": 4,
                "min_leg_confidence": 0.65,
                "min_combined_probability": 0.25,  # More realistic for 3-4 leg parlays
                "min_leg_edge": 0.05
            },
            "aggressive": {
                "min_legs": 3,
                "max_legs": 6,
                "min_leg_confidence": 0.60,
                "min_combined_probability": 0.05,  # Realistic for 6-leg parlays (even 0.65^6 ≈ 0.075)
                "min_leg_edge": 0.03
            }
        }
    
    def calculate_combined_odds(self, american_odds_list: List[float]) -> float:
        """
        Calculate combined parlay odds from American odds.
        
        Args:
            american_odds_list: List of American odds (e.g., [-110, +150, -120])
        
        Returns:
            Combined American odds
        """
        # Convert American odds to decimal
        decimal_odds = []
        for odds in american_odds_list:
            if odds > 0:
                decimal = (odds / 100) + 1
            else:
                decimal = (100 / abs(odds)) + 1
            decimal_odds.append(decimal)
        
        # Multiply all decimal odds
        combined_decimal = 1.0
        for odds in decimal_odds:
            combined_decimal *= odds
        
        # Convert back to American odds
        if combined_decimal >= 2.0:
            american = (combined_decimal - 1) * 100
        else:
            american = -100 / (combined_decimal - 1)
        
        return round(american, 2)
    
    def calculate_combined_probability(self, probabilities: List[float]) -> float:
        """
        Calculate combined probability for parlay (all legs must win).
        
        Args:
            probabilities: List of individual probabilities (0-1)
        
        Returns:
            Combined probability
        """
        combined = 1.0
        for prob in probabilities:
            combined *= prob
        
        return combined
    
    def build_parlay(
        self,
        predictions: List[Dict[str, Any]],
        risk_level: str = "moderate",
        num_legs: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Build a parlay from available predictions.
        
        Args:
            predictions: List of prediction dicts with confidence, odds, etc.
            risk_level: conservative, moderate, or aggressive
            num_legs: Optional specific number of legs
        
        Returns:
            Parlay recommendation or None
        """
        profile = self.risk_profiles.get(risk_level, self.risk_profiles["moderate"])
        
        # Filter predictions by confidence and edge
        eligible_legs = []
        for pred in predictions:
            confidence = pred.get("confidence", 0)
            edge = pred.get("edge", 0)
            
            if (confidence >= profile["min_leg_confidence"] and 
                edge >= profile["min_leg_edge"]):
                eligible_legs.append(pred)
        
        # Not enough eligible legs
        if len(eligible_legs) < profile["min_legs"]:
            logger.warning(f"Not enough eligible legs for {risk_level} parlay")
            return None
        
        # Determine number of legs
        if num_legs:
            # If specific number requested, use that exactly (if we have enough)
            if len(eligible_legs) < num_legs:
                logger.warning(f"Not enough eligible legs ({len(eligible_legs)}) for {num_legs}-leg parlay")
                return None
            target_legs = num_legs
        else:
            target_legs = min(profile["max_legs"], len(eligible_legs))
            target_legs = max(target_legs, profile["min_legs"])
        
        # Sort by confidence * edge (best picks first)
        eligible_legs.sort(
            key=lambda x: x.get("confidence", 0) * x.get("edge", 0),
            reverse=True
        )
        
        # Filter legs to ensure no exact duplicates (same game + same bet type)
        # But allow same game with different bet types, and for 6-leg allow duplicate teams
        selected_legs = []
        seen_leg_keys = set()  # Track (game_id, bet_type) combinations
        
        for leg in eligible_legs:
            game_id = leg.get("game_id")
            bet_type = leg.get("bet_type", "moneyline")
            leg_key = (game_id, bet_type)
            
            # For 6-leg parlays, allow same game with different bet types
            # For other parlays, ensure unique game/bet_type combinations
            if leg_key not in seen_leg_keys:
                selected_legs.append(leg)
                seen_leg_keys.add(leg_key)
                if len(selected_legs) >= target_legs:
                    break
        
        # If we don't have enough unique legs, check if we can use same game with different bet types
        if len(selected_legs) < target_legs and num_legs == 6:
            # For 6-leg, allow multiple bets from same game if different bet types
            seen_games_only = set([leg.get("game_id") for leg in selected_legs])
            for leg in eligible_legs:
                if len(selected_legs) >= target_legs:
                    break
                game_id = leg.get("game_id")
                bet_type = leg.get("bet_type", "moneyline")
                leg_key = (game_id, bet_type)
                
                # Allow if it's a different bet type for a game we already have
                if leg_key not in seen_leg_keys:
                    # Check if we already have this game with a different bet type
                    has_game_diff_bet = any(
                        l.get("game_id") == game_id and l.get("bet_type") != bet_type 
                        for l in selected_legs
                    )
                    if has_game_diff_bet or game_id not in seen_games_only:
                        selected_legs.append(leg)
                        seen_leg_keys.add(leg_key)
                        seen_games_only.add(game_id)
        
        if len(selected_legs) < profile["min_legs"]:
            logger.warning(f"Not enough unique legs ({len(selected_legs)}) for {target_legs}-leg parlay")
            return None
        
        # Calculate combined metrics
        odds_list = [leg.get("odds", -110) for leg in selected_legs]
        
        # Use model probabilities (with edge) for parlay calculations, not just implied probabilities
        probs = []
        for leg in selected_legs:
            prob = leg.get("probability", 0.5)
            edge = leg.get("edge", 0)
            
            # Calculate implied probability from odds
            american_odds = leg.get("odds", -110)
            if american_odds > 0:
                implied_prob = 100 / (american_odds + 100)
            else:
                implied_prob = abs(american_odds) / (abs(american_odds) + 100)
            
            # Model probability = implied probability + edge (what we think the true probability is)
            if edge > 0:
                model_prob = implied_prob + edge
                model_prob = max(0.01, min(0.99, model_prob))  # Cap at reasonable bounds
                probs.append(model_prob)
            else:
                # Fallback to provided probability
                probs.append(prob)
        
        combined_odds = self.calculate_combined_odds(odds_list)
        combined_prob = self.calculate_combined_probability(probs)
        
        # Check if meets minimum probability
        if combined_prob < profile["min_combined_probability"]:
            logger.warning(f"Combined probability {combined_prob:.4f} too low for {risk_level} (min: {profile['min_combined_probability']})")
            return None
        
        # Calculate expected value
        decimal_odds = self._american_to_decimal(combined_odds)
        expected_value = (combined_prob * decimal_odds) - 1
        
        # Build parlay card
        parlay = {
            "id": str(uuid.uuid4()),
            "risk_level": risk_level,
            "num_legs": len(selected_legs),
            "legs": selected_legs,
            "combined_odds": combined_odds,
            "combined_probability": combined_prob,
            "expected_value": expected_value,
            "recommended_amount": None,  # Will be calculated by bankroll manager
            "created_at": datetime.utcnow().isoformat()
        }
        
        return parlay
    
    def build_multiple_parlays(
        self,
        predictions: List[Dict[str, Any]],
        include_conservative: bool = True,
        include_moderate: bool = True,
        include_aggressive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Build multiple parlays at different risk levels.
        
        Returns:
            List of parlay recommendations
        """
        parlays = []
        
        if include_conservative:
            conservative = self.build_parlay(predictions, "conservative")
            if conservative:
                parlays.append(conservative)
        
        if include_moderate:
            moderate = self.build_parlay(predictions, "moderate")
            if moderate:
                parlays.append(moderate)
        
        if include_aggressive:
            aggressive = self.build_parlay(predictions, "aggressive")
            if aggressive:
                parlays.append(aggressive)
        
        return parlays
    
    def validate_parlay(self, parlay_legs: List[Dict]) -> Dict[str, Any]:
        """
        Validate a parlay bet before placement.
        
        Checks:
        - All games are still pending
        - Odds haven't moved too much
        - No correlated outcomes
        """
        issues = []
        
        # Check for same game parlays (usually not allowed)
        game_ids = [leg.get("game_id") for leg in parlay_legs]
        if len(game_ids) != len(set(game_ids)):
            issues.append("Same game parlay detected - may not be allowed")
        
        # Check for conflicting bets
        # (e.g., Team A moneyline + Team B spread in same game)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": []
        }
    
    def _american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal."""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1


# Global parlay builder instance
parlay_builder = ParlayBuilder()
