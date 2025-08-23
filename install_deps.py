#!/usr/bin/env python3
"""
Install dependencies for MultiSportsBettingPlatform
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("🔧 Installing MultiSportsBettingPlatform dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        
        # Install additional packages that might be missing
        additional_packages = [
            "python-dotenv",
            "fastapi",
            "uvicorn",
            "pydantic"
        ]
        
        for package in additional_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError:
                print(f"⚠️  {package} installation failed (might already be installed)")
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = install_dependencies()
    if success:
        print("\n🎉 Installation complete! You can now run:")
        print("   py run.py")
    else:
        print("\n❌ Installation failed. Please check your Python environment.")
        sys.exit(1) 