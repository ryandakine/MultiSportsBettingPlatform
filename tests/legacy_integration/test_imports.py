"""
Test to check if authentication and preferences modules can be imported.
"""

def test_imports():
    """Test importing all the modules."""
    print("🔍 Testing Module Imports")
    print("=" * 50)
    
    # Test basic imports
    print("📦 Testing Basic Imports...")
    try:
        from src.api.routes import router
        print("✅ src.api.routes imported successfully")
    except Exception as e:
        print(f"❌ src.api.routes import failed: {e}")
        return False
    
    # Test authentication imports
    print("\n🔐 Testing Authentication Imports...")
    try:
        from src.api.auth_routes import router as auth_router
        print("✅ src.api.auth_routes imported successfully")
    except Exception as e:
        print(f"❌ src.api.auth_routes import failed: {e}")
        return False
    
    try:
        from src.services.auth_service import AuthService
        print("✅ src.services.auth_service imported successfully")
    except Exception as e:
        print(f"❌ src.services.auth_service import failed: {e}")
        return False
    
    # Test preferences imports
    print("\n⚙️ Testing Preferences Imports...")
    try:
        from src.api.preferences_routes import router as prefs_router
        print("✅ src.api.preferences_routes imported successfully")
    except Exception as e:
        print(f"❌ src.api.preferences_routes import failed: {e}")
        return False
    
    try:
        from src.services.user_preferences import UserPreferencesService
        print("✅ src.services.user_preferences imported successfully")
    except Exception as e:
        print(f"❌ src.services.user_preferences import failed: {e}")
        return False
    
    # Test route inclusion
    print("\n🌐 Testing Route Inclusion...")
    try:
        from src.api.routes import router
        routes = router.routes
        print(f"✅ Router has {len(routes)} routes")
        
        # Check if auth and preferences routes are included
        auth_routes = [r for r in routes if hasattr(r, 'path') and '/auth' in str(r.path)]
        prefs_routes = [r for r in routes if hasattr(r, 'path') and '/preferences' in str(r.path)]
        
        print(f"   Auth routes found: {len(auth_routes)}")
        print(f"   Preferences routes found: {len(prefs_routes)}")
        
        if len(auth_routes) == 0:
            print("❌ No auth routes found in router")
            return False
        
        if len(prefs_routes) == 0:
            print("❌ No preferences routes found in router")
            return False
        
        print("✅ Auth and preferences routes are included")
        
    except Exception as e:
        print(f"❌ Route inclusion test failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ All modules can be imported correctly")
    else:
        print("\n❌ Some modules failed to import") 