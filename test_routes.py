"""
Test to check available routes and identify import issues.
"""

import requests
import json

def test_available_routes():
    """Test what routes are actually available."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Available Routes")
    print("=" * 50)
    
    # Test basic endpoints
    basic_endpoints = [
        "/",
        "/health",
        "/docs",
        "/redoc"
    ]
    
    print("📋 Basic Endpoints:")
    for endpoint in basic_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    # Test API endpoints
    api_endpoints = [
        "/api/v1/health",
        "/api/v1/status",
        "/api/v1/sports",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/health",
        "/api/v1/preferences/",
        "/api/v1/preferences/health"
    ]
    
    print("\n🌐 API Endpoints:")
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    # Test OpenAPI schema
    print("\n📚 OpenAPI Schema:")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            print(f"   Available paths: {len(paths)}")
            
            # List some key paths
            auth_paths = [path for path in paths.keys() if "/auth/" in path]
            pref_paths = [path for path in paths.keys() if "/preferences/" in path]
            
            print(f"   Auth paths: {len(auth_paths)}")
            for path in auth_paths[:5]:  # Show first 5
                print(f"     {path}")
            
            print(f"   Preferences paths: {len(pref_paths)}")
            for path in pref_paths[:5]:  # Show first 5
                print(f"     {path}")
        else:
            print(f"   OpenAPI schema: HTTP {response.status_code}")
    except Exception as e:
        print(f"   OpenAPI schema: Error - {e}")

if __name__ == "__main__":
    test_available_routes() 