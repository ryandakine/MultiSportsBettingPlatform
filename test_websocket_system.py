#!/usr/bin/env python3
"""
Test Enhanced WebSocket System
=============================
Comprehensive testing of the enhanced WebSocket communication system.
"""

import asyncio
import json
import websockets
import time
from datetime import datetime
from typing import Dict, Any, List

class WebSocketTester:
    """Test the enhanced WebSocket system."""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.connections = []
    
    async def test_websocket_connection(self, endpoint: str, test_name: str) -> Dict[str, Any]:
        """Test a WebSocket endpoint."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}{endpoint}"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            
            print(f"✅ {test_name}: Connected successfully")
            print(f"   Welcome message: {welcome_data.get('data', {}).get('message', 'No message')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Connection successful",
                "welcome_data": welcome_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_authenticated_websocket(self, test_name: str) -> Dict[str, Any]:
        """Test authenticated WebSocket functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/authenticated"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            
            # Test authentication (with dummy token)
            auth_message = {
                "type": "authenticate",
                "token": "dummy_token_for_testing"
            }
            await websocket.send(json.dumps(auth_message))
            
            # Wait for authentication response
            auth_response = await websocket.recv()
            auth_data = json.loads(auth_response)
            
            print(f"✅ {test_name}: Authentication test completed")
            print(f"   Auth response: {auth_data.get('data', {}).get('message', 'No message')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Authentication test completed",
                "welcome_data": welcome_data,
                "auth_data": auth_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_prediction_websocket(self, test_name: str) -> Dict[str, Any]:
        """Test prediction WebSocket functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/predictions"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for initial predictions
            predictions_msg = await websocket.recv()
            predictions_data = json.loads(predictions_msg)
            
            # Test requesting new prediction
            request_message = {
                "type": "request_new_prediction",
                "sport": "baseball",
                "teams": ["Yankees", "Red Sox"]
            }
            await websocket.send(json.dumps(request_message))
            
            # Wait for new prediction
            new_prediction_msg = await websocket.recv()
            new_prediction_data = json.loads(new_prediction_msg)
            
            print(f"✅ {test_name}: Prediction test completed")
            print(f"   Initial predictions: {len(predictions_data.get('data', {}).get('predictions', []))}")
            print(f"   New prediction: {new_prediction_data.get('data', {}).get('new_prediction', {}).get('prediction', 'No prediction')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Prediction test completed",
                "predictions_data": predictions_data,
                "new_prediction_data": new_prediction_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_notification_websocket(self, test_name: str) -> Dict[str, Any]:
        """Test notification WebSocket functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/notifications"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            
            # Test subscription
            sub_message = {
                "type": "subscribe",
                "channel": "notifications"
            }
            await websocket.send(json.dumps(sub_message))
            
            # Wait for subscription confirmation
            sub_response = await websocket.recv()
            sub_data = json.loads(sub_response)
            
            print(f"✅ {test_name}: Notification test completed")
            print(f"   Subscription: {sub_data.get('data', {}).get('action', 'No action')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Notification test completed",
                "welcome_data": welcome_data,
                "subscription_data": sub_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_yolo_websocket(self, test_name: str) -> Dict[str, Any]:
        """Test YOLO WebSocket functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/yolo-predictions"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for YOLO stats
            stats_msg = await websocket.recv()
            stats_data = json.loads(stats_msg)
            
            # Test YOLO prediction request
            yolo_message = {
                "type": "request_prediction",
                "sport": "baseball",
                "teams": ["YOLO Team A", "YOLO Team B"]
            }
            await websocket.send(json.dumps(yolo_message))
            
            # Wait for YOLO prediction
            prediction_msg = await websocket.recv()
            prediction_data = json.loads(prediction_msg)
            
            print(f"✅ {test_name}: YOLO test completed")
            print(f"   YOLO stats: {stats_data.get('data', {}).get('yolo_stats', {})}")
            print(f"   YOLO prediction: {prediction_data.get('data', {}).get('prediction', {}).get('prediction', 'No prediction')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "YOLO test completed",
                "stats_data": stats_data,
                "prediction_data": prediction_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_heartbeat(self, test_name: str) -> Dict[str, Any]:
        """Test WebSocket heartbeat functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/predictions"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            
            # Send ping
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong
            pong_msg = await websocket.recv()
            pong_data = json.loads(pong_msg)
            
            print(f"✅ {test_name}: Heartbeat test completed")
            print(f"   Pong response: {pong_data.get('type', 'No type')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Heartbeat test completed",
                "pong_data": pong_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_error_handling(self, test_name: str) -> Dict[str, Any]:
        """Test WebSocket error handling."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            uri = f"{self.base_url}/ws/predictions"
            websocket = await websockets.connect(uri)
            self.connections.append(websocket)
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            
            # Send invalid JSON
            await websocket.send("invalid json")
            
            # Wait for error response
            error_msg = await websocket.recv()
            error_data = json.loads(error_msg)
            
            print(f"✅ {test_name}: Error handling test completed")
            print(f"   Error response: {error_data.get('data', {}).get('message', 'No error message')}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Error handling test completed",
                "error_data": error_data
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all WebSocket tests."""
        print("🚀 Starting Enhanced WebSocket System Tests")
        print("=" * 50)
        
        tests = [
            ("/ws/authenticated", "Authenticated WebSocket Connection"),
            ("/ws/predictions", "Predictions WebSocket Connection"),
            ("/ws/notifications", "Notifications WebSocket Connection"),
            ("/ws/yolo-predictions", "YOLO WebSocket Connection")
        ]
        
        # Test basic connections
        for endpoint, test_name in tests:
            result = await self.test_websocket_connection(endpoint, test_name)
            self.test_results.append(result)
        
        # Test specific functionality
        specific_tests = [
            self.test_authenticated_websocket("Authenticated WebSocket Functionality"),
            self.test_prediction_websocket("Prediction WebSocket Functionality"),
            self.test_notification_websocket("Notification WebSocket Functionality"),
            self.test_yolo_websocket("YOLO WebSocket Functionality"),
            self.test_heartbeat("WebSocket Heartbeat"),
            self.test_error_handling("WebSocket Error Handling")
        ]
        
        for test in specific_tests:
            result = await test
            self.test_results.append(result)
        
        # Close all connections
        for websocket in self.connections:
            try:
                await websocket.close()
            except:
                pass
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 WebSocket Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed = sum(1 for result in self.test_results if result["status"] == "FAILED")
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🎯 Test Results:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            print(f"   {status_emoji} {result['test']}: {result['status']}")

async def main():
    """Main test function."""
    tester = WebSocketTester()
    
    try:
        results = await tester.run_all_tests()
        tester.print_summary()
        
        # Save results to file
        with open("websocket_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "summary": {
                    "total": len(results),
                    "passed": sum(1 for r in results if r["status"] == "PASSED"),
                    "failed": sum(1 for r in results if r["status"] == "FAILED")
                }
            }, f, indent=2)
        
        print(f"\n💾 Test results saved to websocket_test_results.json")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 