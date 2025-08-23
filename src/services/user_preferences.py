"""
User Preferences Service

This module manages user preferences, settings, and personalized features
for the MultiSportsBettingPlatform.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportType(Enum):
    """Supported sports."""
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HOCKEY = "hockey"

class BettingType(Enum):
    """Types of betting preferences."""
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTALS = "totals"
    PROPS = "props"
    PARLAYS = "parlays"

class RiskLevel(Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class NotificationType(Enum):
    """Notification preferences."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

@dataclass
class BettingPreferences:
    """User betting preferences."""
    preferred_sports: List[SportType] = None
    risk_level: RiskLevel = RiskLevel.MODERATE
    max_bet_amount: float = 100.0
    min_confidence_threshold: float = 0.6
    preferred_betting_types: List[BettingType] = None
    auto_betting_enabled: bool = False
    max_daily_bets: int = 10
    max_weekly_loss: float = 500.0
    
    def __post_init__(self):
        if self.preferred_sports is None:
            self.preferred_sports = [SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL, SportType.HOCKEY]
        if self.preferred_betting_types is None:
            self.preferred_betting_types = [BettingType.MONEYLINE, BettingType.SPREAD]

@dataclass
class NotificationPreferences:
    """User notification preferences."""
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    in_app_notifications: bool = True
    prediction_alerts: bool = True
    bet_results: bool = True
    system_updates: bool = False
    marketing_emails: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"

@dataclass
class DisplayPreferences:
    """User display and UI preferences."""
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"
    currency: str = "USD"
    odds_format: str = "american"
    show_confidence_scores: bool = True
    show_historical_accuracy: bool = True
    compact_view: bool = False
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds

@dataclass
class UserPreferences:
    """Complete user preferences."""
    user_id: str
    betting: BettingPreferences = None
    notifications: NotificationPreferences = None
    display: DisplayPreferences = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.betting is None:
            self.betting = BettingPreferences()
        if self.notifications is None:
            self.notifications = NotificationPreferences()
        if self.display is None:
            self.display = DisplayPreferences()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

class UserPreferencesService:
    """Service for managing user preferences."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize the preferences service."""
        self.redis_url = redis_url
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis connection established for preferences")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed for preferences: {e}")
            self.redis_client = None
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        try:
            if not self.redis_client:
                return self._get_default_preferences(user_id)
            
            key = f"user_preferences:{user_id}"
            preferences_data = self.redis_client.get(key)
            
            if preferences_data:
                data = json.loads(preferences_data)
                return self._deserialize_preferences(data)
            else:
                # Create default preferences
                default_prefs = self._get_default_preferences(user_id)
                self.save_user_preferences(default_prefs)
                return default_prefs
                
        except Exception as e:
            logger.error(f"❌ Failed to get user preferences: {e}")
            return self._get_default_preferences(user_id)
    
    def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """Save user preferences."""
        try:
            if not self.redis_client:
                return False
            
            preferences.updated_at = datetime.utcnow()
            key = f"user_preferences:{preferences.user_id}"
            
            # Serialize preferences
            data = self._serialize_preferences(preferences)
            json_data = json.dumps(data)
            
            # Save to Redis with expiration (30 days)
            self.redis_client.setex(key, 86400 * 30, json_data)
            
            logger.info(f"✅ Preferences saved for user: {preferences.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save user preferences: {e}")
            return False
    
    def update_betting_preferences(self, user_id: str, 
                                 betting_prefs: Dict[str, Any]) -> bool:
        """Update user betting preferences."""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                return False
            
            # Update betting preferences
            for key, value in betting_prefs.items():
                if hasattr(preferences.betting, key):
                    setattr(preferences.betting, key, value)
            
            return self.save_user_preferences(preferences)
            
        except Exception as e:
            logger.error(f"❌ Failed to update betting preferences: {e}")
            return False
    
    def update_notification_preferences(self, user_id: str, 
                                      notification_prefs: Dict[str, Any]) -> bool:
        """Update user notification preferences."""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                return False
            
            # Update notification preferences
            for key, value in notification_prefs.items():
                if hasattr(preferences.notifications, key):
                    setattr(preferences.notifications, key, value)
            
            return self.save_user_preferences(preferences)
            
        except Exception as e:
            logger.error(f"❌ Failed to update notification preferences: {e}")
            return False
    
    def update_display_preferences(self, user_id: str, 
                                 display_prefs: Dict[str, Any]) -> bool:
        """Update user display preferences."""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences:
                return False
            
            # Update display preferences
            for key, value in display_prefs.items():
                if hasattr(preferences.display, key):
                    setattr(preferences.display, key, value)
            
            return self.save_user_preferences(preferences)
            
        except Exception as e:
            logger.error(f"❌ Failed to update display preferences: {e}")
            return False
    
    def get_user_sport_preferences(self, user_id: str) -> List[SportType]:
        """Get user's preferred sports."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.betting:
                return preferences.betting.preferred_sports
            return [SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL, SportType.HOCKEY]
        except Exception as e:
            logger.error(f"❌ Failed to get sport preferences: {e}")
            return [SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL, SportType.HOCKEY]
    
    def get_user_risk_level(self, user_id: str) -> RiskLevel:
        """Get user's risk level."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.betting:
                return preferences.betting.risk_level
            return RiskLevel.MODERATE
        except Exception as e:
            logger.error(f"❌ Failed to get risk level: {e}")
            return RiskLevel.MODERATE
    
    def get_user_confidence_threshold(self, user_id: str) -> float:
        """Get user's minimum confidence threshold."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.betting:
                return preferences.betting.min_confidence_threshold
            return 0.6
        except Exception as e:
            logger.error(f"❌ Failed to get confidence threshold: {e}")
            return 0.6
    
    def get_user_max_bet_amount(self, user_id: str) -> float:
        """Get user's maximum bet amount."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.betting:
                return preferences.betting.max_bet_amount
            return 100.0
        except Exception as e:
            logger.error(f"❌ Failed to get max bet amount: {e}")
            return 100.0
    
    def is_notification_enabled(self, user_id: str, notification_type: NotificationType) -> bool:
        """Check if a specific notification type is enabled for the user."""
        try:
            preferences = self.get_user_preferences(user_id)
            if not preferences or not preferences.notifications:
                return True  # Default to enabled
            
            if notification_type == NotificationType.EMAIL:
                return preferences.notifications.email_notifications
            elif notification_type == NotificationType.PUSH:
                return preferences.notifications.push_notifications
            elif notification_type == NotificationType.SMS:
                return preferences.notifications.sms_notifications
            elif notification_type == NotificationType.IN_APP:
                return preferences.notifications.in_app_notifications
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check notification status: {e}")
            return True
    
    def get_user_timezone(self, user_id: str) -> str:
        """Get user's timezone."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.display:
                return preferences.display.timezone
            return "UTC"
        except Exception as e:
            logger.error(f"❌ Failed to get timezone: {e}")
            return "UTC"
    
    def get_user_currency(self, user_id: str) -> str:
        """Get user's preferred currency."""
        try:
            preferences = self.get_user_preferences(user_id)
            if preferences and preferences.display:
                return preferences.display.currency
            return "USD"
        except Exception as e:
            logger.error(f"❌ Failed to get currency: {e}")
            return "USD"
    
    def reset_user_preferences(self, user_id: str) -> bool:
        """Reset user preferences to defaults."""
        try:
            default_prefs = self._get_default_preferences(user_id)
            return self.save_user_preferences(default_prefs)
        except Exception as e:
            logger.error(f"❌ Failed to reset preferences: {e}")
            return False
    
    def delete_user_preferences(self, user_id: str) -> bool:
        """Delete user preferences."""
        try:
            if not self.redis_client:
                return False
            
            key = f"user_preferences:{user_id}"
            self.redis_client.delete(key)
            
            logger.info(f"✅ Preferences deleted for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete preferences: {e}")
            return False
    
    def get_preferences_stats(self) -> Dict[str, Any]:
        """Get statistics about user preferences."""
        try:
            if not self.redis_client:
                return {"error": "Redis not available"}
            
            pattern = "user_preferences:*"
            keys = self.redis_client.keys(pattern)
            
            total_users = len(keys)
            
            # Sample some preferences for statistics
            sport_counts = {sport.value: 0 for sport in SportType}
            risk_counts = {risk.value: 0 for risk in RiskLevel}
            theme_counts = {"light": 0, "dark": 0}
            
            sample_size = min(100, total_users)  # Sample up to 100 users
            sample_keys = keys[:sample_size]
            
            for key in sample_keys:
                try:
                    data = self.redis_client.get(key)
                    if data:
                        prefs_data = json.loads(data)
                        if "betting" in prefs_data:
                            betting = prefs_data["betting"]
                            if "preferred_sports" in betting:
                                for sport in betting["preferred_sports"]:
                                    if sport in sport_counts:
                                        sport_counts[sport] += 1
                            if "risk_level" in betting:
                                risk = betting["risk_level"]
                                if risk in risk_counts:
                                    risk_counts[risk] += 1
                        if "display" in prefs_data:
                            display = prefs_data["display"]
                            if "theme" in display:
                                theme = display["theme"]
                                if theme in theme_counts:
                                    theme_counts[theme] += 1
                except Exception:
                    continue
            
            return {
                "total_users_with_preferences": total_users,
                "sport_preferences": sport_counts,
                "risk_levels": risk_counts,
                "theme_preferences": theme_counts,
                "sample_size": sample_size
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get preferences stats: {e}")
            return {"error": str(e)}
    
    def _get_default_preferences(self, user_id: str) -> UserPreferences:
        """Get default preferences for a user."""
        return UserPreferences(
            user_id=user_id,
            betting=BettingPreferences(),
            notifications=NotificationPreferences(),
            display=DisplayPreferences()
        )
    
    def _serialize_preferences(self, preferences: UserPreferences) -> Dict[str, Any]:
        """Serialize preferences to dictionary."""
        return {
            "user_id": preferences.user_id,
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
    
    def _deserialize_preferences(self, data: Dict[str, Any]) -> UserPreferences:
        """Deserialize preferences from dictionary."""
        try:
            betting = BettingPreferences(
                preferred_sports=[SportType(sport) for sport in data["betting"]["preferred_sports"]],
                risk_level=RiskLevel(data["betting"]["risk_level"]),
                max_bet_amount=data["betting"]["max_bet_amount"],
                min_confidence_threshold=data["betting"]["min_confidence_threshold"],
                preferred_betting_types=[BettingType(bet_type) for bet_type in data["betting"]["preferred_betting_types"]],
                auto_betting_enabled=data["betting"]["auto_betting_enabled"],
                max_daily_bets=data["betting"]["max_daily_bets"],
                max_weekly_loss=data["betting"]["max_weekly_loss"]
            )
            
            notifications = NotificationPreferences(
                email_notifications=data["notifications"]["email_notifications"],
                push_notifications=data["notifications"]["push_notifications"],
                sms_notifications=data["notifications"]["sms_notifications"],
                in_app_notifications=data["notifications"]["in_app_notifications"],
                prediction_alerts=data["notifications"]["prediction_alerts"],
                bet_results=data["notifications"]["bet_results"],
                system_updates=data["notifications"]["system_updates"],
                marketing_emails=data["notifications"]["marketing_emails"],
                quiet_hours_start=data["notifications"]["quiet_hours_start"],
                quiet_hours_end=data["notifications"]["quiet_hours_end"]
            )
            
            display = DisplayPreferences(
                theme=data["display"]["theme"],
                language=data["display"]["language"],
                timezone=data["display"]["timezone"],
                currency=data["display"]["currency"],
                odds_format=data["display"]["odds_format"],
                show_confidence_scores=data["display"]["show_confidence_scores"],
                show_historical_accuracy=data["display"]["show_historical_accuracy"],
                compact_view=data["display"]["compact_view"],
                auto_refresh=data["display"]["auto_refresh"],
                refresh_interval=data["display"]["refresh_interval"]
            )
            
            return UserPreferences(
                user_id=data["user_id"],
                betting=betting,
                notifications=notifications,
                display=display,
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to deserialize preferences: {e}")
            return self._get_default_preferences(data["user_id"]) 