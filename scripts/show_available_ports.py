#!/usr/bin/env python3
"""
Show available ports for MultiSportsBettingPlatform
"""

import json
import socket
from typing import Dict, List

def check_port_status(port: int) -> Dict:
    """Check if a port is available and accessible."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            available = result != 0
            accessible = result == 0
            return {"available": available, "accessible": accessible}
    except Exception:
        return {"available": False, "accessible": False}

def main():
    """Show current port status."""
    print("🚀 MultiSportsBettingPlatform - Port Status")
    print("=" * 50)
    
    # Core ports for the betting platform
    core_ports = {
        8000: "Main FastAPI Server",
        8001: "Alternative Server Port", 
        8002: "Backup Server Port",
        8003: "Development Server Port",
        5432: "PostgreSQL Database",
        6379: "Redis Cache",
        3000: "Frontend Development Server",
        3001: "Alternative Frontend Port"
    }
    
    # AI Service ports
    ai_ports = {
        8004: "Claude AI Service",
        8005: "Perplexity AI Service", 
        8006: "OpenAI Service",
        8007: "AI Model Service",
        8008: "Prediction Engine",
        8009: "Analytics Service"
    }
    
    # Sport Agent ports
    sport_ports = {
        8010: "Baseball Agent",
        8011: "Basketball Agent",
        8012: "Football Agent", 
        8013: "Hockey Agent",
        8014: "Head Agent Coordinator",
        8015: "Prediction Aggregator"
    }
    
    print("\n🎯 Core Platform Ports:")
    print("-" * 30)
    for port, description in core_ports.items():
        status = check_port_status(port)
        if status["available"]:
            print(f"✅ Port {port}: {description} - AVAILABLE")
        elif status["accessible"]:
            print(f"🟡 Port {port}: {description} - IN USE (accessible)")
        else:
            print(f"🔴 Port {port}: {description} - BLOCKED")
    
    print("\n🤖 AI Service Ports:")
    print("-" * 30)
    for port, description in ai_ports.items():
        status = check_port_status(port)
        if status["available"]:
            print(f"✅ Port {port}: {description} - AVAILABLE")
        elif status["accessible"]:
            print(f"🟡 Port {port}: {description} - IN USE (accessible)")
        else:
            print(f"🔴 Port {port}: {description} - BLOCKED")
    
    print("\n🏈 Sport Agent Ports:")
    print("-" * 30)
    for port, description in sport_ports.items():
        status = check_port_status(port)
        if status["available"]:
            print(f"✅ Port {port}: {description} - AVAILABLE")
        elif status["accessible"]:
            print(f"🟡 Port {port}: {description} - IN USE (accessible)")
        else:
            print(f"🔴 Port {port}: {description} - BLOCKED")
    
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS:")
    print()
    print("🚀 START YOUR MAIN APPLICATION:")
    print("   py run.py")
    print("   (Will automatically find available port)")
    print()
    print("🔧 ALTERNATIVE PORTS IF NEEDED:")
    print("   Main Server: 8001, 8002, 8003")
    print("   Frontend: 3001")
    print("   AI Services: 8004-8009")
    print("   Sport Agents: 8010-8015")
    print()
    print("📊 FULL REPORT:")
    print("   Check port_test_report.json for detailed results")

if __name__ == "__main__":
    main() 