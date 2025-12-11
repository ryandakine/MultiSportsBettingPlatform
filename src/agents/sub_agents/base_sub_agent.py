#!/usr/bin/env python3
"""
Base Sub-Agent for MultiSportsBettingPlatform
=============================================
Abstract base class that all sport-specific agents inherit from.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from src.services.real_sports_service import real_sports_service

from src.agents.head_agent import SubAgentInterface, Prediction, SportType, PredictionConfidence
from src.services.claude_service import ClaudeService
from src.services.perplexity_service import PerplexityService

logger = logging.getLogger(__name__)

class BaseSubAgent(SubAgentInterface, ABC):
    """Base class for all sport-specific sub-agents."""
    
    def __init__(self, sport: SportType, name: str = None):
        self.sport = sport
        self.name = name or f"{sport.value.title()} Agent"
        self.healthy = True
        self.prediction_count = 0
        self.accuracy_history: List[bool] = []
        self.last_activity = datetime.now()
        
        # Initialize AI services
        self.claude_service = ClaudeService()
        self.perplexity_service = PerplexityService()
        self.use_claude = self.claude_service.enabled
        self.use_perplexity = self.perplexity_service.enabled
        
        logger.info(f"Initialized {self.name} (Claude AI: {'Enabled' if self.use_claude else 'Disabled'}, Perplexity Pro: {'Enabled' if self.use_perplexity else 'Disabled'})")
    
    @abstractmethod
    async def analyze_sport_data(self, query_params: dict) -> Dict[str, Any]:
        """Analyze sport-specific data and return insights."""
        pass
    
    @abstractmethod
    async def get_sport_specific_prediction(self, analysis: Dict[str, Any]) -> str:
        """Generate sport-specific prediction based on analysis."""
        pass
    
    @abstractmethod
    async def calculate_confidence(self, analysis: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level based on analysis."""
        pass
    
    @abstractmethod
    async def generate_reasoning(self, analysis: Dict[str, Any], prediction: str) -> str:
        """Generate reasoning for the prediction."""
        pass
    
    async def find_betting_opportunities(self) -> List[Dict[str, Any]]:
        """Find potential betting opportunities (upcoming games) using Real Sports Data."""
        try:
            # Fetch real live games from ESPN via our service
            games = await real_sports_service.get_live_games(self.sport.value)
            
            opportunities = []
            for game in games:
                # Convert to betting opportunity format
                opp = {
                    "game_id": game['id'],
                    "sport": game['sport'],
                    "matchup": f"{game['away_team']} @ {game['home_team']}",
                    "start_time": game['date'],
                    "status": game['status'],
                    "home_team": game['home_team'],
                    "away_team": game['away_team'],
                    "details": game
                }
                opportunities.append(opp)
                
            return opportunities
        except Exception as e:
            logger.error(f"Error finding betting opportunities for {self.sport.value}: {e}")
            return []
    
    async def get_prediction(self, query_params: dict) -> Prediction:
        """Get prediction from sub-agent (implements SubAgentInterface)."""
        try:
            self.last_activity = datetime.now()
            self.prediction_count += 1
            
            # Analyze sport-specific data
            analysis = await self.analyze_sport_data(query_params)
            
            # Get Perplexity Pro AI research insights if available
            research_insights = {}
            if self.use_perplexity:
                try:
                    # Extract teams from analysis for research
                    teams = analysis.get("teams_analyzed", [])
                    if teams:
                        research_insights = await self.perplexity_service.get_research_insights(
                            sport=self.sport.value,
                            teams=teams,
                            query=query_params.get("query_text", ""),
                            include_recent_data=True
                        )
                        logger.info(f"{self.name} used Perplexity Pro AI for research insights")
                except Exception as perplexity_error:
                    logger.warning(f"Perplexity Pro AI failed: {perplexity_error}")
            
            # Try to get enhanced prediction from Claude AI
            if self.use_claude:
                try:
                    # Combine analysis with research insights for Claude
                    enhanced_analysis = analysis.copy()
                    if research_insights:
                        enhanced_analysis["perplexity_research"] = research_insights
                    
                    claude_result = await self.claude_service.get_enhanced_prediction(
                        sport=self.sport.value,
                        analysis=enhanced_analysis,
                        query_text=query_params.get("query_text", ""),
                        context=f"Agent: {self.name}, Prediction Count: {self.prediction_count}, Research: {'Available' if research_insights else 'None'}"
                    )
                    
                    # Use Claude's prediction if available
                    if claude_result.get("prediction") and claude_result["prediction"] != "Claude AI not available":
                        prediction_text = claude_result["prediction"]
                        reasoning = claude_result.get("reasoning", "")
                        confidence_str = claude_result.get("confidence", "medium").lower()
                        
                        # Convert confidence string to enum
                        if confidence_str == "high":
                            confidence = PredictionConfidence.HIGH
                        elif confidence_str == "low":
                            confidence = PredictionConfidence.LOW
                        else:
                            confidence = PredictionConfidence.MEDIUM
                        
                        logger.info(f"{self.name} used Claude AI for enhanced prediction")
                    else:
                        # Fallback to traditional prediction
                        prediction_text = await self.get_sport_specific_prediction(analysis)
                        confidence = await self.calculate_confidence(analysis)
                        reasoning = await self.generate_reasoning(analysis, prediction_text)
                        logger.info(f"{self.name} used traditional prediction (Claude fallback)")
                        
                except Exception as claude_error:
                    logger.warning(f"Claude AI failed, using traditional prediction: {claude_error}")
                    prediction_text = await self.get_sport_specific_prediction(analysis)
                    confidence = await self.calculate_confidence(analysis)
                    reasoning = await self.generate_reasoning(analysis, prediction_text)
            else:
                # Use traditional prediction method
                prediction_text = await self.get_sport_specific_prediction(analysis)
                confidence = await self.calculate_confidence(analysis)
                reasoning = await self.generate_reasoning(analysis, prediction_text)
            
            # Create prediction object
            prediction = Prediction(
                sport=self.sport,
                prediction=prediction_text,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now(),
                                    metadata={
                        "agent_name": self.name,
                        "prediction_id": str(uuid.uuid4()),
                        "analysis": analysis,
                        "prediction_count": self.prediction_count,
                        "claude_enhanced": self.use_claude and "Claude AI" in reasoning,
                        "perplexity_research": bool(research_insights),
                        "ai_services": {
                            "claude": self.use_claude,
                            "perplexity": self.use_perplexity
                        }
                    }
            )
            
            logger.info(f"{self.name} generated prediction: {prediction_text}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error in {self.name} prediction: {e}")
            # Return a fallback prediction
            return Prediction(
                sport=self.sport,
                prediction="Unable to generate prediction",
                confidence=PredictionConfidence.LOW,
                reasoning=f"Error occurred: {str(e)}",
                timestamp=datetime.now(),
                metadata={
                    "agent_name": self.name,
                    "prediction_id": str(uuid.uuid4()),
                    "error": str(e)
                }
            )
    
    async def report_outcome(self, prediction_id: str, outcome: bool) -> None:
        """Report prediction outcome for learning (implements SubAgentInterface)."""
        self.accuracy_history.append(outcome)
        
        # Keep only last 100 outcomes for memory management
        if len(self.accuracy_history) > 100:
            self.accuracy_history = self.accuracy_history[-100:]
        
        logger.info(f"{self.name} received outcome: {prediction_id} = {outcome}")
        
        # Update learning model (to be implemented by subclasses)
        await self.update_learning_model(outcome)
    
    async def update_learning_model(self, outcome: bool) -> None:
        """Update the agent's learning model based on outcome."""
        # Base implementation - subclasses can override
        logger.info(f"{self.name} learning model updated with outcome: {outcome}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get sub-agent health status (implements SubAgentInterface)."""
        # Calculate accuracy from recent history
        recent_accuracy = 0.0
        if self.accuracy_history:
            recent_accuracy = sum(self.accuracy_history[-10:]) / min(len(self.accuracy_history), 10)
        
        # Test AI service connections if enabled
        claude_status = "disabled"
        if self.use_claude:
            try:
                claude_connected = await self.claude_service.test_connection()
                claude_status = "connected" if claude_connected else "error"
            except Exception as e:
                claude_status = f"error: {str(e)}"
        
        perplexity_status = "disabled"
        if self.use_perplexity:
            try:
                perplexity_connected = await self.perplexity_service.test_connection()
                perplexity_status = "connected" if perplexity_connected else "error"
            except Exception as e:
                perplexity_status = f"error: {str(e)}"
        
        return {
            "healthy": self.healthy,
            "agent_name": self.name,
            "sport": self.sport.value,
            "prediction_count": self.prediction_count,
            "recent_accuracy": recent_accuracy,
            "total_accuracy": sum(self.accuracy_history) / len(self.accuracy_history) if self.accuracy_history else 0.0,
            "last_activity": self.last_activity.isoformat(),
            "uptime": (datetime.now() - self.last_activity).total_seconds(),
            "claude_ai": {
                "enabled": self.use_claude,
                "status": claude_status
            },
            "perplexity_pro": {
                "enabled": self.use_perplexity,
                "status": perplexity_status
            }
        }
    
    def set_health_status(self, healthy: bool) -> None:
        """Set agent health status (for testing)."""
        self.healthy = healthy
        logger.info(f"{self.name} health status set to: {healthy}")
    
    async def get_sport_specific_insights(self) -> Dict[str, Any]:
        """Get sport-specific insights and statistics."""
        # Base implementation - subclasses can override
        ai_capabilities = []
        if self.use_claude:
            ai_capabilities.append("Claude AI predictions")
        if self.use_perplexity:
            ai_capabilities.append("Perplexity Pro research")
        
        ai_capabilities_str = " + ".join(ai_capabilities) if ai_capabilities else "Traditional statistical analysis"
        
        return {
            "sport": self.sport.value,
            "agent_name": self.name,
            "prediction_count": self.prediction_count,
            "recent_accuracy": sum(self.accuracy_history[-10:]) / min(len(self.accuracy_history), 10) if self.accuracy_history else 0.0,
            "claude_ai_enhanced": self.use_claude,
            "perplexity_pro_enhanced": self.use_perplexity,
            "ai_capabilities": ai_capabilities_str
        } 