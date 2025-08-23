"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SportType(str, Enum):
    """Supported sports for API."""
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HOCKEY = "hockey"

class PredictionConfidence(str, Enum):
    """Prediction confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class BettingQuery(BaseModel):
    """Request model for betting predictions."""
    user_id: str = Field(..., description="Unique user identifier")
    sports: List[SportType] = Field(..., description="List of sports to analyze")
    query_text: str = Field(..., description="User's betting query or question")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "sports": ["baseball", "basketball"],
                "query_text": "What are the best bets for tonight's games?",
                "preferences": {
                    "risk_tolerance": "medium",
                    "favorite_teams": ["Lakers", "Dodgers"]
                }
            }
        }

class PredictionResponse(BaseModel):
    """Response model for predictions."""
    user_id: str
    query: str
    predictions: Dict[str, Any]
    combined_prediction: Dict[str, Any]
    timestamp: str
    sports_analyzed: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "query": "What are the best bets for tonight's games?",
                "predictions": {
                    "baseball": {
                        "prediction": "Dodgers -1.5",
                        "confidence": "high",
                        "reasoning": "Strong pitching matchup"
                    }
                },
                "combined_prediction": {
                    "recommendation": "Combined prediction based on multiple sports",
                    "confidence": "medium",
                    "reasoning": "Multiple factors considered"
                },
                "timestamp": "2025-01-27T12:00:00Z",
                "sports_analyzed": ["baseball", "basketball"]
            }
        }

class OutcomeReport(BaseModel):
    """Request model for reporting prediction outcomes."""
    prediction_id: str = Field(..., description="Unique prediction identifier")
    outcome: bool = Field(..., description="Whether the prediction was correct")
    user_id: str = Field(..., description="User who made the prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction_id": "pred_123",
                "outcome": True,
                "user_id": "user123"
            }
        }

class UserPreferences(BaseModel):
    """Request model for updating user preferences."""
    user_id: str = Field(..., description="Unique user identifier")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "preferences": {
                    "risk_tolerance": "medium",
                    "favorite_teams": ["Lakers", "Dodgers"],
                    "betting_style": "conservative"
                }
            }
        }

class SystemStatus(BaseModel):
    """Response model for system status."""
    status: str
    active_sports: int
    active_sessions: int
    prediction_history_count: int
    agent_statuses: Dict[str, Any]
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "operational",
                "active_sports": 4,
                "active_sessions": 10,
                "prediction_history_count": 150,
                "agent_statuses": {
                    "baseball": {"healthy": True},
                    "basketball": {"healthy": True}
                },
                "timestamp": "2025-01-27T12:00:00Z"
            }
        }

class HealthCheck(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-27T12:00:00Z",
                "version": "1.0.0"
            }
        } 