#!/usr/bin/env python3
"""
Real Integration Test - YOLO MODE!
Connects to actual MLB system and tests real integration
"""

import requests
import json
import datetime

def test_mlb_system_integration():
    """Test integration with the actual MLB system."""
    print("🚀 Testing Real MLB System Integration - YOLO MODE!")
    print("=" * 60)
    
    mlb_base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing MLB System Health...")
    try:
        health_response = requests.get(f"{mlb_base_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ MLB System is healthy: {health_data}")
        else:
            print(f"   ❌ MLB System health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ MLB System connection failed: {e}")
        return
    
    # Test 2: Get System Status
    print("\n2️⃣ Testing MLB System Status...")
    try:
        status_response = requests.get(f"{mlb_base_url}/api/v1/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   📊 MLB System Status: {status_data}")
        else:
            print(f"   ⚠️  Status endpoint not available: {status_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Status check failed: {e}")
    
    # Test 3: Get Available Sports
    print("\n3️⃣ Testing Available Sports...")
    try:
        sports_response = requests.get(f"{mlb_base_url}/api/v1/sports", timeout=5)
        if sports_response.status_code == 200:
            sports_data = sports_response.json()
            print(f"   🏟️  Available Sports: {sports_data}")
        else:
            print(f"   ⚠️  Sports endpoint not available: {sports_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Sports check failed: {e}")
    
    # Test 4: Make a Prediction
    print("\n4️⃣ Testing MLB Prediction...")
    prediction_request = {
        "sport": "baseball",
        "teams": ["Yankees", "Red Sox"],
        "game_type": "regular_season",
        "venue": "Fenway Park",
        "date": datetime.datetime.now().isoformat()
    }
    
    try:
        prediction_response = requests.post(
            f"{mlb_base_url}/api/v1/predict",
            json=prediction_request,
            timeout=10
        )
        if prediction_response.status_code == 200:
            prediction_data = prediction_response.json()
            print(f"   🎯 MLB Prediction: {prediction_data}")
        else:
            print(f"   ⚠️  Prediction endpoint not available: {prediction_response.status_code}")
            print(f"   📝 Request: {prediction_request}")
    except Exception as e:
        print(f"   ⚠️  Prediction failed: {e}")
    
    # Test 5: Test Different Teams
    print("\n5️⃣ Testing Different Teams...")
    teams_list = [
        ["Dodgers", "Giants"],
        ["Astros", "Rangers"],
        ["Braves", "Mets"]
    ]
    
    for teams in teams_list:
        prediction_request = {
            "sport": "baseball",
            "teams": teams,
            "game_type": "regular_season",
            "venue": "Home Field",
            "date": datetime.datetime.now().isoformat()
        }
        
        try:
            prediction_response = requests.post(
                f"{mlb_base_url}/api/v1/predict",
                json=prediction_request,
                timeout=5
            )
            if prediction_response.status_code == 200:
                prediction_data = prediction_response.json()
                print(f"   ⚾ {' vs '.join(teams)}: {prediction_data.get('prediction', 'No prediction')}")
            else:
                print(f"   ⚾ {' vs '.join(teams)}: Endpoint not available")
        except Exception as e:
            print(f"   ⚾ {' vs '.join(teams)}: Request failed")
    
    print("\n🎉 Real MLB System Integration Test Complete!")
    print("=" * 60)

def test_cfl_nfl_system_integration():
    """Test integration with CFL/NFL system (if available)."""
    print("\n🏈 Testing CFL/NFL System Integration...")
    print("=" * 60)
    
    # Try different ports where the CFL/NFL system might be running
    possible_ports = [8010, 8011, 8012, 8080]
    
    for port in possible_ports:
        try:
            health_response = requests.get(f"http://localhost:{port}/health", timeout=3)
            if health_response.status_code == 200:
                print(f"   ✅ Found system on port {port}")
                health_data = health_response.json()
                print(f"   📊 System Status: {health_data}")
                
                # Try to get a prediction
                prediction_request = {
                    "sport": "football",
                    "teams": ["Patriots", "Bills"],
                    "game_type": "regular_season"
                }
                
                try:
                    prediction_response = requests.post(
                        f"http://localhost:{port}/api/v1/predict",
                        json=prediction_request,
                        timeout=5
                    )
                    if prediction_response.status_code == 200:
                        prediction_data = prediction_response.json()
                        print(f"   🏈 Football Prediction: {prediction_data}")
                    else:
                        print(f"   ⚠️  Prediction endpoint not available on port {port}")
                except Exception as e:
                    print(f"   ⚠️  Prediction failed on port {port}: {e}")
                
                return  # Found a working system
        except Exception as e:
            print(f"   ❌ Port {port}: No system found")
    
    print("   ❌ No CFL/NFL system found on any tested ports")

if __name__ == "__main__":
    test_mlb_system_integration()
    test_cfl_nfl_system_integration() 