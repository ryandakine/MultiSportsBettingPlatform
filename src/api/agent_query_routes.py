"""
Agent Query API Routes
=====================
HTTP endpoints for remote agent invocation across HeadAgent instances.
Enables cross-instance prediction requests.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from src.agents import SportType

router = APIRouter(prefix="/api/v1/agents", tags=["Agent Communication"])


class AgentQueryRequest(BaseModel):
    """Request to query a specific agent."""
    sport: str
    query_text: str
    user_id: str
    preferences: Dict[str, Any] = {}
    timestamp: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Response from agent query."""
    sport: str
    prediction: str
    confidence: str
    reasoning: str
    metadata: Dict[str, Any]
    agent_id: str
    instance_id: str


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(request: AgentQueryRequest) -> AgentQueryResponse:
    """
    Query a local agent for prediction.
    
    This endpoint is called by remote HeadAgent instances to get
    predictions from agents on this instance.
    
    Args:
        request: Agent query parameters
    
    Returns:
        Prediction from the requested agent
    """
    from src.main import head_agent_instance
    
    try:
        # Convert sport string to enum
        sport = SportType(request.sport)
        
        # Check if we have this agent locally
        if sport not in head_agent_instance._local_agent_refs:
            raise HTTPException(
                status_code=404,
                detail=f"No agent for {request.sport} on this instance"
            )
        
        # Get the agent
        agent = head_agent_instance._local_agent_refs[sport]
        
        # Check agent health
        health = await agent.get_health_status()
        if not health.get("healthy", False):
            raise HTTPException(
                status_code=503,
                detail=f"Agent for {request.sport} is unhealthy"
            )
        
        # Build query parameters
        query_params = {
            "user_id": request.user_id,
            "query_text": request.query_text,
            "preferences": request.preferences,
            "timestamp": request.timestamp or datetime.utcnow().isoformat()
        }
        
        # Get prediction
        prediction = await agent.get_prediction(query_params)
        
        # Get agent ID for this sport
        agent_id = head_agent_instance._local_agent_ids.get(sport, "unknown")
        
        # Return response
        return AgentQueryResponse(
            sport=request.sport,
            prediction=prediction.prediction if hasattr(prediction, 'prediction') else str(prediction),
            confidence=prediction.confidence.value if hasattr(prediction, 'confidence') else "medium",
            reasoning=prediction.reasoning if hasattr(prediction, 'reasoning') else "",
            metadata=prediction.metadata if hasattr(prediction, 'metadata') else {},
            agent_id=agent_id,
            instance_id=head_agent_instance.instance_id
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid sport: {request.sport}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")


@router.get("/health/{sport}")
async def check_agent_health(sport: str) -> Dict[str, Any]:
    """
    Check health of a specific agent on this instance.
    
    Args:
        sport: Sport name
    
    Returns:
        Agent health status
    """
    from src.main import head_agent_instance
    
    try:
        sport_type = SportType(sport)
        
        if sport_type not in head_agent_instance._local_agent_refs:
            raise HTTPException(
                status_code=404,
                detail=f"No agent for {sport} on this instance"
            )
        
        agent = head_agent_instance._local_agent_refs[sport_type]
        health = await agent.get_health_status()
        
        return {
            "sport": sport,
            "healthy": health.get("healthy", False),
            "details": health,
            "instance_id": head_agent_instance.instance_id
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid sport: {sport}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/available")
async def list_available_agents() -> Dict[str, Any]:
    """
    List all agents available on this instance.
    
    Returns:
        Available agents and their status
    """
    from src.main import head_agent_instance
    
    agents = []
    
    for sport, agent in head_agent_instance._local_agent_refs.items():
        try:
            health = await agent.get_health_status()
            agent_id = head_agent_instance._local_agent_ids.get(sport, "unknown")
            
            agents.append({
                "sport": sport.value,
                "agent_id": agent_id,
                "healthy": health.get("healthy", False),
                "instance_id": head_agent_instance.instance_id
            })
        except Exception as e:
            agents.append({
                "sport": sport.value,
                "healthy": False,
                "error": str(e)
            })
    
    return {
        "instance_id": head_agent_instance.instance_id,
        "agent_count": len(agents),
        "agents": agents
    }
