#!/usr/bin/env python3
"""
Enhanced AI Models System - No NumPy Version - YOLO MODE!
==========================================================
Ensemble methods and advanced AI models for higher prediction accuracy
(Version without numpy dependency to avoid Python 3.14 alpha issues)
"""

import random
import math
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelPrediction:
    """Individual model prediction"""
    model_name: str
    prediction: str
    confidence: float
    features_used: List[str]
    reasoning: str

@dataclass
class EnsemblePrediction:
    """Ensemble prediction result"""
    final_prediction: str
    confidence: float
    model_predictions: List[ModelPrediction]
    ensemble_method: str
    feature_importance: Dict[str, float]
    timestamp: str

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    total_predictions: int
    correct_predictions: int
    last_updated: str

def calculate_percentile(values, percentile):
    """Calculate percentile without numpy"""
    if not values:
        return 0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[index]

class SimpleLinearModel:
    """Simple linear model for predictions"""
    
    def __init__(self, name: str):
        self.name = name
        self.weights = {}
        self.bias = 0.0
        self.trained = False
        
    def train(self, features: List[str], training_data: List[Dict[str, Any]]):
        """Simple training using linear regression approach"""
        if not training_data:
            return
            
        # Initialize weights
        for feature in features:
            self.weights[feature] = random.uniform(-1, 1)
        
        # Simple gradient descent (simplified)
        learning_rate = 0.01
        epochs = 100
        
        for epoch in range(epochs):
            total_error = 0
            
            for data_point in training_data:
                # Extract features
                feature_values = []
                for feature in features:
                    value = data_point.get(feature, 0.0)
                    feature_values.append(value)
                
                # Calculate prediction
                prediction = self.predict_internal(feature_values)
                actual = 1.0 if data_point.get("winner") == "home" else 0.0
                
                # Calculate error
                error = actual - prediction
                total_error += abs(error)
                
                # Update weights (simplified) with bounds checking
                for i, feature in enumerate(features):
                    weight_update = learning_rate * error * feature_values[i]
                    # Clamp weight updates to prevent explosion
                    if abs(weight_update) > 1.0:
                        weight_update = 1.0 if weight_update > 0 else -1.0
                    self.weights[feature] += weight_update
                    
                    # Clamp final weights
                    if abs(self.weights[feature]) > 10.0:
                        self.weights[feature] = 10.0 if self.weights[feature] > 0 else -10.0
                
                bias_update = learning_rate * error
                if abs(bias_update) > 1.0:
                    bias_update = 1.0 if bias_update > 0 else -1.0
                self.bias += bias_update
                
                # Clamp bias
                if abs(self.bias) > 10.0:
                    self.bias = 10.0 if self.bias > 0 else -10.0
            
            if epoch % 20 == 0:
                logger.info(f"Epoch {epoch}: Average error = {total_error / len(training_data):.4f}")
        
        self.trained = True
        logger.info(f"✅ {self.name} training completed")
    
    def predict_internal(self, feature_values: List[float]) -> float:
        """Internal prediction method"""
        if not self.trained:
            return 0.5
        
        result = self.bias
        for i, (feature, weight) in enumerate(self.weights.items()):
            if i < len(feature_values):
                result += weight * feature_values[i]
        
        # Sigmoid activation with bounds checking to prevent math range error
        try:
            # Clamp the result to prevent overflow
            if result > 500:
                result = 500
            elif result < -500:
                result = -500
            
            return 1.0 / (1.0 + math.exp(-result))
        except (OverflowError, ValueError):
            # Fallback to simple threshold
            return 0.5 if result > 0 else 0.0
    
    def predict(self, feature_values: List[float]) -> Tuple[str, float]:
        """Make prediction"""
        prob = self.predict_internal(feature_values)
        prediction = "home" if prob > 0.5 else "away"
        confidence = prob if prob > 0.5 else 1.0 - prob
        return prediction, confidence

class SimpleRandomForest:
    """Simple random forest implementation"""
    
    def __init__(self, name: str, n_trees: int = 10):
        self.name = name
        self.n_trees = n_trees
        self.trees = []
        self.trained = False
        
    def train(self, features: List[str], training_data: List[Dict[str, Any]]):
        """Train multiple simple decision trees"""
        if not training_data:
            return
            
        for i in range(self.n_trees):
            # Create a simple decision tree
            tree = SimpleDecisionTree(f"Tree_{i}")
            
            # Sample data with replacement (bootstrap)
            sample_size = len(training_data)
            sample_data = random.choices(training_data, k=sample_size)
            
            # Train the tree
            tree.train(features, sample_data)
            self.trees.append(tree)
        
        self.trained = True
        logger.info(f"✅ {self.name} training completed with {self.n_trees} trees")
    
    def predict(self, feature_values: List[float]) -> Tuple[str, float]:
        """Make prediction using majority voting"""
        if not self.trained:
            return "home", 0.5
        
        home_votes = 0
        total_confidence = 0
        
        for tree in self.trees:
            pred, conf = tree.predict(feature_values)
            if pred == "home":
                home_votes += 1
            total_confidence += conf
        
        # Calculate final prediction
        home_prob = home_votes / len(self.trees)
        prediction = "home" if home_prob > 0.5 else "away"
        confidence = home_prob if home_prob > 0.5 else 1.0 - home_prob
        
        return prediction, confidence

class SimpleDecisionTree:
    """Simple decision tree implementation"""
    
    def __init__(self, name: str):
        self.name = name
        self.root = None
        self.trained = False
        
    def train(self, features: List[str], training_data: List[Dict[str, Any]]):
        """Train a simple decision tree"""
        if not training_data:
            return
            
        # Create root node
        self.root = self._create_node(features, training_data)
        self.trained = True
    
    def _create_node(self, features: List[str], data: List[Dict[str, Any]], depth: int = 0) -> Dict:
        """Recursively create decision tree nodes"""
        if depth >= 3 or len(data) < 5:  # Limit depth and minimum data
            # Create leaf node
            home_count = sum(1 for d in data if d.get("winner") == "home")
            total_count = len(data)
            home_prob = home_count / total_count if total_count > 0 else 0.5
            
            return {
                "type": "leaf",
                "home_prob": home_prob,
                "total_count": total_count
            }
        
        # Find best split
        best_feature = None
        best_threshold = 0
        best_gain = -1
        
        for feature in features:
            values = [d.get(feature, 0.0) for d in data]
            if not values:
                continue
                
            # Try different thresholds
            for percentile in [25, 50, 75]:
                threshold = calculate_percentile(values, percentile)
                left_data = [d for d in data if d.get(feature, 0.0) <= threshold]
                right_data = [d for d in data if d.get(feature, 0.0) > threshold]
                
                if len(left_data) == 0 or len(right_data) == 0:
                    continue
                
                # Calculate information gain (simplified)
                gain = self._calculate_gain(data, left_data, right_data)
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        
        if best_feature is None:
            # Create leaf node
            home_count = sum(1 for d in data if d.get("winner") == "home")
            total_count = len(data)
            home_prob = home_count / total_count if total_count > 0 else 0.5
            
            return {
                "type": "leaf",
                "home_prob": home_prob,
                "total_count": total_count
            }
        
        # Split data
        left_data = [d for d in data if d.get(best_feature, 0.0) <= best_threshold]
        right_data = [d for d in data if d.get(best_feature, 0.0) > best_threshold]
        
        return {
            "type": "split",
            "feature": best_feature,
            "threshold": best_threshold,
            "left": self._create_node(features, left_data, depth + 1),
            "right": self._create_node(features, right_data, depth + 1)
        }
    
    def _calculate_gain(self, parent_data: List[Dict], left_data: List[Dict], right_data: List[Dict]) -> float:
        """Calculate information gain (simplified)"""
        def entropy(data):
            if not data:
                return 0
            home_count = sum(1 for d in data if d.get("winner") == "home")
            total = len(data)
            if total == 0:
                return 0
            p = home_count / total
            if p == 0 or p == 1:
                return 0
            return -p * math.log2(p) - (1-p) * math.log2(1-p)
        
        parent_entropy = entropy(parent_data)
        left_entropy = entropy(left_data)
        right_entropy = entropy(right_data)
        
        left_weight = len(left_data) / len(parent_data)
        right_weight = len(right_data) / len(parent_data)
        
        return parent_entropy - (left_weight * left_entropy + right_weight * right_entropy)
    
    def predict(self, feature_values: List[float]) -> Tuple[str, float]:
        """Make prediction by traversing the tree"""
        if not self.trained or self.root is None:
            return "home", 0.5
        
        node = self.root
        while node["type"] == "split":
            feature_idx = 0  # Simplified - assume feature order matches
            if feature_values[feature_idx] <= node["threshold"]:
                node = node["left"]
            else:
                node = node["right"]
        
        # Leaf node
        home_prob = node["home_prob"]
        prediction = "home" if home_prob > 0.5 else "away"
        confidence = home_prob if home_prob > 0.5 else 1.0 - home_prob
        
        return prediction, confidence

class EnhancedAIModels:
    """Enhanced AI models with ensemble methods (no numpy version)"""
    
    def __init__(self):
        self.models = {
            "linear_model": SimpleLinearModel("Linear Model"),
            "random_forest": SimpleRandomForest("Random Forest", n_trees=5),
            "decision_tree": SimpleDecisionTree("Decision Tree"),
            "ensemble": SimpleRandomForest("Ensemble", n_trees=3)
        }
        
        self.feature_names = []
        self.model_performance = {}
        self.ensemble_weights = {
            "linear_model": 0.25,
            "random_forest": 0.3,
            "decision_tree": 0.25,
            "ensemble": 0.2
        }
        
        # Feature engineering configurations
        self.feature_configs = {
            "basketball": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_points_for", "away_team_points_for",
                "home_team_points_against", "away_team_points_against", "head_to_head_wins"
            ],
            "football": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_points_for", "away_team_points_for",
                "home_team_points_against", "away_team_points_against", "head_to_head_wins"
            ],
            "baseball": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_runs_for", "away_team_runs_for",
                "home_team_runs_against", "away_team_runs_against", "head_to_head_wins"
            ],
            "hockey": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_goals_for", "away_team_goals_for",
                "home_team_goals_against", "away_team_goals_against", "head_to_head_wins"
            ]
        }
        
        logger.info("🚀 Enhanced AI Models System (No NumPy) initialized - YOLO MODE!")

    def extract_features(self, team_data: Dict[str, Any], sport: str) -> List[float]:
        """Extract features from team data"""
        features = []
        feature_names = self.feature_configs.get(sport, [])
        
        for feature in feature_names:
            if feature in team_data:
                features.append(float(team_data[feature]))
            else:
                # Default value for missing features
                features.append(0.0)
        
        return features

    def create_training_data(self, historical_data: List[Dict[str, Any]], sport: str) -> List[Dict[str, Any]]:
        """Create training data from historical matches"""
        training_data = []
        
        for match in historical_data:
            # Extract features for both teams
            home_features = self.extract_features(match.get("home_team", {}), sport)
            away_features = self.extract_features(match.get("away_team", {}), sport)
            
            # Combine features (home team features first, then away team)
            combined_features = home_features + away_features
            
            # Create training data point
            data_point = {
                "winner": match.get("winner", "home")
            }
            
            # Add features
            feature_names = self.feature_configs.get(sport, [])
            for i, feature in enumerate(feature_names):
                if i < len(home_features):
                    data_point[feature] = home_features[i]
                if i < len(away_features):
                    data_point[f"away_{feature}"] = away_features[i]
            
            training_data.append(data_point)
        
        return training_data

    def train_models(self, sport: str, historical_data: List[Dict[str, Any]]) -> Dict[str, ModelPerformance]:
        """Train all models with historical data"""
        logger.info(f"🔄 Training models for {sport}")
        
        # Create training data
        training_data = self.create_training_data(historical_data, sport)
        
        if len(training_data) < 5:
            logger.warning(f"⚠️ Insufficient training data for {sport}: {len(training_data)} samples")
            return {}
        
        # Split data for validation
        random.shuffle(training_data)
        split_idx = int(len(training_data) * 0.8)
        train_data = training_data[:split_idx]
        test_data = training_data[split_idx:]
        
        performance_results = {}
        
        # Train each model
        for model_name, model in self.models.items():
            try:
                logger.info(f"🔄 Training {model_name} for {sport}")
                
                # Get feature names for this sport
                feature_names = self.feature_configs.get(sport, [])
                
                # Train the model
                model.train(feature_names, train_data)
                
                # Test the model
                correct_predictions = 0
                total_predictions = len(test_data)
                
                for data_point in test_data:
                    # Extract features for prediction
                    home_features = []
                    away_features = []
                    
                    for feature in feature_names:
                        home_features.append(data_point.get(feature, 0.0))
                        away_features.append(data_point.get(f"away_{feature}", 0.0))
                    
                    combined_features = home_features + away_features
                    
                    # Make prediction
                    prediction, confidence = model.predict(combined_features)
                    actual = data_point.get("winner", "home")
                    
                    if prediction == actual:
                        correct_predictions += 1
                
                # Calculate metrics
                accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
                
                performance_results[model_name] = ModelPerformance(
                    model_name=model_name,
                    accuracy=accuracy,
                    precision=accuracy,  # Simplified
                    recall=accuracy,     # Simplified
                    f1_score=accuracy,   # Simplified
                    total_predictions=total_predictions,
                    correct_predictions=correct_predictions,
                    last_updated=datetime.now().isoformat()
                )
                
                logger.info(f"✅ {model_name} trained - Accuracy: {accuracy:.3f}")
                
            except Exception as e:
                logger.error(f"❌ Error training {model_name}: {e}")
        
        # Update ensemble weights based on performance
        self._update_ensemble_weights(performance_results)
        
        return performance_results

    def _update_ensemble_weights(self, performance_results: Dict[str, ModelPerformance]):
        """Update ensemble weights based on model performance"""
        total_accuracy = sum(perf.accuracy for perf in performance_results.values())
        
        if total_accuracy > 0:
            for model_name, perf in performance_results.items():
                self.ensemble_weights[model_name] = perf.accuracy / total_accuracy
        
        logger.info(f"🔄 Updated ensemble weights: {self.ensemble_weights}")

    def predict_match(self, home_team_data: Dict[str, Any], away_team_data: Dict[str, Any], 
                     sport: str) -> EnsemblePrediction:
        """Make ensemble prediction for a match"""
        logger.info(f"🎯 Making ensemble prediction for {sport} match")
        
        # Extract features
        home_features = self.extract_features(home_team_data, sport)
        away_features = self.extract_features(away_team_data, sport)
        
        # Combine features
        combined_features = home_features + away_features
        
        model_predictions = []
        
        # Get predictions from each model
        for model_name, model in self.models.items():
            try:
                # Get prediction and confidence
                prediction, confidence = model.predict(combined_features)
                
                # Get feature importance (simplified)
                feature_importance = {}
                feature_names = self.feature_configs.get(sport, [])
                for i, feature in enumerate(feature_names):
                    if i < len(home_features):
                        feature_importance[feature] = abs(home_features[i]) / 100.0  # Simplified importance
                
                model_predictions.append(ModelPrediction(
                    model_name=model_name,
                    prediction=prediction,
                    confidence=confidence,
                    features_used=feature_names,
                    reasoning=f"{model_name} predicts {prediction} team win with {confidence:.3f} confidence"
                ))
                
            except Exception as e:
                logger.error(f"❌ Error with {model_name} prediction: {e}")
        
        # Ensemble prediction using weighted voting
        home_votes = 0.0
        away_votes = 0.0
        
        for pred in model_predictions:
            weight = self.ensemble_weights.get(pred.model_name, 0.25)
            if pred.prediction == "home":
                home_votes += weight * pred.confidence
            else:
                away_votes += weight * pred.confidence
        
        # Determine final prediction
        if home_votes > away_votes:
            final_prediction = "home"
            final_confidence = home_votes / (home_votes + away_votes) if (home_votes + away_votes) > 0 else 0.5
        else:
            final_prediction = "away"
            final_confidence = away_votes / (home_votes + away_votes) if (home_votes + away_votes) > 0 else 0.5
        
        # Calculate overall feature importance (simplified)
        overall_feature_importance = {}
        feature_names = self.feature_configs.get(sport, [])
        for i, feature in enumerate(feature_names):
            if i < len(home_features):
                overall_feature_importance[feature] = abs(home_features[i]) / 100.0
        
        return EnsemblePrediction(
            final_prediction=final_prediction,
            confidence=final_confidence,
            model_predictions=model_predictions,
            ensemble_method="weighted_voting",
            feature_importance=overall_feature_importance,
            timestamp=datetime.now().isoformat()
        )

    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all model performances"""
        summary = {
            "total_models": len(self.models),
            "ensemble_weights": self.ensemble_weights,
            "model_performances": {},
            "overall_accuracy": 0.0
        }
        
        total_accuracy = 0.0
        valid_models = 0
        
        for model_name, perf in self.model_performance.items():
            summary["model_performances"][model_name] = asdict(perf)
            total_accuracy += perf.accuracy
            valid_models += 1
        
        if valid_models > 0:
            summary["overall_accuracy"] = total_accuracy / valid_models
        
        return summary

def main():
    """Main function to test the enhanced AI models"""
    ai_system = EnhancedAIModels()
    
    print("🚀 Testing Enhanced AI Models System (No NumPy) - YOLO MODE!")
    print("=" * 70)
    
    # Sample historical data for training
    sample_data = [
        {
            "home_team": {
                "home_team_wins": 25, "home_team_losses": 15, "home_team_win_percentage": 0.625,
                "home_team_streak": 3, "home_team_points_for": 110, "home_team_points_against": 105
            },
            "away_team": {
                "away_team_wins": 20, "away_team_losses": 20, "away_team_win_percentage": 0.5,
                "away_team_streak": -1, "away_team_points_for": 105, "away_team_points_against": 108
            },
            "winner": "home"
        },
        {
            "home_team": {
                "home_team_wins": 18, "home_team_losses": 22, "home_team_win_percentage": 0.45,
                "home_team_streak": -2, "home_team_points_for": 100, "home_team_points_against": 110
            },
            "away_team": {
                "away_team_wins": 28, "away_team_losses": 12, "away_team_win_percentage": 0.7,
                "away_team_streak": 4, "away_team_points_for": 115, "away_team_points_against": 100
            },
            "winner": "away"
        }
    ]
    
    # Add more sample data for better training
    for i in range(20):
        sample_data.append({
            "home_team": {
                "home_team_wins": random.randint(15, 35),
                "home_team_losses": random.randint(10, 25),
                "home_team_win_percentage": random.uniform(0.4, 0.8),
                "home_team_streak": random.randint(-5, 6),
                "home_team_points_for": random.randint(90, 120),
                "home_team_points_against": random.randint(90, 120)
            },
            "away_team": {
                "away_team_wins": random.randint(15, 35),
                "away_team_losses": random.randint(10, 25),
                "away_team_win_percentage": random.uniform(0.4, 0.8),
                "away_team_streak": random.randint(-5, 6),
                "away_team_points_for": random.randint(90, 120),
                "away_team_points_against": random.randint(90, 120)
            },
            "winner": "home" if random.random() > 0.5 else "away"
        })
    
    try:
        # Train models
        print("\n🔄 Training AI Models:")
        print("-" * 40)
        performance = ai_system.train_models("basketball", sample_data)
        
        for model_name, perf in performance.items():
            print(f"✅ {model_name}: Accuracy {perf.accuracy:.3f}")
        
        # Make prediction
        print("\n🎯 Making Ensemble Prediction:")
        print("-" * 40)
        
        home_team_data = {
            "home_team_wins": 30, "home_team_losses": 10, "home_team_win_percentage": 0.75,
            "home_team_streak": 5, "home_team_points_for": 115, "home_team_points_against": 100
        }
        
        away_team_data = {
            "away_team_wins": 20, "away_team_losses": 20, "away_team_win_percentage": 0.5,
            "away_team_streak": -2, "away_team_points_for": 105, "away_team_points_against": 110
        }
        
        prediction = ai_system.predict_match(home_team_data, away_team_data, "basketball")
        
        print(f"🏆 Final Prediction: {prediction.final_prediction.upper()} team")
        print(f"🎯 Confidence: {prediction.confidence:.3f}")
        print(f"🧠 Ensemble Method: {prediction.ensemble_method}")
        
        print(f"\n📊 Model Predictions:")
        for model_pred in prediction.model_predictions:
            print(f"   - {model_pred.model_name}: {model_pred.prediction} ({model_pred.confidence:.3f})")
        
        # Performance summary
        summary = ai_system.get_model_performance_summary()
        print(f"\n📈 Model Performance Summary:")
        print(f"   Overall Accuracy: {summary['overall_accuracy']:.3f}")
        print(f"   Total Models: {summary['total_models']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Enhanced AI Models System (No NumPy) Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    main() 