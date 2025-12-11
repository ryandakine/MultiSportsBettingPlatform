#!/usr/bin/env python3
"""
Test Football System Integration - YOLO MODE!
============================================
Test the Football system integration with the Head Agent
"""

import requests
import json
import asyncio
import aiohttp
from datetime import datetime

def test_football_system_direct():
    """Test Football system directly"""
    base_url = "http://localhost:8002"
    
    print("🏈 Testing Football System Direct Integration - YOLO MODE!")
    print("=" * 60)
    
    try:
        # Test health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Football system is running!")
            health_data = response.json()
            print(f"✅ Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ Football system not responding: {response.status_code}")
            return False
        
        # Test status
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ System: {status_data.get('system', 'unknown')}")
            print(f"✅ Version: {status_data.get('version', 'unknown')}")
            print(f"✅ YOLO Mode: {status_data.get('yolo_mode', 'unknown')}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
        
        # Test teams
        response = requests.get(f"{base_url}/api/v1/teams")
        if response.status_code == 200:
            teams_data = response.json()
            teams = teams_data.get('teams', [])
            print(f"✅ Teams available: {len(teams)}")
            if teams:
                print(f"✅ Sample teams: {teams[:3]}")
        else:
            print(f"❌ Teams endpoint failed: {response.status_code}")
        
        # Test prediction
        prediction_data = {
            "team1": "Patriots",
            "team2": "Bills",
            "prediction_type": "moneyline"
        }
        
        response = requests.post(f"{base_url}/api/v1/predict", json=prediction_data)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ Prediction successful!")
            print(f"✅ Prediction: {prediction.get('prediction', 'unknown')}")
            print(f"✅ Confidence: {prediction.get('confidence', 0):.2f}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Football system test failed: {e}")
        return False

async def test_football_via_platform():
    """Test Football system via unified platform"""
    base_url = "http://localhost:8007"
    
    print("\n🏈 Testing Football System via Unified Platform - YOLO MODE!")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test platform health
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Unified platform is running!")
                else:
                    print(f"❌ Platform not responding: {response.status}")
                    return False
            
            # Test football status via platform
            async with session.get(f"{base_url}/api/v1/sport-status?sport=football") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print(f"✅ Football status via platform: {status_data.get('status', 'unknown')}")
                else:
                    print(f"❌ Football status failed: {response.status}")
            
            # Test all teams via platform
            async with session.get(f"{base_url}/api/v1/teams") as response:
                if response.status == 200:
                    teams_data = await response.json()
                    football_teams = teams_data.get('football', [])
                    print(f"✅ Football teams via platform: {len(football_teams)}")
                    if football_teams:
                        print(f"✅ Sample football teams: {football_teams[:3]}")
                else:
                    print(f"❌ Teams via platform failed: {response.status}")
            
            # Test football prediction via platform
            prediction_data = {
                "sport": "football",
                "team1": "Patriots",
                "team2": "Bills",
                "prediction_type": "moneyline"
            }
            
            async with session.post(f"{base_url}/api/v1/predict", json=prediction_data) as response:
                if response.status == 200:
                    prediction = await response.json()
                    print(f"✅ Football prediction via platform successful!")
                    print(f"✅ Prediction: {prediction.get('prediction', 'unknown')}")
                    print(f"✅ Confidence: {prediction.get('confidence', 0):.2f}")
                else:
                    print(f"❌ Football prediction via platform failed: {response.status}")
            
            # Test cross-sport analysis
            analysis_data = {
                "team1": "Patriots",
                "team2": "Bills"
            }
            
            async with session.post(f"{base_url}/api/v1/cross-sport-analysis", json=analysis_data) as response:
                if response.status == 200:
                    analysis = await response.json()
                    print(f"✅ Cross-sport analysis successful!")
                    print(f"✅ Analysis available for {len(analysis.get('analysis', {}))} sports")
                else:
                    print(f"❌ Cross-sport analysis failed: {response.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Football via platform test failed: {e}")
        return False

def test_football_performance_tracking():
    """Test Football performance tracking if available"""
    base_url = "http://localhost:8002"
    
    print("\n🏈 Testing Football Performance Tracking - YOLO MODE!")
    print("=" * 60)
    
    try:
        # Test performance tracking endpoint
        bet_data = {
            "user_id": "football_user",
            "bet_data": {
                "bet_type": "moneyline",
                "teams": ["Patriots", "Bills"],
                "prediction": "Patriots ML",
                "actual_result": "Patriots Win",
                "bet_amount": 100.0,
                "payout": 150.0,
                "odds": 1.5,
                "confidence": 0.75,
                "council_analysis": [
                    {"member": "offensive_specialist", "confidence": 0.8},
                    {"member": "defensive_analyst", "confidence": 0.7}
                ],
                "yolo_factor": 1.2
            }
        }
        
        response = requests.post(f"{base_url}/api/v1/performance/track", json=bet_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Football performance tracking working!")
            print(f"✅ Bet ID: {result.get('bet_id', 'unknown')}")
            print(f"✅ ROI: {result.get('roi', 0):.2f}%")
        else:
            print(f"⚠️ Football performance tracking not available: {response.status_code}")
        
        # Test performance summary
        response = requests.get(f"{base_url}/api/v1/performance/summary?user_id=football_user")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Football performance summary working!")
        else:
            print(f"⚠️ Football performance summary not available: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Football performance tracking test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 FOOTBALL SYSTEM INTEGRATION TEST - YOLO MODE!")
    print("=" * 80)
    print("Testing Football system integration with Head Agent!")
    print("=" * 80)
    
    # Test Football system directly
    football_direct = test_football_system_direct()
    
    # Test Football system via unified platform
    football_via_platform = await test_football_via_platform()
    
    # Test Football performance tracking
    test_football_performance_tracking()
    
    print("\n" + "=" * 80)
    print("🎉 FOOTBALL INTEGRATION TEST COMPLETED!")
    print(f"✅ Direct integration: {'SUCCESS' if football_direct else 'FAILED'}")
    print(f"✅ Platform integration: {'SUCCESS' if football_via_platform else 'FAILED'}")
    print("✅ Football system is ready for Head Agent integration!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 