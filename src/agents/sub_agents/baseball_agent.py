#!/usr/bin/env python3
"""
Baseball Agent for MultiSportsBettingPlatform
============================================
MLB-specific prediction agent with baseball analytics and insights.
"""

import random
from typing import Dict, Any, List
from datetime import datetime

from src.agents.head_agent import SportType, PredictionConfidence
from .base_sub_agent import BaseSubAgent

class BaseballAgent(BaseSubAgent):
    """MLB-specific prediction agent."""
    
    def __init__(self, name: str = "MLB Baseball Agent"):
        super().__init__(SportType.BASEBALL, name)
        
        # MLB-specific data structures
        self.team_stats = {
            "Dodgers": {"wins": 100, "losses": 62, "runs_per_game": 5.2, "era": 3.45},
            "Yankees": {"wins": 99, "losses": 63, "runs_per_game": 4.9, "era": 3.67},
            "Astros": {"wins": 95, "losses": 67, "runs_per_game": 4.7, "era": 3.23},
            "Braves": {"wins": 101, "losses": 61, "runs_per_game": 5.1, "era": 3.56},
            "Mets": {"wins": 87, "losses": 75, "runs_per_game": 4.6, "era": 3.78},
            "Phillies": {"wins": 87, "losses": 75, "runs_per_game": 4.5, "era": 3.89},
            "Giants": {"wins": 81, "losses": 81, "runs_per_game": 4.3, "era": 3.92},
            "Padres": {"wins": 89, "losses": 73, "runs_per_game": 4.8, "era": 3.67}
        }
        
        self.pitcher_stats = {
            "deGrom": {"era": 1.98, "whip": 0.89, "k_per_9": 12.3},
            "Scherzer": {"era": 2.29, "whip": 0.91, "k_per_9": 11.2},
            "Cole": {"era": 2.76, "whip": 1.02, "k_per_9": 10.8},
            "Burnes": {"era": 2.43, "whip": 0.94, "k_per_9": 11.1},
            "Ohtani": {"era": 2.58, "whip": 1.01, "k_per_9": 11.9}
        }
        
        self.betting_types = [
            "moneyline", "run_line", "total_runs", "first_5_innings", "player_props"
        ]
    
    async def analyze_sport_data(self, query_params: dict) -> Dict[str, Any]:
        """Analyze MLB-specific data and return insights."""
        analysis = {
            "sport": "baseball",
            "league": "MLB",
            "analysis_type": "comprehensive",
            "teams_analyzed": [],
            "pitching_matchup": {},
            "offensive_analysis": {},
            "defensive_analysis": {},
            "weather_factors": {},
            "historical_data": {},
            "key_metrics": {}
        }
        
        # Simulate analyzing teams from query
        query_text = query_params.get("query_text", "").lower()
        
        # Extract team mentions from query
        mentioned_teams = []
        for team in self.team_stats.keys():
            if team.lower() in query_text:
                mentioned_teams.append(team)
        
        # If no teams mentioned, use random teams for demo
        if not mentioned_teams:
            mentioned_teams = random.sample(list(self.team_stats.keys()), 2)
        
        analysis["teams_analyzed"] = mentioned_teams[:2]  # Limit to 2 teams
        
        # Analyze team matchups
        if len(analysis["teams_analyzed"]) >= 2:
            team1, team2 = analysis["teams_analyzed"][0], analysis["teams_analyzed"][1]
            
            # Pitching analysis
            analysis["pitching_matchup"] = {
                "team1": {"name": team1, "era": self.team_stats[team1]["era"]},
                "team2": {"name": team2, "era": self.team_stats[team2]["era"]},
                "advantage": team1 if self.team_stats[team1]["era"] < self.team_stats[team2]["era"] else team2
            }
            
            # Offensive analysis
            analysis["offensive_analysis"] = {
                "team1": {"name": team1, "runs_per_game": self.team_stats[team1]["runs_per_game"]},
                "team2": {"name": team2, "runs_per_game": self.team_stats[team2]["runs_per_game"]},
                "total_runs_expected": self.team_stats[team1]["runs_per_game"] + self.team_stats[team2]["runs_per_game"]
            }
            
            # Defensive analysis
            analysis["defensive_analysis"] = {
                "team1": {"name": team1, "era": self.team_stats[team1]["era"]},
                "team2": {"name": team2, "era": self.team_stats[team2]["era"]},
                "defensive_advantage": team1 if self.team_stats[team1]["era"] < self.team_stats[team2]["era"] else team2
            }
        
        # Weather factors (simulated)
        analysis["weather_factors"] = {
            "temperature": random.randint(65, 85),
            "wind_speed": random.randint(5, 15),
            "wind_direction": random.choice(["in", "out", "left", "right"]),
            "humidity": random.randint(40, 80),
            "ballpark_factor": random.uniform(0.9, 1.1)
        }
        
        # Historical data
        analysis["historical_data"] = {
            "head_to_head": {"team1_wins": random.randint(3, 7), "team2_wins": random.randint(3, 7)},
            "recent_form": {"team1_last_10": random.randint(4, 8), "team2_last_10": random.randint(4, 8)},
            "home_away": {"team1_home_record": f"{random.randint(25, 35)}-{random.randint(15, 25)}", 
                         "team2_away_record": f"{random.randint(20, 30)}-{random.randint(20, 30)}"}
        }
        
        # Key metrics
        analysis["key_metrics"] = {
            "run_differential": random.uniform(-50, 50),
            "bullpen_era": random.uniform(3.0, 4.5),
            "clutch_hitting": random.uniform(0.250, 0.350),
            "strikeout_rate": random.uniform(0.20, 0.30),
            "walk_rate": random.uniform(0.08, 0.12)
        }
        
        return analysis
    
    async def get_sport_specific_prediction(self, analysis: Dict[str, Any]) -> str:
        """Generate MLB-specific prediction based on analysis."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Dodgers -1.5 (Strong pitching matchup)"
        
        team1, team2 = teams[0], teams[1]
        
        # Determine prediction type based on analysis
        offensive_total = analysis.get("offensive_analysis", {}).get("total_runs_expected", 9.0)
        pitching_advantage = analysis.get("pitching_matchup", {}).get("advantage", team1)
        
        # Generate different types of predictions
        predictions = []
        
        # Moneyline prediction
        if pitching_advantage == team1:
            predictions.append(f"{team1} ML (Pitching advantage)")
        else:
            predictions.append(f"{team2} ML (Pitching advantage)")
        
        # Run line prediction
        if analysis["key_metrics"]["run_differential"] > 20:
            predictions.append(f"{team1} -1.5 (Strong run differential)")
        elif analysis["key_metrics"]["run_differential"] < -20:
            predictions.append(f"{team2} -1.5 (Strong run differential)")
        else:
            predictions.append(f"{team1} +1.5 (Close game expected)")
        
        # Total runs prediction
        if offensive_total > 9.5:
            predictions.append(f"Over {offensive_total:.1f} runs (High-scoring teams)")
        else:
            predictions.append(f"Under {offensive_total:.1f} runs (Pitching duel)")
        
        # Player props (simulated)
        predictions.append(f"{team1} first 5 innings -0.5 (Early lead)")
        
        # Return the most confident prediction
        return predictions[0]
    
    async def calculate_confidence(self, analysis: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level based on MLB analysis."""
        # Factors that increase confidence
        confidence_score = 0
        
        # Pitching advantage
        if analysis.get("pitching_matchup", {}).get("advantage"):
            confidence_score += 2
        
        # Run differential
        run_diff = abs(analysis.get("key_metrics", {}).get("run_differential", 0))
        if run_diff > 30:
            confidence_score += 3
        elif run_diff > 15:
            confidence_score += 2
        elif run_diff > 5:
            confidence_score += 1
        
        # Recent form
        recent_form = analysis.get("historical_data", {}).get("recent_form", {})
        if recent_form.get("team1_last_10", 5) >= 7 or recent_form.get("team2_last_10", 5) >= 7:
            confidence_score += 2
        
        # Weather factors
        weather = analysis.get("weather_factors", {})
        if weather.get("wind_direction") == "out" and weather.get("wind_speed", 0) > 10:
            confidence_score += 1
        
        # Determine confidence level
        if confidence_score >= 6:
            return PredictionConfidence.HIGH
        elif confidence_score >= 3:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    async def generate_reasoning(self, analysis: Dict[str, Any], prediction: str) -> str:
        """Generate detailed reasoning for the MLB prediction."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Analysis based on general MLB trends and team performance metrics."
        
        team1, team2 = teams[0], teams[1]
        
        reasoning_parts = []
        
        # Pitching analysis
        pitching = analysis.get("pitching_matchup", {})
        if pitching.get("advantage"):
            reasoning_parts.append(f"{pitching['advantage']} has the pitching advantage with a {pitching.get('team1' if pitching['advantage'] == team1 else 'team2', {}).get('era', 0):.2f} ERA.")
        
        # Offensive analysis
        offensive = analysis.get("offensive_analysis", {})
        if offensive.get("total_runs_expected"):
            reasoning_parts.append(f"Expected total runs: {offensive['total_runs_expected']:.1f} based on {team1} ({offensive.get('team1', {}).get('runs_per_game', 0):.1f} RPG) and {team2} ({offensive.get('team2', {}).get('runs_per_game', 0):.1f} RPG).")
        
        # Recent form
        recent = analysis.get("historical_data", {}).get("recent_form", {})
        if recent:
            reasoning_parts.append(f"Recent form: {team1} {recent.get('team1_last_10', 5)}-{10-recent.get('team1_last_10', 5)} last 10, {team2} {recent.get('team2_last_10', 5)}-{10-recent.get('team2_last_10', 5)} last 10.")
        
        # Weather impact
        weather = analysis.get("weather_factors", {})
        if weather.get("wind_direction") == "out" and weather.get("wind_speed", 0) > 10:
            reasoning_parts.append(f"Weather favors offense with {weather.get('wind_speed')} mph wind blowing out.")
        
        # Key metrics
        metrics = analysis.get("key_metrics", {})
        if abs(metrics.get("run_differential", 0)) > 20:
            reasoning_parts.append(f"Run differential analysis shows significant advantage for one team.")
        
        return " ".join(reasoning_parts) if reasoning_parts else "Analysis based on comprehensive MLB metrics and team performance data."
    
    async def get_sport_specific_insights(self) -> Dict[str, Any]:
        """Get MLB-specific insights and statistics."""
        base_insights = await super().get_sport_specific_insights()
        
        # Add MLB-specific insights
        mlb_insights = {
            "league": "MLB",
            "season": "2024",
            "teams_tracked": len(self.team_stats),
            "pitchers_tracked": len(self.pitcher_stats),
            "betting_types": self.betting_types,
            "top_teams": sorted(self.team_stats.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_pitchers": sorted(self.pitcher_stats.items(), key=lambda x: x[1]["era"])[:3]
        }
        
        base_insights.update(mlb_insights)
        return base_insights 