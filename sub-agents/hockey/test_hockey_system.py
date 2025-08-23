#!/usr/bin/env python3
"""
Test Hockey Betting System - YOLO MODE!
=======================================
Test script to demonstrate the hockey betting system with 5 AI council.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_hockey_system():
    """Test the hockey betting system - YOLO MODE!"""
    base_url = "http://localhost:8005"
    
    print("🏒 Testing Hockey Betting System - YOLO MODE!")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("🔍 Testing Health Endpoint...")
        async with session.get(f"{base_url}/health") as response:
            health_data = await response.json()
            print(f"✅ Health Status: {health_data['status']}")
            print(f"✅ YOLO Mode: {health_data['yolo_mode']}")
        
        # Test system status
        print("\n📊 Testing System Status...")
        async with session.get(f"{base_url}/api/v1/status") as response:
            status_data = await response.json()
            print(f"✅ System: {status_data['system_name']}")
            print(f"✅ Version: {status_data['version']}")
            print(f"✅ Council Members: {status_data['council_members']}")
            print(f"✅ Teams: {status_data['teams_in_database']}")
            print(f"✅ Players: {status_data['players_in_database']}")
            print(f"✅ Goalies: {status_data['goalies_in_database']}")
            print(f"✅ YOLO Mode: {status_data['yolo_mode']}")
        
        # Test teams endpoint
        print("\n🏆 Testing Teams Endpoint...")
        async with session.get(f"{base_url}/api/v1/teams") as response:
            teams_data = await response.json()
            print(f"✅ Available Teams: {teams_data['count']}")
            print(f"✅ Teams: {', '.join(teams_data['teams'][:5])}...")
        
        # Test prediction endpoint
        print("\n🎯 Testing Prediction Endpoint...")
        prediction_data = {
            "team1": "Bruins",
            "team2": "Oilers",
            "prediction_type": "moneyline"
        }
        
        async with session.post(f"{base_url}/api/v1/predict", json=prediction_data) as response:
            prediction_result = await response.json()
            print(f"✅ Prediction ID: {prediction_result['prediction_id']}")
            print(f"✅ Teams: {prediction_result['teams']}")
            print(f"✅ Prediction: {prediction_result['prediction']}")
            print(f"✅ Confidence: {prediction_result['confidence']:.2%}")
            print(f"✅ YOLO Factor: {prediction_result['yolo_factor']}")
            
            # Show council analysis
            print(f"\n🏛️ Council Analysis:")
            for analysis in prediction_result['council_analysis']:
                print(f"  • {analysis['member'].replace('_', ' ').title()}: {analysis['recommendation']}")
                print(f"    Confidence: {analysis['confidence']:.2%}")
        
        # Test another prediction
        print("\n🎯 Testing Second Prediction...")
        prediction_data2 = {
            "team1": "Maple Leafs",
            "team2": "Lightning",
            "prediction_type": "total_goals"
        }
        
        async with session.post(f"{base_url}/api/v1/predict", json=prediction_data2) as response:
            prediction_result2 = await response.json()
            print(f"✅ Prediction: {prediction_result2['prediction']}")
            print(f"✅ Confidence: {prediction_result2['confidence']:.2%}")
        
        # Test recent predictions
        print("\n📈 Testing Recent Predictions...")
        async with session.get(f"{base_url}/api/v1/recent-predictions?limit=5") as response:
            recent_data = await response.json()
            print(f"✅ Recent Predictions: {recent_data['count']}")
            for pred in recent_data['predictions']:
                print(f"  • {pred['teams'][0]} vs {pred['teams'][1]}: {pred['prediction']} (Confidence: {pred['confidence']:.2%})")
    
    print("\n" + "=" * 60)
    print("🏒 Hockey Betting System Test Complete - YOLO MODE!")
    print("✅ All endpoints working with MAXIMUM CONFIDENCE!")
    print("✅ 5 AI Council system operational!")
    print("✅ YOLO MODE: MAXIMUM CONFIDENCE!")

if __name__ == "__main__":
    asyncio.run(test_hockey_system()) 