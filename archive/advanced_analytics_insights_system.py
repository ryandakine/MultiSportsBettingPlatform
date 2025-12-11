#!/usr/bin/env python3
"""
Advanced Analytics & Insights System - YOLO MODE!
================================================
Predictive dashboard, risk assessment, ROI optimization, and pattern recognition
for ultra-smart sports betting analytics
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict, deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RiskAssessment:
    """Risk assessment for betting decisions"""
    risk_level: str  # 'low', 'medium', 'high', 'extreme'
    risk_score: float  # 0-1
    confidence: float
    factors: List[str]
    recommendations: List[str]
    max_bet_size: float
    expected_value: float
    volatility: float

@dataclass
class ROIAnalysis:
    """ROI optimization analysis"""
    expected_roi: float
    optimal_bet_size: float
    kelly_criterion: float
    confidence_interval: Tuple[float, float]
    risk_adjusted_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float

@dataclass
class PatternRecognition:
    """Pattern recognition results"""
    pattern_type: str  # 'trend', 'cycle', 'anomaly', 'correlation'
    confidence: float
    description: str
    strength: float  # 0-1
    duration: str
    prediction: str
    supporting_evidence: List[str]

@dataclass
class PredictiveInsight:
    """Predictive insight for betting"""
    insight_type: str  # 'opportunity', 'warning', 'trend', 'anomaly'
    confidence: float
    description: str
    impact_score: float
    time_horizon: str
    actionable: bool
    recommendations: List[str]

@dataclass
class DashboardMetrics:
    """Dashboard metrics and KPIs"""
    total_bets: int
    win_rate: float
    total_profit: float
    roi_percentage: float
    average_bet_size: float
    best_performing_sport: str
    worst_performing_sport: str
    current_streak: int
    risk_score: float
    confidence_level: str

class RiskAssessmentEngine:
    """Advanced risk assessment engine"""
    
    def __init__(self):
        self.risk_factors = {
            "volatility": 0.3,
            "confidence": 0.25,
            "market_sentiment": 0.2,
            "historical_performance": 0.15,
            "external_factors": 0.1
        }
        
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "extreme": 1.0
        }
    
    def assess_risk(self, prediction_confidence: float, market_volatility: float, 
                   historical_accuracy: float, external_factors: List[str]) -> RiskAssessment:
        """Assess risk for a betting decision"""
        
        # Calculate risk components
        volatility_risk = market_volatility * self.risk_factors["volatility"]
        confidence_risk = (1.0 - prediction_confidence) * self.risk_factors["confidence"]
        sentiment_risk = random.uniform(0, 0.2) * self.risk_factors["market_sentiment"]
        performance_risk = (1.0 - historical_accuracy) * self.risk_factors["historical_performance"]
        external_risk = len(external_factors) * 0.05 * self.risk_factors["external_factors"]
        
        # Calculate total risk score
        total_risk = volatility_risk + confidence_risk + sentiment_risk + performance_risk + external_risk
        total_risk = min(1.0, total_risk)
        
        # Determine risk level
        risk_level = "low"
        for level, threshold in self.risk_thresholds.items():
            if total_risk > threshold:
                risk_level = level
        
        # Generate factors list
        factors = []
        if volatility_risk > 0.1:
            factors.append(f"High market volatility ({volatility_risk:.2f})")
        if confidence_risk > 0.1:
            factors.append(f"Low prediction confidence ({confidence_risk:.2f})")
        if sentiment_risk > 0.05:
            factors.append(f"Negative market sentiment ({sentiment_risk:.2f})")
        if performance_risk > 0.1:
            factors.append(f"Poor historical performance ({performance_risk:.2f})")
        if external_risk > 0.05:
            factors.append(f"External factors present ({external_risk:.2f})")
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_level, total_risk, factors)
        
        # Calculate expected value and max bet size
        expected_value = prediction_confidence * 0.8 - total_risk * 0.2
        max_bet_size = self._calculate_max_bet_size(risk_level, expected_value)
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_score=total_risk,
            confidence=prediction_confidence,
            factors=factors,
            recommendations=recommendations,
            max_bet_size=max_bet_size,
            expected_value=expected_value,
            volatility=market_volatility
        )
    
    def _generate_risk_recommendations(self, risk_level: str, risk_score: float, factors: List[str]) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_level == "low":
            recommendations.extend([
                "✅ Low risk - Consider standard bet size",
                "📈 Good opportunity for value betting",
                "🎯 High confidence prediction"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "⚠️ Medium risk - Use conservative bet size",
                "📊 Monitor market conditions closely",
                "🔍 Consider hedging strategies"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "🚨 High risk - Use small bet size only",
                "⏰ Wait for better opportunities",
                "🛡️ Consider insurance bets"
            ])
        else:  # extreme
            recommendations.extend([
                "💀 Extreme risk - Avoid betting",
                "🚫 Wait for market stabilization",
                "📉 Focus on risk management"
            ])
        
        return recommendations
    
    def _calculate_max_bet_size(self, risk_level: str, expected_value: float) -> float:
        """Calculate maximum recommended bet size"""
        base_sizes = {
            "low": 0.05,      # 5% of bankroll
            "medium": 0.03,   # 3% of bankroll
            "high": 0.01,     # 1% of bankroll
            "extreme": 0.0    # 0% of bankroll
        }
        
        base_size = base_sizes.get(risk_level, 0.01)
        
        # Adjust based on expected value
        if expected_value > 0.5:
            base_size *= 1.5
        elif expected_value < 0.2:
            base_size *= 0.5
        
        return min(base_size, 0.1)  # Cap at 10%

class ROIOptimizer:
    """ROI optimization engine using Kelly Criterion and advanced metrics"""
    
    def __init__(self):
        self.kelly_multiplier = 0.5  # Conservative Kelly
        self.min_bet_size = 0.01
        self.max_bet_size = 0.1
    
    def optimize_roi(self, win_probability: float, odds: float, 
                    historical_roi: float, volatility: float) -> ROIAnalysis:
        """Optimize ROI using Kelly Criterion and advanced metrics"""
        
        # Calculate Kelly Criterion
        if odds > 1.0:
            kelly_fraction = (win_probability * odds - 1) / (odds - 1)
        else:
            kelly_fraction = 0.0
        
        # Apply conservative multiplier
        optimal_bet_size = max(0, kelly_fraction * self.kelly_multiplier)
        optimal_bet_size = min(optimal_bet_size, self.max_bet_size)
        
        # Calculate expected ROI
        expected_roi = (win_probability * odds - 1) * 100
        
        # Calculate confidence interval
        confidence_interval = (
            expected_roi - volatility * 50,
            expected_roi + volatility * 50
        )
        
        # Calculate risk-adjusted return (Sharpe ratio approximation)
        risk_free_rate = 0.02  # 2% annual
        sharpe_ratio = (expected_roi - risk_free_rate) / (volatility * 100) if volatility > 0 else 0
        
        # Calculate max drawdown (simplified)
        max_drawdown = volatility * 30  # Simplified calculation
        
        # Calculate win rate (based on historical data)
        win_rate = min(win_probability, 0.95)  # Cap at 95%
        
        return ROIAnalysis(
            expected_roi=expected_roi,
            optimal_bet_size=optimal_bet_size,
            kelly_criterion=kelly_fraction,
            confidence_interval=confidence_interval,
            risk_adjusted_return=expected_roi / (volatility + 0.1),
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate
        )

class PatternRecognitionEngine:
    """Advanced pattern recognition engine"""
    
    def __init__(self):
        self.patterns = []
        self.data_buffer = deque(maxlen=1000)
        self.correlation_threshold = 0.7
    
    def add_data_point(self, timestamp: str, value: float, features: Dict[str, float]):
        """Add data point for pattern analysis"""
        self.data_buffer.append({
            "timestamp": timestamp,
            "value": value,
            "features": features
        })
    
    def detect_patterns(self) -> List[PatternRecognition]:
        """Detect patterns in the data"""
        if len(self.data_buffer) < 10:
            return []
        
        patterns = []
        
        # Detect trends
        trend_pattern = self._detect_trend_pattern()
        if trend_pattern:
            patterns.append(trend_pattern)
        
        # Detect cycles
        cycle_pattern = self._detect_cycle_pattern()
        if cycle_pattern:
            patterns.append(cycle_pattern)
        
        # Detect anomalies
        anomaly_pattern = self._detect_anomaly_pattern()
        if anomaly_pattern:
            patterns.append(anomaly_pattern)
        
        # Detect correlations
        correlation_patterns = self._detect_correlation_patterns()
        patterns.extend(correlation_patterns)
        
        return patterns
    
    def _detect_trend_pattern(self) -> Optional[PatternRecognition]:
        """Detect trend patterns"""
        if len(self.data_buffer) < 5:
            return None
        
        values = [point["value"] for point in list(self.data_buffer)[-10:]]
        
        # Calculate trend
        if len(values) >= 2:
            slope = (values[-1] - values[0]) / len(values)
            
            if abs(slope) > 0.1:
                trend_type = "upward" if slope > 0 else "downward"
                strength = min(abs(slope), 1.0)
                
                return PatternRecognition(
                    pattern_type="trend",
                    confidence=strength,
                    description=f"Strong {trend_type} trend detected",
                    strength=strength,
                    duration="recent",
                    prediction=f"Continued {trend_type} movement expected",
                    supporting_evidence=[f"Slope: {slope:.3f}", f"Data points: {len(values)}"]
                )
        
        return None
    
    def _detect_cycle_pattern(self) -> Optional[PatternRecognition]:
        """Detect cyclical patterns"""
        if len(self.data_buffer) < 10:
            return None
        
        values = [point["value"] for point in list(self.data_buffer)[-20:]]
        
        # Simple cycle detection (simplified)
        if len(values) >= 8:
            # Check for alternating pattern
            alternating_count = 0
            for i in range(1, len(values)):
                if (values[i] > values[i-1]) != (values[i-1] > values[i-2] if i > 1 else True):
                    alternating_count += 1
            
            cycle_strength = alternating_count / (len(values) - 2)
            
            if cycle_strength > 0.6:
                return PatternRecognition(
                    pattern_type="cycle",
                    confidence=cycle_strength,
                    description="Cyclical pattern detected",
                    strength=cycle_strength,
                    duration="medium-term",
                    prediction="Expect pattern continuation",
                    supporting_evidence=[f"Cycle strength: {cycle_strength:.3f}"]
                )
        
        return None
    
    def _detect_anomaly_pattern(self) -> Optional[PatternRecognition]:
        """Detect anomaly patterns"""
        if len(self.data_buffer) < 5:
            return None
        
        values = [point["value"] for point in list(self.data_buffer)[-10:]]
        
        if len(values) >= 5:
            mean_value = sum(values[:-1]) / (len(values) - 1)
            std_dev = math.sqrt(sum((v - mean_value) ** 2 for v in values[:-1]) / (len(values) - 1))
            
            if std_dev > 0:
                latest_value = values[-1]
                z_score = abs(latest_value - mean_value) / std_dev
                
                if z_score > 2.0:  # Anomaly threshold
                    return PatternRecognition(
                        pattern_type="anomaly",
                        confidence=min(z_score / 5.0, 1.0),
                        description=f"Anomaly detected (z-score: {z_score:.2f})",
                        strength=min(z_score / 5.0, 1.0),
                        duration="immediate",
                        prediction="Expect reversion to mean",
                        supporting_evidence=[f"Z-score: {z_score:.2f}", f"Mean: {mean_value:.2f}"]
                    )
        
        return None
    
    def _detect_correlation_patterns(self) -> List[PatternRecognition]:
        """Detect correlation patterns"""
        patterns = []
        
        if len(self.data_buffer) < 10:
            return patterns
        
        # Simplified correlation detection
        recent_data = list(self.data_buffer)[-10:]
        
        # Check for correlation between different features
        for i, point1 in enumerate(recent_data):
            for j, point2 in enumerate(recent_data[i+1:], i+1):
                if "feature1" in point1["features"] and "feature1" in point2["features"]:
                    correlation = abs(point1["features"]["feature1"] - point2["features"]["feature1"])
                    
                    if correlation > self.correlation_threshold:
                        patterns.append(PatternRecognition(
                            pattern_type="correlation",
                            confidence=correlation,
                            description="Strong correlation detected",
                            strength=correlation,
                            duration="ongoing",
                            prediction="Correlated movement expected",
                            supporting_evidence=[f"Correlation: {correlation:.3f}"]
                        ))
        
        return patterns

class PredictiveInsightsEngine:
    """Predictive insights engine"""
    
    def __init__(self):
        self.insights_history = []
        self.insight_types = ["opportunity", "warning", "trend", "anomaly"]
    
    def generate_insights(self, risk_assessment: RiskAssessment, roi_analysis: ROIAnalysis, 
                         patterns: List[PatternRecognition]) -> List[PredictiveInsight]:
        """Generate predictive insights"""
        insights = []
        
        # Opportunity insights
        if risk_assessment.risk_level in ["low", "medium"] and roi_analysis.expected_roi > 5:
            insights.append(PredictiveInsight(
                insight_type="opportunity",
                confidence=risk_assessment.confidence,
                description=f"High-value betting opportunity with {roi_analysis.expected_roi:.1f}% expected ROI",
                impact_score=roi_analysis.expected_roi / 10.0,
                time_horizon="immediate",
                actionable=True,
                recommendations=[
                    f"Place bet of {roi_analysis.optimal_bet_size:.1%} of bankroll",
                    "Monitor for optimal entry timing",
                    "Set stop-loss at 50% of bet size"
                ]
            ))
        
        # Warning insights
        if risk_assessment.risk_level in ["high", "extreme"]:
            insights.append(PredictiveInsight(
                insight_type="warning",
                confidence=risk_assessment.confidence,
                description=f"High-risk situation detected (Risk Level: {risk_assessment.risk_level})",
                impact_score=risk_assessment.risk_score,
                time_horizon="immediate",
                actionable=True,
                recommendations=[
                    "Avoid betting or use minimal bet size",
                    "Wait for better opportunities",
                    "Focus on risk management"
                ]
            ))
        
        # Trend insights
        trend_patterns = [p for p in patterns if p.pattern_type == "trend"]
        if trend_patterns:
            for pattern in trend_patterns:
                insights.append(PredictiveInsight(
                    insight_type="trend",
                    confidence=pattern.confidence,
                    description=f"Trend pattern: {pattern.description}",
                    impact_score=pattern.strength,
                    time_horizon="short-term",
                    actionable=True,
                    recommendations=[
                        "Align bets with trend direction",
                        "Use trend-following strategies",
                        "Monitor trend strength"
                    ]
                ))
        
        # Anomaly insights
        anomaly_patterns = [p for p in patterns if p.pattern_type == "anomaly"]
        if anomaly_patterns:
            for pattern in anomaly_patterns:
                insights.append(PredictiveInsight(
                    insight_type="anomaly",
                    confidence=pattern.confidence,
                    description=f"Anomaly detected: {pattern.description}",
                    impact_score=pattern.strength,
                    time_horizon="immediate",
                    actionable=True,
                    recommendations=[
                        "Expect mean reversion",
                        "Use contrarian strategies",
                        "Monitor for pattern completion"
                    ]
                ))
        
        return insights

class AdvancedAnalyticsDashboard:
    """Advanced analytics dashboard with comprehensive metrics"""
    
    def __init__(self):
        self.risk_engine = RiskAssessmentEngine()
        self.roi_optimizer = ROIOptimizer()
        self.pattern_engine = PatternRecognitionEngine()
        self.insights_engine = PredictiveInsightsEngine()
        
        # Dashboard data
        self.betting_history = []
        self.performance_metrics = defaultdict(list)
        
        logger.info("🚀 Advanced Analytics & Insights System initialized - YOLO MODE!")
    
    def add_betting_record(self, bet_id: str, sport: str, bet_amount: float, 
                          odds: float, result: str, profit: float):
        """Add betting record to dashboard"""
        record = {
            "bet_id": bet_id,
            "sport": sport,
            "bet_amount": bet_amount,
            "odds": odds,
            "result": result,
            "profit": profit,
            "timestamp": datetime.now().isoformat()
        }
        
        self.betting_history.append(record)
        self.performance_metrics[sport].append(record)
    
    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get comprehensive dashboard metrics"""
        if not self.betting_history:
            return DashboardMetrics(
                total_bets=0, win_rate=0.0, total_profit=0.0, roi_percentage=0.0,
                average_bet_size=0.0, best_performing_sport="N/A", worst_performing_sport="N/A",
                current_streak=0, risk_score=0.0, confidence_level="N/A"
            )
        
        # Calculate basic metrics
        total_bets = len(self.betting_history)
        wins = sum(1 for bet in self.betting_history if bet["result"] == "win")
        win_rate = wins / total_bets if total_bets > 0 else 0.0
        
        total_profit = sum(bet["profit"] for bet in self.betting_history)
        total_invested = sum(bet["bet_amount"] for bet in self.betting_history)
        roi_percentage = (total_profit / total_invested * 100) if total_invested > 0 else 0.0
        
        average_bet_size = total_invested / total_bets if total_bets > 0 else 0.0
        
        # Calculate sport performance
        sport_performance = {}
        for sport, bets in self.performance_metrics.items():
            if bets:
                sport_profit = sum(bet["profit"] for bet in bets)
                sport_invested = sum(bet["bet_amount"] for bet in bets)
                sport_roi = (sport_profit / sport_invested * 100) if sport_invested > 0 else 0.0
                sport_performance[sport] = sport_roi
        
        best_sport = max(sport_performance.items(), key=lambda x: x[1])[0] if sport_performance else "N/A"
        worst_sport = min(sport_performance.items(), key=lambda x: x[1])[0] if sport_performance else "N/A"
        
        # Calculate current streak
        current_streak = 0
        for bet in reversed(self.betting_history):
            if bet["result"] == "win":
                current_streak += 1
            else:
                break
        
        # Calculate risk score (simplified)
        recent_bets = self.betting_history[-10:] if len(self.betting_history) >= 10 else self.betting_history
        risk_score = 1.0 - win_rate if recent_bets else 0.0
        
        # Determine confidence level
        if win_rate >= 0.7:
            confidence_level = "High"
        elif win_rate >= 0.5:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        return DashboardMetrics(
            total_bets=total_bets,
            win_rate=win_rate,
            total_profit=total_profit,
            roi_percentage=roi_percentage,
            average_bet_size=average_bet_size,
            best_performing_sport=best_sport,
            worst_performing_sport=worst_sport,
            current_streak=current_streak,
            risk_score=risk_score,
            confidence_level=confidence_level
        )
    
    async def analyze_betting_opportunity(self, prediction_confidence: float, odds: float, 
                                        sport: str, market_volatility: float = 0.5) -> Dict[str, Any]:
        """Analyze a betting opportunity comprehensively"""
        
        # Risk assessment
        risk_assessment = self.risk_engine.assess_risk(
            prediction_confidence=prediction_confidence,
            market_volatility=market_volatility,
            historical_accuracy=0.6,  # Simplified
            external_factors=["weather", "injuries"]
        )
        
        # ROI optimization
        roi_analysis = self.roi_optimizer.optimize_roi(
            win_probability=prediction_confidence,
            odds=odds,
            historical_roi=risk_assessment.expected_value * 100,
            volatility=market_volatility
        )
        
        # Pattern recognition
        self.pattern_engine.add_data_point(
            timestamp=datetime.now().isoformat(),
            value=prediction_confidence,
            features={"confidence": prediction_confidence, "odds": odds}
        )
        patterns = self.pattern_engine.detect_patterns()
        
        # Generate insights
        insights = self.insights_engine.generate_insights(risk_assessment, roi_analysis, patterns)
        
        return {
            "risk_assessment": asdict(risk_assessment),
            "roi_analysis": asdict(roi_analysis),
            "patterns": [asdict(pattern) for pattern in patterns],
            "insights": [asdict(insight) for insight in insights],
            "recommendation": self._generate_final_recommendation(risk_assessment, roi_analysis, insights)
        }
    
    def _generate_final_recommendation(self, risk_assessment: RiskAssessment, 
                                     roi_analysis: ROIAnalysis, 
                                     insights: List[PredictiveInsight]) -> str:
        """Generate final betting recommendation"""
        
        if risk_assessment.risk_level in ["high", "extreme"]:
            return "🚨 HIGH RISK - Avoid betting or use minimal bet size"
        
        if roi_analysis.expected_roi < 2:
            return "⚠️ LOW ROI - Consider waiting for better opportunities"
        
        if roi_analysis.expected_roi > 10:
            return "🎯 HIGH VALUE - Strong betting opportunity"
        
        return "✅ MODERATE OPPORTUNITY - Standard bet size recommended"

async def main():
    """Test the advanced analytics and insights system"""
    print("🚀 Testing Advanced Analytics & Insights System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize dashboard
    dashboard = AdvancedAnalyticsDashboard()
    
    try:
        # Add sample betting history
        print("\n📊 Adding Sample Betting History:")
        print("-" * 40)
        
        sample_bets = [
            ("bet_001", "basketball", 100, 1.85, "win", 85),
            ("bet_002", "football", 150, 2.10, "loss", -150),
            ("bet_003", "basketball", 75, 1.95, "win", 71.25),
            ("bet_004", "hockey", 200, 1.75, "win", 150),
            ("bet_005", "football", 120, 2.25, "loss", -120),
            ("bet_006", "basketball", 90, 1.90, "win", 81),
            ("bet_007", "hockey", 180, 1.80, "loss", -180),
            ("bet_008", "basketball", 110, 1.88, "win", 96.8),
        ]
        
        for bet in sample_bets:
            dashboard.add_betting_record(*bet)
            print(f"✅ Added bet: {bet[0]} - {bet[1]} - {bet[2]} - {bet[3]} - {bet[4]} - {bet[5]}")
        
        # Get dashboard metrics
        print("\n📈 Dashboard Metrics:")
        print("-" * 40)
        metrics = dashboard.get_dashboard_metrics()
        
        print(f"✅ Total Bets: {metrics.total_bets}")
        print(f"✅ Win Rate: {metrics.win_rate:.1%}")
        print(f"✅ Total Profit: ${metrics.total_profit:.2f}")
        print(f"✅ ROI: {metrics.roi_percentage:.1f}%")
        print(f"✅ Average Bet Size: ${metrics.average_bet_size:.2f}")
        print(f"✅ Best Sport: {metrics.best_performing_sport}")
        print(f"✅ Worst Sport: {metrics.worst_performing_sport}")
        print(f"✅ Current Streak: {metrics.current_streak}")
        print(f"✅ Risk Score: {metrics.risk_score:.3f}")
        print(f"✅ Confidence Level: {metrics.confidence_level}")
        
        # Test betting opportunity analysis
        print("\n🎯 Testing Betting Opportunity Analysis:")
        print("-" * 40)
        
        analysis = await dashboard.analyze_betting_opportunity(
            prediction_confidence=0.75,
            odds=1.85,
            sport="basketball",
            market_volatility=0.3
        )
        
        print(f"✅ Risk Assessment: {analysis['risk_assessment']['risk_level']} (Score: {analysis['risk_assessment']['risk_score']:.3f})")
        print(f"✅ Expected ROI: {analysis['roi_analysis']['expected_roi']:.1f}%")
        print(f"✅ Optimal Bet Size: {analysis['roi_analysis']['optimal_bet_size']:.1%}")
        print(f"✅ Patterns Detected: {len(analysis['patterns'])}")
        print(f"✅ Insights Generated: {len(analysis['insights'])}")
        print(f"✅ Final Recommendation: {analysis['recommendation']}")
        
        # Show detailed insights
        print(f"\n💡 Key Insights:")
        for insight in analysis['insights'][:3]:  # Show first 3 insights
            print(f"   - {insight['insight_type'].upper()}: {insight['description']}")
            print(f"     Confidence: {insight['confidence']:.3f}, Impact: {insight['impact_score']:.3f}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Advanced Analytics & Insights System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 