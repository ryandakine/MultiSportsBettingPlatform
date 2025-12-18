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
from src.services.parlay_tracker import parlay_tracker
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
    # Get current predictions from database (recent predictions with betting metadata)
    from src.db.database import AsyncSessionLocal
    from src.db.models.prediction import Prediction
    from sqlalchemy import select
    from datetime import datetime, timedelta
    
    # Get recent predictions (last 24 hours) with betting metadata
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prediction)
            .where(Prediction.timestamp >= cutoff)
            .order_by(Prediction.timestamp.desc())
            .limit(20)
        )
        db_predictions = result.scalars().all()
    
    # Convert to betting format
    predictions = []
    for pred in db_predictions:
        metadata = pred.metadata_json or {}
        
        # Only include predictions with betting metadata
        if not (metadata.get("game_id") and metadata.get("odds") and metadata.get("probability")):
            continue
        
        # Convert confidence string to float if needed
        confidence_value = pred.confidence
        if isinstance(confidence_value, str):
            confidence_map = {"low": 0.5, "medium": 0.65, "high": 0.85}
            confidence_value = confidence_map.get(confidence_value.lower(), 0.65)
        elif isinstance(confidence_value, (int, float)):
            confidence_value = float(confidence_value) / 100.0 if confidence_value > 1 else float(confidence_value)
        else:
            confidence_value = 0.65
        
        predictions.append({
            "game_id": metadata.get("game_id", f"game_{pred.id}"),
            "sport": pred.sport,
            "team": metadata.get("team"),
            "bet_type": metadata.get("bet_type", "moneyline"),
            "line": metadata.get("line"),
            "odds": float(metadata.get("odds", -110)),
            "confidence": float(confidence_value),
            "probability": float(metadata.get("probability", confidence_value)),
            "edge": float(metadata.get("edge", 0.05))
        })
    
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
    # Get predictions from database filtered by requested sports
    from src.db.database import AsyncSessionLocal
    from src.db.models.prediction import Prediction
    from sqlalchemy import select, or_
    from datetime import datetime, timedelta
    
    # Get recent predictions (last 24 hours) for requested sports
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Build sport filter if sports are specified
    sport_filter = None
    if request.sports:
        sport_filter = Prediction.sport.in_(request.sports)
    
    async with AsyncSessionLocal() as session:
        query = select(Prediction).where(
            Prediction.timestamp >= cutoff
        )
        if sport_filter:
            query = query.where(sport_filter)
        query = query.order_by(Prediction.timestamp.desc()).limit(50)
        
        result = await session.execute(query)
        db_predictions = result.scalars().all()
    
    # Convert to betting format
    predictions = []
    for pred in db_predictions:
        metadata = pred.metadata_json or {}
        
        # Only include predictions with betting metadata
        if not (metadata.get("game_id") and metadata.get("odds") and metadata.get("probability")):
            continue
        
        # Convert confidence string to float if needed
        confidence_value = pred.confidence
        if isinstance(confidence_value, str):
            confidence_map = {"low": 0.5, "medium": 0.65, "high": 0.85}
            confidence_value = confidence_map.get(confidence_value.lower(), 0.65)
        elif isinstance(confidence_value, (int, float)):
            confidence_value = float(confidence_value) / 100.0 if confidence_value > 1 else float(confidence_value)
        else:
            confidence_value = 0.65
        
        predictions.append({
            "game_id": metadata.get("game_id", f"game_{pred.id}"),
            "sport": pred.sport,
            "team": metadata.get("team"),
            "bet_type": metadata.get("bet_type", "moneyline"),
            "line": metadata.get("line"),
            "odds": float(metadata.get("odds", -110)),
            "confidence": float(confidence_value),
            "probability": float(metadata.get("probability", confidence_value)),
            "edge": float(metadata.get("edge", 0.05))
        })
    
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
    
    # Calculate combined odds from legs
    from src.services.parlay_builder import parlay_builder
    odds_list = [leg.get("odds", -110) for leg in request.legs]
    combined_odds = parlay_builder.calculate_combined_odds(odds_list)
    
    # Calculate combined probability
    probs = [leg.get("probability", 0.5) for leg in request.legs]
    combined_prob = parlay_builder.calculate_combined_probability(probs)
    
    # Prepare parlay data for storage
    parlay_data = {
        "legs": request.legs,
        "amount": request.amount,
        "combined_odds": combined_odds,
        "combined_probability": combined_prob,
        "sportsbook": request.sportsbook
    }
    
    # Store parlay in database
    bet_id = await parlay_tracker.place_parlay(
        user_id, parlay_data, is_autonomous=False
    )
    
    return {
        "success": True,
        "bet_id": bet_id,
        "legs": request.legs,
        "amount": request.amount,
        "sportsbook": request.sportsbook,
        "combined_odds": combined_odds,
        "message": f"Parlay bet placed successfully ({len(request.legs)} legs)"
    }


@router.get("/active")
async def get_active_parlays(current_user: dict = Depends(get_current_user)):
    """Get active parlay bets."""
    from src.services.bet_tracker import bet_tracker
    from src.db.models.bet import BetStatus, BetType
    from sqlalchemy import select, and_
    from src.db.database import AsyncSessionLocal
    
    user_id = current_user.get("user_id")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.bet_type == BetType.PARLAY,
                    Bet.status == BetStatus.PENDING
                )
            ).order_by(Bet.placed_at.desc())
        )
        parlay_bets = result.scalars().all()
        
        parlays_with_legs = []
        for bet in parlay_bets:
            legs = await parlay_tracker.get_parlay_legs(bet.id)
            parlays_with_legs.append({
                "bet_id": bet.id,
                "amount": bet.amount,
                "odds": bet.odds,
                "status": bet.status.value,
                "placed_at": bet.placed_at.isoformat() if bet.placed_at else None,
                "legs": legs
            })
    
    return {
        "active_parlays": parlays_with_legs,
        "count": len(parlays_with_legs)
    }


@router.get("/history")
async def get_parlay_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get parlay betting history."""
    user_id = current_user.get("user_id")
    
    # Query database for parlay history
    from src.db.database import AsyncSessionLocal
    from src.db.models.bet import Bet, BetStatus, BetType
    from src.db.models.parlay import ParlayCard, ParlayLeg
    from sqlalchemy import select, func, and_, or_
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    async with AsyncSessionLocal() as session:
        # Get parlay bets
        result = await session.execute(
            select(Bet)
            .where(
                and_(
                    Bet.user_id == user_id,
                    Bet.bet_type == BetType.PARLAY,
                    Bet.placed_at >= cutoff_date
                )
            )
            .order_by(Bet.placed_at.desc())
            .limit(limit)
        )
        parlay_bets = result.scalars().all()
        
        # Get parlay legs for each bet
        parlays_with_legs = []
        total_wagered = 0.0
        total_won = 0.0
        wins = 0
        losses = 0
        
        for bet in parlay_bets:
            # Get legs for this parlay
            legs_result = await session.execute(
                select(ParlayLeg)
                .where(ParlayLeg.parlay_bet_id == bet.id)
                .order_by(ParlayLeg.created_at)
            )
            legs = legs_result.scalars().all()
            
            parlays_with_legs.append({
                "id": bet.id,
                "placed_at": bet.placed_at.isoformat() if bet.placed_at else None,
                "amount": bet.amount,
                "odds": bet.odds,
                "status": bet.status.value,
                "payout": bet.payout,
                "roi": bet.roi,
                "legs": [
                    {
                        "leg_number": leg.leg_number,
                        "sport": leg.sport,
                        "team": leg.team,
                        "bet_type": leg.bet_type,
                        "line": leg.line,
                        "odds": leg.odds,
                        "status": leg.status.value if leg.status else None
                    }
                    for leg in legs
                ]
            })
            
            total_wagered += bet.amount
            if bet.status == BetStatus.WON:
                total_won += bet.payout or 0
                wins += 1
            elif bet.status == BetStatus.LOST:
                losses += 1
        
        # Calculate stats
        total_parlays = len(parlays_with_legs)
        win_rate = (wins / total_parlays * 100) if total_parlays > 0 else 0.0
        
        # Calculate average odds
        if parlay_bets:
            avg_odds = sum(bet.odds for bet in parlay_bets) / len(parlay_bets)
        else:
            avg_odds = 0
    
    return {
        "parlays": parlays_with_legs,
        "count": total_parlays,
        "stats": {
            "total_parlays": total_parlays,
            "win_rate": round(win_rate, 2),
            "average_odds": round(avg_odds, 2),
            "total_wagered": round(total_wagered, 2),
            "total_won": round(total_won, 2)
        }
    }
