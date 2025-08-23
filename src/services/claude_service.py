#!/usr/bin/env python3
"""
Claude AI Service for MultiSportsBettingPlatform
===============================================
Service for integrating Claude AI into sub-agents for enhanced predictions.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
import httpx

from src.config import settings

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for interacting with Claude AI API."""
    
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-sonnet-20240229"
        
        if not self.api_key:
            logger.warning("Claude API key not configured. Claude features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Claude AI service initialized")
    
    async def get_enhanced_prediction(
        self, 
        sport: str, 
        analysis: Dict[str, Any], 
        query_text: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Get enhanced prediction from Claude AI."""
        if not self.enabled:
            return {
                "prediction": "Claude AI not available",
                "reasoning": "Claude AI service is disabled due to missing API key",
                "confidence": "low"
            }
        
        try:
            # Prepare the prompt for Claude
            prompt = self._build_prediction_prompt(sport, analysis, query_text, context)
            
            # Call Claude API
            response = await self._call_claude_api(prompt)
            
            # Parse Claude's response
            return self._parse_claude_response(response)
            
        except Exception as e:
            logger.error(f"Error getting Claude prediction: {e}")
            return {
                "prediction": "Error getting Claude prediction",
                "reasoning": f"Claude AI error: {str(e)}",
                "confidence": "low"
            }
    
    def _build_prediction_prompt(
        self, 
        sport: str, 
        analysis: Dict[str, Any], 
        query_text: str,
        context: str
    ) -> str:
        """Build a comprehensive prompt for Claude AI."""
        
        # Sport-specific instructions
        sport_instructions = {
            "baseball": """
            You are an expert MLB betting analyst. Consider:
            - Pitching matchups and ERA comparisons
            - Team offensive and defensive statistics
            - Weather conditions and ballpark factors
            - Recent form and head-to-head history
            - Bullpen strength and late-game scenarios
            """,
            "basketball": """
            You are an expert NBA/NCAAB betting analyst. Consider:
            - Team offensive and defensive efficiency
            - Player matchups and star power
            - Pace of play and tempo factors
            - Home/away performance differences
            - Recent form and injury impacts
            """,
            "football": """
            You are an expert NFL/NCAAF betting analyst. Consider:
            - Team offensive and defensive statistics
            - Weather conditions and field impact
            - Home field advantage and crowd factors
            - Quarterback and key player performance
            - Recent form and head-to-head history
            """,
            "hockey": """
            You are an expert NHL betting analyst. Consider:
            - Team offensive and defensive statistics
            - Goalie matchups and save percentages
            - Special teams (power play, penalty kill)
            - Home ice advantage and crowd factors
            - Recent form and head-to-head history
            """
        }
        
        # Build the analysis summary
        analysis_summary = self._format_analysis_for_claude(analysis)
        
        prompt = f"""
        {sport_instructions.get(sport.lower(), "You are an expert sports betting analyst.")}
        
        USER QUERY: {query_text}
        
        SPORT: {sport.upper()}
        
        ANALYSIS DATA:
        {analysis_summary}
        
        {f"ADDITIONAL CONTEXT: {context}" if context else ""}
        
        TASK: Based on the provided analysis data, generate a betting prediction and detailed reasoning.
        
        REQUIREMENTS:
        1. Provide a specific betting recommendation (e.g., "Team A -3.5", "Over 220.5 points")
        2. Give detailed reasoning explaining your prediction
        3. Assess confidence level (high/medium/low) with explanation
        4. Consider all relevant factors from the analysis
        5. Be specific about why this bet has value
        
        RESPONSE FORMAT (JSON):
        {{
            "prediction": "specific betting recommendation",
            "reasoning": "detailed explanation of the prediction",
            "confidence": "high/medium/low",
            "confidence_explanation": "why this confidence level",
            "key_factors": ["factor1", "factor2", "factor3"],
            "risk_assessment": "brief risk assessment"
        }}
        
        Provide only the JSON response, no additional text.
        """
        
        return prompt
    
    def _format_analysis_for_claude(self, analysis: Dict[str, Any]) -> str:
        """Format analysis data for Claude AI consumption."""
        formatted = []
        
        # Teams analyzed
        if "teams_analyzed" in analysis:
            formatted.append(f"Teams: {', '.join(analysis['teams_analyzed'])}")
        
        # Offensive analysis
        if "offensive_analysis" in analysis:
            off = analysis["offensive_analysis"]
            if "offensive_advantage" in off:
                formatted.append(f"Offensive Advantage: {off['offensive_advantage']}")
            if "total_points_expected" in off:
                formatted.append(f"Expected Total: {off['total_points_expected']:.1f}")
        
        # Defensive analysis
        if "defensive_analysis" in analysis:
            def_analysis = analysis["defensive_analysis"]
            if "defensive_advantage" in def_analysis:
                formatted.append(f"Defensive Advantage: {def_analysis['defensive_advantage']}")
        
        # Historical data
        if "historical_data" in analysis:
            hist = analysis["historical_data"]
            if "recent_form" in hist:
                recent = hist["recent_form"]
                formatted.append(f"Recent Form: Team1 {recent.get('team1_last_10', 'N/A')}-{10-recent.get('team1_last_10', 5)} last 10, Team2 {recent.get('team2_last_10', 'N/A')}-{10-recent.get('team2_last_10', 5)} last 10")
        
        # Weather factors (if applicable)
        if "weather_analysis" in analysis:
            weather = analysis["weather_analysis"]
            formatted.append(f"Weather: {weather.get('temperature', 'N/A')}°C, Wind: {weather.get('wind_speed', 'N/A')} mph, Conditions: {weather.get('precipitation', 'N/A')}")
        
        # Key metrics
        if "key_metrics" in analysis:
            metrics = analysis["key_metrics"]
            for key, value in metrics.items():
                if isinstance(value, float):
                    formatted.append(f"{key.replace('_', ' ').title()}: {value:.3f}")
                else:
                    formatted.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted)
    
    async def _call_claude_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to Claude."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")
    
    def _parse_claude_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response into structured format."""
        try:
            # Extract the content from Claude's response
            content = response.get("content", [{}])[0].get("text", "")
            
            # Try to parse as JSON
            if content.strip().startswith("{"):
                return json.loads(content)
            else:
                # Fallback parsing if not JSON
                return {
                    "prediction": "Claude response parsing failed",
                    "reasoning": content[:200] + "..." if len(content) > 200 else content,
                    "confidence": "medium"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return {
                "prediction": "JSON parsing failed",
                "reasoning": "Unable to parse Claude's response",
                "confidence": "low"
            }
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return {
                "prediction": "Response parsing error",
                "reasoning": f"Error: {str(e)}",
                "confidence": "low"
            }
    
    async def get_enhanced_reasoning(
        self, 
        sport: str, 
        analysis: Dict[str, Any], 
        prediction: str
    ) -> str:
        """Get enhanced reasoning from Claude AI."""
        if not self.enabled:
            return "Claude AI reasoning not available"
        
        try:
            prompt = f"""
            You are an expert {sport} betting analyst. Given this prediction:
            "{prediction}"
            
            And this analysis data:
            {self._format_analysis_for_claude(analysis)}
            
            Provide a detailed, professional explanation of why this prediction makes sense.
            Focus on the key factors that support this bet and any risks to consider.
            Keep it concise but comprehensive (2-3 paragraphs).
            """
            
            response = await self._call_claude_api(prompt)
            content = response.get("content", [{}])[0].get("text", "")
            
            return content if content else "Unable to generate enhanced reasoning"
            
        except Exception as e:
            logger.error(f"Error getting enhanced reasoning: {e}")
            return f"Error generating enhanced reasoning: {str(e)}"
    
    async def test_connection(self) -> bool:
        """Test Claude API connection."""
        if not self.enabled:
            return False
        
        try:
            test_prompt = "Respond with 'OK' if you can read this message."
            response = await self._call_claude_api(test_prompt)
            return "OK" in response.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error(f"Claude connection test failed: {e}")
            return False 