"""
Betting Control API Routes
===========================
Control autonomous betting and view performance.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.services.autonomous_betting_engine import autonomous_engine
from src.services.bet_tracker import bet_tracker
from src.services.bet_settlement_service import bet_settlement_service
from src.api.auth_routes import get_current_user

router = APIRouter(prefix="/api/v1/betting", tags=["Autonomous Betting"])


class StartBettingRequest(BaseModel):
    """Request to start autonomous betting."""
    paper_trading: bool = True
    max_bet_percentage: Optional[float] = 0.05
    min_edge: Optional[float] = 0.05
    enable_parlays: Optional[bool] = True


@router.post("/start")
async def start_autonomous_betting(
    request: StartBettingRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start autonomous betting.
    
    ⚠️ This will automatically place bets based on AI predictions.
    """
    user_id = current_user.get("user_id")
    
    # Update engine settings
    autonomous_engine.paper_trading = request.paper_trading
    autonomous_engine.max_bet_percentage = request.max_bet_percentage
    autonomous_engine.min_edge_threshold = request.min_edge
    autonomous_engine.enable_parlays = request.enable_parlays
    
    # Start engine
    await autonomous_engine.start(user_id)
    
    return {
        "success": True,
        "status": "running",
        "mode": "paper_trading" if request.paper_trading else "live",
        "message": "Autonomous betting started",
        "settings": {
            "max_bet_percentage": request.max_bet_percentage,
            "min_edge": request.min_edge,
            "enable_parlays": request.enable_parlays
        }
    }


@router.post("/stop")
async def stop_autonomous_betting(current_user: dict = Depends(get_current_user)):
    """Stop autonomous betting."""
    await autonomous_engine.stop()
    
    return {
        "success": True,
        "status": "stopped",
        "message": "Autonomous betting stopped"
    }


@router.get("/status")
async def get_betting_status(current_user: dict = Depends(get_current_user)):
    """Get current autonomous betting status."""
    return {
        "enabled": autonomous_engine.enabled,
        "running": autonomous_engine.running,
        "mode": "paper_trading" if autonomous_engine.paper_trading else "live",
        "settings": {
            "min_edge": autonomous_engine.min_edge_threshold,
            "max_bet_percentage": autonomous_engine.max_bet_percentage,
            "kelly_multiplier": autonomous_engine.kelly_multiplier,
            "enable_parlays": autonomous_engine.enable_parlays
        }
    }


@router.get("/status/public")
async def get_betting_status_public():
    """Get current autonomous betting status (public endpoint, no auth required)."""
    return {
        "enabled": autonomous_engine.enabled,
        "running": autonomous_engine.running,
        "mode": "paper_trading" if autonomous_engine.paper_trading else "live",
        "settings": {
            "min_edge": autonomous_engine.min_edge_threshold,
            "max_bet_percentage": autonomous_engine.max_bet_percentage,
            "kelly_multiplier": autonomous_engine.kelly_multiplier,
            "enable_parlays": autonomous_engine.enable_parlays
        }
    }


@router.get("/performance")
async def get_performance(
    days: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get betting performance metrics.
    
    Args:
        days: Optional days to look back (None = all time)
    """
    user_id = current_user.get("user_id")
    
    # Get ROI metrics
    roi_metrics = await bet_tracker.calculate_roi(user_id, days)
    
    # Get bankroll status
    bankroll = await bet_tracker.get_bankroll(user_id)
    
    # Get active bets
    active_bets = await bet_tracker.get_active_bets(user_id)
    
    return {
        "roi_metrics": roi_metrics,
        "bankroll": bankroll,
        "active_bets": {
            "count": len(active_bets),
            "bets": active_bets
        },
        "period": f"{days} days" if days else "all time"
    }


@router.get("/history")
async def get_bet_history(
    limit: int = 50,
    sport: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get betting history."""
    user_id = current_user.get("user_id")
    
    history = await bet_tracker.get_bet_history(user_id, limit, sport)
    
    return {
        "bets": history,
        "count": len(history)
    }


@router.get("/roi")
async def get_roi_dashboard(current_user: dict = Depends(get_current_user)):
    """
    Get comprehensive ROI dashboard.
    
    Returns all-time, monthly, weekly, and daily ROI.
    """
    user_id = current_user.get("user_id")
    
    all_time = await bet_tracker.calculate_roi(user_id)
    monthly = await bet_tracker.calculate_roi(user_id, 30)
    weekly = await bet_tracker.calculate_roi(user_id, 7)
    daily = await bet_tracker.calculate_roi(user_id, 1)
    
    return {
        "all_time": all_time,
        "monthly": monthly,
        "weekly": weekly,
        "daily": daily
    }


@router.post("/settle")
async def settle_pending_bets(
    days_back: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Settle all pending bets from the last N days.
    
    This endpoint:
    1. Finds all pending bets
    2. Fetches game results from sports APIs
    3. Matches bets to games
    4. Updates bet status (won/lost/pushed)
    5. Calculates payouts
    
    Args:
        days_back: Number of days to look back (default: 7)
    """
    try:
        result = await bet_settlement_service.settle_pending_bets(days_back=days_back)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to settle bets: {str(e)}")
