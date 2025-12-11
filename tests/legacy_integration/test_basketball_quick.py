#!/usr/bin/env python3
"""
Quick Basketball System Test - YOLO MODE!
========================================
Simple test to verify basketball system is working.
"""

import requests
import json

def test_basketball():
    """Quick test of basketball system - YOLO MODE!"""
    base_url = "http://localhost:8006"
    
    print("🏀 Testing Basketball System - YOLO MODE!")
    print("=" * 50)
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data.get('status', 'Unknown')}")
            print(f"✅ System: {data.get('system', 'Basketball')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test teams
    try:
        response = requests.get(f"{base_url}/api/v1/teams")
        if response.status_code == 200:
            data = response.json()
            teams = data.get('teams', [])
            print(f"✅ Teams: {len(teams)} NBA teams available")
            print(f"✅ Sample teams: {', '.join(teams[:5])}")
        else:
            print(f"❌ Teams check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Teams check error: {e}")
    
    # Test prediction
    try:
        prediction_data = {
            "team1": "Lakers",
            "team2": "Celtics",
            "prediction_type": "moneyline"
        }
        
        response = requests.post(f"{base_url}/api/v1/predict", json=prediction_data)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🎯 Prediction Test:")
            print(f"✅ Teams: {data.get('teams', [])}")
            print(f"✅ Prediction: {data.get('prediction', 'Unknown')}")
            print(f"✅ Confidence: {data.get('confidence', 0):.2%}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Prediction error: {e}")
    
    print("\n" + "=" * 50)
    print("🏀 Basketball System Test Complete!")
    print("✅ YOLO MODE: MAXIMUM CONFIDENCE!")

if __name__ == "__main__":
    test_basketball() 