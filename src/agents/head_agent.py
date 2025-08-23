#!/usr/bin/env python3
"""
Head Agent for MultiSportsBettingPlatform
=========================================
Central coordinator that manages user interactions, aggregates picks from sub-agents,
and handles global learning across all sports.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Protocol, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json

from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportType(Enum):
    """Supported sports."""
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HOCKEY = "hockey"

class PredictionConfidence(Enum):
    """Prediction confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Prediction:
    """Prediction data structure."""
    sport: SportType
    prediction: str
    confidence: PredictionConfidence
    reasoning: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class UserQuery:
    """User query data structure."""
    user_id: str
    sports: List[SportType]
    query_text: str
    preferences: Dict[str, Any]
    timestamp: datetime

class SubAgentInterface(Protocol):
    """Protocol for sub-agent interface."""
    
    async def get_prediction(self, query_params: dict) -> Prediction:
        """Get prediction from sub-agent."""
        ...
    
    async def report_outcome(self, prediction_id: str, outcome: bool) -> None:
        """Report prediction outcome for learning."""
        ...
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get sub-agent health status."""
        ...

class HeadAgent:
    """Head Agent - Central coordinator for multi-sport betting predictions."""
    
    def __init__(self):
        self.sub_agents: Dict[SportType, SubAgentInterface] = {}
        self.global_model = None
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.prediction_history: List[Prediction] = []
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Head Agent initialized")
    
    async def register_sub_agent(self, sport: SportType, agent: SubAgentInterface) -> None:
        """Register a sub-agent for a specific sport."""
        self.sub_agents[sport] = agent
        logger.info(f"Registered sub-agent for {sport.value}")
    
    async def unregister_sub_agent(self, sport: SportType) -> None:
        """Unregister a sub-agent."""
        if sport in self.sub_agents:
            del self.sub_agents[sport]
            logger.info(f"Unregistered sub-agent for {sport.value}")
    
    async def get_available_sports(self) -> List[SportType]:
        """Get list of available sports with active sub-agents."""
        return list(self.sub_agents.keys())
    
    async def aggregate_predictions(self, user_query: UserQuery) -> Dict[str, Any]:
        """Aggregate predictions from relevant sub-agents."""
        logger.info(f"Aggregating predictions for user {user_query.user_id}")
        
        predictions = {}
        relevant_sports = []
        
        # Determine which sports are relevant to the query
        for sport in user_query.sports:
            if sport in self.sub_agents:
                relevant_sports.append(sport)
            else:
                logger.warning(f"No sub-agent available for {sport.value}")
        
        if not relevant_sports:
            return {
                "error": "No relevant sub-agents available",
                "available_sports": await self.get_available_sports()
            }
        
        # Collect predictions from relevant sub-agents
        for sport in relevant_sports:
            try:
                agent = self.sub_agents[sport]
                
                # Check agent health
                health = await agent.get_health_status()
                if not health.get("healthy", False):
                    logger.warning(f"Sub-agent for {sport.value} is unhealthy: {health}")
                    continue
                
                # Get prediction
                query_params = {
                    "user_id": user_query.user_id,
                    "query_text": user_query.query_text,
                    "preferences": user_query.preferences,
                    "timestamp": user_query.timestamp.isoformat()
                }
                
                prediction = await agent.get_prediction(query_params)
                predictions[sport.value] = prediction
                
                # Store in history
                self.prediction_history.append(prediction)
                
            except Exception as e:
                logger.error(f"Error getting prediction from {sport.value} agent: {e}")
                predictions[sport.value] = {
                    "error": f"Failed to get prediction: {str(e)}"
                }
        
        # Combine predictions using weighting algorithm
        combined_prediction = await self._combine_predictions(predictions, user_query)
        
        return {
            "user_id": user_query.user_id,
            "query": user_query.query_text,
            "predictions": predictions,
            "combined_prediction": combined_prediction,
            "timestamp": datetime.now().isoformat(),
            "sports_analyzed": [s.value for s in relevant_sports]
        }
    
    async def _combine_predictions(self, predictions: Dict[str, Any], user_query: UserQuery) -> Dict[str, Any]:
        """Combine predictions using intelligent weighting."""
        if not predictions:
            return {"error": "No predictions to combine"}
        
        # Simple weighting based on confidence levels
        confidence_weights = {
            PredictionConfidence.HIGH: 0.5,
            PredictionConfidence.MEDIUM: 0.3,
            PredictionConfidence.LOW: 0.2
        }
        
        weighted_predictions = []
        total_weight = 0
        
        for sport, prediction in predictions.items():
            if isinstance(prediction, Prediction):
                weight = confidence_weights.get(prediction.confidence, 0.2)
                weighted_predictions.append({
                    "sport": sport,
                    "prediction": prediction.prediction,
                    "confidence": prediction.confidence.value,
                    "weight": weight,
                    "reasoning": prediction.reasoning
                })
                total_weight += weight
        
        if not weighted_predictions:
            return {"error": "No valid predictions to combine"}
        
        # Calculate weighted average (simplified)
        combined_reasoning = " | ".join([wp["reasoning"] for wp in weighted_predictions])
        
        return {
            "recommendation": "Combined prediction based on multiple sports",
            "confidence": "medium",  # Could be calculated based on individual confidences
            "reasoning": combined_reasoning,
            "sports_contributing": len(weighted_predictions),
            "total_weight": total_weight,
            "individual_predictions": weighted_predictions
        }
    
    async def report_outcome(self, prediction_id: str, outcome: bool, user_id: str) -> None:
        """Report prediction outcome for learning."""
        logger.info(f"Reporting outcome for prediction {prediction_id}: {outcome}")
        
        # Find the prediction in history
        for prediction in self.prediction_history:
            if hasattr(prediction, 'id') and prediction.id == prediction_id:
                # Report to relevant sub-agent
                if prediction.sport in self.sub_agents:
                    try:
                        await self.sub_agents[prediction.sport].report_outcome(prediction_id, outcome)
                    except Exception as e:
                        logger.error(f"Error reporting outcome to {prediction.sport.value} agent: {e}")
                break
        
        # Update global learning model (placeholder)
        await self._update_global_model(prediction_id, outcome, user_id)
    
    async def _update_global_model(self, prediction_id: str, outcome: bool, user_id: str) -> None:
        """Update global learning model (placeholder for future implementation)."""
        # TODO: Implement global learning across sports
        logger.info(f"Global model update: prediction {prediction_id} outcome {outcome}")
    
    async def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get user session information."""
        return self.active_sessions.get(user_id, {})
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        self.user_preferences[user_id] = preferences
        logger.info(f"Updated preferences for user {user_id}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = {}
        
        for sport, agent in self.sub_agents.items():
            try:
                health = await agent.get_health_status()
                agent_statuses[sport.value] = health
            except Exception as e:
                agent_statuses[sport.value] = {"error": str(e)}
        
        return {
            "status": "operational",
            "active_sports": len(self.sub_agents),
            "active_sessions": len(self.active_sessions),
            "prediction_history_count": len(self.prediction_history),
            "agent_statuses": agent_statuses,
            "timestamp": datetime.now().isoformat()
        } 