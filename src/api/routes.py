"""
FastAPI routes for Head Agent functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

from src.agents.head_agent import HeadAgent, SportType, UserQuery
from src.agents.mock_sub_agent import MockSubAgent
from src.api.models import (
    BettingQuery, PredictionResponse, OutcomeReport, 
    UserPreferences, SystemStatus, HealthCheck
)
from src.config import settings

# Import authentication and preferences routes
from src.api.auth_routes import router as auth_router
from src.api.preferences_routes import router as preferences_router
from src.api.websocket_routes import router as websocket_router
from src.api.social_routes import router as social_router
from src.api.specialized_integration_routes import router as specialized_router

# Create router
router = APIRouter(prefix="/api/v1", tags=["head-agent"])

# Include all routes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(preferences_router, prefix="/preferences", tags=["User Preferences"])
router.include_router(websocket_router, tags=["WebSocket"])
router.include_router(social_router, prefix="/social", tags=["Social Features"])
router.include_router(specialized_router, tags=["Specialized Systems"])

# Global Head Agent instance
head_agent = HeadAgent()

# Initialize real sub-agents
async def initialize_sub_agents():
    """Initialize real sport-specific sub-agents."""
    from src.agents.sub_agents import BaseballAgent, BasketballAgent, FootballAgent, HockeyAgent
    
    sub_agents = [
        BaseballAgent("MLB Baseball Agent"),
        BasketballAgent("NBA/NCAAB Basketball Agent"),
        FootballAgent("NFL/NCAAF Football Agent"),
        HockeyAgent("NHL Hockey Agent")
    ]

    for agent in sub_agents:
        await head_agent.register_sub_agent(agent.sport, agent)

    print("✅ Real sub-agents initialized for production")

# Initialize agents on startup
import asyncio
try:
    asyncio.create_task(initialize_sub_agents())
except RuntimeError:
    # If no event loop is running, we'll initialize later
    pass

def get_head_agent() -> HeadAgent:
    """Dependency to get Head Agent instance."""
    return head_agent

@router.post("/predict", response_model=PredictionResponse)
async def get_predictions(
    query: BettingQuery,
    head_agent: HeadAgent = Depends(get_head_agent)
) -> PredictionResponse:
    """
    Get betting predictions from the Head Agent.
    
    This endpoint aggregates predictions from multiple sport-specific sub-agents
    and provides a combined recommendation.
    """
    try:
        # Convert API sport types to internal sport types
        sports = [SportType(sport.value) for sport in query.sports]
        
        # Create user query
        user_query = UserQuery(
            user_id=query.user_id,
            sports=sports,
            query_text=query.query_text,
            preferences=query.preferences or {},
            timestamp=datetime.now()
        )
        
        # Get aggregated predictions
        result = await head_agent.aggregate_predictions(user_query)
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/report-outcome")
async def report_outcome(
    report: OutcomeReport,
    head_agent: HeadAgent = Depends(get_head_agent)
) -> Dict[str, str]:
    """
    Report the outcome of a prediction for learning purposes.
    
    This helps improve the accuracy of future predictions by providing
    feedback on previous predictions.
    """
    try:
        await head_agent.report_outcome(
            prediction_id=report.prediction_id,
            outcome=report.outcome,
            user_id=report.user_id
        )
        
        return {
            "message": "Outcome reported successfully",
            "prediction_id": report.prediction_id,
            "outcome": report.outcome
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to report outcome: {str(e)}")

@router.post("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    head_agent: HeadAgent = Depends(get_head_agent)
) -> Dict[str, str]:
    """
    Update user preferences for personalized predictions.
    """
    try:
        await head_agent.update_user_preferences(
            user_id=preferences.user_id,
            preferences=preferences.preferences
        )
        
        return {
            "message": "Preferences updated successfully",
            "user_id": preferences.user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    head_agent: HeadAgent = Depends(get_head_agent)
) -> SystemStatus:
    """
    Get the overall system status including sub-agent health.
    """
    try:
        status = await head_agent.get_system_status()
        return SystemStatus(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/sports")
async def get_available_sports(
    head_agent: HeadAgent = Depends(get_head_agent)
) -> Dict[str, Any]:
    """
    Get list of available sports with active sub-agents.
    """
    try:
        sports = await head_agent.get_available_sports()
        return {
            "available_sports": [sport.value for sport in sports],
            "count": len(sports)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available sports: {str(e)}")

@router.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """
    Health check endpoint for the Head Agent.
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.app_version
    )

@router.get("/user/{user_id}/session")
async def get_user_session(
    user_id: str,
    head_agent: HeadAgent = Depends(get_head_agent)
) -> Dict[str, Any]:
    """
    Get user session information.
    """
    try:
        session = await head_agent.get_user_session(user_id)
        return {
            "user_id": user_id,
            "session": session
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user session: {str(e)}") 