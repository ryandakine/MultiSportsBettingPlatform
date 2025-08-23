"""
Social API Routes - YOLO MODE!
============================
Community features, leaderboards, and social interactions.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException

from src.services.social_features import social_service

router = APIRouter()

@router.get("/api/v1/social/communities")
async def get_communities():
    """Get all YOLO communities."""
    communities = await social_service.get_communities()
    return {
        "success": True,
        "communities": communities,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/social/communities/{community_id}")
async def get_community(community_id: str):
    """Get specific community details."""
    communities = await social_service.get_communities()
    community = next((c for c in communities if c["community_id"] == community_id), None)
    
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    return {
        "success": True,
        "community": community,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/social/join-community")
async def join_community(request: Dict[str, Any]):
    """Join a YOLO community."""
    user_id = request.get("user_id")
    community_id = request.get("community_id")
    
    if not user_id or not community_id:
        raise HTTPException(status_code=400, detail="user_id and community_id required")
    
    success = await social_service.join_community(user_id, community_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to join community")
    
    return {
        "success": True,
        "message": f"Successfully joined YOLO community! 🚀",
        "user_id": user_id,
        "community_id": community_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/social/share-prediction")
async def share_prediction(request: Dict[str, Any]):
    """Share a prediction in a community."""
    user_id = request.get("user_id")
    community_id = request.get("community_id")
    sport = request.get("sport")
    prediction = request.get("prediction")
    confidence = request.get("confidence", 0.8)
    reasoning = request.get("reasoning", "YOLO mode activated! 🚀")
    
    if not all([user_id, community_id, sport, prediction]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    try:
        shared_pred = await social_service.share_prediction(
            user_id, community_id, sport, prediction, confidence, reasoning
        )
        
        return {
            "success": True,
            "message": "YOLO prediction shared successfully! 🎯",
            "prediction": {
                "prediction_id": shared_pred.prediction_id,
                "user_id": shared_pred.user_id,
                "username": shared_pred.username,
                "sport": shared_pred.sport,
                "prediction": shared_pred.prediction,
                "confidence": shared_pred.confidence,
                "reasoning": shared_pred.reasoning,
                "community_id": shared_pred.community_id,
                "likes": shared_pred.likes,
                "comments_count": len(shared_pred.comments),
                "timestamp": shared_pred.timestamp.isoformat(),
                "yolo_factor": shared_pred.yolo_factor
            },
            "timestamp": datetime.now().isoformat(),
            "mode": "yolo"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/v1/social/communities/{community_id}/predictions")
async def get_community_predictions(community_id: str):
    """Get predictions from a specific community."""
    predictions = await social_service.get_community_predictions(community_id)
    
    return {
        "success": True,
        "community_id": community_id,
        "predictions": predictions,
        "count": len(predictions),
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/social/like-prediction")
async def like_prediction(request: Dict[str, Any]):
    """Like a shared prediction."""
    prediction_id = request.get("prediction_id")
    user_id = request.get("user_id")
    
    if not prediction_id or not user_id:
        raise HTTPException(status_code=400, detail="prediction_id and user_id required")
    
    success = await social_service.like_prediction(prediction_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {
        "success": True,
        "message": "YOLO prediction liked! 🔥",
        "prediction_id": prediction_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/social/comment-prediction")
async def comment_prediction(request: Dict[str, Any]):
    """Comment on a shared prediction."""
    prediction_id = request.get("prediction_id")
    user_id = request.get("user_id")
    comment = request.get("comment")
    
    if not all([prediction_id, user_id, comment]):
        raise HTTPException(status_code=400, detail="prediction_id, user_id, and comment required")
    
    success = await social_service.comment_on_prediction(prediction_id, user_id, comment)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add comment")
    
    return {
        "success": True,
        "message": "YOLO comment added! 💬",
        "prediction_id": prediction_id,
        "user_id": user_id,
        "comment": comment,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/social/leaderboard")
async def get_leaderboard(community_id: Optional[str] = None):
    """Get YOLO leaderboard."""
    leaderboard = await social_service.get_leaderboard(community_id)
    
    return {
        "success": True,
        "leaderboard": leaderboard,
        "community_id": community_id,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/social/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile with YOLO stats."""
    profile = await social_service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "profile": profile,
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.post("/api/v1/social/users/create")
async def create_user(request: Dict[str, Any]):
    """Create a new YOLO user."""
    user_id = request.get("user_id")
    username = request.get("username")
    favorite_sport = request.get("favorite_sport", "basketball")
    
    if not user_id or not username:
        raise HTTPException(status_code=400, detail="user_id and username required")
    
    user = await social_service.create_user(user_id, username, favorite_sport)
    
    return {
        "success": True,
        "message": "YOLO user created successfully! 🎉",
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "yolo_score": user.yolo_score,
            "favorite_sport": user.favorite_sport,
            "yolo_level": user.yolo_level,
            "yolo_motto": user.yolo_motto
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/social/stats")
async def get_social_stats():
    """Get overall social statistics."""
    communities = await social_service.get_communities()
    leaderboard = await social_service.get_leaderboard()
    
    total_communities = len(communities)
    total_members = sum(c["member_count"] for c in communities)
    total_predictions = sum(c["total_predictions"] for c in communities)
    avg_success_rate = sum(c["success_rate"] for c in communities) / max(total_communities, 1)
    
    return {
        "success": True,
        "stats": {
            "total_communities": total_communities,
            "total_members": total_members,
            "total_predictions": total_predictions,
            "average_success_rate": round(avg_success_rate, 3),
            "top_yolo_user": leaderboard[0]["username"] if leaderboard else "None",
            "top_yolo_score": leaderboard[0]["yolo_score"] if leaderboard else 0,
            "yolo_energy": "MAXIMUM! 🔥"
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    }

@router.get("/api/v1/social/trending")
async def get_trending_predictions():
    """Get trending YOLO predictions."""
    # Get predictions from all communities and sort by YOLO factor
    all_predictions = []
    
    communities = await social_service.get_communities()
    for community in communities:
        predictions = await social_service.get_community_predictions(community["community_id"])
        all_predictions.extend(predictions)
    
    # Sort by YOLO factor (highest first)
    trending_predictions = sorted(all_predictions, key=lambda x: x["yolo_factor"], reverse=True)[:10]
    
    return {
        "success": True,
        "trending_predictions": trending_predictions,
        "count": len(trending_predictions),
        "timestamp": datetime.now().isoformat(),
        "mode": "yolo"
    } 