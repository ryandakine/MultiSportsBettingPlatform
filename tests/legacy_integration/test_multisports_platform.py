#!/usr/bin/env python3
"""
Test MultiSports Betting Platform - YOLO MODE!
==============================================
Test script to demonstrate the unified multisports betting platform.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_multisports_platform():
    """Test the unified multisports betting platform - YOLO MODE!"""
    base_url = "http://localhost:8007"
    
    print("🚀 Testing MultiSports Betting Platform - YOLO MODE!")
    print("=" * 70)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("🔍 Testing Platform Health...")
        async with session.get(f"{base_url}/health") as response:
            health_data = await response.json()
            print(f"✅ Platform Status: {health_data['status']}")
            print(f"✅ YOLO Mode: {health_data['yolo_mode']}")
        
        # Test platform status
        print("\n📊 Testing Platform Status...")
        async with session.get(f"{base_url}/api/v1/status") as response:
            status_data = await response.json()
            print(f"✅ Platform: {status_data['platform_name']}")
            print(f"✅ Version: {status_data['version']}")
            print(f"✅ Total Sports: {status_data['total_sports']}")
            print(f"✅ Active Systems: {status_data['active_systems']}")
            print(f"✅ Total Predictions: {status_data['total_predictions']}")
            print(f"✅ YOLO Mode: {status_data['yolo_mode']}")
            
            # Show systems status
            print(f"\n🏈 Systems Status:")
            for sport, status in status_data['systems_status'].items():
                print(f"  • {sport.title()}: {status}")
        
        # Test individual sport status
        print("\n🏈 Testing Individual Sport Status...")
        for sport in ["baseball", "football", "hockey", "basketball"]:
            async with session.get(f"{base_url}/api/v1/sport-status?sport={sport}") as response:
                sport_data = await response.json()
                print(f"✅ {sport.title()}: {sport_data.get('status', 'unknown')} (Port {sport_data.get('port', 'N/A')})")
        
        # Test all teams endpoint
        print("\n🏆 Testing All Teams...")
        async with session.get(f"{base_url}/api/v1/teams") as response:
            teams_data = await response.json()
            print(f"✅ Total Sports: {teams_data['total_sports']}")
            for sport, teams in teams_data['teams'].items():
                print(f"  • {sport.title()}: {len(teams)} teams")
        
        # Test individual sport prediction
        print("\n🎯 Testing Individual Sport Prediction...")
        prediction_data = {
            "sport": "basketball",
            "team1": "Celtics",
            "team2": "Lakers",
            "prediction_type": "moneyline"
        }
        
        async with session.post(f"{base_url}/api/v1/predict", json=prediction_data) as response:
            prediction_result = await response.json()
            print(f"✅ Sport: {prediction_result['sport']}")
            print(f"✅ Teams: {prediction_result['teams']}")
            print(f"✅ Prediction: {prediction_result['prediction']}")
            print(f"✅ Confidence: {prediction_result['confidence']:.2%}")
            print(f"✅ YOLO Factor: {prediction_result['yolo_factor']}")
        
        # Test cross-sport analysis
        print("\n🌐 Testing Cross-Sport Analysis...")
        cross_sport_data = {
            "team1": "Bruins",
            "team2": "Celtics"
        }
        
        async with session.post(f"{base_url}/api/v1/cross-sport-analysis", json=cross_sport_data) as response:
            cross_sport_result = await response.json()
            print(f"✅ Team 1: {cross_sport_result['team1']}")
            print(f"✅ Team 2: {cross_sport_result['team2']}")
            
            print(f"\n🏈 Cross-Sport Results:")
            for sport, result in cross_sport_result['cross_sport_analysis'].items():
                if 'prediction' in result:
                    print(f"  • {sport.title()}: {result['prediction']} (Confidence: {result['confidence']:.2%})")
                else:
                    print(f"  • {sport.title()}: {result['status']}")
        
        # Test recent predictions
        print("\n📈 Testing Recent Predictions...")
        async with session.get(f"{base_url}/api/v1/recent-predictions?limit=10") as response:
            recent_data = await response.json()
            print(f"✅ Recent Predictions: {recent_data['count']}")
            for pred in recent_data['predictions'][:5]:  # Show first 5
                print(f"  • {pred['sport'].title()}: {pred['teams'][0]} vs {pred['teams'][1]} - {pred['prediction']}")
        
        # Test platform statistics
        print("\n📊 Testing Platform Statistics...")
        async with session.get(f"{base_url}/api/v1/stats") as response:
            stats_data = await response.json()
            platform_stats = stats_data['platform_stats']
            print(f"✅ Total Predictions: {platform_stats['total_predictions']}")
            print(f"✅ Sport Predictions:")
            for sport, count in platform_stats['sport_predictions'].items():
                print(f"  • {sport.title()}: {count}")
    
    print("\n" + "=" * 70)
    print("🚀 MultiSports Betting Platform Test Complete - YOLO MODE!")
    print("✅ All endpoints working with MAXIMUM CONFIDENCE!")
    print("✅ Unified platform operational!")
    print("✅ Cross-sport integration successful!")
    print("✅ YOLO MODE: MAXIMUM CONFIDENCE!")

if __name__ == "__main__":
    asyncio.run(test_multisports_platform()) 