#!/usr/bin/env python3
"""
Hockey Betting System - YOLO MODE!
==================================
NHL-specific betting system with 5 AI council structure.
Features comprehensive hockey analytics, real-time predictions, and YOLO mode.
"""

import asyncio
import json
import random
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

class HockeyCouncilMember(str, Enum):
    """5 AI Council Members for Hockey Analysis."""
    OFFENSIVE_SPECIALIST = "offensive_specialist"
    DEFENSIVE_ANALYST = "defensive_analyst"
    GOALIE_EXPERT = "goalie_expert"
    SPECIAL_TEAMS_COACH = "special_teams_coach"
    MOMENTUM_READER = "momentum_reader"

@dataclass
class HockeyTeam:
    """NHL Team data structure."""
    name: str
    wins: int
    losses: int
    goals_for: int
    goals_against: int
    power_play: float
    penalty_kill: float
    home_record: str
    away_record: str
    last_10: str
    conference: str
    division: str

@dataclass
class HockeyPlayer:
    """NHL Player data structure."""
    name: str
    team: str
    position: str
    goals: int
    assists: int
    points: int
    plus_minus: int
    time_on_ice: str

@dataclass
class HockeyGoalie:
    """NHL Goalie data structure."""
    name: str
    team: str
    wins: int
    losses: int
    gaa: float
    save_pct: float
    shutouts: int

@dataclass
class CouncilAnalysis:
    """Analysis from each council member."""
    council_member: HockeyCouncilMember
    analysis: Dict[str, Any]
    confidence: float
    recommendation: str
    reasoning: str

@dataclass
class HockeyPrediction:
    """Complete hockey prediction with council analysis."""
    id: str
    teams: List[str]
    prediction_type: str
    prediction: str
    confidence: float
    council_analysis: List[CouncilAnalysis]
    yolo_factor: float
    timestamp: datetime.datetime
    odds: Optional[Dict[str, float]] = None

class HockeyBettingSystem:
    """Comprehensive NHL betting system with 5 AI council."""
    
    def __init__(self):
        self.system_name = "Hockey Betting System - YOLO MODE"
        self.version = "1.0.0-yolo"
        self.council_members = list(HockeyCouncilMember)
        
        # NHL Teams Database
        self.nhl_teams = {
            "Bruins": HockeyTeam("Bruins", 65, 12, 305, 177, 22.2, 87.3, "35-6-0", "30-6-0", "8-2-0", "Eastern", "Atlantic"),
            "Lightning": HockeyTeam("Lightning", 46, 30, 283, 254, 25.4, 79.7, "25-15-0", "21-15-0", "6-4-0", "Eastern", "Atlantic"),
            "Maple Leafs": HockeyTeam("Maple Leafs", 50, 21, 279, 222, 23.5, 81.9, "28-10-0", "22-11-0", "7-3-0", "Eastern", "Atlantic"),
            "Oilers": HockeyTeam("Oilers", 50, 23, 325, 260, 32.4, 75.5, "26-12-0", "24-11-0", "8-2-0", "Western", "Pacific"),
            "Rangers": HockeyTeam("Rangers", 47, 22, 254, 207, 24.1, 82.0, "25-11-0", "22-11-0", "6-4-0", "Eastern", "Metropolitan"),
            "Devils": HockeyTeam("Devils", 52, 22, 291, 236, 21.9, 82.6, "28-10-0", "24-12-0", "7-3-0", "Eastern", "Metropolitan"),
            "Avalanche": HockeyTeam("Avalanche", 51, 24, 280, 226, 24.8, 80.1, "28-10-0", "23-14-0", "7-3-0", "Western", "Central"),
            "Golden Knights": HockeyTeam("Golden Knights", 51, 22, 272, 229, 20.3, 77.4, "28-10-0", "23-12-0", "8-2-0", "Western", "Pacific"),
            "Stars": HockeyTeam("Stars", 47, 21, 285, 218, 23.1, 82.5, "26-10-0", "21-11-0", "6-4-0", "Western", "Central"),
            "Hurricanes": HockeyTeam("Hurricanes", 52, 21, 266, 213, 19.8, 84.4, "28-10-0", "24-11-0", "7-3-0", "Eastern", "Metropolitan"),
            "Penguins": HockeyTeam("Penguins", 40, 31, 262, 264, 21.7, 79.8, "22-15-0", "18-16-0", "5-5-0", "Eastern", "Metropolitan"),
            "Capitals": HockeyTeam("Capitals", 35, 37, 229, 263, 17.8, 78.9, "20-17-0", "15-20-0", "4-6-0", "Eastern", "Metropolitan"),
            "Jets": HockeyTeam("Jets", 46, 33, 247, 225, 23.4, 82.3, "25-15-0", "21-18-0", "6-4-0", "Western", "Central"),
            "Wild": HockeyTeam("Wild", 46, 25, 246, 218, 24.7, 82.1, "25-12-0", "21-13-0", "7-3-0", "Western", "Central"),
            "Flames": HockeyTeam("Flames", 38, 27, 232, 226, 20.1, 81.2, "20-14-0", "18-13-0", "5-5-0", "Western", "Pacific"),
            "Kings": HockeyTeam("Kings", 47, 25, 280, 222, 25.1, 81.8, "25-12-0", "22-13-0", "7-3-0", "Western", "Pacific")
        }
        
        # NHL Players Database
        self.nhl_players = {
            "Connor McDavid": HockeyPlayer("Connor McDavid", "Oilers", "C", 64, 89, 153, 35, "22:23"),
            "Leon Draisaitl": HockeyPlayer("Leon Draisaitl", "Oilers", "C", 52, 76, 128, 28, "21:45"),
            "David Pastrnak": HockeyPlayer("David Pastrnak", "Bruins", "RW", 61, 52, 113, 34, "20:12"),
            "Nathan MacKinnon": HockeyPlayer("Nathan MacKinnon", "Avalanche", "C", 42, 69, 111, 22, "21:34"),
            "Mikko Rantanen": HockeyPlayer("Mikko Rantanen", "Avalanche", "RW", 55, 50, 105, 25, "20:56"),
            "Auston Matthews": HockeyPlayer("Auston Matthews", "Maple Leafs", "C", 40, 45, 85, 31, "20:33"),
            "Mitch Marner": HockeyPlayer("Mitch Marner", "Maple Leafs", "RW", 30, 69, 99, 32, "21:12"),
            "Nikita Kucherov": HockeyPlayer("Nikita Kucherov", "Lightning", "RW", 30, 83, 113, 15, "21:45"),
            "Steven Stamkos": HockeyPlayer("Steven Stamkos", "Lightning", "C", 34, 50, 84, 12, "19:23"),
            "Artemi Panarin": HockeyPlayer("Artemi Panarin", "Rangers", "LW", 29, 63, 92, 18, "20:45")
        }
        
        # NHL Goalies Database
        self.nhl_goalies = {
            "Linus Ullmark": HockeyGoalie("Linus Ullmark", "Bruins", 40, 6, 1.89, 0.938, 2),
            "Igor Shesterkin": HockeyGoalie("Igor Shesterkin", "Rangers", 37, 13, 2.48, 0.916, 3),
            "Connor Hellebuyck": HockeyGoalie("Connor Hellebuyck", "Jets", 37, 25, 2.49, 0.920, 4),
            "Andrei Vasilevskiy": HockeyGoalie("Andrei Vasilevskiy", "Lightning", 34, 24, 2.65, 0.915, 2),
            "Jake Oettinger": HockeyGoalie("Jake Oettinger", "Stars", 36, 11, 2.37, 0.919, 5),
            "Juuse Saros": HockeyGoalie("Juuse Saros", "Predators", 33, 23, 2.69, 0.919, 3),
            "Ilya Sorokin": HockeyGoalie("Ilya Sorokin", "Islanders", 31, 22, 2.34, 0.924, 6),
            "Frederik Andersen": HockeyGoalie("Frederik Andersen", "Hurricanes", 21, 11, 2.48, 0.903, 1)
        }
        
        # Betting Types
        self.betting_types = [
            "moneyline", "puck_line", "total_goals", "first_period", 
            "player_props", "period_bets", "power_play_goals", "penalty_kill_success"
        ]
        
        # Prediction History
        self.prediction_history: List[HockeyPrediction] = []
        self.yolo_mode_active = True

    async def council_offensive_specialist(self, team1: str, team2: str) -> CouncilAnalysis:
        """Offensive Specialist Council Member Analysis."""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate offensive metrics
        team1_offense_score = (team1_data.goals_for * 0.4 + 
                              team1_data.power_play * 0.3 + 
                              (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.3)
        
        team2_offense_score = (team2_data.goals_for * 0.4 + 
                              team2_data.power_play * 0.3 + 
                              (team2_data.wins / (team2_data.wins + team2_data.losses)) * 0.3)
        
        offensive_advantage = team1 if team1_offense_score > team2_offense_score else team2
        confidence = min(abs(team1_offense_score - team2_offense_score) / 10, 0.95)
        
        analysis = {
            "team1_offense_score": round(team1_offense_score, 2),
            "team2_offense_score": round(team2_offense_score, 2),
            "offensive_advantage": offensive_advantage,
            "goals_for_comparison": f"{team1}: {team1_data.goals_for} vs {team2}: {team2_data.goals_for}",
            "power_play_comparison": f"{team1}: {team1_data.power_play}% vs {team2}: {team2_data.power_play}%"
        }
        
        recommendation = f"{offensive_advantage} ML (Offensive advantage: {offensive_advantage} scores {round(max(team1_data.goals_for, team2_data.goals_for))} goals/game)"
        
        reasoning = f"Offensive analysis shows {offensive_advantage} has superior scoring ability with {round(max(team1_data.goals_for, team2_data.goals_for))} goals per game and {round(max(team1_data.power_play, team2_data.power_play), 1)}% power play efficiency."
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.OFFENSIVE_SPECIALIST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )

    async def council_defensive_analyst(self, team1: str, team2: str) -> CouncilAnalysis:
        """Defensive Analyst Council Member Analysis."""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate defensive metrics
        team1_defense_score = (team1_data.penalty_kill * 0.4 + 
                              (1 / team1_data.goals_against) * 1000 * 0.4 + 
                              (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.2)
        
        team2_defense_score = (team2_data.penalty_kill * 0.4 + 
                              (1 / team2_data.goals_against) * 1000 * 0.4 + 
                              (team2_data.wins / (team2_data.wins + team2_data.losses)) * 0.2)
        
        defensive_advantage = team1 if team1_defense_score > team2_defense_score else team2
        confidence = min(abs(team1_defense_score - team2_defense_score) / 10, 0.95)
        
        analysis = {
            "team1_defense_score": round(team1_defense_score, 2),
            "team2_defense_score": round(team2_defense_score, 2),
            "defensive_advantage": defensive_advantage,
            "goals_against_comparison": f"{team1}: {team1_data.goals_against} vs {team2}: {team2_data.goals_against}",
            "penalty_kill_comparison": f"{team1}: {team1_data.penalty_kill}% vs {team2}: {team2_data.penalty_kill}%"
        }
        
        recommendation = f"Under {round((team1_data.goals_against + team2_data.goals_against) / 2 + 1)} total goals (Defensive matchup)"
        
        reasoning = f"Defensive analysis shows {defensive_advantage} has superior defensive metrics with {round(min(team1_data.goals_against, team2_data.goals_against))} goals against per game and {round(max(team1_data.penalty_kill, team2_data.penalty_kill), 1)}% penalty kill efficiency."
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.DEFENSIVE_ANALYST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )

    async def council_goalie_expert(self, team1: str, team2: str) -> CouncilAnalysis:
        """Goalie Expert Council Member Analysis."""
        # Find best goalies for each team
        team1_goalies = [g for g in self.nhl_goalies.values() if g.team == team1]
        team2_goalies = [g for g in self.nhl_goalies.values() if g.team == team2]
        
        if not team1_goalies or not team2_goalies:
            # Use default analysis if no goalie data
            return CouncilAnalysis(
                council_member=HockeyCouncilMember.GOALIE_EXPERT,
                analysis={"note": "Insufficient goalie data"},
                confidence=0.5,
                recommendation=f"{team1} ML (Home ice advantage)",
                reasoning="Goalie data unavailable, defaulting to home ice advantage."
            )
        
        # Get best goalie for each team (lowest GAA)
        team1_best = min(team1_goalies, key=lambda x: x.gaa)
        team2_best = min(team2_goalies, key=lambda x: x.gaa)
        
        goalie_advantage = team1 if team1_best.gaa < team2_best.gaa else team2
        confidence = min(abs(team1_best.gaa - team2_best.gaa) * 10, 0.95)
        
        analysis = {
            "team1_goalie": f"{team1_best.name} (GAA: {team1_best.gaa}, SV%: {team1_best.save_pct})",
            "team2_goalie": f"{team2_best.name} (GAA: {team2_best.gaa}, SV%: {team2_best.save_pct})",
            "goalie_advantage": goalie_advantage,
            "gaa_comparison": f"{team1}: {team1_best.gaa} vs {team2}: {team2_best.gaa}",
            "save_pct_comparison": f"{team1}: {team1_best.save_pct} vs {team2}: {team2_best.save_pct}"
        }
        
        recommendation = f"{goalie_advantage} ML (Goalie advantage: {goalie_advantage} has superior netminder)"
        
        reasoning = f"Goalie analysis shows {goalie_advantage} has the superior netminder with {round(min(team1_best.gaa, team2_best.gaa), 2)} GAA and {round(max(team1_best.save_pct, team2_best.save_pct), 3)} save percentage."
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.GOALIE_EXPERT,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )

    async def council_special_teams_coach(self, team1: str, team2: str) -> CouncilAnalysis:
        """Special Teams Coach Council Member Analysis."""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate special teams advantage
        team1_special_teams = (team1_data.power_play + team1_data.penalty_kill) / 2
        team2_special_teams = (team2_data.power_play + team2_data.penalty_kill) / 2
        
        special_teams_advantage = team1 if team1_special_teams > team2_special_teams else team2
        confidence = min(abs(team1_special_teams - team2_special_teams) / 10, 0.95)
        
        analysis = {
            "team1_special_teams_score": round(team1_special_teams, 1),
            "team2_special_teams_score": round(team2_special_teams, 1),
            "special_teams_advantage": special_teams_advantage,
            "power_play_advantage": team1 if team1_data.power_play > team2_data.power_play else team2,
            "penalty_kill_advantage": team1 if team1_data.penalty_kill > team2_data.penalty_kill else team2
        }
        
        if team1_data.power_play > 25 or team2_data.power_play > 25:
            recommendation = f"{special_teams_advantage} power play goal (PP advantage)"
        else:
            recommendation = f"{special_teams_advantage} ML (Special teams advantage)"
        
        reasoning = f"Special teams analysis shows {special_teams_advantage} has superior special teams play with {round(max(team1_data.power_play, team2_data.power_play), 1)}% power play and {round(max(team1_data.penalty_kill, team2_data.penalty_kill), 1)}% penalty kill."
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.SPECIAL_TEAMS_COACH,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )

    async def council_momentum_reader(self, team1: str, team2: str) -> CouncilAnalysis:
        """Momentum Reader Council Member Analysis."""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate momentum metrics (recent form, home/away performance)
        team1_momentum = (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.6 + 0.4  # Home advantage
        team2_momentum = (team2_data.wins / (team1_data.wins + team1_data.losses)) * 0.6 + 0.2  # Away disadvantage
        
        momentum_advantage = team1 if team1_momentum > team2_momentum else team2
        confidence = min(abs(team1_momentum - team2_momentum) * 2, 0.95)
        
        analysis = {
            "team1_momentum_score": round(team1_momentum, 3),
            "team2_momentum_score": round(team2_momentum, 3),
            "momentum_advantage": momentum_advantage,
            "home_advantage": "Team 1 has home ice advantage",
            "recent_form": f"{team1}: {team1_data.last_10} vs {team2}: {team2_data.last_10}"
        }
        
        recommendation = f"{momentum_advantage} ML (Momentum advantage + home ice)"
        
        reasoning = f"Momentum analysis shows {momentum_advantage} has the momentum advantage with home ice factor and recent form of {team1_data.last_10} vs {team2_data.last_10}."
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.MOMENTUM_READER,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )

    async def create_hockey_prediction(self, team1: str, team2: str, prediction_type: str = "moneyline") -> HockeyPrediction:
        """Create comprehensive hockey prediction with all council members."""
        prediction_id = f"hockey_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Get analysis from all council members
        council_analyses = [
            await self.council_offensive_specialist(team1, team2),
            await self.council_defensive_analyst(team1, team2),
            await self.council_goalie_expert(team1, team2),
            await self.council_special_teams_coach(team1, team2),
            await self.council_momentum_reader(team1, team2)
        ]
        
        # Calculate overall confidence
        total_confidence = sum(analysis.confidence for analysis in council_analyses) / len(council_analyses)
        
        # Apply YOLO factor
        yolo_factor = 1.5 if self.yolo_mode_active else 1.0
        adjusted_confidence = min(total_confidence * yolo_factor, 0.95)
        
        # Determine final prediction based on council consensus
        recommendations = [analysis.recommendation for analysis in council_analyses]
        team1_votes = sum(1 for rec in recommendations if team1 in rec)
        team2_votes = sum(1 for rec in recommendations if team2 in rec)
        
        if team1_votes > team2_votes:
            final_prediction = f"{team1} ML (Council consensus: {team1_votes}-{team2_votes})"
        elif team2_votes > team1_votes:
            final_prediction = f"{team2} ML (Council consensus: {team2_votes}-{team1_votes})"
        else:
            final_prediction = f"{team1} ML (Tiebreaker: Home ice advantage)"
        
        prediction = HockeyPrediction(
            id=prediction_id,
            teams=[team1, team2],
            prediction_type=prediction_type,
            prediction=final_prediction,
            confidence=adjusted_confidence,
            council_analysis=council_analyses,
            yolo_factor=yolo_factor,
            timestamp=datetime.datetime.now(),
            odds={"team1": 1.85, "team2": 2.10, "draw": 3.50}
        )
        
        # Store in history
        self.prediction_history.append(prediction)
        
        return prediction

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics."""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "status": "operational",
            "yolo_mode": self.yolo_mode_active,
            "council_members": len(self.council_members),
            "teams_in_database": len(self.nhl_teams),
            "players_in_database": len(self.nhl_players),
            "goalies_in_database": len(self.nhl_goalies),
            "total_predictions": len(self.prediction_history),
            "timestamp": datetime.datetime.now().isoformat()
        }

    async def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent predictions."""
        recent = self.prediction_history[-limit:] if self.prediction_history else []
        return [
            {
                "id": p.id,
                "teams": p.teams,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "yolo_factor": p.yolo_factor,
                "timestamp": p.timestamp.isoformat()
            }
            for p in recent
        ]

# Create Starlette app for the hockey system
hockey_system = HockeyBettingSystem()

async def root(request: Request):
    """Root endpoint."""
    return JSONResponse({
        "message": "Hockey Betting System - YOLO MODE!",
        "system": hockey_system.system_name,
        "version": hockey_system.version,
        "status": "operational",
        "council_members": len(hockey_system.council_members),
        "timestamp": datetime.datetime.now().isoformat()
    })

async def health(request: Request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "system": "hockey_betting_system",
        "yolo_mode": hockey_system.yolo_mode_active,
        "timestamp": datetime.datetime.now().isoformat()
    })

async def status(request: Request):
    """System status endpoint."""
    status_data = await hockey_system.get_system_status()
    return JSONResponse(status_data)

async def predict(request: Request):
    """Prediction endpoint."""
    try:
        body = await request.json()
        team1 = body.get("team1", "Bruins")
        team2 = body.get("team2", "Lightning")
        prediction_type = body.get("prediction_type", "moneyline")
        
        if team1 not in hockey_system.nhl_teams or team2 not in hockey_system.nhl_teams:
            return JSONResponse({
                "error": "Invalid team names",
                "available_teams": list(hockey_system.nhl_teams.keys())
            }, status_code=400)
        
        prediction = await hockey_system.create_hockey_prediction(team1, team2, prediction_type)
        
        return JSONResponse({
            "prediction_id": prediction.id,
            "teams": prediction.teams,
            "prediction": prediction.prediction,
            "confidence": prediction.confidence,
            "yolo_factor": prediction.yolo_factor,
            "council_analysis": [
                {
                    "member": analysis.council_member.value,
                    "recommendation": analysis.recommendation,
                    "confidence": analysis.confidence,
                    "reasoning": analysis.reasoning
                }
                for analysis in prediction.council_analysis
            ],
            "timestamp": prediction.timestamp.isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Prediction failed: {str(e)}"
        }, status_code=500)

async def teams(request: Request):
    """Get all teams endpoint."""
    return JSONResponse({
        "teams": list(hockey_system.nhl_teams.keys()),
        "count": len(hockey_system.nhl_teams)
    })

async def recent_predictions(request: Request):
    """Get recent predictions endpoint."""
    limit = int(request.query_params.get("limit", 10))
    predictions = await hockey_system.get_recent_predictions(limit)
    return JSONResponse({
        "predictions": predictions,
        "count": len(predictions)
    })

# Create Starlette app
app = Starlette(routes=[
    Route("/", root, methods=["GET"]),
    Route("/health", health, methods=["GET"]),
    Route("/api/v1/status", status, methods=["GET"]),
    Route("/api/v1/predict", predict, methods=["POST"]),
    Route("/api/v1/teams", teams, methods=["GET"]),
    Route("/api/v1/recent-predictions", recent_predictions, methods=["GET"])
])

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

def main():
    """Main function to start the hockey betting system."""
    print("🏒 Starting Hockey Betting System - YOLO MODE!")
    print("=" * 60)
    print(f"System: {hockey_system.system_name}")
    print(f"Version: {hockey_system.version}")
    print(f"Council Members: {len(hockey_system.council_members)}")
    print(f"NHL Teams: {len(hockey_system.nhl_teams)}")
    print(f"Players: {len(hockey_system.nhl_players)}")
    print(f"Goalies: {len(hockey_system.nhl_goalies)}")
    print("=" * 60)
    
    host = "0.0.0.0"
    port = 8005  # Hockey system port
    
    print(f"Server: {host}:{port}")
    print(f"Health: http://localhost:{port}/health")
    print(f"Status: http://localhost:{port}/api/v1/status")
    print(f"Teams: http://localhost:{port}/api/v1/teams")
    print("=" * 60)
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main() 