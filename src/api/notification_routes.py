"""
Notification Routes
==================
Endpoints for managing and retrieving user notifications.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, status
from src.services.notification_service import notification_service, Notification, NotificationPreference

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_notifications(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[Dict[str, Any]]:
    """Get paginated notifications for a user."""
    try:
        if not notification_service:
            raise HTTPException(status_code=503, detail="Notification service not initialized")
            
        notifications = await notification_service.get_user_notifications(user_id, limit, offset)
        return [n.to_dict() for n in notifications]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")

@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str, user_id: str):
    """Mark a notification as read."""
    try:
        if not notification_service:
             raise HTTPException(status_code=503, detail="Notification service not initialized")
             
        success = await notification_service.mark_as_read(notification_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        return {"success": True, "message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification: {str(e)}")

@router.get("/preferences")
async def get_preferences(user_id: str):
    """Get user notification preferences."""
    try:
        if not notification_service:
             raise HTTPException(status_code=503, detail="Notification service not initialized")
             
        prefs = await notification_service.get_preferences(user_id)
        if not prefs:
            # Return defaults if not found
            # Effectively, default preferences are managed in service
            # For API response, we can fetch defaults or return empty
             return {}
        return prefs.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")
