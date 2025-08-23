#!/usr/bin/env python3
"""
Prediction Aggregation and Weighting System for MultiSportsBettingPlatform
Intelligently combines predictions from multiple sports with appropriate weighting.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for predictions."""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

class SportType(Enum):
    """Supported sports."""
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HOCKEY = "hockey"

@dataclass
class Prediction:
    """Individual prediction from a sport agent."""
    sport: SportType
    agent_name: str
    prediction: str  # e.g., "Team A wins", "Over 2.5 goals"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime
    metadata: Dict[str, Any]
    historical_accuracy: Optional[float] = None
    user_preference_weight: float = 1.0

@dataclass
class AggregatedPrediction:
    """Final aggregated prediction."""
    combined_prediction: str
    overall_confidence: float
    sport_breakdown: Dict[str, Dict[str, Any]]
    reasoning: str
    timestamp: datetime
    metadata: Dict[str, Any]
    recommendations: List[str]

class WeightingStrategy(Enum):
    """Different weighting strategies for aggregation."""
    CONFIDENCE_ONLY = "confidence_only"
    HISTORICAL_ACCURACY = "historical_accuracy"
    USER_PREFERENCE = "user_preference"
    HYBRID = "hybrid"
    EQUAL_WEIGHT = "equal_weight"

class PredictionAggregator:
    """Main prediction aggregation system."""
    
    def __init__(self, strategy: WeightingStrategy = WeightingStrategy.HYBRID):
        self.strategy = strategy
        self.historical_data = defaultdict(list)
        self.user_preferences = {}
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.performance_metrics = defaultdict(list)
        
        # Sport-specific weights (can be adjusted based on performance)
        self.sport_weights = {
            SportType.BASEBALL: 1.0,
            SportType.BASKETBALL: 1.0,
            SportType.FOOTBALL: 1.0,
            SportType.HOCKEY: 1.0
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "very_high": 0.9
        }
    
    async def collect_predictions(self, sub_agents: Dict[SportType, Any], 
                                query: str, user_id: str = None) -> List[Prediction]:
        """Collect predictions from all sub-agents."""
        predictions = []
        
        for sport, agent in sub_agents.items():
            try:
                logger.info(f"Collecting prediction from {sport.value} agent")
                
                # Get prediction from agent
                agent_prediction = await agent.get_prediction(query)
                
                if agent_prediction:
                    prediction = Prediction(
                        sport=sport,
                        agent_name=agent.name,
                        prediction=agent_prediction.get('prediction', ''),
                        confidence=agent_prediction.get('confidence', 0.5),
                        reasoning=agent_prediction.get('reasoning', ''),
                        timestamp=datetime.now(),
                        metadata=agent_prediction.get('metadata', {}),
                        historical_accuracy=self.get_historical_accuracy(sport, agent.name),
                        user_preference_weight=self.get_user_preference_weight(sport, user_id)
                    )
                    predictions.append(prediction)
                    
                    logger.info(f"✅ Collected prediction from {sport.value}: {prediction.prediction} (confidence: {prediction.confidence})")
                else:
                    logger.warning(f"❌ No prediction received from {sport.value} agent")
                    
            except Exception as e:
                logger.error(f"❌ Error collecting prediction from {sport.value} agent: {e}")
        
        return predictions
    
    def calculate_weighted_confidence(self, prediction: Prediction) -> float:
        """Calculate weighted confidence based on strategy."""
        base_confidence = prediction.confidence
        
        if self.strategy == WeightingStrategy.CONFIDENCE_ONLY:
            return base_confidence
        
        elif self.strategy == WeightingStrategy.HISTORICAL_ACCURACY:
            if prediction.historical_accuracy:
                return (base_confidence + prediction.historical_accuracy) / 2
            return base_confidence
        
        elif self.strategy == WeightingStrategy.USER_PREFERENCE:
            return base_confidence * prediction.user_preference_weight
        
        elif self.strategy == WeightingStrategy.HYBRID:
            # Combine confidence, historical accuracy, and user preference
            weights = {
                'confidence': 0.4,
                'historical': 0.4,
                'user_pref': 0.2
            }
            
            weighted_sum = base_confidence * weights['confidence']
            
            if prediction.historical_accuracy:
                weighted_sum += prediction.historical_accuracy * weights['historical']
            else:
                weighted_sum += base_confidence * weights['historical']
            
            weighted_sum += prediction.user_preference_weight * weights['user_pref']
            
            return min(weighted_sum, 1.0)  # Cap at 1.0
        
        else:  # EQUAL_WEIGHT
            return base_confidence
    
    def aggregate_predictions(self, predictions: List[Prediction]) -> AggregatedPrediction:
        """Aggregate multiple predictions into a single weighted prediction."""
        if not predictions:
            return self._create_empty_prediction()
        
        # Group predictions by sport
        sport_predictions = defaultdict(list)
        for pred in predictions:
            sport_predictions[pred.sport].append(pred)
        
        # Calculate weighted predictions for each sport
        sport_results = {}
        total_weighted_confidence = 0
        total_weight = 0
        
        for sport, sport_preds in sport_predictions.items():
            sport_weight = self.sport_weights[sport]
            
            # Calculate weighted average for this sport
            weighted_confidence_sum = 0
            total_sport_weight = 0
            
            for pred in sport_preds:
                weighted_confidence = self.calculate_weighted_confidence(pred)
                weighted_confidence_sum += weighted_confidence * sport_weight
                total_sport_weight += sport_weight
            
            avg_confidence = weighted_confidence_sum / total_sport_weight if total_sport_weight > 0 else 0
            
            # Get most common prediction for this sport
            prediction_counts = defaultdict(int)
            for pred in sport_preds:
                prediction_counts[pred.prediction] += 1
            
            most_common_prediction = max(prediction_counts.items(), key=lambda x: x[1])[0]
            
            sport_results[sport.value] = {
                'prediction': most_common_prediction,
                'confidence': avg_confidence,
                'agent_count': len(sport_preds),
                'reasoning': self._combine_reasoning([p.reasoning for p in sport_preds]),
                'metadata': self._merge_metadata([p.metadata for p in sport_preds])
            }
            
            total_weighted_confidence += avg_confidence * sport_weight
            total_weight += sport_weight
        
        # Calculate overall confidence
        overall_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0
        
        # Generate combined prediction
        combined_prediction = self._generate_combined_prediction(sport_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sport_results, overall_confidence)
        
        return AggregatedPrediction(
            combined_prediction=combined_prediction,
            overall_confidence=overall_confidence,
            sport_breakdown=sport_results,
            reasoning=self._generate_overall_reasoning(sport_results),
            timestamp=datetime.now(),
            metadata={
                'strategy_used': self.strategy.value,
                'total_predictions': len(predictions),
                'sports_covered': list(sport_results.keys()),
                'aggregation_version': '1.0'
            },
            recommendations=recommendations
        )
    
    def _create_empty_prediction(self) -> AggregatedPrediction:
        """Create an empty prediction when no data is available."""
        return AggregatedPrediction(
            combined_prediction="No predictions available",
            overall_confidence=0.0,
            sport_breakdown={},
            reasoning="No predictions were collected from any sport agents",
            timestamp=datetime.now(),
            metadata={'error': 'no_predictions'},
            recommendations=["Try again later", "Check agent connectivity"]
        )
    
    def _combine_reasoning(self, reasoning_list: List[str]) -> str:
        """Combine multiple reasoning strings into one."""
        if not reasoning_list:
            return "No reasoning provided"
        
        if len(reasoning_list) == 1:
            return reasoning_list[0]
        
        # Combine reasoning with bullet points
        combined = "Combined analysis:\n"
        for i, reasoning in enumerate(reasoning_list, 1):
            combined += f"• {reasoning}\n"
        
        return combined.strip()
    
    def _merge_metadata(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple metadata dictionaries."""
        merged = {}
        
        for metadata in metadata_list:
            for key, value in metadata.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key].update(value)
        
        return merged
    
    def _generate_combined_prediction(self, sport_results: Dict[str, Dict]) -> str:
        """Generate a combined prediction from all sports."""
        if not sport_results:
            return "No predictions available"
        
        # Find the sport with highest confidence
        best_sport = max(sport_results.items(), key=lambda x: x[1]['confidence'])
        sport_name, sport_data = best_sport
        
        # Generate combined prediction
        predictions = []
        for sport, data in sport_results.items():
            if data['confidence'] >= self.confidence_thresholds['medium']:
                predictions.append(f"{sport.title()}: {data['prediction']}")
        
        if predictions:
            return " | ".join(predictions)
        else:
            return f"Primary ({sport_name}): {sport_data['prediction']}"
    
    def _generate_overall_reasoning(self, sport_results: Dict[str, Dict]) -> str:
        """Generate overall reasoning for the aggregated prediction."""
        if not sport_results:
            return "No predictions available for analysis"
        
        reasoning_parts = []
        
        # Add confidence summary
        confidences = [data['confidence'] for data in sport_results.values()]
        avg_confidence = statistics.mean(confidences)
        reasoning_parts.append(f"Average confidence across sports: {avg_confidence:.2f}")
        
        # Add sport coverage
        sport_count = len(sport_results)
        reasoning_parts.append(f"Predictions from {sport_count} sports")
        
        # Add best performing sport
        best_sport = max(sport_results.items(), key=lambda x: x[1]['confidence'])
        reasoning_parts.append(f"Highest confidence: {best_sport[0]} ({best_sport[1]['confidence']:.2f})")
        
        return ". ".join(reasoning_parts)
    
    def _generate_recommendations(self, sport_results: Dict[str, Dict], 
                                overall_confidence: float) -> List[str]:
        """Generate betting recommendations based on aggregated data."""
        recommendations = []
        
        if overall_confidence >= self.confidence_thresholds['high']:
            recommendations.append("High confidence prediction - Consider larger bet")
        elif overall_confidence >= self.confidence_thresholds['medium']:
            recommendations.append("Medium confidence - Moderate bet size recommended")
        else:
            recommendations.append("Low confidence - Small bet or wait for better odds")
        
        # Sport-specific recommendations
        for sport, data in sport_results.items():
            if data['confidence'] >= self.confidence_thresholds['high']:
                recommendations.append(f"Strong {sport} prediction - Focus on this sport")
        
        # Add general recommendations
        recommendations.append("Always bet responsibly and within your limits")
        
        return recommendations
    
    def get_historical_accuracy(self, sport: SportType, agent_name: str) -> Optional[float]:
        """Get historical accuracy for a sport agent."""
        # This would typically query a database
        # For now, return a default value
        return 0.75  # 75% accuracy
    
    def get_user_preference_weight(self, sport: SportType, user_id: str = None) -> float:
        """Get user preference weight for a sport."""
        if not user_id:
            return 1.0
        
        # This would typically query user preferences
        # For now, return default weights
        user_prefs = self.user_preferences.get(user_id, {})
        return user_prefs.get(sport.value, 1.0)
    
    def update_historical_accuracy(self, sport: SportType, agent_name: str, 
                                 prediction: str, actual_result: str, 
                                 was_correct: bool):
        """Update historical accuracy data."""
        accuracy_data = {
            'timestamp': datetime.now(),
            'prediction': prediction,
            'actual_result': actual_result,
            'was_correct': was_correct
        }
        
        key = f"{sport.value}_{agent_name}"
        self.historical_data[key].append(accuracy_data)
        
        # Keep only last 100 predictions
        if len(self.historical_data[key]) > 100:
            self.historical_data[key] = self.historical_data[key][-100:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the aggregator."""
        return {
            'strategy': self.strategy.value,
            'total_predictions_processed': sum(len(data) for data in self.historical_data.values()),
            'sport_weights': {sport.value: weight for sport, weight in self.sport_weights.items()},
            'confidence_thresholds': self.confidence_thresholds,
            'cache_size': len(self.cache)
        } 