"""
User Preferences API Routes

This module provides FastAPI routes for managing user preferences,
settings, and personalized features.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from src.services.user_preferences import (
    UserPreferencesService, SportType, RiskLevel, BettingType,
    NotificationType
)
from src.api.auth_routes import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["User Preferences"])

# Initialize preferences service
preferences_service = UserPreferencesService()

@router.get("/", response_model=Dict[str, Any])
async def get_user_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's preferences."""
    try:
        preferences = preferences_service.get_user_preferences(current_user["id"])
        
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User preferences not found"
            )
        
        return {
            "success": True,
            "preferences": {
                "betting": {
                    "preferred_sports": [sport.value for sport in preferences.betting.preferred_sports],
                    "risk_level": preferences.betting.risk_level.value,
                    "max_bet_amount": preferences.betting.max_bet_amount,
                    "min_confidence_threshold": preferences.betting.min_confidence_threshold,
                    "preferred_betting_types": [bet_type.value for bet_type in preferences.betting.preferred_betting_types],
                    "auto_betting_enabled": preferences.betting.auto_betting_enabled,
                    "max_daily_bets": preferences.betting.max_daily_bets,
                    "max_weekly_loss": preferences.betting.max_weekly_loss
                },
                "notifications": {
                    "email_notifications": preferences.notifications.email_notifications,
                    "push_notifications": preferences.notifications.push_notifications,
                    "sms_notifications": preferences.notifications.sms_notifications,
                    "in_app_notifications": preferences.notifications.in_app_notifications,
                    "prediction_alerts": preferences.notifications.prediction_alerts,
                    "bet_results": preferences.notifications.bet_results,
                    "system_updates": preferences.notifications.system_updates,
                    "marketing_emails": preferences.notifications.marketing_emails,
                    "quiet_hours_start": preferences.notifications.quiet_hours_start,
                    "quiet_hours_end": preferences.notifications.quiet_hours_end
                },
                "display": {
                    "theme": preferences.display.theme,
                    "language": preferences.display.language,
                    "timezone": preferences.display.timezone,
                    "currency": preferences.display.currency,
                    "odds_format": preferences.display.odds_format,
                    "show_confidence_scores": preferences.display.show_confidence_scores,
                    "show_historical_accuracy": preferences.display.show_historical_accuracy,
                    "compact_view": preferences.display.compact_view,
                    "auto_refresh": preferences.display.auto_refresh,
                    "refresh_interval": preferences.display.refresh_interval
                },
                "created_at": preferences.created_at.isoformat(),
                "updated_at": preferences.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user preferences"
        )

@router.put("/betting", response_model=Dict[str, Any])
async def update_betting_preferences(
    betting_prefs: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user's betting preferences."""
    try:
        # Validate betting preferences
        validated_prefs = {}
        
        if "preferred_sports" in betting_prefs:
            sports = []
            for sport in betting_prefs["preferred_sports"]:
                try:
                    sports.append(SportType(sport))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid sport type: {sport}"
                    )
            validated_prefs["preferred_sports"] = sports
        
        if "risk_level" in betting_prefs:
            try:
                validated_prefs["risk_level"] = RiskLevel(betting_prefs["risk_level"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid risk level: {betting_prefs['risk_level']}"
                )
        
        if "preferred_betting_types" in betting_prefs:
            bet_types = []
            for bet_type in betting_prefs["preferred_betting_types"]:
                try:
                    bet_types.append(BettingType(bet_type))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid betting type: {bet_type}"
                    )
            validated_prefs["preferred_betting_types"] = bet_types
        
        # Validate numeric values
        numeric_fields = ["max_bet_amount", "min_confidence_threshold", "max_daily_bets", "max_weekly_loss"]
        for field in numeric_fields:
            if field in betting_prefs:
                try:
                    value = float(betting_prefs[field])
                    if value < 0:
                        raise ValueError(f"{field} must be non-negative")
                    validated_prefs[field] = value
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid value for {field}"
                    )
        
        # Validate boolean values
        boolean_fields = ["auto_betting_enabled"]
        for field in boolean_fields:
            if field in betting_prefs:
                if not isinstance(betting_prefs[field], bool):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{field} must be a boolean"
                    )
                validated_prefs[field] = betting_prefs[field]
        
        # Update preferences
        success = preferences_service.update_betting_preferences(current_user["id"], validated_prefs)
        
        if success:
            logger.info(f"✅ Betting preferences updated for user: {current_user['username']}")
            return {
                "success": True,
                "message": "Betting preferences updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update betting preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update betting preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update betting preferences"
        )

@router.put("/notifications", response_model=Dict[str, Any])
async def update_notification_preferences(
    notification_prefs: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user's notification preferences."""
    try:
        # Validate notification preferences
        validated_prefs = {}
        
        # Validate boolean values
        boolean_fields = [
            "email_notifications", "push_notifications", "sms_notifications",
            "in_app_notifications", "prediction_alerts", "bet_results",
            "system_updates", "marketing_emails"
        ]
        
        for field in boolean_fields:
            if field in notification_prefs:
                if not isinstance(notification_prefs[field], bool):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{field} must be a boolean"
                    )
                validated_prefs[field] = notification_prefs[field]
        
        # Validate time strings
        time_fields = ["quiet_hours_start", "quiet_hours_end"]
        for field in time_fields:
            if field in notification_prefs:
                time_str = notification_prefs[field]
                try:
                    # Validate time format (HH:MM)
                    if not isinstance(time_str, str) or len(time_str) != 5 or time_str[2] != ":":
                        raise ValueError("Invalid time format")
                    hour, minute = map(int, time_str.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError("Invalid time values")
                    validated_prefs[field] = time_str
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid time format for {field}. Use HH:MM format."
                    )
        
        # Update preferences
        success = preferences_service.update_notification_preferences(current_user["id"], validated_prefs)
        
        if success:
            logger.info(f"✅ Notification preferences updated for user: {current_user['username']}")
            return {
                "success": True,
                "message": "Notification preferences updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update notification preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update notification preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )

@router.put("/display", response_model=Dict[str, Any])
async def update_display_preferences(
    display_prefs: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user's display preferences."""
    try:
        # Validate display preferences
        validated_prefs = {}
        
        # Validate theme
        if "theme" in display_prefs:
            theme = display_prefs["theme"]
            if theme not in ["light", "dark", "auto"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Theme must be 'light', 'dark', or 'auto'"
                )
            validated_prefs["theme"] = theme
        
        # Validate language
        if "language" in display_prefs:
            language = display_prefs["language"]
            if not isinstance(language, str) or len(language) != 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Language must be a 2-character code (e.g., 'en', 'es')"
                )
            validated_prefs["language"] = language.lower()
        
        # Validate timezone
        if "timezone" in display_prefs:
            timezone = display_prefs["timezone"]
            if not isinstance(timezone, str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Timezone must be a string"
                )
            validated_prefs["timezone"] = timezone
        
        # Validate currency
        if "currency" in display_prefs:
            currency = display_prefs["currency"]
            if not isinstance(currency, str) or len(currency) != 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Currency must be a 3-character code (e.g., 'USD', 'EUR')"
                )
            validated_prefs["currency"] = currency.upper()
        
        # Validate odds format
        if "odds_format" in display_prefs:
            odds_format = display_prefs["odds_format"]
            if odds_format not in ["american", "decimal", "fractional"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Odds format must be 'american', 'decimal', or 'fractional'"
                )
            validated_prefs["odds_format"] = odds_format
        
        # Validate boolean values
        boolean_fields = [
            "show_confidence_scores", "show_historical_accuracy",
            "compact_view", "auto_refresh"
        ]
        
        for field in boolean_fields:
            if field in display_prefs:
                if not isinstance(display_prefs[field], bool):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{field} must be a boolean"
                    )
                validated_prefs[field] = display_prefs[field]
        
        # Validate refresh interval
        if "refresh_interval" in display_prefs:
            try:
                interval = int(display_prefs["refresh_interval"])
                if interval < 30 or interval > 3600:
                    raise ValueError("Refresh interval must be between 30 and 3600 seconds")
                validated_prefs["refresh_interval"] = interval
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Refresh interval must be an integer between 30 and 3600 seconds"
                )
        
        # Update preferences
        success = preferences_service.update_display_preferences(current_user["id"], validated_prefs)
        
        if success:
            logger.info(f"✅ Display preferences updated for user: {current_user['username']}")
            return {
                "success": True,
                "message": "Display preferences updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update display preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update display preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update display preferences"
        )

@router.get("/sports", response_model=Dict[str, Any])
async def get_user_sport_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's preferred sports."""
    try:
        sports = preferences_service.get_user_sport_preferences(current_user["id"])
        
        return {
            "success": True,
            "preferred_sports": [sport.value for sport in sports],
            "available_sports": [sport.value for sport in SportType]
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get sport preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sport preferences"
        )

@router.get("/risk-level", response_model=Dict[str, Any])
async def get_user_risk_level(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's risk level."""
    try:
        risk_level = preferences_service.get_user_risk_level(current_user["id"])
        
        return {
            "success": True,
            "risk_level": risk_level.value,
            "available_risk_levels": [risk.value for risk in RiskLevel]
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get risk level: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk level"
        )

@router.get("/confidence-threshold", response_model=Dict[str, Any])
async def get_user_confidence_threshold(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's minimum confidence threshold."""
    try:
        threshold = preferences_service.get_user_confidence_threshold(current_user["id"])
        
        return {
            "success": True,
            "min_confidence_threshold": threshold
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get confidence threshold: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get confidence threshold"
        )

@router.get("/max-bet-amount", response_model=Dict[str, Any])
async def get_user_max_bet_amount(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's maximum bet amount."""
    try:
        max_amount = preferences_service.get_user_max_bet_amount(current_user["id"])
        
        return {
            "success": True,
            "max_bet_amount": max_amount
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get max bet amount: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get max bet amount"
        )

@router.get("/timezone", response_model=Dict[str, Any])
async def get_user_timezone(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's timezone."""
    try:
        timezone = preferences_service.get_user_timezone(current_user["id"])
        
        return {
            "success": True,
            "timezone": timezone
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get timezone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get timezone"
        )

@router.get("/currency", response_model=Dict[str, Any])
async def get_user_currency(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's preferred currency."""
    try:
        currency = preferences_service.get_user_currency(current_user["id"])
        
        return {
            "success": True,
            "currency": currency
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get currency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get currency"
        )

@router.post("/reset", response_model=Dict[str, Any])
async def reset_user_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Reset user preferences to defaults."""
    try:
        success = preferences_service.reset_user_preferences(current_user["id"])
        
        if success:
            logger.info(f"✅ Preferences reset for user: {current_user['username']}")
            return {
                "success": True,
                "message": "Preferences reset to defaults successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to reset preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset preferences"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_preferences_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get preferences statistics (admin only)."""
    try:
        # Check if user is admin
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        stats = preferences_service.get_preferences_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get preferences stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences statistics"
        )

@router.get("/health", response_model=Dict[str, Any])
async def preferences_health_check():
    """Health check for preferences service."""
    try:
        # Try to get stats to check service health
        stats = preferences_service.get_preferences_stats()
        
        if "error" in stats:
            return {
                "status": "unhealthy",
                "message": "Preferences service error",
                "error": stats["error"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "status": "healthy",
            "message": "Preferences service is running",
            "total_users": stats.get("total_users_with_preferences", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Preferences health check error: {e}")
        return {
            "status": "unhealthy",
            "message": "Preferences service error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 