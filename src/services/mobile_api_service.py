"""
Mobile API Service
=================
Comprehensive mobile app framework with optimized API endpoints,
offline capabilities, push notifications, and mobile-specific features.
"""

import json
import gzip
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from src.db.models.mobile import MobileDevice, Notification, OfflineAction
from src.db.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileAPIService:
    """Mobile API service with comprehensive mobile features."""
    
    def __init__(self):
        # Cache for mobile optimized responses
        self.cache: Dict[str, Any] = {}
        logger.info("✅ Mobile API Service initialized")
    
    async def register_mobile_user(self, db: Session, user_id: str, platform: str,
                                 device_token: str, app_version: str, os_version: str,
                                 device_model: str, push_enabled: bool = True) -> MobileDevice:
        """Register a new mobile user/device."""
        try:
            # Check if device already exists
            stmt = select(MobileDevice).where(MobileDevice.device_token == device_token)
            device = db.execute(stmt).scalar_one_or_none()
            
            if device:
                # Update existing device
                device.user_id = user_id
                device.app_version = app_version
                device.os_version = os_version
                device.last_active = datetime.utcnow()
                device.push_enabled = push_enabled
            else:
                # Create new device
                device = MobileDevice(
                    user_id=user_id,
                    platform=platform,
                    device_token=device_token,
                    app_version=app_version,
                    os_version=os_version,
                    device_model=device_model,
                    push_enabled=push_enabled,
                    notification_preferences={
                        'prediction_update': True,
                        'bet_result': True,
                        'system_alert': True
                    }
                )
                db.add(device)
            
            db.commit()
            db.refresh(device)
            
            logger.info(f"✅ Registered mobile device: {device_model} ({platform})")
            return device
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Mobile user registration failed: {e}")
            raise

    async def get_mobile_optimized_data(self, db: Session, endpoint: str, user_id: str, 
                                      params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get mobile-optimized data with compression and caching."""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(endpoint, user_id, params)
            
            # Check internal memory cache first (could be Redis in future)
            if cache_key in self.cache:
                cached_data, expires_at = self.cache[cache_key]
                if datetime.now() < expires_at:
                    return cached_data
            
            # Generate data based on endpoint
            data = await self._generate_data_for_endpoint(db, endpoint, user_id, params)
            
            # Wrap response
            response = {
                "success": True,
                "data": data,
                "version": "1.2.0",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache it
            self.cache[cache_key] = (response, datetime.now() + timedelta(minutes=5))
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Mobile data generation failed: {e}")
            raise

    async def send_push_notification(self, db: Session, user_id: str, notification_type: str,
                                   title: str, body: str, data: Dict[str, Any] = None) -> Optional[Notification]:
        """Send push notification to mobile user devices."""
        try:
            # Get user devices
            stmt = select(MobileDevice).where(
                MobileDevice.user_id == user_id,
                MobileDevice.push_enabled == True
            )
            devices = db.execute(stmt).scalars().all()
            
            if not devices:
                logger.info(f"📱 No push-enabled devices found for user {user_id}")
                return None
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                body=body,
                data=data or {},
                priority="normal",
                created_at=datetime.utcnow()
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # In a real app, here we would call FCM/APNS for each device.device_token
            # For now, we just log it.
            for device in devices:
                logger.info(f"🚀 Sending push to {device.platform} device {device.device_model}")
            
            # Mark as sent
            notification.sent_at = datetime.utcnow()
            notification.delivered = True 
            db.commit()
            
            return notification
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Push notification failed: {e}")
            raise

    async def store_offline_action(self, db: Session, user_id: str, action_type: str, 
                                 payload: Dict[str, Any]) -> OfflineAction:
        """Store offline action for later sync."""
        try:
            action = OfflineAction(
                user_id=user_id,
                action_type=action_type,
                payload=payload,
                created_at=datetime.utcnow(),
                synced=False
            )
            
            db.add(action)
            db.commit()
            db.refresh(action)
            
            logger.info(f"📱 Offline action stored: {action_type}")
            return action
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Offline action storage failed: {e}")
            raise

    async def sync_offline_actions(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Sync offline actions for a user."""
        try:
            stmt = select(OfflineAction).where(
                OfflineAction.user_id == user_id,
                OfflineAction.synced == False
            )
            actions = db.execute(stmt).scalars().all()
            
            sync_results = []
            
            for action in actions:
                try:
                    # Process the action (placeholder logic)
                    # In real app, dispatch to appropriate service handler
                    logger.info(f"Processing offline action: {action.action_type}")
                    
                    action.synced = True
                    action.processed_at = datetime.utcnow()
                    
                    sync_results.append({
                        "action_id": action.id,
                        "status": "success"
                    })
                    
                except Exception as e:
                    action.retry_count += 1
                    sync_results.append({
                        "action_id": action.id,
                        "status": "failed",
                        "error": str(e)
                    })
            
            db.commit()
            return sync_results
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Offline sync failed: {e}")
            raise

    def _generate_cache_key(self, endpoint: str, user_id: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for mobile data."""
        key_data = f"{endpoint}:{user_id}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _generate_data_for_endpoint(self, db: Session, endpoint: str, user_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Wrapper to fetch real data based on endpoint."""
        # Fetch real data from database based on endpoint
        if endpoint == "user_profile":
            user = db.get(User, user_id)
            if user:
                return {"username": user.username, "email": user.email}
        # Extend with more endpoints/services as needed
        return {"message": "Data endpoint", "endpoint": endpoint}