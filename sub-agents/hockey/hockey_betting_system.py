#!/usr/bin/env python3
"""
Hockey Betting System - YOLO MODE!
==================================
NHL-specific betting system with 5 AI council structure.
Features comprehensive hockey analytics, real-time predictions, and YOLO mode.
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

class HockeyCouncilMember(str, Enum):
    """5 AI Council Members for Hockey Analysis - YOLO MODE!"""
    OFFENSIVE_SPECIALIST = "offensive_specialist"
    DEFENSIVE_ANALYST = "defensive_analyst"
    GOALIE_EXPERT = "goalie_expert"
    SPECIAL_TEAMS_COACH = "special_teams_coach"
    MOMENTUM_READER = "momentum_reader"

# ============================================================================
# MULTIDIMENSIONAL PERFORMANCE TRACKING SERVICE - YOLO MODE!
# ============================================================================

@dataclass
class BettingPerformance:
    """Individual betting performance tracking - YOLO MODE!"""
    user_id: str
    bet_id: str
    sport: str = "hockey"
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
# ORIGINAL HOCKEY DATA STRUCTURES
# ============================================================================

@dataclass
class HockeyTeam:
    """NHL Team data structure - YOLO MODE!"""
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
    yolo_factor: float = 1.5

@dataclass
class HockeyPlayer:
    """NHL Player data structure - YOLO MODE!"""
    name: str
    team: str
    position: str
    goals: int
    assists: int
    points: int
    plus_minus: int
    time_on_ice: str
    yolo_boost: float = 1.3

@dataclass
class HockeyGoalie:
    """NHL Goalie data structure - YOLO MODE!"""
    name: str
    team: str
    wins: int
    losses: int
    gaa: float
    save_pct: float
    shutouts: int
    yolo_factor: float = 1.4

@dataclass
class CouncilAnalysis:
    """Analysis from each council member - YOLO MODE!"""
    council_member: HockeyCouncilMember
    analysis: Dict[str, Any]
    confidence: float
    recommendation: str
    reasoning: str
    yolo_boost: float = 1.5

@dataclass
class HockeyPrediction:
    """Complete hockey prediction with council analysis - YOLO MODE!"""
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

class HockeyBettingSystem:
    """Comprehensive NHL betting system with 5 AI council and PERFORMANCE TRACKING - YOLO MODE!"""
    
    def __init__(self):
        self.system_name = "Hockey Betting System - YOLO MODE!"
        self.version = "2.0.0-yolo-performance"
        self.sport_type = "hockey"
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
        # ORIGINAL HOCKEY DATA
        # ============================================================================
        
        # NHL team stats (mock data) - YOLO MODE!
        self.nhl_teams = {
            "Bruins": {"wins": 65, "losses": 12, "goals_for": 305, "goals_against": 177, "power_play": 22.2, "penalty_kill": 87.3},
            "Lightning": {"wins": 46, "losses": 30, "goals_for": 283, "goals_against": 254, "power_play": 25.4, "penalty_kill": 79.7},
            "Maple Leafs": {"wins": 50, "losses": 21, "goals_for": 279, "goals_against": 222, "power_play": 23.5, "penalty_kill": 81.9},
            "Oilers": {"wins": 50, "losses": 23, "goals_for": 325, "goals_against": 260, "power_play": 32.4, "penalty_kill": 75.5},
            "Rangers": {"wins": 47, "losses": 22, "goals_for": 254, "goals_against": 207, "power_play": 24.1, "penalty_kill": 82.0},
            "Devils": {"wins": 52, "losses": 22, "goals_for": 291, "goals_against": 236, "power_play": 21.9, "penalty_kill": 82.6},
            "Avalanche": {"wins": 51, "losses": 24, "goals_for": 280, "goals_against": 226, "power_play": 24.8, "penalty_kill": 80.1},
            "Golden Knights": {"wins": 51, "losses": 22, "goals_for": 272, "goals_against": 229, "power_play": 20.3, "penalty_kill": 77.4},
            "Stars": {"wins": 47, "losses": 21, "goals_for": 285, "goals_against": 218, "power_play": 23.7, "penalty_kill": 82.3},
            "Hurricanes": {"wins": 52, "losses": 21, "goals_for": 266, "goals_against": 213, "power_play": 19.8, "penalty_kill": 84.1},
            "Kings": {"wins": 47, "losses": 25, "goals_for": 256, "goals_against": 220, "power_play": 21.5, "penalty_kill": 81.2},
            "Wild": {"wins": 46, "losses": 25, "goals_for": 246, "goals_against": 225, "power_play": 21.1, "penalty_kill": 82.8},
            "Jets": {"wins": 46, "losses": 33, "goals_for": 247, "goals_against": 225, "power_play": 23.4, "penalty_kill": 82.1},
            "Flames": {"wins": 38, "losses": 27, "goals_for": 262, "goals_against": 226, "power_play": 20.8, "penalty_kill": 81.5},
            "Canucks": {"wins": 38, "losses": 37, "goals_for": 276, "goals_against": 298, "power_play": 22.6, "penalty_kill": 76.8},
            "Sharks": {"wins": 22, "losses": 44, "goals_for": 209, "goals_against": 340, "power_play": 18.9, "penalty_kill": 76.2}
        }
        
        # Goalie stats (mock data) - YOLO MODE!
        self.goalie_stats = {
            "Linus Ullmark": {"gaa": 1.89, "save_pct": 0.938, "wins": 40, "team": "Bruins"},
            "Igor Shesterkin": {"gaa": 2.48, "save_pct": 0.916, "wins": 37, "team": "Rangers"},
            "Connor Hellebuyck": {"gaa": 2.49, "save_pct": 0.920, "wins": 37, "team": "Jets"},
            "Andrei Vasilevskiy": {"gaa": 2.65, "save_pct": 0.915, "wins": 34, "team": "Lightning"},
            "Jake Oettinger": {"gaa": 2.37, "save_pct": 0.919, "wins": 36, "team": "Stars"},
            "Jeremy Swayman": {"gaa": 2.27, "save_pct": 0.920, "wins": 24, "team": "Bruins"},
            "Vitek Vanecek": {"gaa": 2.45, "save_pct": 0.911, "wins": 33, "team": "Devils"},
            "Alexandar Georgiev": {"gaa": 2.53, "save_pct": 0.918, "wins": 40, "team": "Avalanche"}
        }
        
        # Player stats (mock data) - YOLO MODE!
        self.player_stats = {
            "Connor McDavid": {"goals": 64, "assists": 89, "points": 153, "team": "Oilers"},
            "Leon Draisaitl": {"goals": 52, "assists": 76, "points": 128, "team": "Oilers"},
            "David Pastrnak": {"goals": 61, "assists": 52, "points": 113, "team": "Bruins"},
            "Nathan MacKinnon": {"goals": 42, "assists": 69, "points": 111, "team": "Avalanche"},
            "Mikko Rantanen": {"goals": 55, "assists": 50, "points": 105, "team": "Avalanche"},
            "Matthew Tkachuk": {"goals": 40, "assists": 69, "points": 109, "team": "Panthers"},
            "Artemi Panarin": {"goals": 29, "assists": 63, "points": 92, "team": "Rangers"},
            "Jack Hughes": {"goals": 43, "assists": 56, "points": 99, "team": "Devils"},
            "Auston Matthews": {"goals": 40, "assists": 44, "points": 84, "team": "Maple Leafs"},
            "Mitch Marner": {"goals": 30, "assists": 69, "points": 99, "team": "Maple Leafs"}
        }
        
        self.betting_types = [
            "moneyline", "puck_line", "total_goals", "first_period", "player_props", "period_bets"
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
            sport="hockey",
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
                "goalie_expert": 0.0,
                "special_teams_coach": 0.0,
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

    async def council_offensive_specialist(self, team1: str, team2: str) -> CouncilAnalysis:
        """Offensive Specialist Council Member Analysis - YOLO MODE!"""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate offensive metrics with YOLO boost
        team1_offense_score = (team1_data.goals_for * 0.4 + 
                              team1_data.power_play * 0.3 + 
                              (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.3) * team1_data.yolo_factor
        
        team2_offense_score = (team2_data.goals_for * 0.4 + 
                              team2_data.power_play * 0.3 + 
                              (team2_data.wins / (team2_data.wins + team2_data.losses)) * 0.3) * team2_data.yolo_factor
        
        offensive_advantage = team1 if team1_offense_score > team2_offense_score else team2
        confidence = min(abs(team1_offense_score - team2_offense_score) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_offense_score": round(team1_offense_score, 2),
            "team2_offense_score": round(team2_offense_score, 2),
            "offensive_advantage": offensive_advantage,
            "goals_for_comparison": f"{team1}: {team1_data.goals_for} vs {team2}: {team2_data.goals_for}",
            "power_play_comparison": f"{team1}: {team1_data.power_play}% vs {team2}: {team2_data.power_play}%",
            "yolo_factor": "MAXIMUM CONFIDENCE!"
        }
        
        recommendation = f"{offensive_advantage} ML (YOLO MODE: Offensive advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Offensive analysis shows {offensive_advantage} has superior scoring ability with {round(max(team1_data.goals_for, team2_data.goals_for))} goals per game and {round(max(team1_data.power_play, team2_data.power_play), 1)}% power play efficiency. MAXIMUM CONFIDENCE!"
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.OFFENSIVE_SPECIALIST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.8
        )

    async def council_defensive_analyst(self, team1: str, team2: str) -> CouncilAnalysis:
        """Defensive Analyst Council Member Analysis - YOLO MODE!"""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate defensive metrics with YOLO boost
        team1_defense_score = (team1_data.penalty_kill * 0.4 + 
                              (1 / team1_data.goals_against) * 1000 * 0.4 + 
                              (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.2) * team1_data.yolo_factor
        
        team2_defense_score = (team2_data.penalty_kill * 0.4 + 
                              (1 / team2_data.goals_against) * 1000 * 0.4 + 
                              (team2_data.wins / (team2_data.wins + team2_data.losses)) * 0.2) * team2_data.yolo_factor
        
        defensive_advantage = team1 if team1_defense_score > team2_defense_score else team2
        confidence = min(abs(team1_defense_score - team2_defense_score) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_defense_score": round(team1_defense_score, 2),
            "team2_defense_score": round(team2_defense_score, 2),
            "defensive_advantage": defensive_advantage,
            "goals_against_comparison": f"{team1}: {team1_data.goals_against} vs {team2}: {team2_data.goals_against}",
            "penalty_kill_comparison": f"{team1}: {team1_data.penalty_kill}% vs {team2}: {team2_data.penalty_kill}%",
            "yolo_factor": "DEFENSIVE DOMINANCE!"
        }
        
        recommendation = f"Under {round((team1_data.goals_against + team2_data.goals_against) / 2 + 1)} total goals (YOLO MODE: Defensive matchup with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Defensive analysis shows {defensive_advantage} has superior defensive metrics with {round(min(team1_data.goals_against, team2_data.goals_against))} goals against per game and {round(max(team1_data.penalty_kill, team2_data.penalty_kill), 1)}% penalty kill efficiency. DEFENSIVE DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.DEFENSIVE_ANALYST,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.7
        )

    async def council_goalie_expert(self, team1: str, team2: str) -> CouncilAnalysis:
        """Goalie Expert Council Member Analysis - YOLO MODE!"""
        # Find best goalies for each team
        team1_goalies = [g for g in self.nhl_goalies.values() if g.team == team1]
        team2_goalies = [g for g in self.nhl_goalies.values() if g.team == team2]
        
        if not team1_goalies or not team2_goalies:
            # Use default analysis if no goalie data
            return CouncilAnalysis(
                council_member=HockeyCouncilMember.GOALIE_EXPERT,
                analysis={"note": "Insufficient goalie data", "yolo_factor": "DEFAULT YOLO!"},
                confidence=0.5 * 1.5,  # YOLO boost
                recommendation=f"{team1} ML (YOLO MODE: Home ice advantage with MAXIMUM CONFIDENCE!)",
                reasoning="YOLO MODE: Goalie data unavailable, defaulting to home ice advantage with MAXIMUM CONFIDENCE!",
                yolo_boost=1.5
            )
        
        # Get best goalie for each team (lowest GAA)
        team1_best = min(team1_goalies, key=lambda x: x.gaa)
        team2_best = min(team2_goalies, key=lambda x: x.gaa)
        
        goalie_advantage = team1 if team1_best.gaa < team2_best.gaa else team2
        confidence = min(abs(team1_best.gaa - team2_best.gaa) * 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_goalie": f"{team1_best.name} (GAA: {team1_best.gaa}, SV%: {team1_best.save_pct})",
            "team2_goalie": f"{team2_best.name} (GAA: {team2_best.gaa}, SV%: {team2_best.save_pct})",
            "goalie_advantage": goalie_advantage,
            "gaa_comparison": f"{team1}: {team1_best.gaa} vs {team2}: {team2_best.gaa}",
            "save_pct_comparison": f"{team1}: {team1_best.save_pct} vs {team2}: {team2_best.save_pct}",
            "yolo_factor": "GOALIE DOMINANCE!"
        }
        
        recommendation = f"{goalie_advantage} ML (YOLO MODE: Goalie advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Goalie analysis shows {goalie_advantage} has the superior netminder with {round(min(team1_best.gaa, team2_best.gaa), 2)} GAA and {round(max(team1_best.save_pct, team2_best.save_pct), 3)} save percentage. GOALIE DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.GOALIE_EXPERT,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.9
        )

    async def council_special_teams_coach(self, team1: str, team2: str) -> CouncilAnalysis:
        """Special Teams Coach Council Member Analysis - YOLO MODE!"""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate special teams advantage with YOLO boost
        team1_special_teams = (team1_data.power_play + team1_data.penalty_kill) / 2 * team1_data.yolo_factor
        team2_special_teams = (team2_data.power_play + team2_data.penalty_kill) / 2 * team2_data.yolo_factor
        
        special_teams_advantage = team1 if team1_special_teams > team2_special_teams else team2
        confidence = min(abs(team1_special_teams - team2_special_teams) / 10, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_special_teams_score": round(team1_special_teams, 1),
            "team2_special_teams_score": round(team2_special_teams, 1),
            "special_teams_advantage": special_teams_advantage,
            "power_play_advantage": team1 if team1_data.power_play > team2_data.power_play else team2,
            "penalty_kill_advantage": team1 if team1_data.penalty_kill > team2_data.penalty_kill else team2,
            "yolo_factor": "SPECIAL TEAMS DOMINANCE!"
        }
        
        if team1_data.power_play > 25 or team2_data.power_play > 25:
            recommendation = f"{special_teams_advantage} power play goal (YOLO MODE: PP advantage with MAXIMUM CONFIDENCE!)"
        else:
            recommendation = f"{special_teams_advantage} ML (YOLO MODE: Special teams advantage with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Special teams analysis shows {special_teams_advantage} has superior special teams play with {round(max(team1_data.power_play, team2_data.power_play), 1)}% power play and {round(max(team1_data.penalty_kill, team2_data.penalty_kill), 1)}% penalty kill. SPECIAL TEAMS DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.SPECIAL_TEAMS_COACH,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.6
        )

    async def council_momentum_reader(self, team1: str, team2: str) -> CouncilAnalysis:
        """Momentum Reader Council Member Analysis - YOLO MODE!"""
        team1_data = self.nhl_teams[team1]
        team2_data = self.nhl_teams[team2]
        
        # Calculate momentum metrics with YOLO boost
        team1_momentum = (team1_data.wins / (team1_data.wins + team1_data.losses)) * 0.6 + 0.4  # Home advantage
        team2_momentum = (team2_data.wins / (team1_data.wins + team1_data.losses)) * 0.6 + 0.2  # Away disadvantage
        
        # Apply YOLO factors
        team1_momentum *= team1_data.yolo_factor
        team2_momentum *= team2_data.yolo_factor
        
        momentum_advantage = team1 if team1_momentum > team2_momentum else team2
        confidence = min(abs(team1_momentum - team2_momentum) * 2, 0.95) * 1.5  # YOLO boost
        
        analysis = {
            "team1_momentum_score": round(team1_momentum, 3),
            "team2_momentum_score": round(team2_momentum, 3),
            "momentum_advantage": momentum_advantage,
            "home_advantage": "Team 1 has home ice advantage",
            "recent_form": f"{team1}: {team1_data.last_10} vs {team2}: {team2_data.last_10}",
            "yolo_factor": "MOMENTUM DOMINANCE!"
        }
        
        recommendation = f"{momentum_advantage} ML (YOLO MODE: Momentum advantage + home ice with MAXIMUM CONFIDENCE!)"
        
        reasoning = f"YOLO MODE: Momentum analysis shows {momentum_advantage} has the momentum advantage with home ice factor and recent form of {team1_data.last_10} vs {team2_data.last_10}. MOMENTUM DOMINANCE!"
        
        return CouncilAnalysis(
            council_member=HockeyCouncilMember.MOMENTUM_READER,
            analysis=analysis,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            yolo_boost=1.7
        )

    async def create_hockey_prediction(self, team1: str, team2: str, prediction_type: str = "moneyline") -> HockeyPrediction:
        """Create comprehensive hockey prediction with all council members - YOLO MODE!"""
        prediction_id = f"hockey_yolo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Get analysis from all council members
        council_analyses = [
            await self.council_offensive_specialist(team1, team2),
            await self.council_defensive_analyst(team1, team2),
            await self.council_goalie_expert(team1, team2),
            await self.council_special_teams_coach(team1, team2),
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
            final_prediction = f"{team1} ML (YOLO MODE: Tiebreaker with home ice advantage and MAXIMUM CONFIDENCE!)"
        
        prediction = HockeyPrediction(
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
            "teams_in_database": len(self.nhl_teams),
            "players_in_database": len(self.nhl_players),
            "goalies_in_database": len(self.nhl_goalies),
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

# Create Starlette app for the hockey system
hockey_system = HockeyBettingSystem()

async def root(request: Request):
    """Root endpoint - YOLO MODE!"""
    return JSONResponse({
        "message": "Hockey Betting System - YOLO MODE!",
        "system": hockey_system.system_name,
        "version": hockey_system.version,
        "status": "operational",
        "council_members": len(hockey_system.council_members),
        "yolo_mode": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def health(request: Request):
    """Health check endpoint - YOLO MODE!"""
    return JSONResponse({
        "status": "healthy",
        "system": "hockey_betting_system",
        "yolo_mode": hockey_system.yolo_mode_active,
        "yolo_factor": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def status(request: Request):
    """System status endpoint - YOLO MODE!"""
    status_data = await hockey_system.get_system_status()
    return JSONResponse(status_data)

async def predict(request: Request):
    """Prediction endpoint - YOLO MODE!"""
    try:
        body = await request.json()
        team1 = body.get("team1", "Bruins")
        team2 = body.get("team2", "Lightning")
        prediction_type = body.get("prediction_type", "moneyline")
        
        if team1 not in hockey_system.nhl_teams or team2 not in hockey_system.nhl_teams:
            return JSONResponse({
                "error": "Invalid team names",
                "available_teams": list(hockey_system.nhl_teams.keys()),
                "yolo_mode": "MAXIMUM CONFIDENCE!"
            }, status_code=400)
        
        prediction = await hockey_system.create_hockey_prediction(team1, team2, prediction_type)
        
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
        "teams": list(hockey_system.nhl_teams.keys()),
        "count": len(hockey_system.nhl_teams),
        "yolo_mode": "MAXIMUM CONFIDENCE!"
    })

async def recent_predictions(request: Request):
    """Get recent predictions endpoint - YOLO MODE!"""
    limit = int(request.query_params.get("limit", 10))
    predictions = await hockey_system.get_recent_predictions(limit)
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
        
        performance = await hockey_system.track_betting_performance(user_id, bet_data)
        
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
        summary = await hockey_system.get_performance_summary(user_id)
        
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
        roi_analysis = await hockey_system.get_roi_analysis(user_id)
        
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
        insights = await hockey_system.generate_performance_insights(user_id)
        
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
            "total_bets_tracked": hockey_system.total_bets_tracked,
            "total_users_tracked": hockey_system.total_users_tracked,
            "performance_update_count": hockey_system.performance_update_count,
            "active_users": len(hockey_system.user_metrics),
            "performance_database_size": len(hockey_system.performance_database),
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
    """Main function to start the hockey betting system - YOLO MODE!"""
    print("🏒 Starting Hockey Betting System - YOLO MODE!")
    print("=" * 60)
    print(f"System: {hockey_system.system_name}")
    print(f"Version: {hockey_system.version}")
    print(f"Council Members: {len(hockey_system.council_members)}")
    print(f"NHL Teams: {len(hockey_system.nhl_teams)}")
    print(f"Players: {len(hockey_system.player_stats)}")
    print(f"Goalies: {len(hockey_system.goalie_stats)}")
    print("YOLO MODE: MAXIMUM CONFIDENCE!")
    print("=" * 60)
    
    host = "0.0.0.0"
    port = 8005  # Hockey system port
    
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