#!/usr/bin/env python3
"""
Basketball Agent for MultiSportsBettingPlatform
==============================================
NBA/NCAAB-specific prediction agent with basketball analytics and insights.
"""

import random
from typing import Dict, Any, List
from datetime import datetime

from src.agents.head_agent import SportType, PredictionConfidence
from .base_sub_agent import BaseSubAgent

class BasketballAgent(BaseSubAgent):
    """NBA/NCAAB-specific prediction agent."""
    
    def __init__(self, name: str = "WNBA/NCAAB/NCAAW Basketball Agent"):
        super().__init__(SportType.BASKETBALL, name)
        
        # WNBA teams
        self.wnba_teams = {
            "Aces": {"wins": 34, "losses": 6, "ppg": 92.8, "opp_ppg": 80.3, "pace": 82.5},
            "Liberty": {"wins": 32, "losses": 8, "ppg": 89.2, "opp_ppg": 80.6, "pace": 80.1},
            "Sun": {"wins": 27, "losses": 13, "ppg": 82.7, "opp_ppg": 79.0, "pace": 77.8},
            "Wings": {"wins": 22, "losses": 18, "ppg": 87.9, "opp_ppg": 84.9, "pace": 81.2},
            "Dream": {"wins": 19, "losses": 21, "ppg": 82.5, "opp_ppg": 84.0, "pace": 79.5},
            "Lynx": {"wins": 19, "losses": 21, "ppg": 80.2, "opp_ppg": 85.0, "pace": 78.4}
        }
        
        # NCAAD Men's teams
        self.ncaab_teams = {
            "Duke": {"wins": 27, "losses": 9, "ppg": 78.5, "opp_ppg": 65.2, "conference": "ACC"},
            "Kentucky": {"wins": 22, "losses": 12, "ppg": 75.8, "opp_ppg": 69.4, "conference": "SEC"},
            "Kansas": {"wins": 28, "losses": 8, "ppg": 74.9, "opp_ppg": 65.8, "conference": "Big 12"},
            "UConn (M)": {"wins": 31, "losses": 3, "ppg": 81.5, "opp_ppg": 64.0, "conference": "Big East"},
            "Purdue": {"wins": 30, "losses": 4, "ppg": 83.2, "opp_ppg": 69.5, "conference": "Big Ten"}
        }

        # NCAAW Women's teams
        self.ncaaw_teams = {
            "South Carolina": {"wins": 32, "losses": 0, "ppg": 86.4, "opp_ppg": 55.4, "conference": "SEC"},
            "Iowa": {"wins": 29, "losses": 4, "ppg": 92.8, "opp_ppg": 71.2, "conference": "Big Ten"},
            "USC": {"wins": 26, "losses": 5, "ppg": 74.5, "opp_ppg": 61.3, "conference": "Pac-12"},
            "UConn (W)": {"wins": 29, "losses": 5, "ppg": 80.8, "opp_ppg": 56.3, "conference": "Big East"},
            "LSU": {"wins": 28, "losses": 5, "ppg": 85.9, "opp_ppg": 62.1, "conference": "SEC"}
        }
        
        # Player stats (WNBA/NCAAW/NCAAB)
        self.player_stats = {
            "A'ja Wilson": {"ppg": 22.8, "rpg": 9.5, "apg": 1.6, "team": "Aces"},
            "Breanna Stewart": {"ppg": 23.0, "rpg": 9.3, "apg": 3.8, "team": "Liberty"},
            "Caitlin Clark": {"ppg": 31.6, "rpg": 7.4, "apg": 8.9, "team": "Iowa"},
            "Zach Edey": {"ppg": 24.2, "rpg": 11.7, "apg": 2.0, "team": "Purdue"},
            "Angel Reese": {"ppg": 19.0, "rpg": 13.1, "apg": 2.3, "team": "LSU"}
        }
        
        self.betting_types = [
            "moneyline", "spread", "total_points", "first_half", "player_props", "quarter_bets"
        ]
    
    async def analyze_sport_data(self, query_params: dict) -> Dict[str, Any]:
        """Analyze WNBA/NCAAB/NCAAW-specific data and return insights."""
        analysis = {
            "sport": "basketball",
            "league": "NCAAB", # Default
            "analysis_type": "comprehensive",
            "teams_analyzed": [],
            "offensive_analysis": {},
            "defensive_analysis": {},
            "pace_analysis": {},
            "player_analysis": {},
            "historical_data": {},
            "key_metrics": {}
        }
        
        # Determine league and teams from query
        query_text = query_params.get("query_text", "").lower()
        
        # Determine league
        is_wnba = "wnba" in query_text
        is_ncaaw = any(word in query_text for word in ["women", "ncaaw"]) and not is_wnba
        is_ncaab = any(word in query_text for word in ["college", "ncaa", "ncaab", "men"]) or (not is_wnba and not is_ncaaw)
        
        # Select appropriate team database
        if is_wnba:
            team_db = self.wnba_teams
            analysis["league"] = "WNBA"
        elif is_ncaaw:
            team_db = self.ncaaw_teams
            analysis["league"] = "NCAAW"
        else:
            team_db = self.ncaab_teams
            analysis["league"] = "NCAAB"
        
        # Extract team mentions
        mentioned_teams = []
        for team in team_db.keys():
            if team.lower() in query_text:
                mentioned_teams.append(team)
        
        # If no teams mentioned, use random teams from selected league
        if not mentioned_teams:
            mentioned_teams = random.sample(list(team_db.keys()), 2)
        
        analysis["teams_analyzed"] = mentioned_teams[:2]
        
        # Analyze team matchups
        if len(analysis["teams_analyzed"]) >= 2:
            team1, team2 = analysis["teams_analyzed"][0], analysis["teams_analyzed"][1]
            
            # Offensive analysis
            analysis["offensive_analysis"] = {
                "team1": {"name": team1, "ppg": team_db[team1]["ppg"]},
                "team2": {"name": team2, "ppg": team_db[team2]["ppg"]},
                "total_points_expected": team_db[team1]["ppg"] + team_db[team2]["ppg"],
                "offensive_advantage": team1 if team_db[team1]["ppg"] > team_db[team2]["ppg"] else team2
            }
            
            # Defensive analysis
            analysis["defensive_analysis"] = {
                "team1": {"name": team1, "opp_ppg": team_db[team1]["opp_ppg"]},
                "team2": {"name": team2, "opp_ppg": team_db[team2]["opp_ppg"]},
                "defensive_advantage": team1 if team_db[team1]["opp_ppg"] < team_db[team2]["opp_ppg"] else team2
            }
            
            # Pace analysis (WNBA only has explicit pace stats in our mock, others implied)
            if "pace" in team_db[team1] and "pace" in team_db[team2]:
                analysis["pace_analysis"] = {
                    "team1_pace": team_db[team1]["pace"],
                    "team2_pace": team_db[team2]["pace"],
                    "expected_pace": (team_db[team1]["pace"] + team_db[team2]["pace"]) / 2,
                    "pace_advantage": team1 if team_db[team1]["pace"] > team_db[team2]["pace"] else team2
                }
        
        # Player analysis
        relevant_players = []
        for player, stats in self.player_stats.items():
            if stats["team"] in analysis["teams_analyzed"]:
                relevant_players.append({"name": player, "stats": stats})
        
        analysis["player_analysis"] = {
            "key_players": relevant_players,
            "star_power": len(relevant_players)
        }
        
        # Historical data
        analysis["historical_data"] = {
            "head_to_head": {"team1_wins": random.randint(2, 8), "team2_wins": random.randint(2, 8)},
            "recent_form": {"team1_last_10": random.randint(4, 9), "team2_last_10": random.randint(4, 9)},
            "home_away": {"team1_home": f"{random.randint(10, 20)}-{random.randint(2, 10)}", 
                         "team2_away": f"{random.randint(5, 15)}-{random.randint(5, 15)}"}
        }
        
        # Key metrics
        analysis["key_metrics"] = {
            "efficiency_rating": random.uniform(100, 120),
            "turnover_rate": random.uniform(0.10, 0.18),
            "rebound_rate": random.uniform(0.45, 0.55),
            "three_point_percentage": random.uniform(0.30, 0.40),
            "free_throw_percentage": random.uniform(0.70, 0.85)
        }
        
        return analysis
    
    async def get_sport_specific_prediction(self, analysis: Dict[str, Any]) -> str:
        """Generate WNBA/NCAAB/NCAAW-specific prediction based on analysis."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Aces -5.5 (Championship pedigree)"
        
        team1, team2 = teams[0], teams[1]
        
        # Get team databases
        league = analysis.get("league", "NCAAB")
        if league == "WNBA":
            team_db = self.wnba_teams
        elif league == "NCAAW":
            team_db = self.ncaaw_teams
        else:
            team_db = self.ncaab_teams
        
        # Calculate expected total
        total_points = analysis.get("offensive_analysis", {}).get("total_points_expected", 220)
        
        # Generate predictions
        predictions = []
        
        # Spread prediction
        team1_ppg = team_db[team1]["ppg"]
        team2_ppg = team_db[team2]["ppg"]
        team1_opp_ppg = team_db[team1]["opp_ppg"]
        team2_opp_ppg = team_db[team2]["opp_ppg"]
        
        # Calculate expected margin
        team1_expected = (team1_ppg + team2_opp_ppg) / 2
        team2_expected = (team2_ppg + team1_opp_ppg) / 2
        expected_margin = team1_expected - team2_expected
        
        if expected_margin > 3:
            predictions.append(f"{team1} -{abs(expected_margin):.1f} (Offensive advantage)")
        elif expected_margin < -3:
            predictions.append(f"{team2} -{abs(expected_margin):.1f} (Offensive advantage)")
        else:
            predictions.append(f"{team1} +{abs(expected_margin):.1f} (Close game)")
        
        # Total points prediction
        if total_points > 220:
            predictions.append(f"Over {total_points:.1f} points (High-scoring teams)")
        else:
            predictions.append(f"Under {total_points:.1f} points (Defensive matchup)")
        
        # First half prediction
        first_half_total = total_points * 0.48  # Typically 48% of total
        if first_half_total > 105:
            predictions.append(f"First half over {first_half_total:.1f} points")
        else:
            predictions.append(f"First half under {first_half_total:.1f} points")
        
        # Player props (if relevant players)
        players = analysis.get("player_analysis", {}).get("key_players", [])
        if players:
            top_player = players[0]
            player_name = top_player["name"]
            avg_ppg = top_player["stats"]["ppg"]
            predictions.append(f"{player_name} over {avg_ppg - 2:.1f} points")
        
        return predictions[0]
    
    async def calculate_confidence(self, analysis: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level based on basketball analysis."""
        confidence_score = 0
        
        # Offensive advantage
        offensive_advantage = analysis.get("offensive_analysis", {}).get("offensive_advantage")
        if offensive_advantage:
            confidence_score += 2
        
        # Defensive advantage
        defensive_advantage = analysis.get("defensive_analysis", {}).get("defensive_advantage")
        if defensive_advantage:
            confidence_score += 2
        
        # Star power
        star_power = analysis.get("player_analysis", {}).get("star_power", 0)
        if star_power >= 2:
            confidence_score += 2
        elif star_power >= 1:
            confidence_score += 1
        
        # Recent form
        recent_form = analysis.get("historical_data", {}).get("recent_form", {})
        if recent_form.get("team1_last_10", 5) >= 7 or recent_form.get("team2_last_10", 5) >= 7:
            confidence_score += 2
        
        # Efficiency rating
        efficiency = analysis.get("key_metrics", {}).get("efficiency_rating", 110)
        if efficiency > 115 or efficiency < 105:
            confidence_score += 1
        
        # Determine confidence level
        if confidence_score >= 6:
            return PredictionConfidence.HIGH
        elif confidence_score >= 3:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    async def generate_reasoning(self, analysis: Dict[str, Any], prediction: str) -> str:
        """Generate detailed reasoning for the basketball prediction."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Analysis based on general basketball trends and team performance metrics."
        
        team1, team2 = teams[0], teams[1]
        league = analysis.get("league", "NBA")
        
        reasoning_parts = []
        
        # Offensive analysis
        offensive = analysis.get("offensive_analysis", {})
        if offensive.get("offensive_advantage"):
            reasoning_parts.append(f"{offensive['offensive_advantage']} has the offensive advantage averaging {offensive.get('team1' if offensive['offensive_advantage'] == team1 else 'team2', {}).get('ppg', 0):.1f} PPG.")
        
        # Defensive analysis
        defensive = analysis.get("defensive_analysis", {})
        if defensive.get("defensive_advantage"):
            reasoning_parts.append(f"{defensive['defensive_advantage']} has the defensive advantage allowing {defensive.get('team1' if defensive['defensive_advantage'] == team1 else 'team2', {}).get('opp_ppg', 0):.1f} PPG.")
        
        # Total points
        if offensive.get("total_points_expected"):
            reasoning_parts.append(f"Expected total: {offensive['total_points_expected']:.1f} points based on offensive averages.")
        
        # Player analysis
        players = analysis.get("player_analysis", {}).get("key_players", [])
        if players:
            player_names = [p["name"] for p in players[:2]]
            reasoning_parts.append(f"Key players: {', '.join(player_names)} expected to impact the game.")
        
        # Recent form
        recent = analysis.get("historical_data", {}).get("recent_form", {})
        if recent:
            reasoning_parts.append(f"Recent form: {team1} {recent.get('team1_last_10', 5)}-{10-recent.get('team1_last_10', 5)} last 10, {team2} {recent.get('team2_last_10', 5)}-{10-recent.get('team2_last_10', 5)} last 10.")
        
        return " ".join(reasoning_parts) if reasoning_parts else f"Analysis based on comprehensive {league} metrics and team performance data."
    


    async def get_sport_specific_insights(self) -> Dict[str, Any]:
        """Get Basketball-specific insights and statistics."""
        base_insights = await super().get_sport_specific_insights()
        
        # Add basketball-specific insights
        basketball_insights = {
            "league": "WNBA/NCAAB/NCAAW",
            "wnba_teams_tracked": len(self.wnba_teams),
            "ncaab_teams_tracked": len(self.ncaab_teams),
            "ncaaw_teams_tracked": len(self.ncaaw_teams),
            "players_tracked": len(self.player_stats),
            "betting_types": self.betting_types,
            "top_wnba_teams": sorted(self.wnba_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_ncaab_teams": sorted(self.ncaab_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_ncaaw_teams": sorted(self.ncaaw_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3]
        }
        
        base_insights.update(basketball_insights)
        return base_insights 