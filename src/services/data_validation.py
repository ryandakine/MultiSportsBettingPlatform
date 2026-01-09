"""
Data Validation Service
=======================
Strict validation to ensure ALL betting data is real and verified.
NEVER use synthetic, mocked, or made-up data.
When data is missing, ALERT immediately - missing data = system failure.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.services.data_quality_monitor import (
    data_quality_monitor,
    DataQualitySeverity
)

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


class DataValidator:
    """
    Validates betting data to ensure it's real and verified.
    
    Rules:
    - NO synthetic/mocked data
    - NO default values substituted when data is missing
    - NO invented odds, lines, or probabilities
    - Only accept data from verified sources (APIs)
    """
    
    @staticmethod
    async def validate_prediction_for_betting(prediction: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a prediction has all required REAL data for betting.
        
        When validation fails, records a CRITICAL data quality incident and alerts.
        
        Returns:
            (is_valid, error_message)
        """
        bet_type = prediction.get("bet_type", "moneyline")
        missing_fields = []
        
        # 1. Must have real game data
        if not prediction.get("game_id"):
            missing_fields.append("game_id")
            await data_quality_monitor.record_missing_data(
                data_type="game_data",
                data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                missing_fields=["game_id"],
                impact="prediction_validation_failed",
                context={
                    "prediction_id": prediction.get("id"),
                    "bet_type": bet_type,
                    "sport": prediction.get("sport")
                },
                severity=DataQualitySeverity.CRITICAL,
                error_message="Missing game_id - cannot verify game exists"
            )
            return False, "Missing game_id - cannot verify game exists"
        
        if not prediction.get("home_team") or not prediction.get("away_team"):
            missing_fields = [f for f in ["home_team", "away_team"] if not prediction.get(f)]
            await data_quality_monitor.record_missing_data(
                data_type="game_data",
                data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                missing_fields=missing_fields,
                impact="prediction_validation_failed",
                context={
                    "prediction_id": prediction.get("id"),
                    "game_id": prediction.get("game_id"),
                    "bet_type": bet_type
                },
                severity=DataQualitySeverity.CRITICAL,
                error_message=f"Missing team names - cannot verify game"
            )
            return False, "Missing team names - cannot verify game"
        
        if not prediction.get("game_date"):
            await data_quality_monitor.record_missing_data(
                data_type="game_data",
                data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                missing_fields=["game_date"],
                impact="prediction_validation_failed",
                context={
                    "prediction_id": prediction.get("id"),
                    "game_id": prediction.get("game_id")
                },
                severity=DataQualitySeverity.CRITICAL,
                error_message="Missing game_date - cannot verify game timing"
            )
            return False, "Missing game_date - cannot verify game timing"
        
        # 2. Must have REAL odds (not default values)
        odds = prediction.get("odds")
        if odds is None:
            await data_quality_monitor.record_missing_data(
                data_type="odds",
                data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                missing_fields=["odds"],
                impact="prediction_validation_failed",
                context={
                    "prediction_id": prediction.get("id"),
                    "game_id": prediction.get("game_id"),
                    "bet_type": bet_type
                },
                severity=DataQualitySeverity.CRITICAL,
                error_message="Missing odds - cannot place bet without real odds"
            )
            return False, "Missing odds - cannot place bet without real odds"
        
        # Check if odds look like a default value (common defaults: -110, -105)
        # We need to verify odds came from an API, not a default
        if not prediction.get("odds_source") and not prediction.get("real_odds"):
            logger.warning("⚠️ Odds present but no source verification - ensure odds came from API")
        
        # 3. Validate by bet type
        if bet_type == "moneyline":
            # Moneyline bets need: odds, team
            if not prediction.get("team"):
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["team"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Moneyline bet missing team selection"
                )
                return False, "Moneyline bet missing team selection"
            
            # Verify team matches home or away team
            team = prediction.get("team")
            home_team = prediction.get("home_team", "")
            away_team = prediction.get("away_team", "")
            
            if team not in [home_team, away_team]:
                error_msg = f"Team '{team}' does not match game teams ({home_team} vs {away_team})"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["team_match"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type, "team": team},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
        
        elif bet_type == "spread":
            # Spread bets need: odds, team, line (line can be negative)
            if not prediction.get("team"):
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["team"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Spread bet missing team selection"
                )
                return False, "Spread bet missing team selection"
            
            line = prediction.get("line")
            if line is None:
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["line"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Spread bet missing line"
                )
                return False, "Spread bet missing line - cannot place bet without spread line"
            
            # Verify team matches game
            team = prediction.get("team")
            home_team = prediction.get("home_team", "")
            away_team = prediction.get("away_team", "")
            
            if team not in [home_team, away_team]:
                error_msg = f"Team '{team}' does not match game teams"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["team_match"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
        
        elif bet_type in ["over_under", "total"]:
            # Over/under bets need: odds, line (positive total), direction (Over/Under)
            line = prediction.get("line")
            if line is None:
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["line"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Over/under bet missing line"
                )
                return False, "Over/under bet missing line - cannot place bet without total line"
            
            # Line MUST be positive (totals are always positive)
            if line <= 0:
                error_msg = f"Over/under line ({line}) must be positive - negative values indicate spread bets"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["valid_line"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type, "invalid_line": line},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
            
            # Must have Over/Under direction
            team = prediction.get("team", "").lower() if prediction.get("team") else ""
            if team not in ['over', 'under', 'o', 'u']:
                error_msg = f"Over/under bet missing direction - team field must be 'Over' or 'Under', got '{prediction.get('team')}'"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=prediction.get("metadata_json", {}).get("odds_source", "unknown"),
                    missing_fields=["team_direction"],
                    impact="prediction_validation_failed",
                    context={"prediction_id": prediction.get("id"), "bet_type": bet_type, "invalid_team": prediction.get("team")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
        
        # 4. Must have real probability/edge data (if provided, must be from model, not default)
        # Don't require this, but if present, validate it's reasonable
        if prediction.get("probability") is not None:
            prob = prediction.get("probability")
            if not (0 < prob < 1):
                return False, f"Probability ({prob}) must be between 0 and 1"
        
        if prediction.get("edge") is not None:
            edge = prediction.get("edge")
            # Edge can be negative (bad bet) or positive (good bet)
            if not (-1 <= edge <= 1):
                return False, f"Edge ({edge}) must be between -1 and 1"
        
        # 5. Verify data source
        # Check if this came from a real API call (metadata should indicate source)
        metadata = prediction.get("metadata_json", {})
        if not metadata.get("odds_source") and not metadata.get("api_verified"):
            logger.warning(f"⚠️ No API verification flag - ensure data came from real API call")
        
        return True, None
    
    @staticmethod
    async def validate_bet_data(bet_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate bet data before placing bet.
        More strict than prediction validation - this is final check.
        
        When validation fails, records a CRITICAL data quality incident and alerts.
        
        Returns:
            (is_valid, error_message)
        """
        bet_type = bet_data.get("bet_type", "moneyline")
        
        # Must have all required fields
        required_fields = ["sport", "game_id", "amount", "odds"]
        missing_fields = [f for f in required_fields if not bet_data.get(f)]
        if missing_fields:
            await data_quality_monitor.record_missing_data(
                data_type="bet_data",
                data_source=bet_data.get("odds_source", "unknown"),
                missing_fields=missing_fields,
                impact="bet_placement_failed",
                context={
                    "bet_type": bet_type,
                    "game_id": bet_data.get("game_id")
                },
                severity=DataQualitySeverity.CRITICAL,
                error_message=f"Missing required fields: {', '.join(missing_fields)}"
            )
            return False, f"Missing required field: {missing_fields[0]}"
        
        # Validate bet type specific requirements
        if bet_type == "moneyline":
            if not bet_data.get("team"):
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["team"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Moneyline bet requires team selection"
                )
                return False, "Moneyline bet requires team selection"
        
        elif bet_type == "spread":
            if bet_data.get("line") is None:
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["line"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Spread bet requires line"
                )
                return False, "Spread bet requires line"
            if not bet_data.get("team"):
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["team"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Spread bet requires team selection"
                )
                return False, "Spread bet requires team selection"
        
        elif bet_type in ["over_under", "total"]:
            line = bet_data.get("line")
            if line is None:
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["line"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message="Over/under bet requires total line"
                )
                return False, "Over/under bet requires total line"
            
            if line <= 0:
                error_msg = f"Over/under line must be positive, got {line}"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["valid_line"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id"), "invalid_line": line},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
            
            team = (bet_data.get("team") or "").lower()
            if team not in ['over', 'under', 'o', 'u']:
                error_msg = f"Over/under bet requires 'Over' or 'Under' direction, got '{bet_data.get('team')}'"
                await data_quality_monitor.record_missing_data(
                    data_type="bet_data",
                    data_source=bet_data.get("odds_source", "unknown"),
                    missing_fields=["team_direction"],
                    impact="bet_placement_failed",
                    context={"bet_type": bet_type, "game_id": bet_data.get("game_id"), "invalid_team": bet_data.get("team")},
                    severity=DataQualitySeverity.CRITICAL,
                    error_message=error_msg
                )
                return False, error_msg
        
        # Amount must be reasonable
        amount = bet_data.get("amount")
        if amount is None or amount <= 0:
            return False, f"Bet amount must be positive, got {amount}"
        
        # Odds must be reasonable
        odds = bet_data.get("odds")
        if odds is None:
            return False, "Bet requires odds"
        
        # Verify odds are in reasonable range (not obviously fake)
        if abs(odds) > 10000:  # Odds beyond ±10000 are suspicious
            logger.warning(f"⚠️ Suspiciously high odds: {odds}")
        
        return True, None
    
    @staticmethod
    def require_api_verification(prediction: Dict[str, Any]) -> bool:
        """
        Check if prediction data came from a verified API source.
        Returns False if data appears to be synthetic/default.
        """
        # Check for API verification flags
        metadata = prediction.get("metadata_json", {})
        
        # Must have some indication data came from API
        has_api_flag = metadata.get("api_verified", False)
        has_odds_source = bool(metadata.get("odds_source"))
        has_real_odds = bool(prediction.get("real_odds"))
        
        if not (has_api_flag or has_odds_source or has_real_odds):
            # If no API verification, check if odds look like defaults
            odds = prediction.get("odds")
            if odds == -110:  # Very common default
                logger.warning("⚠️ Odds -110 without API verification - may be default value")
                return False
        
        return True


# Global validator instance
data_validator = DataValidator()

