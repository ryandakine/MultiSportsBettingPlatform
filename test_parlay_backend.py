import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_parlay_strategy(strategy_name, sports):
    print(f"\n🧪 Testing Parlay Strategy: {strategy_name}")
    print(f"   Sports: {sports}")
    
    payload = {
        "user_id": "test_user_parlay",
        "sports": sports,
        "query_text": f"Generate a winning parlay combo for {strategy_name}",
        "preferences": {
            "type": "parlay",
            "strategy": strategy_name,
            "risk_level": "medium"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Success!")
            print(f"   Confidence: {data.get('combined_prediction', {}).get('confidence')}")
            print(f"   Reasoning: {data.get('combined_prediction', {}).get('reasoning')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_parlay_strategy("Winter Classics", ["basketball", "hockey"])
    test_parlay_strategy("The Big 4", ["baseball", "basketball", "football", "hockey"])
