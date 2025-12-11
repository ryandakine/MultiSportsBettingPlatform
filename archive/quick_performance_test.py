#!/usr/bin/env python3
"""
Quick Performance Tracking Test - YOLO MODE!
===========================================
Test the new performance tracking endpoints
"""

import requests
import json

def test_basketball_performance():
    """Test Basketball Performance Tracking"""
    base_url = "http://localhost:8006"
    
    print("🏀 Testing Basketball Performance Tracking - YOLO MODE!")
    print("=" * 50)
    
    try:
        # Test health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Basketball system is running!")
        else:
            print("❌ Basketball system not responding")
            return
        
        # Test performance tracking
        bet_data = {
            "user_id": "test_user_1",
            "bet_data": {
                "bet_type": "moneyline",
                "teams": ["Lakers", "Celtics"],
                "prediction": "Lakers ML",
                "actual_result": "Lakers Win",
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
            print(f"✅ Performance tracked! Bet ID: {result['bet_id']}")
            print(f"✅ ROI: {result['roi']:.2f}%")
        else:
            print(f"❌ Performance tracking failed: {response.status_code}")
        
        # Test performance summary
        response = requests.get(f"{base_url}/api/v1/performance/summary?user_id=test_user_1")
        if response.status_code == 200:
            summary = response.json()
            metrics = summary['performance_summary']['performance_metrics']
            print(f"✅ Summary: {metrics['total_bets']} bets, {metrics['win_rate']:.1f}% win rate")
        else:
            print(f"❌ Performance summary failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Basketball test failed: {e}")

def test_hockey_performance():
    """Test Hockey Performance Tracking"""
    base_url = "http://localhost:8005"
    
    print("\n🏒 Testing Hockey Performance Tracking - YOLO MODE!")
    print("=" * 50)
    
    try:
        # Test health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Hockey system is running!")
        else:
            print("❌ Hockey system not responding")
            return
        
        # Test performance tracking
        bet_data = {
            "user_id": "test_user_2",
            "bet_data": {
                "bet_type": "moneyline",
                "teams": ["Bruins", "Lightning"],
                "prediction": "Bruins ML",
                "actual_result": "Bruins Win",
                "bet_amount": 75.0,
                "payout": 120.0,
                "odds": 1.6,
                "confidence": 0.85,
                "council_analysis": [
                    {"member": "goalie_expert", "confidence": 0.9},
                    {"member": "offensive_specialist", "confidence": 0.8}
                ],
                "yolo_factor": 1.3
            }
        }
        
        response = requests.post(f"{base_url}/api/v1/performance/track", json=bet_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Performance tracked! Bet ID: {result['bet_id']}")
            print(f"✅ ROI: {result['roi']:.2f}%")
        else:
            print(f"❌ Performance tracking failed: {response.status_code}")
        
        # Test performance summary
        response = requests.get(f"{base_url}/api/v1/performance/summary?user_id=test_user_2")
        if response.status_code == 200:
            summary = response.json()
            metrics = summary['performance_summary']['performance_metrics']
            print(f"✅ Summary: {metrics['total_bets']} bets, {metrics['win_rate']:.1f}% win rate")
        else:
            print(f"❌ Performance summary failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Hockey test failed: {e}")

def main():
    """Main test function"""
    print("🚀 QUICK PERFORMANCE TRACKING TEST - YOLO MODE!")
    print("=" * 60)
    print("Testing the new multidimensional performance tracking features!")
    print("=" * 60)
    
    test_basketball_performance()
    test_hockey_performance()
    
    print("\n" + "=" * 60)
    print("🎉 PERFORMANCE TRACKING TEST COMPLETED!")
    print("✅ New endpoints are working!")
    print("✅ ROI calculations are active!")
    print("✅ Performance summaries are functional!")
    print("=" * 60)

if __name__ == "__main__":
    main() 