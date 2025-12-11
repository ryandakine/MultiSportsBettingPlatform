#!/usr/bin/env python3
"""
Hockey Agent for MultiSportsBettingPlatform
==========================================
NHL-specific prediction agent with hockey analytics and insights.
"""

import random
from typing import Dict, Any, List
from datetime import datetime

from src.agents.head_agent import SportType, PredictionConfidence
from .base_sub_agent import BaseSubAgent

class HockeyAgent(BaseSubAgent):
    """NHL-specific prediction agent."""
    
    def __init__(self, name: str = "NHL Hockey Agent"):
        super().__init__(SportType.HOCKEY, name)
        
        # NHL team stats
        self.nhl_teams = {
            "Bruins": {"wins": 65, "losses": 12, "goals_for": 305, "goals_against": 177, "power_play": 22.2, "penalty_kill": 87.3},
            "Lightning": {"wins": 46, "losses": 30, "goals_for": 283, "goals_against": 254, "power_play": 25.4, "penalty_kill": 79.7},
            "Maple Leafs": {"wins": 50, "losses": 21, "goals_for": 279, "goals_against": 222, "power_play": 23.5, "penalty_kill": 81.9},
            "Oilers": {"wins": 50, "losses": 23, "goals_for": 325, "goals_against": 260, "power_play": 32.4, "penalty_kill": 75.5},
            "Rangers": {"wins": 47, "losses": 22, "goals_for": 254, "goals_against": 207, "power_play": 24.1, "penalty_kill": 82.0},
            "Devils": {"wins": 52, "losses": 22, "goals_for": 291, "goals_against": 236, "power_play": 21.9, "penalty_kill": 82.6},
            "Avalanche": {"wins": 51, "losses": 24, "goals_for": 280, "goals_against": 226, "power_play": 24.8, "penalty_kill": 80.1},
            "Golden Knights": {"wins": 51, "losses": 22, "goals_for": 272, "goals_against": 229, "power_play": 20.3, "penalty_kill": 77.4}
        }
        
        # Goalie stats
        self.goalie_stats = {
            "Linus Ullmark": {"gaa": 1.89, "save_pct": 0.938, "wins": 40, "team": "Bruins"},
            "Igor Shesterkin": {"gaa": 2.48, "save_pct": 0.916, "wins": 37, "team": "Rangers"},
            "Connor Hellebuyck": {"gaa": 2.49, "save_pct": 0.920, "wins": 37, "team": "Jets"},
            "Andrei Vasilevskiy": {"gaa": 2.65, "save_pct": 0.915, "wins": 34, "team": "Lightning"},
            "Jake Oettinger": {"gaa": 2.37, "save_pct": 0.919, "wins": 36, "team": "Stars"}
        }
        
        # Player stats
        self.player_stats = {
            "Connor McDavid": {"goals": 64, "assists": 89, "points": 153, "team": "Oilers"},
            "Leon Draisaitl": {"goals": 52, "assists": 76, "points": 128, "team": "Oilers"},
            "David Pastrnak": {"goals": 61, "assists": 52, "points": 113, "team": "Bruins"},
            "Nathan MacKinnon": {"goals": 42, "assists": 69, "points": 111, "team": "Avalanche"},
            "Mikko Rantanen": {"goals": 55, "assists": 50, "points": 105, "team": "Avalanche"}
        }
        
        self.betting_types = [
            "moneyline", "puck_line", "total_goals", "first_period", "player_props", "period_bets"
        ]
    
    async def analyze_sport_data(self, query_params: dict) -> Dict[str, Any]:
        """Analyze NHL-specific data and return insights."""
        analysis = {
            "sport": "hockey",
            "league": "NHL",
            "analysis_type": "comprehensive",
            "teams_analyzed": [],
            "offensive_analysis": {},
            "defensive_analysis": {},
            "goalie_analysis": {},
            "special_teams": {},
            "ice_conditions": {},
            "historical_data": {},
            "key_metrics": {}
        }
        
        # Extract team mentions from query
        query_text = query_params.get("query_text", "").lower()
        
        mentioned_teams = []
        for team in self.nhl_teams.keys():
            if team.lower() in query_text:
                mentioned_teams.append(team)
        
        # If no teams mentioned, use random teams
        if not mentioned_teams:
            mentioned_teams = random.sample(list(self.nhl_teams.keys()), 2)
        
        analysis["teams_analyzed"] = mentioned_teams[:2]
        
        # Analyze team matchups
        if len(analysis["teams_analyzed"]) >= 2:
            team1, team2 = analysis["teams_analyzed"][0], analysis["teams_analyzed"][1]
            
            # Offensive analysis
            analysis["offensive_analysis"] = {
                "team1": {"name": team1, "goals_for": self.nhl_teams[team1]["goals_for"]},
                "team2": {"name": team2, "goals_for": self.nhl_teams[team2]["goals_for"]},
                "total_goals_expected": self.nhl_teams[team1]["goals_for"] + self.nhl_teams[team2]["goals_for"],
                "offensive_advantage": team1 if self.nhl_teams[team1]["goals_for"] > self.nhl_teams[team2]["goals_for"] else team2
            }
            
            # Defensive analysis
            analysis["defensive_analysis"] = {
                "team1": {"name": team1, "goals_against": self.nhl_teams[team1]["goals_against"]},
                "team2": {"name": team2, "goals_against": self.nhl_teams[team2]["goals_against"]},
                "defensive_advantage": team1 if self.nhl_teams[team1]["goals_against"] < self.nhl_teams[team2]["goals_against"] else team2
            }
            
            # Special teams analysis
            analysis["special_teams"] = {
                "team1_pp": self.nhl_teams[team1]["power_play"],
                "team2_pp": self.nhl_teams[team2]["power_play"],
                "team1_pk": self.nhl_teams[team1]["penalty_kill"],
                "team2_pk": self.nhl_teams[team2]["penalty_kill"],
                "power_play_advantage": team1 if self.nhl_teams[team1]["power_play"] > self.nhl_teams[team2]["power_play"] else team2,
                "penalty_kill_advantage": team1 if self.nhl_teams[team1]["penalty_kill"] > self.nhl_teams[team2]["penalty_kill"] else team2
            }
        
        # Goalie analysis
        goalies_involved = []
        for goalie, stats in self.goalie_stats.items():
            if stats["team"] in analysis["teams_analyzed"]:
                goalies_involved.append({"name": goalie, "stats": stats})
        
        analysis["goalie_analysis"] = {
            "starting_goalies": goalies_involved,
            "goalie_advantage": None
        }
        
        if len(goalies_involved) >= 2:
             analysis["goalie_analysis"]["goalie_advantage"] = goalies_involved[0]["name"] if goalies_involved[0]["stats"]["gaa"] < goalies_involved[1]["stats"]["gaa"] else goalies_involved[1]["name"]
        
        # Ice conditions (simulated)
        analysis["ice_conditions"] = {
            "temperature": random.randint(18, 22),  # Celsius
            "humidity": random.randint(40, 60),
            "ice_quality": random.choice(["excellent", "good", "average", "poor"]),
            "rink_size": "standard",  # NHL standard
            "home_ice_advantage": random.uniform(1.0, 1.15)
        }
        
        # Historical data
        analysis["historical_data"] = {
            "head_to_head": {"team1_wins": random.randint(2, 6), "team2_wins": random.randint(2, 6)},
            "recent_form": {"team1_last_10": random.randint(4, 9), "team2_last_10": random.randint(4, 9)},
            "home_away": {"team1_home": f"{random.randint(20, 30)}-{random.randint(5, 15)}", 
                         "team2_away": f"{random.randint(15, 25)}-{random.randint(10, 20)}"}
        }
        
        # Key metrics
        analysis["key_metrics"] = {
            "faceoff_percentage": random.uniform(0.45, 0.55),
            "shots_per_game": random.uniform(28, 35),
            "hits_per_game": random.uniform(15, 25),
            "blocked_shots": random.uniform(12, 20),
            "giveaways": random.uniform(8, 15),
            "takeaways": random.uniform(6, 12)
        }
        
        return analysis
    
    async def get_sport_specific_prediction(self, analysis: Dict[str, Any]) -> str:
        """Generate NHL-specific prediction based on analysis."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Bruins ML (Home ice advantage)"
        
        team1, team2 = teams[0], teams[1]
        
        # Calculate expected total goals
        total_goals = analysis.get("offensive_analysis", {}).get("total_goals_expected", 5.5)
        
        # Generate predictions
        predictions = []
        
        # Moneyline prediction
        team1_goals_for = self.nhl_teams[team1]["goals_for"]
        team2_goals_for = self.nhl_teams[team2]["goals_for"]
        team1_goals_against = self.nhl_teams[team1]["goals_against"]
        team2_goals_against = self.nhl_teams[team2]["goals_against"]
        
        # Calculate expected goals for each team
        team1_expected = (team1_goals_for + team2_goals_against) / 2
        team2_expected = (team2_goals_for + team1_goals_against) / 2
        
        # Adjust for home ice advantage
        home_advantage = 0.2  # 0.2 goals
        team1_expected += home_advantage
        
        if team1_expected > team2_expected + 0.5:
            predictions.append(f"{team1} ML (Home ice + offensive edge)")
        elif team2_expected > team1_expected + 0.5:
            predictions.append(f"{team2} ML (Road team advantage)")
        else:
            predictions.append(f"{team1} ML (Close game, home ice)")
        
        # Puck line prediction
        expected_margin = abs(team1_expected - team2_expected)
        if expected_margin > 1.5:
            predictions.append(f"{team1 if team1_expected > team2_expected else team2} -1.5 (Expected blowout)")
        else:
            predictions.append(f"{team1} +1.5 (Close game expected)")
        
        # Total goals prediction
        if total_goals > 6.5:
            predictions.append(f"Over {total_goals:.1f} goals (High-scoring teams)")
        else:
            predictions.append(f"Under {total_goals:.1f} goals (Defensive matchup)")
        
        # First period prediction
        first_period_goals = total_goals * 0.33  # Typically 33% of total
        if first_period_goals > 2.5:
            predictions.append(f"First period over {first_period_goals:.1f} goals")
        else:
            predictions.append(f"First period under {first_period_goals:.1f} goals")
        
        # Special teams prediction
        special_teams = analysis.get("special_teams", {})
        if special_teams.get("power_play_advantage"):
            pp_team = special_teams["power_play_advantage"]
            pp_percentage = special_teams.get(f"team1_pp" if pp_team == team1 else "team2_pp", 20)
            if pp_percentage > 25:
                predictions.append(f"{pp_team} power play goal (PP: {pp_percentage}%)")
        
        return predictions[0]
    
    async def calculate_confidence(self, analysis: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level based on hockey analysis."""
        confidence_score = 0
        
        # Offensive advantage
        offensive_advantage = analysis.get("offensive_analysis", {}).get("offensive_advantage")
        if offensive_advantage:
            confidence_score += 2
        
        # Defensive advantage
        defensive_advantage = analysis.get("defensive_analysis", {}).get("defensive_advantage")
        if defensive_advantage:
            confidence_score += 2
        
        # Goalie advantage
        goalie_advantage = analysis.get("goalie_analysis", {}).get("goalie_advantage")
        if goalie_advantage:
            confidence_score += 3  # Goalies are crucial in hockey
        
        # Special teams advantage
        special_teams = analysis.get("special_teams", {})
        if special_teams.get("power_play_advantage") and special_teams.get("penalty_kill_advantage"):
            if special_teams["power_play_advantage"] == special_teams["penalty_kill_advantage"]:
                confidence_score += 2  # Same team has both advantages
        
        # Recent form
        recent_form = analysis.get("historical_data", {}).get("recent_form", {})
        if recent_form.get("team1_last_10", 5) >= 7 or recent_form.get("team2_last_10", 5) >= 7:
            confidence_score += 2
        
        # Ice conditions
        ice_quality = analysis.get("ice_conditions", {}).get("ice_quality", "average")
        if ice_quality in ["excellent", "good"]:
            confidence_score += 1
        
        # Faceoff percentage
        faceoff_pct = analysis.get("key_metrics", {}).get("faceoff_percentage", 0.50)
        if faceoff_pct > 0.52 or faceoff_pct < 0.48:
            confidence_score += 1
        
        # Determine confidence level
        if confidence_score >= 8:
            return PredictionConfidence.HIGH
        elif confidence_score >= 4:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    async def generate_reasoning(self, analysis: Dict[str, Any], prediction: str) -> str:
        """Generate detailed reasoning for the hockey prediction."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Analysis based on general hockey trends and team performance metrics."
        
        team1, team2 = teams[0], teams[1]
        
        reasoning_parts = []
        
        # Offensive analysis
        offensive = analysis.get("offensive_analysis", {})
        if offensive.get("offensive_advantage"):
            reasoning_parts.append(f"{offensive['offensive_advantage']} has the offensive advantage with {offensive.get('team1' if offensive['offensive_advantage'] == team1 else 'team2', {}).get('goals_for', 0)} goals scored.")
        
        # Defensive analysis
        defensive = analysis.get("defensive_analysis", {})
        if defensive.get("defensive_advantage"):
            reasoning_parts.append(f"{defensive['defensive_advantage']} has the defensive advantage allowing {defensive.get('team1' if defensive['defensive_advantage'] == team1 else 'team2', {}).get('goals_against', 0)} goals against.")
        
        # Goalie analysis
        goalie_analysis = analysis.get("goalie_analysis", {})
        if goalie_analysis.get("goalie_advantage"):
            reasoning_parts.append(f"Goalie advantage: {goalie_analysis['goalie_advantage']} expected to start.")
        
        # Special teams
        special_teams = analysis.get("special_teams", {})
        if special_teams.get("power_play_advantage"):
            pp_team = special_teams["power_play_advantage"]
            pp_percentage = special_teams.get(f"team1_pp" if pp_team == team1 else "team2_pp", 20)
            reasoning_parts.append(f"{pp_team} power play: {pp_percentage}% efficiency.")
        
        # Total goals
        if offensive.get("total_goals_expected"):
            reasoning_parts.append(f"Expected total: {offensive['total_goals_expected']:.1f} goals based on offensive averages.")
        
        # Recent form
        recent = analysis.get("historical_data", {}).get("recent_form", {})
        if recent:
            reasoning_parts.append(f"Recent form: {team1} {recent.get('team1_last_10', 5)}-{10-recent.get('team1_last_10', 5)} last 10, {team2} {recent.get('team2_last_10', 5)}-{10-recent.get('team2_last_10', 5)} last 10.")
        
        return " ".join(reasoning_parts) if reasoning_parts else "Analysis based on comprehensive NHL metrics and team performance data."
    
    async def find_betting_opportunities(self) -> List[Dict[str, Any]]:
        """Find upcoming betting opportunities for NHL."""
        opportunities = []
        
        # Simulate finding 1-3 upcoming games
        num_games = random.randint(1, 3)
        teams = list(self.nhl_teams.keys())
        
        if len(teams) < 2:
            return []
            
        for _ in range(num_games):
            t1, t2 = random.sample(teams, 2)
            
            # Create a game opportunity
            game = {
                "sport": self.sport.value,
                "title": f"{t1} vs {t2}",
                "teams": [t1, t2],
                "time": datetime.now().isoformat(),
                "query_text": f"NHL prediction for {t1} vs {t2}",
                "context": "Autonomous Market Scan",
                "league": "NHL"
            }
            opportunities.append(game)
            
        return opportunities

    async def get_sport_specific_insights(self) -> Dict[str, Any]:
        """Get NHL-specific insights and statistics."""
        base_insights = await super().get_sport_specific_insights()
        
        # Add hockey-specific insights
        hockey_insights = {
            "league": "NHL",
            "teams_tracked": len(self.nhl_teams),
            "goalies_tracked": len(self.goalie_stats),
            "players_tracked": len(self.player_stats),
            "betting_types": self.betting_types,
            "top_teams": sorted(self.nhl_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_goalies": sorted(self.goalie_stats.items(), key=lambda x: x[1]["gaa"])[:3],
            "top_scorers": sorted(self.player_stats.items(), key=lambda x: x[1]["points"], reverse=True)[:3]
        }
        
        base_insights.update(hockey_insights)
        return base_insights 