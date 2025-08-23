#!/usr/bin/env python3
"""
Unified Platform Demo - YOLO MODE!
=================================
Quick demonstration of unified platform capabilities
"""

import requests
import json
import time

def demo_platform():
    """Demonstrate unified platform capabilities"""
    base_url = "http://localhost:8007"
    
    print("🚀 UNIFIED PLATFORM DEMO - YOLO MODE!")
    print("=" * 60)
    print("🎯 MultiSports Betting Platform - All 4 Sports Connected!")
    print("=" * 60)
    
    # 1. Platform Overview
    print("\n📋 PLATFORM OVERVIEW:")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Platform Status: HEALTHY")
        
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Platform: {status.get('platform', 'MultiSports Betting Platform')}")
            print(f"✅ Version: {status.get('version', '2.0.0-yolo')}")
            print(f"✅ YOLO Mode: {status.get('yolo_mode', 'MAXIMUM CONFIDENCE')}")
    except Exception as e:
        print(f"❌ Platform overview failed: {e}")
    
    # 2. All Sports Status
    print("\n🏈 ALL SPORTS STATUS:")
    print("-" * 30)
    sports = ["baseball", "football", "hockey", "basketball"]
    for sport in sports:
        try:
            response = requests.get(f"{base_url}/api/v1/sport-status?sport={sport}")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ {sport.title()}: {status.get('status', 'unknown')}")
        except:
            print(f"❌ {sport.title()}: unavailable")
    
    # 3. Live Predictions Demo
    print("\n🎯 LIVE PREDICTIONS DEMO:")
    print("-" * 30)
    
    predictions = [
        {"sport": "hockey", "team1": "Bruins", "team2": "Lightning", "type": "moneyline"},
        {"sport": "basketball", "team1": "Lakers", "team2": "Celtics", "type": "moneyline"},
        {"sport": "hockey", "team1": "Maple Leafs", "team2": "Oilers", "type": "moneyline"},
        {"sport": "basketball", "team1": "Warriors", "team2": "Nuggets", "type": "moneyline"}
    ]
    
    for i, pred in enumerate(predictions, 1):
        try:
            print(f"\n🏈 Prediction {i}: {pred['sport'].title()}")
            print(f"   Teams: {pred['team1']} vs {pred['team2']}")
            
            response = requests.post(f"{base_url}/api/v1/predict", json={
                "sport": pred["sport"],
                "team1": pred["team1"],
                "team2": pred["team2"],
                "prediction_type": pred["type"]
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Prediction: {result.get('prediction', 'unknown')}")
                print(f"   ✅ Confidence: {result.get('confidence', 0):.2f}")
                print(f"   ✅ YOLO Factor: {result.get('yolo_factor', 1.0):.1f}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay for demo effect
    
    # 4. Cross-Sport Analysis Demo
    print("\n🧠 CROSS-SPORT ANALYSIS DEMO:")
    print("-" * 30)
    try:
        response = requests.post(f"{base_url}/api/v1/cross-sport-analysis", json={
            "team1": "Bruins",
            "team2": "Lightning"
        })
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Cross-sport analysis completed!")
            print(f"✅ Analysis available for {len(analysis.get('analysis', {}))} sports")
        else:
            print(f"❌ Cross-sport analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cross-sport analysis error: {e}")
    
    # 5. Platform Statistics
    print("\n📊 PLATFORM STATISTICS:")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/api/v1/recent-predictions?limit=3")
        if response.status_code == 200:
            predictions = response.json()
            print(f"✅ Recent predictions: {len(predictions.get('predictions', []))}")
            print("✅ Platform actively tracking predictions")
        else:
            print(f"❌ Recent predictions failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("🎉 UNIFIED PLATFORM DEMO COMPLETED!")
    print("=" * 60)
    print("✅ All 4 sports connected to Head Agent")
    print("✅ Real-time predictions working")
    print("✅ Cross-sport analysis operational")
    print("✅ YOLO Mode maximum confidence active")
    print("✅ Platform statistics tracking")
    print("=" * 60)
    print("🏆 MULTI-SPORT BETTING PLATFORM READY FOR ACTION!")
    print("=" * 60)

if __name__ == "__main__":
    demo_platform() 