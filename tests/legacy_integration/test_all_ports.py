#!/usr/bin/env python3
"""
Comprehensive port testing for MultiSportsBettingPlatform
Opens and tests all necessary server ports to ensure they're working.
"""

import socket
import threading
import time
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PortTester:
    def __init__(self):
        self.test_results = {}
        self.running_servers = {}
        
    def is_port_available(self, port: int, host: str = "localhost") -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    def test_port_connectivity(self, port: int, host: str = "localhost", timeout: int = 5) -> bool:
        """Test if a port is accepting connections."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0  # Port is accessible if connection succeeds
        except Exception:
            return False
    
    def test_http_endpoint(self, port: int, endpoint: str = "/", host: str = "localhost", timeout: int = 5) -> Tuple[bool, str]:
        """Test HTTP endpoint on a port."""
        try:
            url = f"http://{host}:{port}{endpoint}"
            response = requests.get(url, timeout=timeout, verify=False)
            return True, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def start_test_server(self, port: int, server_type: str = "http") -> bool:
        """Start a test server on a specific port."""
        try:
            if server_type == "http":
                # Start a simple HTTP server
                def http_server():
                    import http.server
                    import socketserver
                    
                    class TestHandler(http.server.SimpleHTTPRequestHandler):
                        def do_GET(self):
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(f"Test server running on port {port}".encode())
                    
                    with socketserver.TCPServer(("", port), TestHandler) as httpd:
                        print(f"🔧 Started test HTTP server on port {port}")
                        httpd.serve_forever()
                
                thread = threading.Thread(target=http_server, daemon=True)
                thread.start()
                self.running_servers[port] = thread
                time.sleep(1)  # Give server time to start
                return True
                
        except Exception as e:
            print(f"❌ Failed to start test server on port {port}: {e}")
            return False
    
    def test_core_ports(self):
        """Test core ports needed for the betting platform."""
        print("🧪 Testing Core Platform Ports")
        print("=" * 50)
        
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
        
        for port, description in core_ports.items():
            print(f"\n📋 Testing {description} (Port {port})")
            
            # Check if port is available
            available = self.is_port_available(port)
            print(f"   Available: {'✅ Yes' if available else '❌ No'}")
            
            if available:
                # Try to start a test server
                if self.start_test_server(port):
                    time.sleep(2)  # Wait for server to start
                    
                    # Test connectivity
                    accessible = self.test_port_connectivity(port)
                    print(f"   Accessible: {'✅ Yes' if accessible else '❌ No'}")
                    
                    # Test HTTP endpoint if it's a web server
                    if port in [8000, 8001, 8002, 8003, 3000, 3001]:
                        http_ok, http_msg = self.test_http_endpoint(port)
                        print(f"   HTTP Test: {'✅ ' + http_msg if http_ok else '❌ ' + http_msg}")
                    
                    self.test_results[port] = {
                        "description": description,
                        "available": available,
                        "accessible": accessible,
                        "http_working": port in [8000, 8001, 8002, 8003, 3000, 3001] and self.test_http_endpoint(port)[0]
                    }
                else:
                    self.test_results[port] = {
                        "description": description,
                        "available": available,
                        "accessible": False,
                        "http_working": False
                    }
            else:
                # Port is in use, test if it's accessible
                accessible = self.test_port_connectivity(port)
                print(f"   In Use: {'✅ Accessible' if accessible else '❌ Not accessible'}")
                
                # Test HTTP endpoint if it's a web server
                if port in [8000, 8001, 8002, 8003, 3000, 3001]:
                    http_ok, http_msg = self.test_http_endpoint(port)
                    print(f"   HTTP Test: {'✅ ' + http_msg if http_ok else '❌ ' + http_msg}")
                
                self.test_results[port] = {
                    "description": description,
                    "available": available,
                    "accessible": accessible,
                    "http_working": port in [8000, 8001, 8002, 8003, 3000, 3001] and self.test_http_endpoint(port)[0]
                }
    
    def test_database_ports(self):
        """Test database and cache ports."""
        print("\n🗄️  Testing Database & Cache Ports")
        print("=" * 50)
        
        db_ports = {
            5432: "PostgreSQL",
            3306: "MySQL",
            27017: "MongoDB",
            6379: "Redis",
            9200: "Elasticsearch",
            8086: "InfluxDB"
        }
        
        for port, db_name in db_ports.items():
            print(f"\n📋 Testing {db_name} (Port {port})")
            
            available = self.is_port_available(port)
            accessible = self.test_port_connectivity(port)
            
            print(f"   Available: {'✅ Yes' if available else '❌ No'}")
            print(f"   Accessible: {'✅ Yes' if accessible else '❌ No'}")
            
            self.test_results[port] = {
                "description": f"{db_name} Database",
                "available": available,
                "accessible": accessible,
                "http_working": False
            }
    
    def test_ai_service_ports(self):
        """Test ports for AI services."""
        print("\n🤖 Testing AI Service Ports")
        print("=" * 50)
        
        ai_ports = {
            8004: "Claude AI Service",
            8005: "Perplexity AI Service",
            8006: "OpenAI Service",
            8007: "AI Model Service",
            8008: "Prediction Engine",
            8009: "Analytics Service"
        }
        
        for port, service_name in ai_ports.items():
            print(f"\n📋 Testing {service_name} (Port {port})")
            
            available = self.is_port_available(port)
            print(f"   Available: {'✅ Yes' if available else '❌ No'}")
            
            if available:
                if self.start_test_server(port):
                    time.sleep(1)
                    accessible = self.test_port_connectivity(port)
                    http_ok, http_msg = self.test_http_endpoint(port)
                    
                    print(f"   Accessible: {'✅ Yes' if accessible else '❌ No'}")
                    print(f"   HTTP Test: {'✅ ' + http_msg if http_ok else '❌ ' + http_msg}")
                    
                    self.test_results[port] = {
                        "description": service_name,
                        "available": available,
                        "accessible": accessible,
                        "http_working": http_ok
                    }
                else:
                    self.test_results[port] = {
                        "description": service_name,
                        "available": available,
                        "accessible": False,
                        "http_working": False
                    }
            else:
                accessible = self.test_port_connectivity(port)
                print(f"   In Use: {'✅ Accessible' if accessible else '❌ Not accessible'}")
                
                self.test_results[port] = {
                    "description": service_name,
                    "available": available,
                    "accessible": accessible,
                    "http_working": False
                }
    
    def test_sport_agent_ports(self):
        """Test ports for sport-specific agents."""
        print("\n🏈 Testing Sport Agent Ports")
        print("=" * 50)
        
        sport_ports = {
            8010: "Baseball Agent",
            8011: "Basketball Agent", 
            8012: "Football Agent",
            8013: "Hockey Agent",
            8014: "Head Agent Coordinator",
            8015: "Prediction Aggregator"
        }
        
        for port, agent_name in sport_ports.items():
            print(f"\n📋 Testing {agent_name} (Port {port})")
            
            available = self.is_port_available(port)
            print(f"   Available: {'✅ Yes' if available else '❌ No'}")
            
            if available:
                if self.start_test_server(port):
                    time.sleep(1)
                    accessible = self.test_port_connectivity(port)
                    http_ok, http_msg = self.test_http_endpoint(port)
                    
                    print(f"   Accessible: {'✅ Yes' if accessible else '❌ No'}")
                    print(f"   HTTP Test: {'✅ ' + http_msg if http_ok else '❌ ' + http_msg}")
                    
                    self.test_results[port] = {
                        "description": agent_name,
                        "available": available,
                        "accessible": accessible,
                        "http_working": http_ok
                    }
                else:
                    self.test_results[port] = {
                        "description": agent_name,
                        "available": available,
                        "accessible": False,
                        "http_working": False
                    }
            else:
                accessible = self.test_port_connectivity(port)
                print(f"   In Use: {'✅ Accessible' if accessible else '❌ Not accessible'}")
                
                self.test_results[port] = {
                    "description": agent_name,
                    "available": available,
                    "accessible": accessible,
                    "http_working": False
                }
    
    def generate_port_report(self):
        """Generate a comprehensive port report."""
        print("\n📊 Port Status Report")
        print("=" * 60)
        
        # Categorize results
        available_ports = []
        in_use_accessible = []
        in_use_inaccessible = []
        failed_ports = []
        
        for port, result in self.test_results.items():
            if result["available"]:
                available_ports.append((port, result))
            elif result["accessible"]:
                in_use_accessible.append((port, result))
            else:
                in_use_inaccessible.append((port, result))
        
        print(f"\n✅ Available Ports ({len(available_ports)}):")
        for port, result in available_ports:
            print(f"   Port {port}: {result['description']}")
        
        print(f"\n🟡 In Use & Accessible ({len(in_use_accessible)}):")
        for port, result in in_use_accessible:
            print(f"   Port {port}: {result['description']}")
        
        print(f"\n🔴 In Use & Inaccessible ({len(in_use_inaccessible)}):")
        for port, result in in_use_inaccessible:
            print(f"   Port {port}: {result['description']}")
        
        # Save report to file
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_ports_tested": len(self.test_results),
            "available_ports": len(available_ports),
            "in_use_accessible": len(in_use_accessible),
            "in_use_inaccessible": len(in_use_inaccessible),
            "results": self.test_results
        }
        
        with open("port_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Report saved to: port_test_report.json")
        
        return available_ports, in_use_accessible, in_use_inaccessible
    
    def cleanup(self):
        """Clean up test servers."""
        print("\n🧹 Cleaning up test servers...")
        # Test servers are daemon threads, they'll stop when main thread ends
        time.sleep(1)
        print("✅ Cleanup complete")

def main():
    """Run comprehensive port testing."""
    print("🚀 MultiSportsBettingPlatform - Comprehensive Port Testing")
    print("=" * 70)
    print("This will test all necessary ports for your betting platform")
    print("and start test servers to verify connectivity.")
    print()
    
    tester = PortTester()
    
    try:
        # Test all port categories
        tester.test_core_ports()
        tester.test_database_ports()
        tester.test_ai_service_ports()
        tester.test_sport_agent_ports()
        
        # Generate report
        available, in_use_accessible, in_use_inaccessible = tester.generate_port_report()
        
        print("\n" + "=" * 70)
        print("🎉 Port Testing Complete!")
        print()
        print("💡 Recommendations:")
        
        if available:
            print(f"   ✅ {len(available)} ports are available for use")
            print("   🚀 You can start your services on these ports")
        
        if in_use_accessible:
            print(f"   ⚠️  {len(in_use_accessible)} ports are in use but accessible")
            print("   🔍 Check if these are your other projects")
        
        if in_use_inaccessible:
            print(f"   ❌ {len(in_use_inaccessible)} ports are blocked or unreachable")
            print("   🔧 May need firewall configuration or service restart")
        
        print("\n🔧 Next Steps:")
        print("   1. Review the port_test_report.json for details")
        print("   2. Start your main application: py run.py")
        print("   3. Use available ports for additional services")
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 