"""
Parlay API Routes
=================
Endpoints for parlay betting recommendations and placement.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.services.parlay_builder import parlay_builder
from src.api.auth_routes import get_current_user

router = APIRouter(prefix="/api/v1/parlays", tags=["Parlays"])


class ParlayRequest(BaseModel):
    """Request to build parlay recommendations."""
    risk_level: Optional[str] = "moderate"  # conservative, moderate, aggressive
    num_legs: Optional[int] = None
    sports: Optional[List[str]] = None  # Filter by sports


class PlaceParlayRequest(BaseModel):
    """Request to place a parlay bet."""
    legs: List[Dict[str, Any]]
    amount: float
    sportsbook: str = "draftkings"


@router.get("/recommendations")
async def get_parlay_recommendations(
    risk_level: Optional[str] = "moderate",
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated parlay recommendations.
    
    Returns parlays at different risk levels based on current predictions.
    """
    # TODO: Get current predictions from head_agent
    # For now, return mock data
    
    predictions = [
        {
            "game_id": "game_1",
            "sport": "basketball",
            "team": "Lakers",
            "bet_type": "moneyline",
            "odds": -150,
            "confidence": 0.75,
            "probability": 0.60,
            "edge": 0.10
        },
        {
            "game_id": "game_2",
            "sport": "football",
            "team": "Chiefs",
            "bet_type": "spread",
            "line": -7.5,
            "odds": -110,
            "confidence": 0.70,
            "probability": 0.55,
            "edge": 0.08
        },
        {
            "game_id": "game_3",
            "sport": "basketball",
            "team": "Over",
            "bet_type": "total",
            "line": 220.5,
            "odds": -105,
            "confidence": 0.68,
            "probability": 0.52,
            "edge": 0.05
        }
    ]
    
    # Build parlay recommendations
    if risk_level == "all":
        parlays = parlay_builder.build_multiple_parlays(predictions)
    else:
        parlay = parlay_builder.build_parlay(predictions, risk_level)
        parlays = [parlay] if parlay else []
    
    return {
        "count": len(parlays),
        "parlays": parlays,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/build")
async def build_custom_parlay(
    request: ParlayRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Build a custom parlay with specific parameters.
    """
    # TODO: Get filtered predictions based on sports
    predictions = []  # Placeholder
    
    parlay = parlay_builder.build_parlay(
        predictions,
        risk_level=request.risk_level,
        num_legs=request.num_legs
    )
    
    if not parlay:
        raise HTTPException(
            status_code=404,
            detail="Not enough eligible predictions to build parlay"
        )
    
    return parlay


@router.post("/validate")
async def validate_parlay(
    legs: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """
    Validate a parlay before placement.
    
    Checks for conflicts, same-game parlays, and other issues.
    """
    validation = parlay_builder.validate_parlay(legs)
    
    return validation


@router.post("/place")
async def place_parlay(
    request: PlaceParlayRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Place a parlay bet.
    
    This will:
    1. Validate the parlay
    2. Check betting limits
    3. Place bet via sportsbook API
    4. Track in database
    """
    user_id = current_user.get("user_id")
    
    # Validate parlay
    validation = parlay_builder.validate_parlay(request.legs)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parlay: {validation['issues']}"
        )
    
    # TODO: Check user bankroll and limits
    # TODO: Place bet via sportsbook API
    # TODO: Save to database
    
    # Mock response
    bet_id = "bet_parlay_123"
    
    return {
        "success": True,
        "bet_id": bet_id,
        "legs": request.legs,
        "amount": request.amount,
        "sportsbook": request.sportsbook,
        "message": f"Parlay bet placed successfully ({len(request.legs)} legs)"
    }


@router.get("/active")
async def get_active_parlays(current_user: dict = Depends(get_current_user)):
    """Get active parlay bets."""
    user_id = current_user.get("user_id")
    
    # TODO: Query database for active parlays
    
    return {
        "active_parlays": [],
        "count": 0
    }


@router.get("/history")
async def get_parlay_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get parlay betting history."""
    user_id = current_user.get("user_id")
    
    # TODO: Query database for parlay history
    
    return {
        "parlays": [],
        "count": 0,
        "stats": {
            "total_parlays": 0,
            "win_rate": 0.0,
            "average_odds": 0,
            "total_wagered": 0.0,
            "total_won": 0.0
        }
    }
