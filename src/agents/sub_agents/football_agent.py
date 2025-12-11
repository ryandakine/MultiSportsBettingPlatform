#!/usr/bin/env python3
"""
Football Agent for MultiSportsBettingPlatform
===========================================
NFL/NCAAF-specific prediction agent with football analytics and insights.
"""

import random
from typing import Dict, Any, List
from datetime import datetime

from src.agents.head_agent import SportType, PredictionConfidence
from .base_sub_agent import BaseSubAgent

class FootballAgent(BaseSubAgent):
    """NFL/NCAAF-specific prediction agent."""
    
    def __init__(self, name: str = "NFL/NCAAF Football Agent"):
        super().__init__(SportType.FOOTBALL, name)
        
        # NFL team stats
        self.nfl_teams = {
            "Chiefs": {"wins": 11, "losses": 6, "ppg": 21.8, "opp_ppg": 17.3, "pass_yds": 258.9, "rush_yds": 108.2},
            "Bills": {"wins": 11, "losses": 6, "ppg": 26.5, "opp_ppg": 18.3, "pass_yds": 245.8, "rush_yds": 130.1},
            "Eagles": {"wins": 11, "losses": 6, "ppg": 25.5, "opp_ppg": 20.2, "pass_yds": 241.6, "rush_yds": 147.6},
            "Cowboys": {"wins": 12, "losses": 5, "ppg": 27.5, "opp_ppg": 18.3, "pass_yds": 248.5, "rush_yds": 135.2},
            "49ers": {"wins": 12, "losses": 5, "ppg": 28.9, "opp_ppg": 17.5, "pass_yds": 238.9, "rush_yds": 140.5},
            "Ravens": {"wins": 13, "losses": 4, "ppg": 28.4, "opp_ppg": 16.5, "pass_yds": 213.8, "rush_yds": 156.5},
            "Bengals": {"wins": 9, "losses": 8, "ppg": 22.6, "opp_ppg": 20.1, "pass_yds": 248.9, "rush_yds": 95.8},
            "Dolphins": {"wins": 11, "losses": 6, "ppg": 23.4, "opp_ppg": 23.1, "pass_yds": 265.5, "rush_yds": 142.2}
        }
        
        # NCAAF teams
        self.ncaaf_teams = {
            "Alabama": {"wins": 12, "losses": 2, "ppg": 35.1, "opp_ppg": 18.2, "conference": "SEC"},
            "Michigan": {"wins": 15, "losses": 0, "ppg": 36.1, "opp_ppg": 9.5, "conference": "Big Ten"},
            "Georgia": {"wins": 13, "losses": 1, "ppg": 40.1, "opp_ppg": 15.6, "conference": "SEC"},
            "Ohio State": {"wins": 11, "losses": 2, "ppg": 30.5, "opp_ppg": 11.2, "conference": "Big Ten"},
            "Texas": {"wins": 12, "losses": 2, "ppg": 35.9, "opp_ppg": 18.3, "conference": "Big 12"},
            "Florida State": {"wins": 13, "losses": 1, "ppg": 41.1, "opp_ppg": 15.9, "conference": "ACC"}
        }
        
        # Player stats
        self.player_stats = {
            "Patrick Mahomes": {"pass_yds": 4183, "tds": 31, "ints": 8, "team": "Chiefs"},
            "Josh Allen": {"pass_yds": 4306, "tds": 35, "ints": 14, "team": "Bills"},
            "Jalen Hurts": {"pass_yds": 3858, "tds": 23, "ints": 15, "team": "Eagles"},
            "Dak Prescott": {"pass_yds": 4516, "tds": 36, "ints": 9, "team": "Cowboys"},
            "Christian McCaffrey": {"rush_yds": 1459, "tds": 14, "team": "49ers"}
        }
        
        self.betting_types = [
            "moneyline", "spread", "total_points", "first_half", "player_props", "quarter_bets"
        ]
    
    async def analyze_sport_data(self, query_params: dict) -> Dict[str, Any]:
        """Analyze NFL/NCAAF-specific data and return insights."""
        analysis = {
            "sport": "football",
            "league": "NFL/NCAAF",
            "analysis_type": "comprehensive",
            "teams_analyzed": [],
            "offensive_analysis": {},
            "defensive_analysis": {},
            "passing_analysis": {},
            "rushing_analysis": {},
            "weather_analysis": {},
            "historical_data": {},
            "key_metrics": {}
        }
        
        # Determine league and teams from query
        query_text = query_params.get("query_text", "").lower()
        
        # Check if it's NCAAF
        is_ncaaf = any(word in query_text for word in ["college", "ncaa", "ncaaf", "alabama", "michigan", "georgia"])
        
        # Select appropriate team database
        team_db = self.ncaaf_teams if is_ncaaf else self.nfl_teams
        analysis["league"] = "NCAAF" if is_ncaaf else "NFL"
        
        # Extract team mentions
        mentioned_teams = []
        for team in team_db.keys():
            if team.lower() in query_text:
                mentioned_teams.append(team)
        
        # If no teams mentioned, use random teams
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
            
            # Passing analysis (NFL only)
            if "pass_yds" in team_db[team1] and "pass_yds" in team_db[team2]:
                analysis["passing_analysis"] = {
                    "team1_pass": team_db[team1]["pass_yds"],
                    "team2_pass": team_db[team2]["pass_yds"],
                    "passing_advantage": team1 if team_db[team1]["pass_yds"] > team_db[team2]["pass_yds"] else team2
                }
            
            # Rushing analysis (NFL only)
            if "rush_yds" in team_db[team1] and "rush_yds" in team_db[team2]:
                analysis["rushing_analysis"] = {
                    "team1_rush": team_db[team1]["rush_yds"],
                    "team2_rush": team_db[team2]["rush_yds"],
                    "rushing_advantage": team1 if team_db[team1]["rush_yds"] > team_db[team2]["rush_yds"] else team2
                }
        
        # Weather analysis
        analysis["weather_analysis"] = {
            "temperature": random.randint(20, 80),
            "wind_speed": random.randint(0, 25),
            "precipitation": random.choice(["none", "light", "moderate", "heavy"]),
            "field_condition": random.choice(["dry", "wet", "snow", "muddy"]),
            "wind_impact": "high" if random.randint(0, 25) > 15 else "low"
        }
        
        # Historical data
        analysis["historical_data"] = {
            "head_to_head": {"team1_wins": random.randint(3, 8), "team2_wins": random.randint(3, 8)},
            "recent_form": {"team1_last_5": random.randint(2, 5), "team2_last_5": random.randint(2, 5)},
            "home_away": {"team1_home": f"{random.randint(4, 8)}-{random.randint(1, 4)}", 
                         "team2_away": f"{random.randint(3, 7)}-{random.randint(2, 5)}"}
        }
        
        # Key metrics
        analysis["key_metrics"] = {
            "turnover_margin": random.uniform(-10, 10),
            "red_zone_efficiency": random.uniform(0.60, 0.85),
            "third_down_conversion": random.uniform(0.30, 0.50),
            "time_of_possession": random.uniform(28, 32),
            "sack_rate": random.uniform(0.05, 0.12)
        }
        
        return analysis
    
    async def get_sport_specific_prediction(self, analysis: Dict[str, Any]) -> str:
        """Generate NFL/NCAAF-specific prediction based on analysis."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Chiefs -7.5 (Home field advantage)"
        
        team1, team2 = teams[0], teams[1]
        league = analysis.get("league", "NFL")
        
        # Get team database
        team_db = self.nfl_teams if league == "NFL" else self.ncaaf_teams
        
        # Calculate expected total
        total_points = analysis.get("offensive_analysis", {}).get("total_points_expected", 45)
        
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
        
        # Adjust for home field advantage (3 points in NFL, 2.5 in NCAAF)
        home_advantage = 3 if league == "NFL" else 2.5
        adjusted_margin = expected_margin + home_advantage
        
        if adjusted_margin > 7:
            predictions.append(f"{team1} -{adjusted_margin:.1f} (Home advantage + offensive edge)")
        elif adjusted_margin < -7:
            predictions.append(f"{team2} -{abs(adjusted_margin):.1f} (Road team advantage)")
        else:
            predictions.append(f"{team1} +{abs(adjusted_margin):.1f} (Close game)")
        
        # Total points prediction
        if total_points > 50:
            predictions.append(f"Over {total_points:.1f} points (High-scoring matchup)")
        else:
            predictions.append(f"Under {total_points:.1f} points (Defensive battle)")
        
        # First half prediction
        first_half_total = total_points * 0.52  # Typically 52% of total in football
        if first_half_total > 25:
            predictions.append(f"First half over {first_half_total:.1f} points")
        else:
            predictions.append(f"First half under {first_half_total:.1f} points")
        
        # Weather-based predictions
        weather = analysis.get("weather_analysis", {})
        if weather.get("wind_speed", 0) > 15:
            predictions.append(f"Under {total_points * 0.9:.1f} points (Windy conditions)")
        
        if weather.get("precipitation") in ["moderate", "heavy"]:
            predictions.append(f"Under {total_points * 0.85:.1f} points (Weather impact)")
        
        return predictions[0]
    
    async def calculate_confidence(self, analysis: Dict[str, Any]) -> PredictionConfidence:
        """Calculate confidence level based on football analysis."""
        confidence_score = 0
        
        # Offensive advantage
        offensive_advantage = analysis.get("offensive_analysis", {}).get("offensive_advantage")
        if offensive_advantage:
            confidence_score += 2
        
        # Defensive advantage
        defensive_advantage = analysis.get("defensive_analysis", {}).get("defensive_advantage")
        if defensive_advantage:
            confidence_score += 2
        
        # Weather factors
        weather = analysis.get("weather_analysis", {})
        if weather.get("wind_speed", 0) < 10 and weather.get("precipitation") == "none":
            confidence_score += 1  # Good weather increases confidence
        
        # Recent form
        recent_form = analysis.get("historical_data", {}).get("recent_form", {})
        if recent_form.get("team1_last_5", 3) >= 4 or recent_form.get("team2_last_5", 3) >= 4:
            confidence_score += 2
        
        # Turnover margin
        turnover_margin = abs(analysis.get("key_metrics", {}).get("turnover_margin", 0))
        if turnover_margin > 5:
            confidence_score += 1
        
        # Red zone efficiency
        red_zone_eff = analysis.get("key_metrics", {}).get("red_zone_efficiency", 0.70)
        if red_zone_eff > 0.75 or red_zone_eff < 0.65:
            confidence_score += 1
        
        # Determine confidence level
        if confidence_score >= 6:
            return PredictionConfidence.HIGH
        elif confidence_score >= 3:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    async def generate_reasoning(self, analysis: Dict[str, Any], prediction: str) -> str:
        """Generate detailed reasoning for the football prediction."""
        teams = analysis.get("teams_analyzed", [])
        if len(teams) < 2:
            return "Analysis based on general football trends and team performance metrics."
        
        team1, team2 = teams[0], teams[1]
        league = analysis.get("league", "NFL")
        
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
        
        # Weather impact
        weather = analysis.get("weather_analysis", {})
        if weather.get("wind_speed", 0) > 15:
            reasoning_parts.append(f"Weather factor: {weather.get('wind_speed')} mph winds may impact passing game.")
        
        if weather.get("precipitation") in ["moderate", "heavy"]:
            reasoning_parts.append(f"Weather factor: {weather.get('precipitation')} precipitation expected.")
        
        # Recent form
        recent = analysis.get("historical_data", {}).get("recent_form", {})
        if recent:
            reasoning_parts.append(f"Recent form: {team1} {recent.get('team1_last_5', 3)}-{5-recent.get('team1_last_5', 3)} last 5, {team2} {recent.get('team2_last_5', 3)}-{5-recent.get('team2_last_5', 3)} last 5.")
        
        return " ".join(reasoning_parts) if reasoning_parts else f"Analysis based on comprehensive {league} metrics and team performance data."
    
    async def find_betting_opportunities(self) -> List[Dict[str, Any]]:
        """Find upcoming betting opportunities for NFL/NCAAF."""
        opportunities = []
        
        # Simulate finding 1-3 upcoming games
        num_games = random.randint(1, 3)
        
        # Decide if NFL or NCAAF for this scan
        league = "NFL" if random.random() > 0.4 else "NCAAF"
        teams_db = self.nfl_teams if league == "NFL" else self.ncaaf_teams
        teams = list(teams_db.keys())
        
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
                "query_text": f"{league} prediction for {t1} vs {t2}",
                "context": "Autonomous Market Scan",
                "league": league
            }
            opportunities.append(game)
            
        return opportunities

    async def get_sport_specific_insights(self) -> Dict[str, Any]:
        """Get NFL/NCAAF-specific insights and statistics."""
        base_insights = await super().get_sport_specific_insights()
        
        # Add football-specific insights
        football_insights = {
            "league": "NFL/NCAAF",
            "nfl_teams_tracked": len(self.nfl_teams),
            "ncaaf_teams_tracked": len(self.ncaaf_teams),
            "players_tracked": len(self.player_stats),
            "betting_types": self.betting_types,
            "top_nfl_teams": sorted(self.nfl_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_ncaaf_teams": sorted(self.ncaaf_teams.items(), key=lambda x: x[1]["wins"], reverse=True)[:3],
            "top_qbs": sorted(self.player_stats.items(), key=lambda x: x[1].get("pass_yds", 0), reverse=True)[:3]
        }
        
        base_insights.update(football_insights)
        return base_insights 