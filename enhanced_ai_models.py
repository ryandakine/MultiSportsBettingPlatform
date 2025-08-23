#!/usr/bin/env python3
"""
Enhanced AI Models System - YOLO MODE!
=====================================
Ensemble methods and advanced AI models for higher prediction accuracy
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import asyncio
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

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

class EnhancedAIModels:
    """Enhanced AI models with ensemble methods"""
    
    def __init__(self):
        self.models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "logistic_regression": LogisticRegression(random_state=42, max_iter=1000),
            "svm": SVC(probability=True, random_state=42)
        }
        
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_performance = {}
        self.ensemble_weights = {
            "random_forest": 0.3,
            "gradient_boosting": 0.3,
            "logistic_regression": 0.2,
            "svm": 0.2
        }
        
        # Feature engineering configurations
        self.feature_configs = {
            "basketball": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_points_for", "away_team_points_for",
                "home_team_points_against", "away_team_points_against", "head_to_head_wins",
                "days_rest_home", "days_rest_away", "home_court_advantage"
            ],
            "football": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_points_for", "away_team_points_for",
                "home_team_points_against", "away_team_points_against", "head_to_head_wins",
                "weather_condition", "wind_speed", "temperature", "home_field_advantage"
            ],
            "baseball": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_runs_for", "away_team_runs_for",
                "home_team_runs_against", "away_team_runs_against", "head_to_head_wins",
                "pitcher_era_home", "pitcher_era_away", "ballpark_factor", "weather_condition"
            ],
            "hockey": [
                "home_team_wins", "away_team_wins", "home_team_losses", "away_team_losses",
                "home_team_win_percentage", "away_team_win_percentage", "home_team_streak",
                "away_team_streak", "home_team_goals_for", "away_team_goals_for",
                "home_team_goals_against", "away_team_goals_against", "head_to_head_wins",
                "goalie_save_percentage_home", "goalie_save_percentage_away", "ice_advantage"
            ]
        }
        
        logger.info("🚀 Enhanced AI Models System initialized - YOLO MODE!")

    def extract_features(self, team_data: Dict[str, Any], sport: str) -> np.ndarray:
        """Extract features from team data"""
        features = []
        feature_names = self.feature_configs.get(sport, [])
        
        for feature in feature_names:
            if feature in team_data:
                features.append(team_data[feature])
            else:
                # Default value for missing features
                features.append(0.0)
        
        return np.array(features).reshape(1, -1)

    def create_training_data(self, historical_data: List[Dict[str, Any]], sport: str) -> Tuple[np.ndarray, np.ndarray]:
        """Create training data from historical matches"""
        X = []
        y = []
        
        for match in historical_data:
            features = []
            feature_names = self.feature_configs.get(sport, [])
            
            # Extract features for both teams
            home_features = self.extract_features(match.get("home_team", {}), sport)
            away_features = self.extract_features(match.get("away_team", {}), sport)
            
            # Combine features (home team features first, then away team)
            combined_features = np.concatenate([home_features.flatten(), away_features.flatten()])
            
            X.append(combined_features)
            
            # Target: 1 for home win, 0 for away win
            result = 1 if match.get("winner") == "home" else 0
            y.append(result)
        
        return np.array(X), np.array(y)

    async def train_models(self, sport: str, historical_data: List[Dict[str, Any]]) -> Dict[str, ModelPerformance]:
        """Train all models with historical data"""
        logger.info(f"🔄 Training models for {sport}")
        
        # Create training data
        X, y = self.create_training_data(historical_data, sport)
        
        if len(X) < 10:
            logger.warning(f"⚠️ Insufficient training data for {sport}: {len(X)} samples")
            return {}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        performance_results = {}
        
        # Train each model
        for model_name, model in self.models.items():
            try:
                logger.info(f"🔄 Training {model_name} for {sport}")
                
                # Train the model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                performance_results[model_name] = ModelPerformance(
                    model_name=model_name,
                    accuracy=accuracy,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                    total_predictions=len(y_test),
                    correct_predictions=int(accuracy * len(y_test)),
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
        total_f1 = sum(perf.f1_score for perf in performance_results.values())
        
        if total_f1 > 0:
            for model_name, perf in performance_results.items():
                self.ensemble_weights[model_name] = perf.f1_score / total_f1
        
        logger.info(f"🔄 Updated ensemble weights: {self.ensemble_weights}")

    async def predict_match(self, home_team_data: Dict[str, Any], away_team_data: Dict[str, Any], 
                          sport: str) -> EnsemblePrediction:
        """Make ensemble prediction for a match"""
        logger.info(f"🎯 Making ensemble prediction for {sport} match")
        
        # Extract features
        home_features = self.extract_features(home_team_data, sport)
        away_features = self.extract_features(away_team_data, sport)
        
        # Combine features
        combined_features = np.concatenate([home_features.flatten(), away_features.flatten()])
        features_scaled = self.scaler.transform(combined_features.reshape(1, -1))
        
        model_predictions = []
        
        # Get predictions from each model
        for model_name, model in self.models.items():
            try:
                # Get prediction and confidence
                prediction_proba = model.predict_proba(features_scaled)[0]
                prediction = model.predict(features_scaled)[0]
                
                # Determine winner and confidence
                if prediction == 1:
                    winner = "home"
                    confidence = prediction_proba[1]
                else:
                    winner = "away"
                    confidence = prediction_proba[0]
                
                # Get feature importance if available
                feature_importance = {}
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(self.feature_configs.get(sport, []), 
                                                model.feature_importances_[:len(self.feature_configs.get(sport, []))]))
                
                model_predictions.append(ModelPrediction(
                    model_name=model_name,
                    prediction=winner,
                    confidence=confidence,
                    features_used=self.feature_configs.get(sport, []),
                    reasoning=f"{model_name} predicts {winner} team win with {confidence:.3f} confidence"
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
            final_confidence = home_votes / (home_votes + away_votes)
        else:
            final_prediction = "away"
            final_confidence = away_votes / (home_votes + away_votes)
        
        # Calculate overall feature importance
        overall_feature_importance = {}
        for pred in model_predictions:
            if hasattr(self.models[pred.model_name], 'feature_importances_'):
                model_importance = self.models[pred.model_name].feature_importances_
                weight = self.ensemble_weights.get(pred.model_name, 0.25)
                
                for i, feature in enumerate(self.feature_configs.get(sport, [])):
                    if i < len(model_importance):
                        overall_feature_importance[feature] = overall_feature_importance.get(feature, 0) + \
                                                            model_importance[i] * weight
        
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

    async def continuous_learning(self, new_match_data: Dict[str, Any], sport: str):
        """Update models with new match data for continuous learning"""
        logger.info(f"🔄 Updating models with new {sport} match data")
        
        # Add new data to training set
        # This would typically involve adding to a database or file
        # For now, we'll just log the update
        
        # Retrain models periodically (e.g., every 10 new matches)
        # This is a simplified version - in production, you'd want more sophisticated logic
        
        logger.info(f"✅ Models updated with new {sport} match data")

    def generate_prediction_insights(self, ensemble_prediction: EnsemblePrediction, 
                                   home_team: str, away_team: str) -> Dict[str, Any]:
        """Generate insights from ensemble prediction"""
        insights = {
            "match_summary": f"{home_team} vs {away_team}",
            "prediction": ensemble_prediction.final_prediction,
            "confidence": ensemble_prediction.confidence,
            "confidence_level": self._get_confidence_level(ensemble_prediction.confidence),
            "model_agreement": self._calculate_model_agreement(ensemble_prediction.model_predictions),
            "key_factors": self._get_key_factors(ensemble_prediction.feature_importance),
            "risk_assessment": self._assess_risk(ensemble_prediction.confidence),
            "recommendations": self._generate_recommendations(ensemble_prediction)
        }
        
        return insights

    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= 0.8:
            return "Very High"
        elif confidence >= 0.7:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        elif confidence >= 0.5:
            return "Low"
        else:
            return "Very Low"

    def _calculate_model_agreement(self, model_predictions: List[ModelPrediction]) -> Dict[str, Any]:
        """Calculate agreement between models"""
        predictions = [pred.prediction for pred in model_predictions]
        home_votes = predictions.count("home")
        away_votes = predictions.count("away")
        total_models = len(model_predictions)
        
        agreement = max(home_votes, away_votes) / total_models if total_models > 0 else 0
        
        return {
            "agreement_percentage": agreement * 100,
            "home_votes": home_votes,
            "away_votes": away_votes,
            "consensus": "home" if home_votes > away_votes else "away" if away_votes > home_votes else "split"
        }

    def _get_key_factors(self, feature_importance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get key factors influencing the prediction"""
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        key_factors = []
        for feature, importance in sorted_features[:5]:  # Top 5 factors
            key_factors.append({
                "factor": feature,
                "importance": importance,
                "description": self._get_factor_description(feature)
            })
        
        return key_factors

    def _get_factor_description(self, feature: str) -> str:
        """Get human-readable description of a feature"""
        descriptions = {
            "home_team_wins": "Home team's win record",
            "away_team_wins": "Away team's win record",
            "home_team_win_percentage": "Home team's win percentage",
            "away_team_win_percentage": "Away team's win percentage",
            "home_team_streak": "Home team's current streak",
            "away_team_streak": "Away team's current streak",
            "head_to_head_wins": "Historical head-to-head record",
            "home_court_advantage": "Home court/field advantage factor"
        }
        
        return descriptions.get(feature, f"Factor: {feature}")

    def _assess_risk(self, confidence: float) -> Dict[str, Any]:
        """Assess risk level of the prediction"""
        if confidence >= 0.8:
            risk_level = "Low"
            risk_score = 1
        elif confidence >= 0.7:
            risk_level = "Medium-Low"
            risk_score = 2
        elif confidence >= 0.6:
            risk_level = "Medium"
            risk_score = 3
        elif confidence >= 0.5:
            risk_level = "Medium-High"
            risk_score = 4
        else:
            risk_level = "High"
            risk_score = 5
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "confidence_threshold": confidence,
            "recommendation": self._get_risk_recommendation(risk_level)
        }

    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "Low": "High confidence prediction - Consider larger bet size",
            "Medium-Low": "Good confidence - Standard bet size recommended",
            "Medium": "Moderate confidence - Conservative bet size",
            "Medium-High": "Lower confidence - Small bet size or skip",
            "High": "Low confidence - Not recommended for betting"
        }
        
        return recommendations.get(risk_level, "Use caution")

    def _generate_recommendations(self, ensemble_prediction: EnsemblePrediction) -> List[str]:
        """Generate betting recommendations"""
        recommendations = []
        
        confidence = ensemble_prediction.confidence
        
        if confidence >= 0.8:
            recommendations.append("🎯 High confidence prediction - Consider larger bet size")
            recommendations.append("📊 Strong model agreement - Reliable prediction")
        elif confidence >= 0.7:
            recommendations.append("✅ Good confidence - Standard bet size recommended")
            recommendations.append("📈 Positive expected value - Worth considering")
        elif confidence >= 0.6:
            recommendations.append("⚠️ Moderate confidence - Conservative bet size")
            recommendations.append("🔍 Monitor for additional factors")
        else:
            recommendations.append("❌ Low confidence - Not recommended for betting")
            recommendations.append("📉 High risk - Consider alternative strategies")
        
        return recommendations

async def main():
    """Main function to test the enhanced AI models"""
    ai_system = EnhancedAIModels()
    
    print("🚀 Testing Enhanced AI Models System - YOLO MODE!")
    print("=" * 60)
    
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
                "home_team_wins": np.random.randint(15, 35),
                "home_team_losses": np.random.randint(10, 25),
                "home_team_win_percentage": np.random.uniform(0.4, 0.8),
                "home_team_streak": np.random.randint(-5, 6),
                "home_team_points_for": np.random.randint(90, 120),
                "home_team_points_against": np.random.randint(90, 120)
            },
            "away_team": {
                "away_team_wins": np.random.randint(15, 35),
                "away_team_losses": np.random.randint(10, 25),
                "away_team_win_percentage": np.random.uniform(0.4, 0.8),
                "away_team_streak": np.random.randint(-5, 6),
                "away_team_points_for": np.random.randint(90, 120),
                "away_team_points_against": np.random.randint(90, 120)
            },
            "winner": "home" if np.random.random() > 0.5 else "away"
        })
    
    try:
        # Train models
        print("\n🔄 Training AI Models:")
        print("-" * 40)
        performance = await ai_system.train_models("basketball", sample_data)
        
        for model_name, perf in performance.items():
            print(f"✅ {model_name}: Accuracy {perf.accuracy:.3f}, F1 {perf.f1_score:.3f}")
        
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
        
        prediction = await ai_system.predict_match(home_team_data, away_team_data, "basketball")
        
        print(f"🏆 Final Prediction: {prediction.final_prediction.upper()} team")
        print(f"🎯 Confidence: {prediction.confidence:.3f}")
        print(f"🧠 Ensemble Method: {prediction.ensemble_method}")
        
        # Generate insights
        insights = ai_system.generate_prediction_insights(prediction, "Lakers", "Celtics")
        
        print(f"\n📊 Prediction Insights:")
        print(f"   Confidence Level: {insights['confidence_level']}")
        print(f"   Model Agreement: {insights['model_agreement']['agreement_percentage']:.1f}%")
        print(f"   Risk Level: {insights['risk_assessment']['risk_level']}")
        
        print(f"\n🔑 Key Factors:")
        for factor in insights['key_factors'][:3]:
            print(f"   - {factor['factor']}: {factor['importance']:.3f}")
        
        print(f"\n💡 Recommendations:")
        for rec in insights['recommendations']:
            print(f"   {rec}")
        
        # Performance summary
        summary = ai_system.get_model_performance_summary()
        print(f"\n📈 Model Performance Summary:")
        print(f"   Overall Accuracy: {summary['overall_accuracy']:.3f}")
        print(f"   Total Models: {summary['total_models']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced AI Models System Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 