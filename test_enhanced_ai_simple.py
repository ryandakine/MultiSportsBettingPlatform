#!/usr/bin/env python3
"""
Test Enhanced AI Models Simple System
"""

import asyncio
import sys
import traceback

def test_imports():
    """Test if all required imports work"""
    print("🔍 Testing imports...")
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        from enhanced_ai_models_simple import EnhancedAIModels
        print("✅ EnhancedAIModels imported successfully")
    except ImportError as e:
        print(f"❌ EnhancedAIModels import failed: {e}")
        return False
    
    return True

async def test_basic_functionality():
    """Test basic functionality of the AI system"""
    print("\n🚀 Testing basic functionality...")
    
    try:
        from enhanced_ai_models_simple import EnhancedAIModels
        
        # Create AI system
        ai_system = EnhancedAIModels()
        print("✅ AI system created successfully")
        
        # Test feature extraction
        home_team_data = {
            "home_team_wins": 25,
            "home_team_losses": 15,
            "home_team_win_percentage": 0.625,
            "home_team_streak": 3,
            "home_team_points_for": 110,
            "home_team_points_against": 105
        }
        
        features = ai_system.extract_features(home_team_data, "basketball")
        print(f"✅ Feature extraction works: {len(features)} features extracted")
        
        # Test prediction
        away_team_data = {
            "away_team_wins": 20,
            "away_team_losses": 20,
            "away_team_win_percentage": 0.5,
            "away_team_streak": -1,
            "away_team_points_for": 105,
            "away_team_points_against": 108
        }
        
        prediction = await ai_system.predict_match(home_team_data, away_team_data, "basketball")
        print(f"✅ Prediction made: {prediction.final_prediction} (confidence: {prediction.confidence:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

async def test_training():
    """Test model training"""
    print("\n🔄 Testing model training...")
    
    try:
        from enhanced_ai_models_simple import EnhancedAIModels
        
        ai_system = EnhancedAIModels()
        
        # Create sample training data
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
        
        # Train models
        performance = await ai_system.train_models("basketball", sample_data)
        print(f"✅ Training completed: {len(performance)} models trained")
        
        for model_name, perf in performance.items():
            print(f"   - {model_name}: {perf.accuracy:.3f} accuracy")
        
        return True
        
    except Exception as e:
        print(f"❌ Training test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🧪 Testing Enhanced AI Models Simple System")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed - cannot proceed")
        return
    
    # Test basic functionality
    if not await test_basic_functionality():
        print("❌ Basic functionality test failed")
        return
    
    # Test training
    if not await test_training():
        print("❌ Training test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Enhanced AI Models Simple System is working!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 