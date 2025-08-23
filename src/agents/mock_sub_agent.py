#!/usr/bin/env python3
"""
Mock Sub-Agent for testing Head Agent functionality.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

from src.agents.head_agent import SubAgentInterface, Prediction, SportType, PredictionConfidence

logger = logging.getLogger(__name__)

class MockSubAgent(SubAgentInterface):
    """Mock sub-agent for testing purposes."""
    
    def __init__(self, sport: SportType, name: str = None):
        self.sport = sport
        self.name = name or f"Mock {sport.value.title()} Agent"
        self.healthy = True
        self.prediction_count = 0
        
        logger.info(f"Initialized {self.name}")
    
    async def get_prediction(self, query_params: dict) -> Prediction:
        """Generate a mock prediction."""
        self.prediction_count += 1
        
        # Mock prediction logic based on sport
        predictions = {
            SportType.BASEBALL: [
                "Dodgers -1.5 (Strong pitching matchup)",
                "Over 8.5 runs (High-scoring teams)",
                "Yankees ML (Home field advantage)"
            ],
            SportType.BASKETBALL: [
                "Lakers -3.5 (Star player returning)",
                "Under 220.5 (Defensive matchup)",
                "Warriors +2.5 (Road underdog value)"
            ],
            SportType.FOOTBALL: [
                "Chiefs -7.5 (Offensive firepower)",
                "Under 45.5 (Weather conditions)",
                "Bills +3.5 (Defensive strength)"
            ],
            SportType.HOCKEY: [
                "Bruins ML (Home ice advantage)",
                "Over 5.5 goals (High-scoring teams)",
                "Lightning -1.5 (Power play efficiency)"
            ]
        }
        
        # Select prediction based on sport
        sport_predictions = predictions.get(self.sport, ["Mock prediction"])
        prediction_text = sport_predictions[self.prediction_count % len(sport_predictions)]
        
        # Generate confidence based on prediction count (simulate learning)
        confidence_levels = [PredictionConfidence.LOW, PredictionConfidence.MEDIUM, PredictionConfidence.HIGH]
        confidence = confidence_levels[self.prediction_count % 3]
        
        # Generate reasoning
        reasoning = f"Mock analysis for {self.sport.value}: {prediction_text}. This is prediction #{self.prediction_count}."
        
        return Prediction(
            sport=self.sport,
            prediction=prediction_text,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now(),
            metadata={
                "agent_name": self.name,
                "prediction_id": str(uuid.uuid4()),
                "mock_data": True
            }
        )
    
    async def report_outcome(self, prediction_id: str, outcome: bool) -> None:
        """Report prediction outcome (mock implementation)."""
        logger.info(f"{self.name} received outcome report: {prediction_id} = {outcome}")
        # In a real implementation, this would update the agent's learning model
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "healthy": self.healthy,
            "agent_name": self.name,
            "sport": self.sport.value,
            "prediction_count": self.prediction_count,
            "last_activity": datetime.now().isoformat()
        }
    
    def set_health_status(self, healthy: bool) -> None:
        """Set agent health status (for testing)."""
        self.healthy = healthy
        logger.info(f"{self.name} health status set to: {healthy}") 