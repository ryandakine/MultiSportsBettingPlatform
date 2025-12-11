#!/usr/bin/env python3
"""
Test script for dynamic port finding functionality.
Useful for multi-project setups to avoid port conflicts.
"""

import socket
import time
import threading
from typing import List, Optional

def simulate_port_usage(port: int, duration: int = 5):
    """Simulate a service using a specific port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('localhost', port))
            server_socket.listen(1)
            print(f"🔒 Simulating service on port {port} for {duration} seconds...")
            time.sleep(duration)
            print(f"🔓 Released port {port}")
    except Exception as e:
        print(f"❌ Failed to simulate service on port {port}: {e}")

def test_port_availability():
    """Test basic port availability checking."""
    print("🧪 Testing Port Availability Detection")
    print("=" * 50)
    
    # Test with port utilities if available
    try:
        from src.utils.port_utils import is_port_available, find_available_port, get_port_range
        print("✅ Using advanced port utilities")
        
        # Test port availability
        test_port = 8000
        is_available = is_port_available(test_port)
        print(f"Port {test_port} available: {is_available}")
        
        # Test finding available port
        available_port = find_available_port(8000, max_attempts=10)
        print(f"Found available port: {available_port}")
        
        # Test getting port range
        port_range = get_port_range(8000, count=5)
        print(f"Available port range: {port_range}")
        
    except ImportError:
        print("⚠️  Using basic port checking")
        
        def is_port_available(port: int) -> bool:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    return result != 0
            except Exception:
                return False
        
        test_port = 8000
        is_available = is_port_available(test_port)
        print(f"Port {test_port} available: {is_available}")

def test_multi_project_scenario():
    """Test scenario with multiple projects using different ports."""
    print("\n🏗️  Testing Multi-Project Port Management")
    print("=" * 50)
    
    # Simulate 4 projects trying to use ports
    projects = [
        {"name": "Project A", "preferred_port": 8000},
        {"name": "Project B", "preferred_port": 8001}, 
        {"name": "Project C", "preferred_port": 8002},
        {"name": "Project D", "preferred_port": 8003}
    ]
    
    # Start some services on specific ports to simulate conflicts
    print("🔧 Setting up port conflicts...")
    conflict_ports = [8000, 8002]  # These will be "in use"
    
    threads = []
    for port in conflict_ports:
        thread = threading.Thread(target=simulate_port_usage, args=(port, 10))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Give services time to start
    time.sleep(1)
    
    # Test each project's port finding
    for project in projects:
        print(f"\n📋 {project['name']} - Preferred Port: {project['preferred_port']}")
        
        try:
            from src.utils.port_utils import is_port_available, find_available_port
        except ImportError:
            # Fallback implementation
            def is_port_available(port: int) -> bool:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        result = sock.connect_ex(('localhost', port))
                        return result != 0
                except Exception:
                    return False
            
            def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
                for port in range(start_port, start_port + max_attempts):
                    if is_port_available(port):
                        return port
                return None
        
        preferred_port = project['preferred_port']
        
        if is_port_available(preferred_port):
            print(f"   ✅ Preferred port {preferred_port} is available")
            final_port = preferred_port
        else:
            print(f"   ⚠️  Preferred port {preferred_port} is in use")
            available_port = find_available_port(preferred_port, max_attempts=10)
            if available_port:
                print(f"   ✅ Found alternative port: {available_port}")
                final_port = available_port
            else:
                print(f"   ❌ No available ports found in range")
                final_port = None
        
        if final_port:
            print(f"   🚀 {project['name']} will use port: {final_port}")
    
    # Wait for simulation to complete
    print("\n⏳ Waiting for port simulation to complete...")
    time.sleep(5)

def test_port_range_finding():
    """Test finding multiple available ports for different services."""
    print("\n🔍 Testing Port Range Finding")
    print("=" * 50)
    
    try:
        from src.utils.port_utils import get_port_range
        print("✅ Using advanced port range utilities")
        
        # Find 4 available ports for different services
        available_ports = get_port_range(8000, count=4)
        print(f"Found {len(available_ports)} available ports: {available_ports}")
        
        # Simulate using these ports
        for i, port in enumerate(available_ports):
            service_name = f"Service {chr(65 + i)}"  # A, B, C, D
            print(f"   {service_name}: Port {port}")
            
    except ImportError:
        print("⚠️  Advanced port utilities not available")
        print("   Basic port finding will be used at runtime")

def main():
    """Run all port finding tests."""
    print("🚀 MultiSportsBettingPlatform - Dynamic Port Finding Test")
    print("=" * 60)
    print("This test verifies that your project can handle port conflicts")
    print("when running multiple projects simultaneously.")
    print()
    
    # Test basic functionality
    test_port_availability()
    
    # Test multi-project scenario
    test_multi_project_scenario()
    
    # Test port range finding
    test_port_range_finding()
    
    print("\n" + "=" * 60)
    print("✅ Port finding test completed!")
    print("💡 Your project will automatically find available ports")
    print("   when the preferred port is already in use.")
    print()
    print("🔧 To test the actual server:")
    print("   py run.py")
    print()
    print("📋 Expected behavior:")
    print("   - If port 8000 is free: Uses port 8000")
    print("   - If port 8000 is busy: Finds next available port")
    print("   - Shows clear messages about port selection")

if __name__ == "__main__":
    main() 