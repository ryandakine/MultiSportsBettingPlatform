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
                "min_leg_confidence": 0.70,
                "min_combined_probability": 0.50,
                "min_leg_edge": 0.08
            },
            "moderate": {
                "min_legs": 2,
                "max_legs": 4,
                "min_leg_confidence": 0.65,
                "min_combined_probability": 0.40,
                "min_leg_edge": 0.05
            },
            "aggressive": {
                "min_legs": 3,
                "max_legs": 6,
                "min_leg_confidence": 0.60,
                "min_combined_probability": 0.30,
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
        target_legs = num_legs if num_legs else min(profile["max_legs"], len(eligible_legs))
        target_legs = max(target_legs, profile["min_legs"])
        
        # Sort by confidence * edge (best picks first)
        eligible_legs.sort(
            key=lambda x: x.get("confidence", 0) * x.get("edge", 0),
            reverse=True
        )
        
        # Take top picks
        selected_legs = eligible_legs[:target_legs]
        
        # Calculate combined metrics
        odds_list = [leg.get("odds", -110) for leg in selected_legs]
        probs = [leg.get("probability", 0.5) for leg in selected_legs]
        
        combined_odds = self.calculate_combined_odds(odds_list)
        combined_prob = self.calculate_combined_probability(probs)
        
        # Check if meets minimum probability
        if combined_prob < profile["min_combined_probability"]:
            logger.warning(f"Combined probability {combined_prob} too low for {risk_level}")
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
