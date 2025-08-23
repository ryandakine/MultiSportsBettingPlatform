#!/usr/bin/env python3
"""
Simple Football System Test - YOLO MODE!
=======================================
Quick test to verify Football system integration
"""

import requests
import json

def test_football_system():
    """Test Football system accessibility"""
    base_url = "http://localhost:8002"
    
    print("🏈 Testing Football System - YOLO MODE!")
    print("=" * 50)
    
    try:
        # Test health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Football system is accessible!")
            health_data = response.json()
            print(f"✅ Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ Football system not accessible: {response.status_code}")
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
        
        return True
        
    except Exception as e:
        print(f"❌ Football system test failed: {e}")
        return False

def test_unified_platform():
    """Test unified platform with Football"""
    base_url = "http://localhost:8007"
    
    print("\n🎯 Testing Unified Platform with Football - YOLO MODE!")
    print("=" * 50)
    
    try:
        # Test platform health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Unified platform is accessible!")
        else:
            print(f"❌ Platform not accessible: {response.status_code}")
            return False
        
        # Test football status via platform
        response = requests.get(f"{base_url}/api/v1/sport-status?sport=football")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Football status via platform: {status_data.get('status', 'unknown')}")
        else:
            print(f"❌ Football status failed: {response.status_code}")
        
        # Test all teams via platform
        response = requests.get(f"{base_url}/api/v1/teams")
        if response.status_code == 200:
            teams_data = response.json()
            football_teams = teams_data.get('football', [])
            print(f"✅ Football teams via platform: {len(football_teams)}")
            if football_teams:
                print(f"✅ Sample football teams: {football_teams[:3]}")
        else:
            print(f"❌ Teams via platform failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified platform test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SIMPLE FOOTBALL INTEGRATION TEST - YOLO MODE!")
    print("=" * 60)
    print("Testing Football system integration with Head Agent!")
    print("=" * 60)
    
    # Test Football system directly
    football_ok = test_football_system()
    
    # Test unified platform
    platform_ok = test_unified_platform()
    
    print("\n" + "=" * 60)
    print("🎉 FOOTBALL INTEGRATION TEST COMPLETED!")
    print(f"✅ Football system: {'ACCESSIBLE' if football_ok else 'NOT ACCESSIBLE'}")
    print(f"✅ Unified platform: {'ACCESSIBLE' if platform_ok else 'NOT ACCESSIBLE'}")
    if football_ok and platform_ok:
        print("✅ Football system is fully integrated with Head Agent!")
    else:
        print("⚠️ Some integration issues detected")
    print("=" * 60)

if __name__ == "__main__":
    main() 