"""
Enhanced Prediction Aggregator Service - YOLO MODE!
================================================
Advanced prediction aggregation with multiple weighting strategies and YOLO enhancements.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, OrderedDict

class AggregationStrategy(str, Enum):
    """Prediction aggregation strategies."""
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    HISTORICAL_ACCURACY = "historical_accuracy"
    USER_PREFERENCE = "user_preference"
    HYBRID = "hybrid"
    EQUAL_WEIGHT = "equal_weight"
    YOLO_MODE = "yolo_mode"

@dataclass
class SportPrediction:
    """Individual sport prediction."""
    sport: str
    prediction: str
    confidence: float
    reasoning: str
    timestamp: datetime
    agent_id: str
    yolo_factor: float
    odds: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class AggregatedPrediction:
    """Aggregated prediction result."""
    prediction_id: str
    query: str
    individual_predictions: Dict[str, SportPrediction]
    combined_prediction: str
    overall_confidence: float
    strategy_used: AggregationStrategy
    sports_analyzed: List[str]
    timestamp: datetime
    yolo_boost: float
    reasoning: str
    recommendations: List[str]

class PredictionAggregatorV2:
    """Enhanced prediction aggregator with YOLO mode."""
    
    def __init__(self):
        self.prediction_history: List[AggregatedPrediction] = []
        self.sport_accuracy: Dict[str, float] = {
            "baseball": 0.85,
            "basketball": 0.88,
            "football": 0.82,
            "hockey": 0.80
        }
        self.user_preferences: Dict[str, Dict[str, float]] = {}
        self.yolo_mode_active = True
        
        # YOLO prediction templates
        self.yolo_templates = {
            "baseball": [
                "YOLO bet on the underdog! The stats don't lie! 🎯",
                "Home run prediction: YOLO style! This is going to be epic! 💥",
                "Pitcher's duel - YOLO under! Defense wins championships! ⚾"
            ],
            "basketball": [
                "YOLO bet on the home team! Home court advantage is real! 🏀",
                "Three-pointer barrage incoming! YOLO over is the way! 🎯",
                "Defense wins championships - YOLO under! Lockdown mode! 🛡️"
            ],
            "football": [
                "YOLO bet on the under! Defense wins championships! 🏈",
                "Touchdown prediction: YOLO style! Offense is unstoppable! 🎯",
                "Field goal frenzy - YOLO over! Special teams matter! ⚡"
            ],
            "hockey": [
                "YOLO bet on overtime! Hockey is unpredictable - perfect! 🏒",
                "Hat trick prediction incoming! Offense is on fire! 🎩",
                "Goalie showdown - YOLO under! Defense wins games! 🥅"
            ]
        }
    
    async def aggregate_predictions(self, predictions: Dict[str, SportPrediction], 
                                  strategy: AggregationStrategy = AggregationStrategy.YOLO_MODE,
                                  user_id: Optional[str] = None) -> AggregatedPrediction:
        """Aggregate predictions using specified strategy."""
        
        if not predictions:
            raise ValueError("No predictions provided for aggregation")
        
        prediction_id = f"agg_pred_{int(datetime.now().timestamp())}"
        sports_analyzed = list(predictions.keys())
        
        # Apply YOLO mode enhancements
        if self.yolo_mode_active:
            for sport, pred in predictions.items():
                pred.yolo_factor = min(2.0, pred.yolo_factor * random.uniform(1.1, 1.5))
                pred.confidence = min(1.0, pred.confidence * random.uniform(1.05, 1.2))
        
        # Aggregate based on strategy
        if strategy == AggregationStrategy.CONFIDENCE_WEIGHTED:
            combined_pred, overall_conf, reasoning = self._confidence_weighted_aggregation(predictions)
        elif strategy == AggregationStrategy.HISTORICAL_ACCURACY:
            combined_pred, overall_conf, reasoning = self._historical_accuracy_aggregation(predictions)
        elif strategy == AggregationStrategy.USER_PREFERENCE:
            combined_pred, overall_conf, reasoning = self._user_preference_aggregation(predictions, user_id)
        elif strategy == AggregationStrategy.HYBRID:
            combined_pred, overall_conf, reasoning = self._hybrid_aggregation(predictions, user_id)
        elif strategy == AggregationStrategy.EQUAL_WEIGHT:
            combined_pred, overall_conf, reasoning = self._equal_weight_aggregation(predictions)
        elif strategy == AggregationStrategy.YOLO_MODE:
            combined_pred, overall_conf, reasoning = self._yolo_mode_aggregation(predictions)
        else:
            combined_pred, overall_conf, reasoning = self._yolo_mode_aggregation(predictions)
        
        # Generate YOLO boost
        yolo_boost = random.uniform(1.0, 2.0)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(predictions, overall_conf)
        
        aggregated = AggregatedPrediction(
            prediction_id=prediction_id,
            query=f"YOLO prediction for {', '.join(sports_analyzed)}",
            individual_predictions=predictions,
            combined_prediction=combined_pred,
            overall_confidence=overall_conf,
            strategy_used=strategy,
            sports_analyzed=sports_analyzed,
            timestamp=datetime.now(),
            yolo_boost=yolo_boost,
            reasoning=reasoning,
            recommendations=recommendations
        )
        
        self.prediction_history.append(aggregated)
        
        return aggregated
    
    def _confidence_weighted_aggregation(self, predictions: Dict[str, SportPrediction]) -> Tuple[str, float, str]:
        """Aggregate based on confidence scores."""
        total_weight = 0
        weighted_predictions = []
        
        for sport, pred in predictions.items():
            weight = pred.confidence * pred.yolo_factor
            total_weight += weight
            weighted_predictions.append((pred.prediction, weight))
        
        if total_weight == 0:
            return "YOLO bet with confidence!", 0.8, "Confidence-based aggregation with YOLO boost"
        
        # Select prediction based on weights
        random_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for prediction, weight in weighted_predictions:
            current_weight += weight
            if random_val <= current_weight:
                return prediction, total_weight / len(predictions), "Confidence-weighted aggregation"
        
        return weighted_predictions[-1][0], total_weight / len(predictions), "Confidence-weighted aggregation"
    
    def _historical_accuracy_aggregation(self, predictions: Dict[str, SportPrediction]) -> Tuple[str, float, str]:
        """Aggregate based on historical accuracy."""
        total_weight = 0
        weighted_predictions = []
        
        for sport, pred in predictions.items():
            accuracy = self.sport_accuracy.get(sport, 0.75)
            weight = accuracy * pred.yolo_factor
            total_weight += weight
            weighted_predictions.append((pred.prediction, weight))
        
        if total_weight == 0:
            return "YOLO bet based on history!", 0.8, "Historical accuracy aggregation"
        
        # Select prediction based on historical accuracy
        random_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for prediction, weight in weighted_predictions:
            current_weight += weight
            if random_val <= current_weight:
                return prediction, total_weight / len(predictions), "Historical accuracy aggregation"
        
        return weighted_predictions[-1][0], total_weight / len(predictions), "Historical accuracy aggregation"
    
    def _user_preference_aggregation(self, predictions: Dict[str, SportPrediction], 
                                   user_id: Optional[str]) -> Tuple[str, float, str]:
        """Aggregate based on user preferences."""
        if not user_id or user_id not in self.user_preferences:
            return self._yolo_mode_aggregation(predictions)
        
        user_prefs = self.user_preferences[user_id]
        total_weight = 0
        weighted_predictions = []
        
        for sport, pred in predictions.items():
            pref_weight = user_prefs.get(sport, 0.5)
            weight = pref_weight * pred.yolo_factor
            total_weight += weight
            weighted_predictions.append((pred.prediction, weight))
        
        if total_weight == 0:
            return "YOLO bet based on your preferences!", 0.8, "User preference aggregation"
        
        # Select prediction based on user preferences
        random_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for prediction, weight in weighted_predictions:
            current_weight += weight
            if random_val <= current_weight:
                return prediction, total_weight / len(predictions), "User preference aggregation"
        
        return weighted_predictions[-1][0], total_weight / len(predictions), "User preference aggregation"
    
    def _hybrid_aggregation(self, predictions: Dict[str, SportPrediction], 
                          user_id: Optional[str]) -> Tuple[str, float, str]:
        """Hybrid aggregation combining multiple strategies."""
        # Get predictions from different strategies
        conf_pred, conf_conf, _ = self._confidence_weighted_aggregation(predictions)
        hist_pred, hist_conf, _ = self._historical_accuracy_aggregation(predictions)
        user_pred, user_conf, _ = self._user_preference_aggregation(predictions, user_id)
        
        # Combine with YOLO boost
        strategies = [
            (conf_pred, conf_conf * 0.4),
            (hist_pred, hist_conf * 0.3),
            (user_pred, user_conf * 0.3)
        ]
        
        total_weight = sum(weight for _, weight in strategies)
        random_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for prediction, weight in strategies:
            current_weight += weight
            if random_val <= current_weight:
                return prediction, total_weight, "Hybrid aggregation with YOLO boost"
        
        return strategies[-1][0], total_weight, "Hybrid aggregation with YOLO boost"
    
    def _equal_weight_aggregation(self, predictions: Dict[str, SportPrediction]) -> Tuple[str, float, str]:
        """Equal weight aggregation."""
        predictions_list = list(predictions.values())
        selected_pred = random.choice(predictions_list)
        
        avg_confidence = sum(p.confidence for p in predictions_list) / len(predictions_list)
        
        return selected_pred.prediction, avg_confidence, "Equal weight aggregation"
    
    def _yolo_mode_aggregation(self, predictions: Dict[str, SportPrediction]) -> Tuple[str, float, str]:
        """YOLO mode aggregation - maximum confidence!"""
        # Select the prediction with highest YOLO factor
        best_pred = max(predictions.values(), key=lambda p: p.yolo_factor)
        
        # Apply YOLO boost
        yolo_boost = random.uniform(1.2, 2.0)
        boosted_confidence = min(1.0, best_pred.confidence * yolo_boost)
        
        # Generate YOLO reasoning
        reasoning = f"YOLO mode activated! {best_pred.sport} analysis with maximum confidence. When in doubt, YOLO it out! 🚀"
        
        return best_pred.prediction, boosted_confidence, reasoning
    
    def _generate_recommendations(self, predictions: Dict[str, SportPrediction], 
                                overall_confidence: float) -> List[str]:
        """Generate YOLO recommendations."""
        recommendations = []
        
        if overall_confidence > 0.9:
            recommendations.append("🚀 YOLO MODE: Maximum confidence - bet with conviction!")
        elif overall_confidence > 0.8:
            recommendations.append("🎯 High confidence: Strong YOLO prediction!")
        elif overall_confidence > 0.7:
            recommendations.append("⚡ Good confidence: YOLO bet recommended!")
        else:
            recommendations.append("🤔 Moderate confidence: YOLO with caution!")
        
        # Sport-specific recommendations
        for sport, pred in predictions.items():
            if pred.yolo_factor > 1.5:
                recommendations.append(f"🔥 {sport.title()}: YOLO factor is off the charts!")
        
        # Add random YOLO wisdom
        yolo_wisdom = [
            "When in doubt, YOLO it out! 🚀",
            "YOLO predictions never fail! 🎯",
            "Trust the YOLO! 🏆",
            "YOLO mode is always right! ⚡",
            "High risk, high reward! 💰"
        ]
        
        recommendations.append(random.choice(yolo_wisdom))
        
        return recommendations
    
    def update_sport_accuracy(self, sport: str, accuracy: float):
        """Update historical accuracy for a sport."""
        self.sport_accuracy[sport] = max(0.0, min(1.0, accuracy))
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, float]):
        """Set user preferences for sports."""
        self.user_preferences[user_id] = preferences
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics."""
        if not self.prediction_history:
            return {
                "total_predictions": 0,
                "average_confidence": 0.0,
                "most_used_strategy": "none",
                "yolo_predictions": 0,
                "yolo_energy": "MINIMAL"
            }
        
        total_predictions = len(self.prediction_history)
        avg_confidence = sum(p.overall_confidence for p in self.prediction_history) / total_predictions
        
        # Count strategies
        strategy_counts = defaultdict(int)
        for pred in self.prediction_history:
            strategy_counts[pred.strategy_used] += 1
        
        most_used_strategy = max(strategy_counts.items(), key=lambda x: x[1])[0]
        yolo_predictions = strategy_counts.get(AggregationStrategy.YOLO_MODE, 0)
        
        return {
            "total_predictions": total_predictions,
            "average_confidence": round(avg_confidence, 3),
            "most_used_strategy": most_used_strategy,
            "yolo_predictions": yolo_predictions,
            "yolo_energy": "MAXIMUM!" if yolo_predictions > total_predictions * 0.5 else "HIGH" if yolo_predictions > 0 else "MINIMAL",
            "sport_accuracy": self.sport_accuracy,
            "active_users": len(self.user_preferences)
        }

# Global instance
prediction_aggregator_v2 = PredictionAggregatorV2() 