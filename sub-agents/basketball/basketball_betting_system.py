#!/usr/bin/env python3
"""
Basketball Betting System - YOLO MODE!
======================================
NBA-specific betting system with 5 AI council structure.
Features comprehensive basketball analytics, real-time predictions, and YOLO mode.
Now with MULTIDIMENSIONAL PERFORMANCE TRACKING SERVICE!
"""

import asyncio
import json
import random
import datetime
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

class BasketballCouncilMember(str, Enum):
    """5 AI Council Members for Basketball Analysis - YOLO MODE!"""
    OFFENSIVE_SPECIALIST = "offensive_specialist"
    DEFENSIVE_ANALYST = "defensive_analyst"
    THREE_POINT_EXPERT = "three_point_expert"
    REBOUNDING_COACH = "rebounding_coach"
    MOMENTUM_READER = "momentum_reader"

# ============================================================================
# MULTIDIMENSIONAL PERFORMANCE TRACKING SERVICE - YOLO MODE!
# ============================================================================

@dataclass
class BettingPerformance:
    """Individual betting performance tracking - YOLO MODE!"""
    user_id: str
    bet_id: str
    sport: str = "basketball"
    bet_type: str = ""
    teams: List[str] = field(default_factory=list)
    prediction: str = ""
    actual_result: str = ""
    bet_amount: float = 0.0
    payout: float = 0.0
    odds: float = 0.0
    confidence: float = 0.0
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    council_analysis: List[Dict[str, Any]] = field(default_factory=list)
    yolo_factor: float = 1.0
    success: bool = False
    roi: float = 0.0

@dataclass
class UserPerformanceMetrics:
    """Comprehensive user performance metrics - YOLO MODE!"""
    user_id: str
    total_bets: int = 0
    wins: int = 0
    losses: int = 0
    total_bet_amount: float = 0.0
    total_payout: float = 0.0
    overall_roi: float = 0.0
    win_rate: float = 0.0
    average_confidence: float = 0.0
    average_yolo_factor: float = 0.0
    current_streak: int = 0
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    best_bet_type: str = ""
    worst_bet_type: str = ""
    favorite_teams: List[str] = field(default_factory=list)
    council_performance: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class PerformanceInsights:
    """AI-generated performance insights - YOLO MODE!"""
    user_id: str
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_assessment: str = ""
    pattern_analysis: Dict[str, Any] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    generated_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class StreakAnalysis:
    """Advanced streak and pattern analysis - YOLO MODE!"""
    user_id: str
    current_win_streak: int = 0
    current_loss_streak: int = 0
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    streak_patterns: List[Dict[str, Any]] = field(default_factory=list)
    momentum_score: float = 0.0
    volatility_index: float = 0.0
    hot_cold_cycles: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ROIAnalysis:
    """Comprehensive ROI analysis - YOLO MODE!"""
    user_id: str
    overall_roi: float = 0.0
    roi_by_bet_type: Dict[str, float] = field(default_factory=dict)
    roi_by_team: Dict[str, float] = field(default_factory=dict)
    roi_by_confidence: Dict[str, float] = field(default_factory=dict)
    roi_by_council: Dict[str, float] = field(default_factory=dict)
    roi_trends: List[Dict[str, Any]] = field(default_factory=list)
    breakeven_analysis: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# ORIGINAL BASKETBALL DATA STRUCTURES
# ============================================================================

@dataclass
class BasketballTeam:
    """NBA Team data structure - YOLO MODE!"""
    name: str
    wins: int
    losses: int
    points_per_game: float
    points_allowed: float
    field_goal_pct: float
    three_point_pct: float
    free_throw_pct: float
    rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    turnovers_per_game: float
    home_record: str
    away_record: str
    last_10: str
    conference: str
    division: str
    yolo_factor: float = 1.5

@dataclass
class BasketballPlayer:
    """NBA Player data structure - YOLO MODE!"""
    name: str
    team: str
    position: str
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    field_goal_pct: float
    three_point_pct: float
    free_throw_pct: float
    minutes_per_game: float
    yolo_boost: float = 1.3

@dataclass
class BasketballGame:
    """NBA Game data structure - YOLO MODE!"""
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    total_points: int
    home_three_pointers: int
    away_three_pointers: int
    home_rebounds: int
    away_rebounds: int
    home_assists: int
    away_assists: int
    yolo_factor: float = 1.4

@dataclass
class CouncilAnalysis:
    """Analysis from each council member - YOLO MODE!"""
    council_member: BasketballCouncilMember
    analysis: Dict[str, Any]
    confidence: float
    recommendation: str
    reasoning: str
    yolo_boost: float = 1.5

@dataclass
class BasketballPrediction:
    """Complete basketball prediction with council analysis - YOLO MODE!"""
    id: str
    teams: List[str]
    prediction_type: str
    prediction: str
    confidence: float
    council_analysis: List[CouncilAnalysis]
    yolo_factor: float
    timestamp: datetime.datetime
    odds: Optional[Dict[str, float]] = None
    yolo_mode: bool = True

class BasketballBettingSystem:
    """Comprehensive NBA betting system with 5 AI council and PERFORMANCE TRACKING - YOLO MODE!"""
    
    def __init__(self):
        self.system_name = "Basketball Betting System - YOLO MODE!"
        self.version = "2.0.0-yolo-performance"
        self.sport_type = "basketball"
        self.yolo_mode_active = True
        self.total_predictions = 0
        self.recent_predictions: List[Dict[str, Any]] = []
        
        # ============================================================================
        # PERFORMANCE TRACKING DATABASE - YOLO MODE!
        # ============================================================================
        self.performance_database: Dict[str, BettingPerformance] = {}
        self.user_metrics: Dict[str, UserPerformanceMetrics] = {}
        self.performance_insights: Dict[str, PerformanceInsights] = {}
        self.streak_analysis: Dict[str, StreakAnalysis] = {}
        self.roi_analysis: Dict[str, ROIAnalysis] = {}
        
        # Performance tracking counters
        self.total_bets_tracked = 0
        self.total_users_tracked = 0
        self.performance_update_count = 0
        
        # ============================================================================
        # ORIGINAL BASKETBALL DATA
        # ============================================================================
        
        # NBA team stats (mock data) - YOLO MODE!
        self.nba_teams = {
            "Lakers": {"ppg": 115.5, "opp_ppg": 112.1, "fg_pct": 0.475, "3pt_pct": 0.350, "rpg": 45.2, "apg": 25.8, "spg": 7.5, "bpg": 5.1},
            "Celtics": {"ppg": 118.2, "opp_ppg": 110.8, "fg_pct": 0.482, "3pt_pct": 0.378, "rpg": 44.8, "apg": 26.5, "spg": 8.2, "bpg": 4.8},
            "Warriors": {"ppg": 116.8, "opp_ppg": 113.5, "fg_pct": 0.468, "3pt_pct": 0.365, "rpg": 43.9, "apg": 29.1, "spg": 7.8, "bpg": 4.2},
            "Nets": {"ppg": 114.7, "opp_ppg": 111.9, "fg_pct": 0.471, "3pt_pct": 0.372, "rpg": 44.1, "apg": 24.6, "spg": 7.1, "bpg": 4.9},
            "Heat": {"ppg": 112.3, "opp_ppg": 109.8, "fg_pct": 0.469, "3pt_pct": 0.358, "rpg": 42.8, "apg": 25.3, "spg": 8.5, "bpg": 3.8},
            "Bucks": {"ppg": 116.9, "opp_ppg": 111.2, "fg_pct": 0.476, "3pt_pct": 0.361, "rpg": 48.2, "apg": 24.7, "spg": 6.9, "bpg": 4.5},
            "Suns": {"ppg": 113.4, "opp_ppg": 110.1, "fg_pct": 0.473, "3pt_pct": 0.367, "rpg": 43.5, "apg": 27.2, "spg": 7.3, "bpg": 4.1},
            "Mavericks": {"ppg": 115.8, "opp_ppg": 112.7, "fg_pct": 0.470, "3pt_pct": 0.364, "rpg": 42.1, "apg": 23.8, "spg": 6.7, "bpg": 3.9},
            "Clippers": {"ppg": 113.9, "opp_ppg": 111.4, "fg_pct": 0.472, "3pt_pct": 0.369, "rpg": 44.7, "apg": 24.9, "spg": 7.6, "bpg": 4.3},
            "Nuggets": {"ppg": 117.2, "opp_ppg": 112.8, "fg_pct": 0.481, "3pt_pct": 0.375, "rpg": 45.8, "apg": 28.4, "spg": 7.2, "bpg": 4.7},
            "76ers": {"ppg": 114.6, "opp_ppg": 110.9, "fg_pct": 0.474, "3pt_pct": 0.363, "rpg": 43.9, "apg": 25.1, "spg": 7.8, "bpg": 4.6},
            "Knicks": {"ppg": 112.8, "opp_ppg": 109.5, "fg_pct": 0.467, "3pt_pct": 0.356, "rpg": 44.2, "apg": 23.7, "spg": 7.4, "bpg": 4.0},
            "Bulls": {"ppg": 113.1, "opp_ppg": 111.6, "fg_pct": 0.470, "3pt_pct": 0.360, "rpg": 43.8, "apg": 24.3, "spg": 7.9, "bpg": 4.4},
            "Hawks": {"ppg": 115.7, "opp_ppg": 113.2, "fg_pct": 0.468, "3pt_pct": 0.362, "rpg": 44.5, "apg": 26.8, "spg": 7.1, "bpg": 3.7},
            "Trail Blazers": {"ppg": 114.3, "opp_ppg": 112.0, "fg_pct": 0.465, "3pt_pct": 0.358, "rpg": 42.9, "apg": 24.5, "spg": 6.8, "bpg": 4.2}
        }
        
        # Player stats (mock data) - YOLO MODE!
        self.player_stats = {
            "LeBron James": {"ppg": 25.0, "rpg": 7.3, "apg": 8.5, "fg_pct": 0.500, "3pt_pct": 0.300, "ft_pct": 0.700, "team": "Lakers"},
            "Stephen Curry": {"ppg": 29.4, "rpg": 6.1, "apg": 6.3, "fg_pct": 0.492, "3pt_pct": 0.427, "ft_pct": 0.915, "team": "Warriors"},
            "Kevin Durant": {"ppg": 29.7, "rpg": 7.3, "apg": 5.8, "fg_pct": 0.556, "3pt_pct": 0.406, "ft_pct": 0.910, "team": "Suns"},
            "Giannis Antetokounmpo": {"ppg": 31.1, "rpg": 11.8, "apg": 5.7, "fg_pct": 0.553, "3pt_pct": 0.275, "ft_pct": 0.645, "team": "Bucks"},
            "Nikola Jokic": {"ppg": 24.5, "rpg": 11.8, "apg": 9.8, "fg_pct": 0.632, "3pt_pct": 0.383, "ft_pct": 0.821, "team": "Nuggets"},
            "Joel Embiid": {"ppg": 33.1, "rpg": 10.2, "apg": 4.2, "fg_pct": 0.548, "3pt_pct": 0.330, "ft_pct": 0.857, "team": "76ers"},
            "Luka Doncic": {"ppg": 32.4, "rpg": 8.6, "apg": 8.0, "fg_pct": 0.496, "3pt_pct": 0.342, "ft_pct": 0.742, "team": "Mavericks"},
            "Jayson Tatum": {"ppg": 30.1, "rpg": 8.8, "apg": 4.6, "fg_pct": 0.466, "3pt_pct": 0.350, "ft_pct": 0.854, "team": "Celtics"},
            "Damian Lillard": {"ppg": 32.2, "rpg": 4.8, "apg": 7.3, "fg_pct": 0.464, "3pt_pct": 0.371, "ft_pct": 0.914, "team": "Bucks"},
            "Anthony Davis": {"ppg": 24.7, "rpg": 12.3, "apg": 3.7, "fg_pct": 0.556, "3pt_pct": 0.257, "ft_pct": 0.784, "team": "Lakers"}
        }
        
        self.betting_types = [
            "moneyline", "spread", "total_points", "three_pointers", "rebounds", "assists", "steals", "blocks", "player_props"
        ]

    async def council_offensive_specialist(self, team1: str, team2: str) -> CouncilAnalysis:
        """Offensive Specialist Council Member Analysis - YOLO MODE!"""
        team1_data = self.nba_teams[team1]
        team2_data = self.nba_teams[team2]
        
        # Calculate offensive metrics with YOLO boost
        team1_offense_score = (team1_data.points_per_game * 0.4 + 
                              team1_data.field_goal_pct * 0.3 + 
                              team1_data.assists_per_game * 0.3) * team1_data.yolo_factor
        
        team2_offense_score = (team2_data.points_per_game * 0.4 + 
                              team2_data.field_goal_pct * 0.3 + 
                              team2_data.assists_per_game * 0.3) * team2_data.yolo_factor
        
        offensive_advantage = team1 if team1_offense_score > team2_offense_score else team2
        confidence = min(abs(team1_offense_score - team2_offense_score) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_offense_score": round(team1_offense_score, 2),
            "team2_offense_score": round(team2_offense_score, 2),
            "offensive_advantage": offensive_advantage,
            "points_comparison": f"{team1}: {team1_data.points_per_game} vs {team2}: {team2_data.points_per_game}",
            "fg_pct_comparison": f"{team1}: {team1_data.field_goal_pct}% vs {team2}: {team2_data.field_goal_pct}%",
            "yolo_factor": "OFFENSIVE DOMINANCE!"
        }
        
        recommendation = f"{offensive_advantage} ML (YOLO MODE: Offensive advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Offensive analysis shows {offensive_advantage} has superior scoring ability with {round(max(team1_data.points_per_game, team2_data.points_per_game), 1)} PPG and {round(max(team1_data.field_goal_pct, team2_data.field_goal_pct), 1)}% FG%. OFFENSIVE DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=BasketballCouncilMember.OFFENSIVE_SPECIALIST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.8
        )

    async def council_defensive_analyst(self, team1: str, team2: str) -> CouncilAnalysis:
        """Defensive Analyst Council Member Analysis - YOLO MODE!"""
        team1_data = self.nba_teams[team1]
        team2_data = self.nba_teams[team2]
        
        # Calculate defensive metrics with YOLO boost
        team1_defense_score = (1 / team1_data.points_allowed * 1000 * 0.4 + 
                              team1_data.steals_per_game * 0.3 + 
                              team1_data.blocks_per_game * 0.3) * team1_data.yolo_factor
        
        team2_defense_score = (1 / team2_data.points_allowed * 1000 * 0.4 + 
                              team2_data.steals_per_game * 0.3 + 
                              team2_data.blocks_per_game * 0.3) * team2_data.yolo_factor
        
        defensive_advantage = team1 if team1_defense_score > team2_defense_score else team2
        confidence = min(abs(team1_defense_score - team2_defense_score) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_defense_score": round(team1_defense_score, 2),
            "team2_defense_score": round(team2_defense_score, 2),
            "defensive_advantage": defensive_advantage,
            "points_allowed_comparison": f"{team1}: {team1_data.points_allowed} vs {team2}: {team2_data.points_allowed}",
            "steals_comparison": f"{team1}: {team1_data.steals_per_game} vs {team2}: {team2_data.steals_per_game}",
            "yolo_factor": "DEFENSIVE DOMINANCE!"
        }
        
        recommendation = f"Under {round((team1_data.points_allowed + team2_data.points_allowed) + 5)} total points (YOLO MODE: Defensive matchup with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Defensive analysis shows {defensive_advantage} has superior defensive metrics with {round(min(team1_data.points_allowed, team2_data.points_allowed), 1)} points allowed per game and {round(max(team1_data.steals_per_game, team2_data.steals_per_game), 1)} steals per game. DEFENSIVE DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=BasketballCouncilMember.DEFENSIVE_ANALYST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.7
        )

    async def council_three_point_expert(self, team1: str, team2: str) -> CouncilAnalysis:
        """Three Point Expert Council Member Analysis - YOLO MODE!"""
        team1_data = self.nba_teams[team1]
        team2_data = self.nba_teams[team2]
        
        # Calculate three-point metrics with YOLO boost
        team1_three_point_score = (team1_data.three_point_pct * 0.6 + 
                                  team1_data.points_per_game * 0.4) * team1_data.yolo_factor
        
        team2_three_point_score = (team2_data.three_point_pct * 0.6 + 
                                  team2_data.points_per_game * 0.4) * team2_data.yolo_factor
        
        three_point_advantage = team1 if team1_three_point_score > team2_three_point_score else team2
        confidence = min(abs(team1_three_point_score - team2_three_point_score) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_three_point_score": round(team1_three_point_score, 2),
            "team2_three_point_score": round(team2_three_point_score, 2),
            "three_point_advantage": three_point_advantage,
            "three_point_pct_comparison": f"{team1}: {team1_data.three_point_pct}% vs {team2}: {team2_data.three_point_pct}%",
            "yolo_factor": "THREE POINT DOMINANCE!"
        }
        
        if team1_data.three_point_pct > 38 or team2_data.three_point_pct > 38:
            recommendation = f"{three_point_advantage} three pointers (YOLO MODE: 3PT advantage with MAXIMUM CONFIDENCE!)"
        else:
            recommendation = f"{three_point_advantage} ML (YOLO MODE: Three-point advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Three-point analysis shows {three_point_advantage} has superior shooting with {round(max(team1_data.three_point_pct, team2_data.three_point_pct), 1)}% 3PT% and {round(max(team1_data.points_per_game, team2_data.points_per_game), 1)} PPG. THREE POINT DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=BasketballCouncilMember.THREE_POINT_EXPERT,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.9
        )

    async def council_rebounding_coach(self, team1: str, team2: str) -> CouncilAnalysis:
        """Rebounding Coach Council Member Analysis - YOLO MODE!"""
        team1_data = self.nba_teams[team1]
        team2_data = self.nba_teams[team2]
        
        # Calculate rebounding metrics with YOLO boost
        team1_rebounding_score = (team1_data.rebounds_per_game * 0.7 + 
                                 team1_data.blocks_per_game * 0.3) * team1_data.yolo_factor
        
        team2_rebounding_score = (team2_data.rebounds_per_game * 0.7 + 
                                 team2_data.blocks_per_game * 0.3) * team2_data.yolo_factor
        
        rebounding_advantage = team1 if team1_rebounding_score > team2_rebounding_score else team2
        confidence = min(abs(team1_rebounding_score - team2_rebounding_score) / 5, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_rebounding_score": round(team1_rebounding_score, 2),
            "team2_rebounding_score": round(team2_rebounding_score, 2),
            "rebounding_advantage": rebounding_advantage,
            "rebounds_comparison": f"{team1}: {team1_data.rebounds_per_game} vs {team2}: {team2_data.rebounds_per_game}",
            "blocks_comparison": f"{team1}: {team1_data.blocks_per_game} vs {team2}: {team2_data.blocks_per_game}",
            "yolo_factor": "REBOUNDING DOMINANCE!"
        }
        
        recommendation = f"{rebounding_advantage} rebounds (YOLO MODE: Rebounding advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Rebounding analysis shows {rebounding_advantage} has superior board control with {round(max(team1_data.rebounds_per_game, team2_data.rebounds_per_game), 1)} RPG and {round(max(team1_data.blocks_per_game, team2_data.blocks_per_game), 1)} BPG. REBOUNDING DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=BasketballCouncilMember.REBOUNDING_COACH,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.6
        )

    async def council_momentum_reader(self, team1: str, team2: str) -> CouncilAnalysis:
        """Momentum Reader Council Member Analysis - YOLO MODE!"""
        team1_data = self.nba_teams[team1]
        team2_data = self.nba_teams[team2]
        
        # Calculate momentum metrics with YOLO boost
        team1_momentum = (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.6 + 0.4  # Home advantage
        team2_momentum = (team2_data.wins / (team2_data.wins + team2_data.losses)) * 0.6 + 0.2  # Away disadvantage
        
        # Apply YOLO factors
        team1_momentum *= team1_data.yolo_factor
        team2_momentum *= team2_data.yolo_factor
        
        momentum_advantage = team1 if team1_momentum > team2_momentum else team2
        confidence = min(abs(team1_momentum - team2_momentum) * 2, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_momentum_score": round(team1_momentum, 3),
            "team2_momentum_score": round(team2_momentum, 3),
            "momentum_advantage": momentum_advantage,
            "home_advantage": "Team 1 has home court advantage",
            "recent_form": f"{team1}: {team1_data.last_10} vs {team2}: {team2_data.last_10}",
            "yolo_factor": "MOMENTUM DOMINANCE!"
        }
        
        recommendation = f"{momentum_advantage} ML (YOLO MODE: Momentum advantage + home court with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Momentum analysis shows {momentum_advantage} has the momentum advantage with home court factor and recent form of {team1_data.last_10} vs {team2_data.last_10}. MOMENTUM DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=BasketballCouncilMember.MOMENTUM_READER,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.7
        )

    async def create_basketball_prediction(self, team1: str, team2: str, prediction_type: str = "moneyline") -> BasketballPrediction:
        """Create comprehensive basketball prediction with all council members - YOLO MODE!"""
        prediction_id = f"basketball_yolo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Get analysis from all council members
        council_analyses = [
            await self.council_offensive_specialist(team1, team2),
            await self.council_defensive_analyst(team1, team2),
            await self.council_three_point_expert(team1, team2),
            await self.council_rebounding_coach(team1, team2),
            await self.council_momentum_reader(team1, team2)
        ]
        
        # Calculate overall confidence with YOLO boost
        total_confidence = sum(analysis.confidence for analysis in council_analyses) / len(council_analyses)
        
        # Apply YOLO factor
        yolo_factor = 2.0 if self.yolo_mode_active else 1.0  # Maximum YOLO!
        adjusted_confidence = min(total_confidence * yolo_factor, 0.98)  # Almost perfect!
        
        # Determine final prediction based on council consensus
        recommendations = [analysis.recommendation for analysis in council_analyses]
        team1_votes = sum(1 for rec in recommendations if team1 in rec)
        team2_votes = sum(1 for rec in recommendations if team2 in rec)
        
        if team1_votes > team2_votes:
            final_prediction = f"{team1} ML (YOLO MODE: Council consensus {team1_votes}-{team2_votes} with MAXIMUM CONFIDENCE!)"
        elif team2_votes > team1_votes:
            final_prediction = f"{team2} ML (YOLO MODE: Council consensus {team2_votes}-{team1_votes} with MAXIMUM CONFIDENCE!)"
        else:
            final_prediction = f"{team1} ML (YOLO MODE: Tiebreaker with home court advantage and MAXIMUM CONFIDENCE!)"
        
        prediction = BasketballPrediction(
            id=prediction_id,
            teams=[team1, team2],
            prediction_type=prediction_type,
            prediction=final_prediction,
            confidence=adjusted_confidence,
            council_analysis=council_analyses,
            yolo_factor=yolo_factor,
            timestamp=datetime.datetime.now(),
            odds={"team1": 1.85, "team2": 2.10, "draw": 3.50},
            yolo_mode=True
        )
        
        # Store in history
        self.prediction_history.append(prediction)
        
        return prediction

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics - YOLO MODE!"""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "status": "operational",
            "yolo_mode": self.yolo_mode_active,
            "council_members": len(self.council_members),
            "teams_in_database": len(self.nba_teams),
            "players_in_database": len(self.nba_players),
            "total_predictions": len(self.prediction_history),
            "yolo_factor": "MAXIMUM CONFIDENCE!",
            "timestamp": datetime.datetime.now().isoformat()
        }

    async def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent predictions - YOLO MODE!"""
        recent = self.prediction_history[-limit:] if self.prediction_history else []
        return [
            {
                "id": p.id,
                "teams": p.teams,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "yolo_factor": p.yolo_factor,
                "yolo_mode": p.yolo_mode,
                "timestamp": p.timestamp.isoformat()
            }
            for p in recent
        ]

    # ============================================================================
    # PERFORMANCE TRACKING METHODS - YOLO MODE!
    # ============================================================================
    
    async def track_betting_performance(self, user_id: str, bet_data: Dict[str, Any]) -> BettingPerformance:
        """Track individual betting performance - YOLO MODE!"""
        bet_id = f"bet_{self.total_bets_tracked}_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate ROI
        bet_amount = bet_data.get("bet_amount", 0.0)
        payout = bet_data.get("payout", 0.0)
        roi = ((payout - bet_amount) / bet_amount * 100) if bet_amount > 0 else 0.0
        
        # Determine success
        success = payout > bet_amount
        
        performance = BettingPerformance(
            user_id=user_id,
            bet_id=bet_id,
            sport="basketball",
            bet_type=bet_data.get("bet_type", "moneyline"),
            teams=bet_data.get("teams", []),
            prediction=bet_data.get("prediction", ""),
            actual_result=bet_data.get("actual_result", ""),
            bet_amount=bet_amount,
            payout=payout,
            odds=bet_data.get("odds", 0.0),
            confidence=bet_data.get("confidence", 0.0),
            council_analysis=bet_data.get("council_analysis", []),
            yolo_factor=bet_data.get("yolo_factor", 1.0),
            success=success,
            roi=roi
        )
        
        # Store in database
        self.performance_database[bet_id] = performance
        self.total_bets_tracked += 1
        
        # Update user metrics
        await self.update_user_metrics(user_id, performance)
        
        return performance
    
    async def update_user_metrics(self, user_id: str, performance: BettingPerformance):
        """Update comprehensive user performance metrics - YOLO MODE!"""
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = UserPerformanceMetrics(user_id=user_id)
            self.total_users_tracked += 1
        
        metrics = self.user_metrics[user_id]
        
        # Update basic metrics
        metrics.total_bets += 1
        metrics.total_bet_amount += performance.bet_amount
        metrics.total_payout += performance.payout
        
        if performance.success:
            metrics.wins += 1
        else:
            metrics.losses += 1
        
        # Calculate averages
        metrics.win_rate = (metrics.wins / metrics.total_bets * 100) if metrics.total_bets > 0 else 0.0
        metrics.overall_roi = ((metrics.total_payout - metrics.total_bet_amount) / metrics.total_bet_amount * 100) if metrics.total_bet_amount > 0 else 0.0
        
        # Update confidence and YOLO averages
        total_confidence = metrics.average_confidence * (metrics.total_bets - 1) + performance.confidence
        metrics.average_confidence = total_confidence / metrics.total_bets
        
        total_yolo = metrics.average_yolo_factor * (metrics.total_bets - 1) + performance.yolo_factor
        metrics.average_yolo_factor = total_yolo / metrics.total_bets
        
        # Update streaks
        await self.update_streak_analysis(user_id, performance.success)
        
        # Update council performance
        await self.update_council_performance(user_id, performance)
        
        metrics.last_updated = datetime.datetime.now()
        self.performance_update_count += 1
    
    async def update_streak_analysis(self, user_id: str, success: bool):
        """Update streak analysis for user - YOLO MODE!"""
        if user_id not in self.streak_analysis:
            self.streak_analysis[user_id] = StreakAnalysis(user_id=user_id)
        
        streak = self.streak_analysis[user_id]
        
        if success:
            streak.current_win_streak += 1
            streak.current_loss_streak = 0
            streak.longest_win_streak = max(streak.longest_win_streak, streak.current_win_streak)
        else:
            streak.current_loss_streak += 1
            streak.current_win_streak = 0
            streak.longest_loss_streak = max(streak.longest_loss_streak, streak.current_loss_streak)
        
        # Calculate momentum score
        streak.momentum_score = (streak.current_win_streak - streak.current_loss_streak) / 10.0
        
        # Calculate volatility index
        total_bets = self.user_metrics[user_id].total_bets
        if total_bets > 10:
            recent_bets = list(self.performance_database.values())[-10:]
            wins = sum(1 for bet in recent_bets if bet.success)
            streak.volatility_index = abs(wins - 5) / 5.0  # How far from 50/50
    
    async def update_council_performance(self, user_id: str, performance: BettingPerformance):
        """Update council member performance tracking - YOLO MODE!"""
        metrics = self.user_metrics[user_id]
        
        if not metrics.council_performance:
            metrics.council_performance = {
                "offensive_specialist": 0.0,
                "defensive_analyst": 0.0,
                "three_point_expert": 0.0,
                "rebounding_coach": 0.0,
                "momentum_reader": 0.0
            }
        
        # Analyze council recommendations vs actual results
        for analysis in performance.council_analysis:
            council_member = analysis.get("member", "").lower()
            if council_member in metrics.council_performance:
                current_score = metrics.council_performance[council_member]
                if performance.success:
                    metrics.council_performance[council_member] = current_score + 1
                else:
                    metrics.council_performance[council_member] = current_score - 0.5
    
    async def generate_performance_insights(self, user_id: str) -> PerformanceInsights:
        """Generate AI-powered performance insights - YOLO MODE!"""
        if user_id not in self.user_metrics:
            return PerformanceInsights(user_id=user_id)
        
        metrics = self.user_metrics[user_id]
        streak = self.streak_analysis.get(user_id, StreakAnalysis(user_id=user_id))
        
        insights = []
        recommendations = []
        strengths = []
        improvement_areas = []
        
        # Analyze win rate
        if metrics.win_rate > 60:
            insights.append(f"🎯 Excellent win rate of {metrics.win_rate:.1f}% - You're crushing it!")
            strengths.append("High win rate")
        elif metrics.win_rate > 50:
            insights.append(f"📈 Solid win rate of {metrics.win_rate:.1f}% - Above average performance")
            strengths.append("Above average win rate")
        else:
            insights.append(f"📉 Win rate of {metrics.win_rate:.1f}% - Room for improvement")
            improvement_areas.append("Improve win rate")
        
        # Analyze ROI
        if metrics.overall_roi > 10:
            insights.append(f"💰 Outstanding ROI of {metrics.overall_roi:.1f}% - Profit machine!")
            strengths.append("High ROI")
        elif metrics.overall_roi > 0:
            insights.append(f"📊 Positive ROI of {metrics.overall_roi:.1f}% - Profitable betting")
            strengths.append("Profitable betting")
        else:
            insights.append(f"⚠️ Negative ROI of {metrics.overall_roi:.1f}% - Need strategy adjustment")
            improvement_areas.append("Improve ROI")
        
        # Analyze streaks
        if streak.current_win_streak >= 3:
            insights.append(f"🔥 Hot streak! {streak.current_win_streak} wins in a row")
            strengths.append("Current hot streak")
        elif streak.current_loss_streak >= 3:
            insights.append(f"❄️ Cold streak! {streak.current_loss_streak} losses in a row")
            improvement_areas.append("Break losing streak")
        
        # Analyze council performance
        best_council = max(metrics.council_performance.items(), key=lambda x: x[1]) if metrics.council_performance else None
        if best_council and best_council[1] > 2:
            insights.append(f"🧠 {best_council[0].replace('_', ' ').title()} is your best council advisor")
            strengths.append(f"Strong {best_council[0]} performance")
        
        # Generate recommendations
        if metrics.win_rate < 50:
            recommendations.append("Focus on higher confidence bets (>70%)")
        if metrics.overall_roi < 0:
            recommendations.append("Consider reducing bet sizes until ROI improves")
        if streak.current_loss_streak >= 3:
            recommendations.append("Take a short break and review recent predictions")
        if metrics.average_confidence < 0.6:
            recommendations.append("Wait for higher confidence predictions from the council")
        
        # Risk assessment
        risk_level = "LOW"
        if metrics.overall_roi < -10 or streak.current_loss_streak >= 5:
            risk_level = "HIGH"
        elif metrics.overall_roi < 0 or streak.current_loss_streak >= 3:
            risk_level = "MEDIUM"
        
        return PerformanceInsights(
            user_id=user_id,
            insights=insights,
            recommendations=recommendations,
            risk_assessment=risk_level,
            improvement_areas=improvement_areas,
            strengths=strengths
        )
    
    async def get_roi_analysis(self, user_id: str) -> ROIAnalysis:
        """Generate comprehensive ROI analysis - YOLO MODE!"""
        if user_id not in self.user_metrics:
            return ROIAnalysis(user_id=user_id)
        
        user_bets = [bet for bet in self.performance_database.values() if bet.user_id == user_id]
        
        roi_analysis = ROIAnalysis(user_id=user_id)
        
        # Overall ROI
        total_bet = sum(bet.bet_amount for bet in user_bets)
        total_payout = sum(bet.payout for bet in user_bets)
        roi_analysis.overall_roi = ((total_payout - total_bet) / total_bet * 100) if total_bet > 0 else 0.0
        
        # ROI by bet type
        bet_types = {}
        for bet in user_bets:
            if bet.bet_type not in bet_types:
                bet_types[bet.bet_type] = {"total_bet": 0, "total_payout": 0}
            bet_types[bet.bet_type]["total_bet"] += bet.bet_amount
            bet_types[bet.bet_type]["total_payout"] += bet.payout
        
        for bet_type, data in bet_types.items():
            roi = ((data["total_payout"] - data["total_bet"]) / data["total_bet"] * 100) if data["total_bet"] > 0 else 0.0
            roi_analysis.roi_by_bet_type[bet_type] = roi
        
        # ROI by team
        team_bets = {}
        for bet in user_bets:
            for team in bet.teams:
                if team not in team_bets:
                    team_bets[team] = {"total_bet": 0, "total_payout": 0}
                team_bets[team]["total_bet"] += bet.bet_amount / len(bet.teams)
                team_bets[team]["total_payout"] += bet.payout / len(bet.teams)
        
        for team, data in team_bets.items():
            roi = ((data["total_payout"] - data["total_bet"]) / data["total_bet"] * 100) if data["total_bet"] > 0 else 0.0
            roi_analysis.roi_by_team[team] = roi
        
        return roi_analysis
    
    async def get_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary - YOLO MODE!"""
        metrics = self.user_metrics.get(user_id, UserPerformanceMetrics(user_id=user_id))
        streak = self.streak_analysis.get(user_id, StreakAnalysis(user_id=user_id))
        insights = await self.generate_performance_insights(user_id)
        roi_analysis = await self.get_roi_analysis(user_id)
        
        return {
            "user_id": user_id,
            "performance_metrics": {
                "total_bets": metrics.total_bets,
                "wins": metrics.wins,
                "losses": metrics.losses,
                "win_rate": metrics.win_rate,
                "total_bet_amount": metrics.total_bet_amount,
                "total_payout": metrics.total_payout,
                "overall_roi": metrics.overall_roi,
                "average_confidence": metrics.average_confidence,
                "average_yolo_factor": metrics.average_yolo_factor
            },
            "streak_analysis": {
                "current_win_streak": streak.current_win_streak,
                "current_loss_streak": streak.current_loss_streak,
                "longest_win_streak": streak.longest_win_streak,
                "longest_loss_streak": streak.longest_loss_streak,
                "momentum_score": streak.momentum_score,
                "volatility_index": streak.volatility_index
            },
            "insights": {
                "insights": insights.insights,
                "recommendations": insights.recommendations,
                "risk_assessment": insights.risk_assessment,
                "strengths": insights.strengths,
                "improvement_areas": insights.improvement_areas
            },
            "roi_analysis": {
                "overall_roi": roi_analysis.overall_roi,
                "roi_by_bet_type": roi_analysis.roi_by_bet_type,
                "roi_by_team": roi_analysis.roi_by_team
            },
            "council_performance": metrics.council_performance,
            "last_updated": metrics.last_updated.isoformat()
        }

# Create Starlette app for the basketball system
basketball_system = BasketballBettingSystem()

async def root(request: Request):
    """Root endpoint - YOLO MODE!"""
    return JSONResponse({
        "message": "Basketball Betting System - YOLO MODE!",
        "system": basketball_system.system_name,
        "version": basketball_system.version,
        "status": "operational",
        "council_members": len(basketball_system.council_members),
        "yolo_mode": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def health(request: Request):
    """Health check endpoint - YOLO MODE!"""
    return JSONResponse({
        "status": "healthy",
        "system": "basketball_betting_system",
        "yolo_mode": basketball_system.yolo_mode_active,
        "yolo_factor": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def status(request: Request):
    """System status endpoint - YOLO MODE!"""
    status_data = await basketball_system.get_system_status()
    return JSONResponse(status_data)

async def predict(request: Request):
    """Prediction endpoint - YOLO MODE!"""
    try:
        body = await request.json()
        team1 = body.get("team1", "Celtics")
        team2 = body.get("team2", "Lakers")
        prediction_type = body.get("prediction_type", "moneyline")
        
        if team1 not in basketball_system.nba_teams or team2 not in basketball_system.nba_teams:
            return JSONResponse({
                "error": "Invalid team names",
                "available_teams": list(basketball_system.nba_teams.keys()),
                "yolo_mode": "MAXIMUM CONFIDENCE!"
            }, status_code=400)
        
        prediction = await basketball_system.create_basketball_prediction(team1, team2, prediction_type)
        
        return JSONResponse({
            "prediction_id": prediction.id,
            "teams": prediction.teams,
            "prediction": prediction.prediction,
            "confidence": prediction.confidence,
            "yolo_factor": prediction.yolo_factor,
            "yolo_mode": prediction.yolo_mode,
            "council_analysis": [
                {
                    "member": analysis.council_member.value,
                    "recommendation": analysis.recommendation,
                    "confidence": analysis.confidence,
                    "reasoning": analysis.reasoning,
                    "yolo_boost": analysis.yolo_boost
                }
                for analysis in prediction.council_analysis
            ],
            "timestamp": prediction.timestamp.isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Prediction failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def teams(request: Request):
    """Get all teams endpoint - YOLO MODE!"""
    return JSONResponse({
        "teams": list(basketball_system.nba_teams.keys()),
        "count": len(basketball_system.nba_teams),
        "yolo_mode": "MAXIMUM CONFIDENCE!"
    })

async def recent_predictions(request: Request):
    """Get recent predictions endpoint - YOLO MODE!"""
    limit = int(request.query_params.get("limit", 10))
    predictions = await basketball_system.get_recent_predictions(limit)
    return JSONResponse({
        "predictions": predictions,
        "count": len(predictions),
        "yolo_mode": "MAXIMUM CONFIDENCE!"
    })

# ============================================================================
# PERFORMANCE TRACKING ENDPOINTS - YOLO MODE!
# ============================================================================

async def track_performance(request: Request):
    """Track betting performance endpoint - YOLO MODE!"""
    try:
        body = await request.json()
        user_id = body.get("user_id", "default_user")
        bet_data = body.get("bet_data", {})
        
        performance = await basketball_system.track_betting_performance(user_id, bet_data)
        
        return JSONResponse({
            "success": True,
            "bet_id": performance.bet_id,
            "user_id": performance.user_id,
            "roi": performance.roi,
            "success": performance.success,
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Performance tracking failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def get_performance_summary(request: Request):
    """Get user performance summary endpoint - YOLO MODE!"""
    try:
        user_id = request.query_params.get("user_id", "default_user")
        summary = await basketball_system.get_performance_summary(user_id)
        
        return JSONResponse({
            "performance_summary": summary,
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Performance summary failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def get_roi_analysis(request: Request):
    """Get ROI analysis endpoint - YOLO MODE!"""
    try:
        user_id = request.query_params.get("user_id", "default_user")
        roi_analysis = await basketball_system.get_roi_analysis(user_id)
        
        return JSONResponse({
            "roi_analysis": {
                "overall_roi": roi_analysis.overall_roi,
                "roi_by_bet_type": roi_analysis.roi_by_bet_type,
                "roi_by_team": roi_analysis.roi_by_team,
                "roi_by_confidence": roi_analysis.roi_by_confidence,
                "roi_by_council": roi_analysis.roi_by_council
            },
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"ROI analysis failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def get_performance_insights(request: Request):
    """Get AI-generated performance insights endpoint - YOLO MODE!"""
    try:
        user_id = request.query_params.get("user_id", "default_user")
        insights = await basketball_system.generate_performance_insights(user_id)
        
        return JSONResponse({
            "insights": {
                "insights": insights.insights,
                "recommendations": insights.recommendations,
                "risk_assessment": insights.risk_assessment,
                "strengths": insights.strengths,
                "improvement_areas": insights.improvement_areas
            },
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Performance insights failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def get_system_performance_stats(request: Request):
    """Get overall system performance statistics - YOLO MODE!"""
    try:
        stats = {
            "total_bets_tracked": basketball_system.total_bets_tracked,
            "total_users_tracked": basketball_system.total_users_tracked,
            "performance_update_count": basketball_system.performance_update_count,
            "active_users": len(basketball_system.user_metrics),
            "performance_database_size": len(basketball_system.performance_database),
            "system_uptime": "YOLO MODE: MAXIMUM CONFIDENCE!"
        }
        
        return JSONResponse({
            "system_performance_stats": stats,
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"System stats failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

# Create Starlette app
app = Starlette(routes=[
    Route("/", root, methods=["GET"]),
    Route("/health", health, methods=["GET"]),
    Route("/api/v1/status", status, methods=["GET"]),
    Route("/api/v1/predict", predict, methods=["POST"]),
    Route("/api/v1/teams", teams, methods=["GET"]),
    Route("/api/v1/recent-predictions", recent_predictions, methods=["GET"]),
    # Performance Tracking Endpoints
    Route("/api/v1/performance/track", track_performance, methods=["POST"]),
    Route("/api/v1/performance/summary", get_performance_summary, methods=["GET"]),
    Route("/api/v1/performance/roi", get_roi_analysis, methods=["GET"]),
    Route("/api/v1/performance/insights", get_performance_insights, methods=["GET"]),
    Route("/api/v1/performance/stats", get_system_performance_stats, methods=["GET"])
])

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

def main():
    """Main function to start the basketball betting system - YOLO MODE!"""
    print("🏀 Starting Basketball Betting System - YOLO MODE!")
    print("=" * 60)
    print(f"System: {basketball_system.system_name}")
    print(f"Version: {basketball_system.version}")
    print(f"Council Members: {len(basketball_system.council_members)}")
    print(f"NBA Teams: {len(basketball_system.nba_teams)}")
    print(f"Players: {len(basketball_system.player_stats)}")
    print("YOLO MODE: MAXIMUM CONFIDENCE!")
    print("=" * 60)
    
    host = "0.0.0.0"
    port = 8006  # Basketball system port
    
    print(f"Server: {host}:{port}")
    print(f"Health: http://localhost:{port}/health")
    print(f"Status: http://localhost:{port}/api/v1/status")
    print(f"Teams: http://localhost:{port}/api/v1/teams")
    print(f"Predictions: http://localhost:{port}/api/v1/predict")
    print("=" * 60)
    print("🎯 PERFORMANCE TRACKING ENDPOINTS - YOLO MODE!")
    print(f"Track Performance: http://localhost:{port}/api/v1/performance/track")
    print(f"Performance Summary: http://localhost:{port}/api/v1/performance/summary")
    print(f"ROI Analysis: http://localhost:{port}/api/v1/performance/roi")
    print(f"Performance Insights: http://localhost:{port}/api/v1/performance/insights")
    print(f"System Stats: http://localhost:{port}/api/v1/performance/stats")
    print("=" * 60)
    print("YOLO MODE: MAXIMUM CONFIDENCE!")
    print("MULTIDIMENSIONAL PERFORMANCE TRACKING ACTIVE!")
    print("=" * 60)
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main() 