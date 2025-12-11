"""
Test Specialized System Integration - YOLO MODE!
==============================================
Test the integration with MLB and CFL_NFL_Gold systems.
"""

import requests
import json
import time
from datetime import datetime

class SpecializedIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8006"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_system_statuses(self):
        """Test getting status of all specialized systems."""
        print("🔍 Testing Specialized System Statuses")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/specialized/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ System statuses retrieved successfully")
                print(f"   YOLO Mode: {data.get('yolo_mode', False)}")
                
                for system, status in data.get('data', {}).items():
                    online_status = "🟢 ONLINE" if status.get('is_online') else "🔴 OFFLINE"
                    print(f"   {system}: {online_status} (Port: {status.get('port', 'N/A')})")
                
                return True
            else:
                print(f"❌ Failed to get system statuses: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing system statuses: {e}")
            return False
    
    def test_integration_health(self):
        """Test integration health check."""
        print("\n🏥 Testing Integration Health")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/specialized/health")
            if response.status_code == 200:
                data = response.json()
                health_data = data.get('data', {})
                print("✅ Integration health check successful")
                print(f"   Health Status: {health_data.get('health_status', 'Unknown')}")
                print(f"   Health Percentage: {health_data.get('health_percentage', 0):.1f}%")
                print(f"   Online Systems: {health_data.get('online_systems', 0)}/{health_data.get('total_systems', 0)}")
                print(f"   YOLO Mode: {health_data.get('yolo_mode_active', False)}")
                return True
            else:
                print(f"❌ Failed to get health status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing health: {e}")
            return False
    
    def test_available_systems(self):
        """Test getting available systems."""
        print("\n📋 Testing Available Systems")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/specialized/systems")
            if response.status_code == 200:
                data = response.json()
                systems = data.get('data', {}).get('systems', [])
                print("✅ Available systems retrieved")
                
                for system in systems:
                    print(f"   {system.get('name', 'Unknown')}: {system.get('base_url', 'N/A')}")
                
                return True
            else:
                print(f"❌ Failed to get available systems: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing available systems: {e}")
            return False
    
    def test_cross_system_prediction(self):
        """Test creating a cross-system prediction."""
        print("\n🎯 Testing Cross-System Prediction")
        print("=" * 50)
        
        # Test MLB prediction
        mlb_request = {
            "sport": "baseball",
            "teams": ["Dodgers", "Yankees"],
            "query_params": {
                "query_text": "Dodgers vs Yankees prediction",
                "user_id": "test_user_123"
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/specialized/predict", json=mlb_request)
            if response.status_code == 200:
                data = response.json()
                prediction_data = data.get('data', {})
                print("✅ Cross-system prediction created successfully")
                print(f"   Sport: {prediction_data.get('sport', 'Unknown')}")
                print(f"   Teams: {prediction_data.get('teams', [])}")
                print(f"   Combined Prediction: {prediction_data.get('combined_prediction', 'N/A')}")
                print(f"   Confidence: {prediction_data.get('overall_confidence', 0):.2f}")
                print(f"   YOLO Boost: {prediction_data.get('yolo_boost', 1.0):.2f}")
                return True
            else:
                print(f"❌ Failed to create prediction: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error testing prediction: {e}")
            return False
    
    def test_football_prediction(self):
        """Test football prediction."""
        print("\n🏈 Testing Football Prediction")
        print("=" * 50)
        
        football_request = {
            "sport": "football",
            "teams": ["Chiefs", "Bills"],
            "query_params": {
                "query_text": "Chiefs vs Bills NFL prediction",
                "user_id": "test_user_123"
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/specialized/predict", json=football_request)
            if response.status_code == 200:
                data = response.json()
                prediction_data = data.get('data', {})
                print("✅ Football prediction created successfully")
                print(f"   Sport: {prediction_data.get('sport', 'Unknown')}")
                print(f"   Teams: {prediction_data.get('teams', [])}")
                print(f"   Combined Prediction: {prediction_data.get('combined_prediction', 'N/A')}")
                print(f"   Confidence: {prediction_data.get('overall_confidence', 0):.2f}")
                print(f"   YOLO Boost: {prediction_data.get('yolo_boost', 1.0):.2f}")
                return True
            else:
                print(f"❌ Failed to create football prediction: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing football prediction: {e}")
            return False
    
    def test_yolo_statistics(self):
        """Test YOLO statistics."""
        print("\n🚀 Testing YOLO Statistics")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/specialized/yolo-stats")
            if response.status_code == 200:
                data = response.json()
                yolo_data = data.get('data', {})
                print("✅ YOLO statistics retrieved successfully")
                print(f"   YOLO Mode Active: {yolo_data.get('yolo_mode_active', False)}")
                print(f"   Average YOLO Boost: {yolo_data.get('average_yolo_boost', 1.0):.2f}")
                print(f"   Total Predictions: {yolo_data.get('total_predictions', 0)}")
                print(f"   YOLO Predictions: {yolo_data.get('yolo_predictions_count', 0)}")
                return True
            else:
                print(f"❌ Failed to get YOLO statistics: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing YOLO statistics: {e}")
            return False
    
    def test_recent_predictions(self):
        """Test getting recent predictions."""
        print("\n📊 Testing Recent Predictions")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/specialized/predictions/recent?limit=5")
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('data', [])
                print("✅ Recent predictions retrieved successfully")
                print(f"   Total Predictions: {len(predictions)}")
                
                for i, pred in enumerate(predictions[:3], 1):
                    print(f"   {i}. {pred.get('sport', 'Unknown')}: {pred.get('teams', [])}")
                    print(f"      Confidence: {pred.get('overall_confidence', 0):.2f}, YOLO: {pred.get('yolo_boost', 1.0):.2f}")
                
                return True
            else:
                print(f"❌ Failed to get recent predictions: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing recent predictions: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 SPECIALIZED SYSTEM INTEGRATION TEST - YOLO MODE!")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        tests = [
            ("System Statuses", self.test_system_statuses),
            ("Integration Health", self.test_integration_health),
            ("Available Systems", self.test_available_systems),
            ("Cross-System Prediction", self.test_cross_system_prediction),
            ("Football Prediction", self.test_football_prediction),
            ("YOLO Statistics", self.test_yolo_statistics),
            ("Recent Predictions", self.test_recent_predictions)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🚀 ALL TESTS PASSED! YOLO MODE INTEGRATION SUCCESSFUL!")
        else:
            print("⚠️  Some tests failed. Check system connectivity.")
        
        return passed == total

def main():
    """Main test function."""
    tester = SpecializedIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Specialized system integration is working perfectly!")
        print("🚀 Ready to coordinate MLB and CFL_NFL_Gold systems!")
    else:
        print("\n⚠️  Integration needs attention. Check system status.")

if __name__ == "__main__":
    main() 