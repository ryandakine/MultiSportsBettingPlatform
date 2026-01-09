#!/usr/bin/env python3
"""
Verify lightgbm Installation
=============================
Tests that lightgbm is properly installed and can be used.
"""

import sys
from pathlib import Path

def test_lightgbm():
    """Test lightgbm installation and basic functionality."""
    print("=" * 60)
    print("🔍 VERIFYING LIGHTGBM INSTALLATION")
    print("=" * 60)
    print()
    
    # Test import
    try:
        import lightgbm as lgb
        print(f"✅ lightgbm imported successfully")
        print(f"   Version: {lgb.__version__}")
        print(f"   Location: {lgb.__file__}")
    except ImportError as e:
        print(f"❌ lightgbm import failed: {e}")
        print()
        print("   To install:")
        print("   pip install lightgbm")
        return False
    
    # Test basic functionality
    try:
        import numpy as np
        
        # Create simple dataset
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 1, 0, 1])
        
        # Train model
        model = lgb.LGBMClassifier(n_estimators=10, verbose=-1, random_state=42)
        model.fit(X, y)
        
        # Make prediction
        pred = model.predict([[2, 3]])
        proba = model.predict_proba([[2, 3]])
        
        print(f"✅ Basic functionality test passed")
        print(f"   Prediction: {pred[0]}")
        print(f"   Probabilities: {proba[0]}")
    except Exception as e:
        print(f"⚠️  Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test loading NHL model if it exists
    print()
    model_path = Path("models/trained/nhl_model.pkl")
    if model_path.exists():
        print(f"📦 Testing NHL model load...")
        try:
            import pickle
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            print(f"   ✅ NHL model loaded successfully")
            if isinstance(model_data, dict):
                print(f"   Model structure: dict with keys: {list(model_data.keys())[:10]}")
                if 'model' in model_data:
                    model = model_data['model']
                    print(f"   Model object type: {type(model).__name__}")
                    
                    # Try to use the model
                    if hasattr(model, 'predict'):
                        print(f"   ✅ Model has predict method")
                    if hasattr(model, 'predict_proba'):
                        print(f"   ✅ Model has predict_proba method")
            else:
                print(f"   Model structure: {type(model_data).__name__}")
                
        except Exception as e:
            print(f"   ⚠️  Error loading NHL model: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"ℹ️  NHL model not found at {model_path}")
        print(f"   (This is okay if you haven't copied models yet)")
    
    print()
    print("=" * 60)
    print("✅ LIGHTGBM VERIFICATION COMPLETE")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_lightgbm()
    sys.exit(0 if success else 1)


