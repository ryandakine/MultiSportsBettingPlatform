"""
Enhanced WebSocket Routes for Real-Time Communication
==================================================
Live updates and real-time prediction streaming with authentication and Redis integration.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import HTTPBearer

from src.services.websocket_service import (
    websocket_manager, 
    WebSocketMessage, 
    MessageType, 
    ConnectionInfo
)
from src.services.real_time_predictions import real_time_service, PredictionType
from src.services.auth_service import verify_token
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

async def get_current_user_from_token(token: str = Depends(security)) -> str:
    """Get current user from JWT token."""
    try:
        user_id = verify_token(token.credentials)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.websocket("/ws/authenticated")
async def websocket_authenticated(websocket: WebSocket):
    """WebSocket endpoint for authenticated users with enhanced features."""
    client_data = {
        "client_id": f"auth_client_{int(datetime.now().timestamp())}",
        "connected_at": datetime.now().isoformat(),
        "preferences": {}
    }
    
    # Connect the WebSocket
    connection_info = await websocket_manager.connect(websocket, client_data)
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "authenticate":
                    token = message.get("token")
                    if token:
                        success = await websocket_manager.authenticate_connection(connection_info, token)
                        if not success:
                            error_message = WebSocketMessage(
                                type=MessageType.ERROR,
                                data={"message": "Authentication failed", "code": "AUTH_FAILED"},
                                timestamp=datetime.now(),
                                session_id=connection_info.session_id
                            )
                            await websocket_manager.send_message(connection_info, error_message)
                
                elif message.get("type") == "subscribe":
                    channel = message.get("channel")
                    if channel:
                        await websocket_manager.subscribe_to_channel(connection_info, channel)
                
                elif message.get("type") == "unsubscribe":
                    channel = message.get("channel")
                    if channel:
                        await websocket_manager.unsubscribe_from_channel(connection_info, channel)
                
                elif message.get("type") == "request_prediction":
                    if connection_info.status.value == "authenticated":
                        sport = message.get("sport", "baseball")
                        teams = message.get("teams", ["Team A", "Team B"])
                        
                        # Generate prediction
                        prediction = await real_time_service.generate_live_prediction(sport, teams)
                        
                        # Send prediction to client
                        prediction_message = WebSocketMessage(
                            type=MessageType.PREDICTION_UPDATE,
                            data={
                                "prediction": {
                                    "id": prediction.id,
                                    "sport": prediction.sport,
                                    "teams": prediction.teams,
                                    "prediction": prediction.prediction,
                                    "confidence": prediction.confidence,
                                    "odds": prediction.odds,
                                    "timestamp": prediction.timestamp.isoformat(),
                                    "type": prediction.type.value,
                                    "reasoning": prediction.reasoning,
                                    "yolo_factor": prediction.yolo_factor
                                }
                            },
                            timestamp=datetime.now(),
                            user_id=connection_info.user_id,
                            session_id=connection_info.session_id
                        )
                        await websocket_manager.send_message(connection_info, prediction_message)
                    else:
                        error_message = WebSocketMessage(
                            type=MessageType.ERROR,
                            data={"message": "Authentication required for predictions", "code": "AUTH_REQUIRED"},
                            timestamp=datetime.now(),
                            session_id=connection_info.session_id
                        )
                        await websocket_manager.send_message(connection_info, error_message)
                
                elif message.get("type") == "ping":
                    await websocket_manager.handle_heartbeat(connection_info)
                
                elif message.get("type") == "get_stats":
                    stats = websocket_manager.get_connection_stats()
                    stats_message = WebSocketMessage(
                        type=MessageType.CONNECTION_STATUS,
                        data={"stats": stats},
                        timestamp=datetime.now(),
                        user_id=connection_info.user_id,
                        session_id=connection_info.session_id
                    )
                    await websocket_manager.send_message(connection_info, stats_message)
                
            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "Invalid JSON format", "code": "INVALID_JSON"},
                    timestamp=datetime.now(),
                    session_id=connection_info.session_id
                )
                await websocket_manager.send_message(connection_info, error_message)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_info.session_id)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        await websocket_manager.disconnect(connection_info.session_id)

@router.websocket("/ws/predictions")
async def websocket_predictions(websocket: WebSocket):
    """WebSocket endpoint for real-time prediction updates."""
    client_data = {
        "client_id": f"pred_client_{int(datetime.now().timestamp())}",
        "connected_at": datetime.now().isoformat(),
        "preferences": {"predictions": True}
    }
    
    connection_info = await websocket_manager.connect(websocket, client_data)
    
    try:
        # Send current live predictions
        live_predictions = await real_time_service.get_live_predictions()
        
        predictions_message = WebSocketMessage(
            type=MessageType.PREDICTION_UPDATE,
            data={
                "predictions": [
                    {
                        "id": p.id,
                        "sport": p.sport,
                        "teams": p.teams,
                        "prediction": p.prediction,
                        "confidence": p.confidence,
                        "odds": p.odds,
                        "timestamp": p.timestamp.isoformat(),
                        "type": p.type.value,
                        "reasoning": p.reasoning,
                        "yolo_factor": p.yolo_factor
                    }
                    for p in live_predictions
                ]
            },
            timestamp=datetime.now(),
            session_id=connection_info.session_id
        )
        
        await websocket_manager.send_message(connection_info, predictions_message)
        
        # Subscribe to prediction updates
        await websocket_manager.subscribe_to_channel(connection_info, "predictions")
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket_manager.handle_heartbeat(connection_info)
                elif message.get("type") == "request_new_prediction":
                    sport = message.get("sport", "baseball")
                    teams = message.get("teams", ["Team A", "Team B"])
                    
                    prediction = await real_time_service.generate_live_prediction(sport, teams)
                    
                    # Broadcast to all prediction subscribers
                    broadcast_message = WebSocketMessage(
                        type=MessageType.PREDICTION_UPDATE,
                        data={
                            "new_prediction": {
                                "id": prediction.id,
                                "sport": prediction.sport,
                                "teams": prediction.teams,
                                "prediction": prediction.prediction,
                                "confidence": prediction.confidence,
                                "odds": prediction.odds,
                                "timestamp": prediction.timestamp.isoformat(),
                                "type": prediction.type.value,
                                "reasoning": prediction.reasoning,
                                "yolo_factor": prediction.yolo_factor
                            }
                        },
                        timestamp=datetime.now()
                    )
                    
                    await websocket_manager.broadcast_message(
                        broadcast_message,
                        filter_func=lambda conn: "predictions" in conn.subscriptions
                    )
                    
            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "Invalid JSON format", "code": "INVALID_JSON"},
                    timestamp=datetime.now(),
                    session_id=connection_info.session_id
                )
                await websocket_manager.send_message(connection_info, error_message)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_info.session_id)
    except Exception as e:
        logger.error(f"❌ Predictions WebSocket error: {e}")
        await websocket_manager.disconnect(connection_info.session_id)

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for user notifications."""
    client_data = {
        "client_id": f"notif_client_{int(datetime.now().timestamp())}",
        "connected_at": datetime.now().isoformat(),
        "preferences": {"notifications": True}
    }
    
    connection_info = await websocket_manager.connect(websocket, client_data)
    
    try:
        # Subscribe to notifications
        await websocket_manager.subscribe_to_channel(connection_info, "notifications")
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket_manager.handle_heartbeat(connection_info)
                elif message.get("type") == "authenticate":
                    token = message.get("token")
                    if token:
                        success = await websocket_manager.authenticate_connection(connection_info, token)
                        if success:
                            # Subscribe to user-specific notifications
                            await websocket_manager.subscribe_to_channel(
                                connection_info, 
                                f"user_notifications:{connection_info.user_id}"
                            )
                            
            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "Invalid JSON format", "code": "INVALID_JSON"},
                    timestamp=datetime.now(),
                    session_id=connection_info.session_id
                )
                await websocket_manager.send_message(connection_info, error_message)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_info.session_id)
    except Exception as e:
        logger.error(f"❌ Notifications WebSocket error: {e}")
        await websocket_manager.disconnect(connection_info.session_id)

# API endpoints for WebSocket management
@router.get("/api/v1/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    stats = websocket_manager.get_connection_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/v1/websocket/stats/detailed")
async def get_detailed_websocket_stats():
    """Get detailed WebSocket connection statistics including Redis pool information."""
    stats = await websocket_manager.get_detailed_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/api/v1/websocket/broadcast")
async def broadcast_message(request: Dict[str, Any], current_user: str = Depends(get_current_user_from_token)):
    """Broadcast a message to all connected WebSocket clients."""
    message_type = request.get("type", "system_alert")
    message_data = request.get("data", {})
    
    broadcast_message = WebSocketMessage(
        type=MessageType(message_type),
        data=message_data,
        timestamp=datetime.now(),
        user_id=current_user
    )
    
    await websocket_manager.broadcast_message(broadcast_message)
    
    return {
        "success": True,
        "message": "Broadcast sent successfully",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/api/v1/websocket/broadcast/advanced")
async def advanced_broadcast(request: Dict[str, Any], current_user: str = Depends(get_current_user_from_token)):
    """Advanced broadcast with priority, targeting, and delivery tracking."""
    from src.services.message_broadcasting import BroadcastMessage, MessagePriority
    
    message_type = request.get("type", "system_alert")
    message_data = request.get("data", {})
    priority = MessagePriority(request.get("priority", "normal"))
    target_channels = request.get("target_channels")
    target_users = request.get("target_users")
    expires_in = request.get("expires_in")  # seconds
    
    # Create broadcast message
    message = BroadcastMessage(
        id=f"broadcast_{int(datetime.now().timestamp())}",
        type=message_type,
        data=message_data,
        priority=priority,
        timestamp=datetime.now(),
        sender_id=current_user,
        target_channels=target_channels,
        target_users=target_users,
        expires_at=datetime.now() + timedelta(seconds=expires_in) if expires_in else None
    )
    
    # Broadcast using message broadcaster
    if websocket_manager.message_broadcaster:
        message_id = await websocket_manager.message_broadcaster.broadcast_message(message)
        
        return {
            "success": True,
            "message": "Advanced broadcast queued successfully",
            "message_id": message_id,
            "priority": priority.value,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Message broadcaster not available")

@router.get("/api/v1/websocket/broadcast/stats/{message_id}")
async def get_broadcast_stats(message_id: str, current_user: str = Depends(get_current_user_from_token)):
    """Get delivery statistics for a specific broadcast message."""
    if websocket_manager.message_broadcaster:
        stats = await websocket_manager.message_broadcaster.get_delivery_stats(message_id)
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Message broadcaster not available")

@router.get("/api/v1/websocket/broadcast/queue-stats")
async def get_broadcast_queue_stats(current_user: str = Depends(get_current_user_from_token)):
    """Get message queue statistics."""
    if websocket_manager.message_broadcaster:
        stats = await websocket_manager.message_broadcaster.get_queue_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Message broadcaster not available")

# Notification endpoints
@router.post("/api/v1/notifications/send")
async def send_notification(request: Dict[str, Any], current_user: str = Depends(get_current_user_from_token)):
    """Send a notification to a user."""
    from src.services.notification_service import Notification, NotificationType, NotificationPriority, NotificationChannel
    
    title = request.get("title", "Notification")
    message = request.get("message", "")
    notification_type = NotificationType(request.get("type", "system_alert"))
    priority = NotificationPriority(request.get("priority", "normal"))
    recipient_id = request.get("recipient_id")
    channels = [NotificationChannel(c) for c in request.get("channels", ["in_app"])]
    data = request.get("data", {})
    expires_in = request.get("expires_in")  # seconds
    
    notification = Notification(
        id=f"notif_{int(datetime.now().timestamp())}",
        type=notification_type,
        title=title,
        message=message,
        priority=priority,
        timestamp=datetime.now(),
        sender_id=current_user,
        recipient_id=recipient_id,
        channels=channels,
        data=data,
        expires_at=datetime.now() + timedelta(seconds=expires_in) if expires_in else None
    )
    
    if websocket_manager.notification_service:
        notification_id = await websocket_manager.notification_service.send_notification(notification, recipient_id)
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "notification_id": notification_id,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.post("/api/v1/notifications/send-bulk")
async def send_bulk_notification(request: Dict[str, Any], current_user: str = Depends(get_current_user_from_token)):
    """Send notification to multiple users."""
    from src.services.notification_service import Notification, NotificationType, NotificationPriority, NotificationChannel
    
    title = request.get("title", "Bulk Notification")
    message = request.get("message", "")
    notification_type = NotificationType(request.get("type", "system_alert"))
    priority = NotificationPriority(request.get("priority", "normal"))
    user_ids = request.get("user_ids", [])
    channels = [NotificationChannel(c) for c in request.get("channels", ["in_app"])]
    data = request.get("data", {})
    expires_in = request.get("expires_in")  # seconds
    
    if not user_ids:
        raise HTTPException(status_code=400, detail="user_ids is required")
    
    notification = Notification(
        id=f"bulk_notif_{int(datetime.now().timestamp())}",
        type=notification_type,
        title=title,
        message=message,
        priority=priority,
        timestamp=datetime.now(),
        sender_id=current_user,
        channels=channels,
        data=data,
        expires_at=datetime.now() + timedelta(seconds=expires_in) if expires_in else None
    )
    
    if websocket_manager.notification_service:
        results = await websocket_manager.notification_service.send_bulk_notification(notification, user_ids)
        
        return {
            "success": True,
            "message": "Bulk notification sent",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.get("/api/v1/notifications/user/{user_id}")
async def get_user_notifications(
    user_id: str, 
    limit: int = 50, 
    offset: int = 0,
    current_user: str = Depends(get_current_user_from_token)
):
    """Get notifications for a user."""
    if websocket_manager.notification_service:
        notifications = await websocket_manager.notification_service.get_user_notifications(user_id, limit, offset)
        
        return {
            "success": True,
            "data": {
                "notifications": [n.to_dict() for n in notifications],
                "limit": limit,
                "offset": offset,
                "total": len(notifications)
            },
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.post("/api/v1/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: str = Depends(get_current_user_from_token)
):
    """Mark a notification as read."""
    if websocket_manager.notification_service:
        success = await websocket_manager.notification_service.mark_as_read(notification_id, current_user)
        
        return {
            "success": success,
            "message": "Notification marked as read" if success else "Failed to mark notification as read",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.get("/api/v1/notifications/stats/{user_id}")
async def get_notification_stats(
    user_id: str,
    current_user: str = Depends(get_current_user_from_token)
):
    """Get notification statistics for a user."""
    if websocket_manager.notification_service:
        stats = await websocket_manager.notification_service.get_notification_stats(user_id)
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.get("/api/v1/notifications/preferences/{user_id}")
async def get_notification_preferences(
    user_id: str,
    current_user: str = Depends(get_current_user_from_token)
):
    """Get notification preferences for a user."""
    if websocket_manager.notification_service:
        preferences = await websocket_manager.notification_service.get_preferences(user_id)
        
        if preferences:
            return {
                "success": True,
                "data": preferences.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "data": None,
                "message": "No preferences found, using defaults",
                "timestamp": datetime.now().isoformat()
            }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.put("/api/v1/notifications/preferences/{user_id}")
async def update_notification_preferences(
    user_id: str,
    request: Dict[str, Any],
    current_user: str = Depends(get_current_user_from_token)
):
    """Update notification preferences for a user."""
    from src.services.notification_service import NotificationPreference, NotificationType, NotificationChannel, NotificationPriority
    
    # Extract preferences from request
    notification_types = {
        NotificationType(k): v for k, v in request.get("notification_types", {}).items()
    }
    channels = {
        NotificationChannel(k): v for k, v in request.get("channels", {}).items()
    }
    priority_levels = {
        NotificationPriority(k): v for k, v in request.get("priority_levels", {}).items()
    }
    
    preferences = NotificationPreference(
        user_id=user_id,
        notification_types=notification_types,
        channels=channels,
        priority_levels=priority_levels,
        quiet_hours_start=request.get("quiet_hours_start"),
        quiet_hours_end=request.get("quiet_hours_end"),
        timezone=request.get("timezone", "UTC"),
        marketing_enabled=request.get("marketing_enabled", False),
        frequency_limit=request.get("frequency_limit")
    )
    
    if websocket_manager.notification_service:
        success = await websocket_manager.notification_service.update_preferences(user_id, preferences)
        
        return {
            "success": success,
            "message": "Preferences updated successfully" if success else "Failed to update preferences",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=503, detail="Notification service not available")

@router.post("/api/v1/websocket/send-to-user")
async def send_message_to_user(
    request: Dict[str, Any], 
    current_user: str = Depends(get_current_user_from_token)
):
    """Send a message to a specific user's WebSocket connections."""
    target_user_id = request.get("user_id")
    message_type = request.get("type", "notification")
    message_data = request.get("data", {})
    
    if not target_user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    message = WebSocketMessage(
        type=MessageType(message_type),
        data=message_data,
        timestamp=datetime.now(),
        user_id=current_user
    )
    
    await websocket_manager.send_to_user(target_user_id, message)
    
    return {
        "success": True,
        "message": f"Message sent to user {target_user_id}",
        "timestamp": datetime.now().isoformat()
    }

# Legacy endpoints for backward compatibility
@router.websocket("/ws/yolo-predictions")
async def websocket_yolo_predictions(websocket: WebSocket):
    """Legacy WebSocket endpoint for YOLO predictions."""
    client_data = {
        "client_id": f"yolo_client_{int(datetime.now().timestamp())}",
        "connected_at": datetime.now().isoformat(),
        "yolo_mode": True
    }
    
    connection_info = await websocket_manager.connect(websocket, client_data)
    
    try:
        # Send initial YOLO stats
        yolo_stats = await real_time_service.get_yolo_stats()
        stats_message = WebSocketMessage(
            type=MessageType.CONNECTION_STATUS,
            data={"yolo_stats": yolo_stats},
            timestamp=datetime.now(),
            session_id=connection_info.session_id
        )
        await websocket_manager.send_message(connection_info, stats_message)
        
        # Subscribe to YOLO predictions
        await websocket_manager.subscribe_to_channel(connection_info, "yolo_predictions")
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "request_prediction":
                    sport = message.get("sport", "baseball")
                    teams = message.get("teams", ["Team A", "Team B"])
                    
                    prediction = await real_time_service.generate_live_prediction(sport, teams)
                    
                    prediction_message = WebSocketMessage(
                        type=MessageType.PREDICTION_UPDATE,
                        data={
                            "prediction": {
                                "id": prediction.id,
                                "sport": prediction.sport,
                                "teams": prediction.teams,
                                "prediction": prediction.prediction,
                                "confidence": prediction.confidence,
                                "odds": prediction.odds,
                                "timestamp": prediction.timestamp.isoformat(),
                                "type": prediction.type.value,
                                "reasoning": prediction.reasoning,
                                "yolo_factor": prediction.yolo_factor
                            }
                        },
                        timestamp=datetime.now(),
                        session_id=connection_info.session_id
                    )
                    await websocket_manager.send_message(connection_info, prediction_message)
                
                elif message.get("type") == "ping":
                    await websocket_manager.handle_heartbeat(connection_info)
                    
            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"message": "Invalid JSON format", "code": "INVALID_JSON"},
                    timestamp=datetime.now(),
                    session_id=connection_info.session_id
                )
                await websocket_manager.send_message(connection_info, error_message)
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_info.session_id)
    except Exception as e:
        logger.error(f"❌ YOLO WebSocket error: {e}")
        await websocket_manager.disconnect(connection_info.session_id)

# Legacy API endpoints
@router.get("/api/v1/yolo/stats")
async def get_yolo_stats():
    """Get YOLO mode statistics."""
    stats = await real_time_service.get_yolo_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/yolo/insights/{sport}")
async def get_yolo_insights(sport: str):
    """Get YOLO insights for a specific sport."""
    insights = await real_time_service.generate_yolo_insights(sport)
    return {
        "success": True,
        "sport": sport,
        "insights": insights,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/yolo/generate-prediction")
async def generate_yolo_prediction(request: Dict[str, Any]):
    """Generate a new YOLO prediction."""
    sport = request.get("sport", "baseball")
    teams = request.get("teams", ["Team A", "Team B"])
    
    prediction = await real_time_service.generate_live_prediction(sport, teams)
    
    # Broadcast to all YOLO subscribers
    broadcast_message = WebSocketMessage(
        type=MessageType.PREDICTION_UPDATE,
        data={
            "new_yolo_prediction": {
                "id": prediction.id,
                "sport": prediction.sport,
                "teams": prediction.teams,
                "prediction": prediction.prediction,
                "confidence": prediction.confidence,
                "odds": prediction.odds,
                "timestamp": prediction.timestamp.isoformat(),
                "type": prediction.type.value,
                "reasoning": prediction.reasoning,
                "yolo_factor": prediction.yolo_factor
            }
        },
        timestamp=datetime.now()
    )
    
    await websocket_manager.broadcast_message(
        broadcast_message,
        filter_func=lambda conn: "yolo_predictions" in conn.subscriptions
    )
    
    return {
        "success": True,
        "prediction": {
            "id": prediction.id,
            "sport": prediction.sport,
            "teams": prediction.teams,
            "prediction": prediction.prediction,
            "confidence": prediction.confidence,
            "odds": prediction.odds,
            "timestamp": prediction.timestamp.isoformat(),
            "type": prediction.type.value,
            "reasoning": prediction.reasoning,
            "yolo_factor": prediction.yolo_factor
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    } 