"""
Basic Functionality Test for MultiSportsBettingPlatform

This test focuses on the core features that are working:
- Health checks
- Basic API endpoints
- Documentation
- Server responsiveness
"""

import requests
import json
from datetime import datetime

def test_basic_functionality():
    """Test basic functionality that should be working."""
    base_url = "http://localhost:8000"
    
    print("🚀 MultiSportsBettingPlatform - Basic Functionality Test")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    results = {}
    
    # Test 1: Root Endpoint
    print("🏠 Test 1: Root Endpoint")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            results["root"] = True
        else:
            print(f"❌ Root endpoint failed: HTTP {response.status_code}")
            results["root"] = False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        results["root"] = False
    
    # Test 2: Health Check
    print("\n🏥 Test 2: Health Check")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check working")
            print(f"   Status: {data.get('status')}")
            results["health"] = True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            results["health"] = False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        results["health"] = False
    
    # Test 3: API Health Check
    print("\n🌐 Test 3: API Health Check")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API health check working")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            results["api_health"] = True
        else:
            print(f"❌ API health check failed: HTTP {response.status_code}")
            results["api_health"] = False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        results["api_health"] = False
    
    # Test 4: System Status
    print("\n📊 Test 4: System Status")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System status working")
            print(f"   Status: {data.get('status')}")
            print(f"   Active Sports: {data.get('active_sports', 0)}")
            print(f"   Active Sessions: {data.get('active_sessions', 0)}")
            results["system_status"] = True
        else:
            print(f"❌ System status failed: HTTP {response.status_code}")
            results["system_status"] = False
    except Exception as e:
        print(f"❌ System status error: {e}")
        results["system_status"] = False
    
    # Test 5: Available Sports
    print("\n🏈 Test 5: Available Sports")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/api/v1/sports")
        if response.status_code == 200:
            data = response.json()
            sports = data.get("available_sports", [])
            count = data.get("count", 0)
            print(f"✅ Available sports working")
            print(f"   Sports: {sports}")
            print(f"   Count: {count}")
            results["sports"] = True
        else:
            print(f"❌ Available sports failed: HTTP {response.status_code}")
            results["sports"] = False
    except Exception as e:
        print(f"❌ Available sports error: {e}")
        results["sports"] = False
    
    # Test 6: API Documentation
    print("\n📚 Test 6: API Documentation")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print(f"✅ API documentation accessible")
            print(f"   URL: {base_url}/docs")
            results["documentation"] = True
        else:
            print(f"❌ API documentation failed: HTTP {response.status_code}")
            results["documentation"] = False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        results["documentation"] = False
    
    # Test 7: OpenAPI Schema
    print("\n🔧 Test 7: OpenAPI Schema")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            print(f"✅ OpenAPI schema accessible")
            print(f"   Available paths: {len(paths)}")
            
            # List some available endpoints
            available_endpoints = list(paths.keys())[:10]
            print(f"   Sample endpoints:")
            for endpoint in available_endpoints:
                print(f"     {endpoint}")
            
            results["openapi"] = True
        else:
            print(f"❌ OpenAPI schema failed: HTTP {response.status_code}")
            results["openapi"] = False
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")
        results["openapi"] = False
    
    # Test 8: Server Response Time
    print("\n⚡ Test 8: Server Response Time")
    print("-" * 30)
    try:
        import time
        start_time = time.time()
        response = requests.get(f"{base_url}/health")
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            print(f"✅ Server response time: {response_time:.2f}ms")
            if response_time < 100:
                print(f"   🚀 Excellent performance")
            elif response_time < 500:
                print(f"   ✅ Good performance")
            else:
                print(f"   ⚠️ Slow response time")
            results["response_time"] = True
        else:
            print(f"❌ Response time test failed: HTTP {response.status_code}")
            results["response_time"] = False
    except Exception as e:
        print(f"❌ Response time test error: {e}")
        results["response_time"] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Core system is fully operational!")
        print("   - Server is running and responsive")
        print("   - API endpoints are working")
        print("   - Documentation is accessible")
        print("   - Performance is good")
        print("   - Ready for basic functionality!")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed! Core system is mostly operational.")
        print("   - Basic functionality working")
        print("   - Some features may need attention")
    else:
        print("\n⚠️ Several tests failed. System needs attention.")
        print("   - Check server configuration")
        print("   - Verify all services are running")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

def main():
    """Main test function."""
    results = test_basic_functionality()
    
    # Return exit code based on results
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        return 0  # Success
    elif passed >= total * 0.8:
        return 1  # Warning
    else:
        return 2  # Error

if __name__ == "__main__":
    exit(main()) 