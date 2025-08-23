#!/usr/bin/env python3
"""
Simple Test for Enhanced AI Models
"""

print("🧪 Testing Enhanced AI Models Simple System")
print("=" * 50)

# Test basic imports
print("🔍 Testing imports...")

try:
    import numpy as np
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
except ImportError as e:
    print(f"❌ pandas import failed: {e}")

try:
    from enhanced_ai_models_simple import EnhancedAIModels
    print("✅ EnhancedAIModels imported successfully")
except ImportError as e:
    print(f"❌ EnhancedAIModels import failed: {e}")

# Test basic functionality
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
    print(f"   Features: {features[:5]}...")  # Show first 5 features
    
    # Test model creation
    print(f"✅ Models created: {list(ai_system.models.keys())}")
    
    # Test ensemble weights
    print(f"✅ Ensemble weights: {ai_system.ensemble_weights}")
    
    print("\n🎉 Basic functionality test passed!")
    
except Exception as e:
    print(f"❌ Basic functionality test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🎉 Enhanced AI Models Simple System Test Completed!")
print("=" * 50) 