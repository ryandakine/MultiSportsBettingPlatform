#!/usr/bin/env python3
"""
Minimal installation script for MultiSportsBettingPlatform
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install minimal required packages."""
    print("🔧 Installing minimal dependencies for MultiSportsBettingPlatform...")
    
    # Essential packages in order
    packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "httpx",
        "anthropic",
        "perplexity-python"
    ]
    
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"   Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("🎉 All packages installed successfully!")
        print("\n🚀 You can now run:")
        print("   py run.py")
        print("   py test_head_agent.py")
    else:
        print("⚠️  Some packages failed to install.")
        print("   Try running: pip install --upgrade pip")
        print("   Then run this script again.")

if __name__ == "__main__":
    main() 