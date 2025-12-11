#!/usr/bin/env python3
"""
Simple test to verify basic functionality.
"""

def test_basic_imports():
    """Test basic imports work."""
    print("🧪 Testing basic imports...")
    
    try:
        # Test FastAPI
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        # Test Pydantic
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        # Test Pydantic Settings
        import pydantic_settings
        print("✅ Pydantic Settings imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic Settings import failed: {e}")
        return False
    
    try:
        # Test dotenv
        import dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from src.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   App name: {settings.app_name}")
        print(f"   Version: {settings.app_version}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 MultiSportsBettingPlatform - Simple Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_basic_imports()
    
    if imports_ok:
        # Test configuration
        config_ok = test_config()
        
        if config_ok:
            print("\n🎉 All tests passed!")
            print("✅ Your environment is ready for development")
            return True
        else:
            print("\n⚠️  Configuration test failed")
            return False
    else:
        print("\n❌ Import tests failed")
        print("   Run: py install_minimal.py")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 To fix issues:")
        print("   1. Run: py install_minimal.py")
        print("   2. Run: py test_simple.py")
        print("   3. If successful, run: py run.py") 