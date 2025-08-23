#!/usr/bin/env python3
"""
Perplexity Pro AI Service for MultiSportsBettingPlatform
======================================================
Service for integrating Perplexity Pro AI for enhanced research and analysis.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import httpx

from src.config import settings

logger = logging.getLogger(__name__)

class PerplexityService:
    """Service for interacting with Perplexity Pro AI API."""
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"
        
        if not self.api_key:
            logger.warning("Perplexity API key not configured. Perplexity features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Perplexity Pro AI service initialized")
    
    async def get_research_insights(
        self, 
        sport: str, 
        teams: List[str], 
        query: str,
        include_recent_data: bool = True
    ) -> Dict[str, Any]:
        """Get research insights from Perplexity Pro AI."""
        if not self.enabled:
            return {
                "insights": "Perplexity Pro AI not available",
                "sources": [],
                "recent_data": "Perplexity Pro AI service is disabled due to missing API key"
            }
        
        try:
            # Build research query
            research_query = self._build_research_query(sport, teams, query, include_recent_data)
            
            # Call Perplexity API
            response = await self._call_perplexity_api(research_query)
            
            # Parse Perplexity's response
            return self._parse_perplexity_response(response)
            
        except Exception as e:
            logger.error(f"Error getting Perplexity insights: {e}")
            return {
                "insights": "Error getting Perplexity insights",
                "sources": [],
                "recent_data": f"Perplexity Pro AI error: {str(e)}"
            }
    
    def _build_research_query(
        self, 
        sport: str, 
        teams: List[str], 
        query: str,
        include_recent_data: bool
    ) -> str:
        """Build a comprehensive research query for Perplexity Pro AI."""
        
        # Sport-specific research focus
        sport_focus = {
            "baseball": """
            Focus on:
            - Recent team performance and statistics
            - Player injuries and roster changes
            - Pitching matchups and bullpen usage
            - Weather conditions and ballpark factors
            - Head-to-head history and trends
            - Expert analysis and predictions
            """,
            "basketball": """
            Focus on:
            - Team offensive and defensive efficiency
            - Player performance and injury status
            - Recent form and momentum
            - Conference standings and playoff implications
            - Expert predictions and analysis
            - Betting line movements
            """,
            "football": """
            Focus on:
            - Team performance and statistics
            - Player injuries and roster updates
            - Weather conditions and field impact
            - Recent form and momentum
            - Expert analysis and predictions
            - Betting trends and line movements
            """,
            "hockey": """
            Focus on:
            - Team performance and statistics
            - Goalie matchups and recent form
            - Special teams performance
            - Injury updates and roster changes
            - Expert analysis and predictions
            - Betting trends and odds
            """
        }
        
        # Build the research prompt
        teams_str = " vs ".join(teams) if len(teams) == 2 else ", ".join(teams)
        
        research_prompt = f"""
        You are a professional sports betting analyst specializing in {sport.upper()}.
        
        RESEARCH REQUEST: {query}
        
        TEAMS: {teams_str}
        SPORT: {sport.upper()}
        
        {sport_focus.get(sport.lower(), "Focus on recent performance, statistics, and expert analysis.")}
        
        {f"INCLUDE RECENT DATA: {include_recent_data}" if include_recent_data else ""}
        
        Please provide:
        1. Recent team performance analysis
        2. Key player statistics and status
        3. Expert predictions and analysis
        4. Betting trends and line movements
        5. Relevant news and updates
        6. Data-driven insights for betting decisions
        
        Use the most recent and reliable sources available.
        Provide specific, actionable insights for sports betting.
        Include relevant statistics and data points.
        Cite your sources for credibility.
        
        Format your response as structured analysis with clear sections.
        """
        
        return research_prompt
    
    async def _call_perplexity_api(self, query: str) -> Dict[str, Any]:
        """Make API call to Perplexity Pro AI."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional sports betting analyst with expertise in all major sports. Provide accurate, data-driven analysis and insights for betting decisions."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
    
    def _parse_perplexity_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Perplexity's response into structured format."""
        try:
            # Extract the content from Perplexity's response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extract sources if available
            sources = []
            if "sources" in response:
                sources = response["sources"]
            
            # Parse the content into structured sections
            sections = self._parse_content_sections(content)
            
            return {
                "insights": content,
                "sources": sources,
                "recent_data": sections.get("recent_data", ""),
                "expert_analysis": sections.get("expert_analysis", ""),
                "betting_insights": sections.get("betting_insights", ""),
                "key_statistics": sections.get("key_statistics", ""),
                "structured_analysis": sections
            }
                
        except Exception as e:
            logger.error(f"Failed to parse Perplexity response: {e}")
            return {
                "insights": "Response parsing failed",
                "sources": [],
                "recent_data": "Unable to parse Perplexity's response",
                "error": str(e)
            }
    
    def _parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parse content into structured sections."""
        sections = {}
        
        # Simple section parsing based on common headers
        lines = content.split('\n')
        current_section = "general"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ["recent", "performance", "stats"]):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "recent_data"
                current_content = []
            elif any(keyword in lower_line for keyword in ["expert", "analysis", "prediction"]):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "expert_analysis"
                current_content = []
            elif any(keyword in lower_line for keyword in ["betting", "odds", "line"]):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "betting_insights"
                current_content = []
            elif any(keyword in lower_line for keyword in ["statistics", "stats", "data"]):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "key_statistics"
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections
    
    async def get_live_data_update(
        self, 
        sport: str, 
        teams: List[str]
    ) -> Dict[str, Any]:
        """Get live data updates for teams."""
        if not self.enabled:
            return {"live_data": "Perplexity Pro AI not available"}
        
        try:
            query = f"Get the most recent live data, statistics, and updates for {', '.join(teams)} in {sport}. Include current standings, recent performance, and any breaking news."
            
            response = await self._call_perplexity_api(query)
            return self._parse_perplexity_response(response)
            
        except Exception as e:
            logger.error(f"Error getting live data: {e}")
            return {"live_data": f"Error: {str(e)}"}
    
    async def get_historical_analysis(
        self, 
        sport: str, 
        teams: List[str], 
        timeframe: str = "last 10 games"
    ) -> Dict[str, Any]:
        """Get historical analysis for teams."""
        if not self.enabled:
            return {"historical_data": "Perplexity Pro AI not available"}
        
        try:
            query = f"Analyze the historical performance and head-to-head record between {', '.join(teams)} in {sport} over the {timeframe}. Include trends, patterns, and key statistics."
            
            response = await self._call_perplexity_api(query)
            return self._parse_perplexity_response(response)
            
        except Exception as e:
            logger.error(f"Error getting historical analysis: {e}")
            return {"historical_data": f"Error: {str(e)}"}
    
    async def test_connection(self) -> bool:
        """Test Perplexity API connection."""
        if not self.enabled:
            return False
        
        try:
            test_query = "Provide a brief sports analysis test response."
            response = await self._call_perplexity_api(test_query)
            return "choices" in response and len(response["choices"]) > 0
        except Exception as e:
            logger.error(f"Perplexity connection test failed: {e}")
            return False 