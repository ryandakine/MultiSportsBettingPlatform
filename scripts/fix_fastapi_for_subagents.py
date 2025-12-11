#!/usr/bin/env python3
"""
🚀 FastAPI Fix Script for Sub-Agents
Automatically fixes FastAPI/Pydantic installation issues that all sub-agents were experiencing.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def log_with_emoji(message, emoji="ℹ️"):
    """Print timestamped log message with emoji"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {emoji} {message}")

def run_command(command, description, check=True):
    """Run a command and log the result"""
    log_with_emoji(f"Running: {description}", "🛠️")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_with_emoji(f"✅ {description} - SUCCESS", "✅")
            return True
        else:
            log_with_emoji(f"❌ {description} - FAILED: {result.stderr}", "❌")
            if check:
                return False
            return True
    except Exception as e:
        log_with_emoji(f"❌ {description} - ERROR: {str(e)}", "❌")
        if check:
            return False
        return True

def check_rust():
    """Check if Rust is installed"""
    log_with_emoji("Checking Rust installation...", "🔍")
    
    # Check if rustc is available
    if run_command("rustc --version", "Checking rustc", check=False):
        log_with_emoji("✅ Rust compiler found", "✅")
        return True
    
    # Check if cargo is available
    if run_command("cargo --version", "Checking cargo", check=False):
        log_with_emoji("✅ Cargo found", "✅")
        return True
    
    log_with_emoji("❌ Rust not found, will install", "⚠️")
    return False

def install_rust():
    """Install Rust compiler"""
    log_with_emoji("Installing Rust compiler...", "🚀")
    
    # Download Rust installer
    if not run_command(
        'Invoke-WebRequest -Uri "https://win.rustup.rs/x86_64" -OutFile "rustup-init.exe"',
        "Downloading Rust installer"
    ):
        return False
    
    # Install Rust
    if not run_command(
        '.\rustup-init.exe --default-toolchain stable --profile default -y',
        "Installing Rust"
    ):
        return False
    
    # Add to PATH
    run_command(
        '$env:PATH += ";$env:USERPROFILE\.cargo\bin"',
        "Adding Cargo to PATH"
    )
    
    log_with_emoji("✅ Rust installation completed", "✅")
    return True

def install_fastapi():
    """Install FastAPI using pre-compiled binaries"""
    log_with_emoji("Installing FastAPI with pre-compiled binaries...", "📦")
    
    # Install FastAPI
    if not run_command(
        "py -m pip install fastapi --only-binary=all --force-reinstall",
        "Installing FastAPI"
    ):
        return False
    
    # Install uvicorn
    if not run_command(
        "py -m pip install uvicorn --only-binary=all",
        "Installing uvicorn"
    ):
        return False
    
    # Install pydantic
    if not run_command(
        "py -m pip install pydantic --only-binary=all",
        "Installing pydantic"
    ):
        return False
    
    log_with_emoji("✅ FastAPI installation completed", "✅")
    return True

def test_fastapi():
    """Test if FastAPI works"""
    log_with_emoji("Testing FastAPI installation...", "🧪")
    
    test_code = """
import fastapi
import uvicorn
print("✅ FastAPI imports successfully!")
print(f"FastAPI version: {fastapi.__version__}")
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log_with_emoji("✅ FastAPI test passed", "✅")
            print(result.stdout)
            return True
        else:
            log_with_emoji(f"❌ FastAPI test failed: {result.stderr}", "❌")
            return False
    except Exception as e:
        log_with_emoji(f"❌ FastAPI test error: {str(e)}", "❌")
        return False

def main():
    """Main installation process"""
    log_with_emoji("🚀 Starting FastAPI fix for sub-agents", "🚀")
    log_with_emoji("This will fix the 'unable to infer type for attribute' error", "🎯")
    
    # Step 1: Check/Install Rust
    if not check_rust():
        if not install_rust():
            log_with_emoji("❌ Failed to install Rust", "❌")
            return False
    
    # Step 2: Install FastAPI
    if not install_fastapi():
        log_with_emoji("❌ Failed to install FastAPI", "❌")
        return False
    
    # Step 3: Test installation
    if not test_fastapi():
        log_with_emoji("❌ FastAPI test failed", "❌")
        return False
    
    log_with_emoji("🎉 FastAPI fix completed successfully!", "🎉")
    log_with_emoji("Your sub-agent should now work without Pydantic errors", "✅")
    log_with_emoji("Try running 'py run.py' to start your server", "🚀")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        log_with_emoji("❌ Installation failed. Check the logs above.", "❌")
        sys.exit(1)
    else:
        log_with_emoji("✅ All done! Your sub-agent is ready.", "✅") 