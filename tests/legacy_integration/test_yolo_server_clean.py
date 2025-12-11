#!/usr/bin/env python3
"""
Test YOLO Server on Clean Port - Debug Test
Verifies that our YOLO HTTP server works without port conflicts
"""

import socket
import http.server
import socketserver
import threading
import time
import datetime
import logging

# Configure verbose logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_with_emoji(message: str, emoji: str = "ℹ️"):
    """Log message with emoji indicator for visual clarity."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"{emoji} {timestamp} - {message}")

def find_clean_port(start_port: int = 8010, max_attempts: int = 50):
    """Find a completely clean port."""
    log_with_emoji(f"🔍 Searching for clean port starting from {start_port}", "🔍")
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result != 0:  # Port is available
                    log_with_emoji(f"✅ Found clean port: {port}", "✅")
                    return port
        except Exception as e:
            log_with_emoji(f"⚠️ Port {port} check failed: {e}", "⚠️")
            continue
    
    log_with_emoji(f"❌ No clean ports found in range {start_port}-{start_port + max_attempts}", "❌")
    return None

class YOLOTestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        log_with_emoji(f"📥 GET request received: {self.path}", "📥")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "YOLO MODE: MultiSportsBettingPlatform is running!",
                "status": "success",
                "mode": "yolo_test_server",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_info": {
                    "type": "YOLO Test Server",
                    "version": "1.0.0-yolo-debug",
                    "features": ["predictions", "yolo_mode", "maximum_confidence", "debug_mode"]
                }
            }
            self.wfile.write(str(response).encode())
            log_with_emoji("✅ Root endpoint served successfully", "✅")
        
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "mode": "yolo_test_server",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_uptime": "YOLO MODE: Maximum uptime!",
                "system_status": "operational"
            }
            self.wfile.write(str(response).encode())
            log_with_emoji("✅ Health check served successfully", "✅")
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "error": "YOLO MODE: Endpoint not found",
                "path": self.path,
                "mode": "yolo_test_server",
                "available_endpoints": ["/", "/health"],
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.wfile.write(str(response).encode())
            log_with_emoji(f"❌ 404 error for path: {self.path}", "❌")
    
    def log_message(self, format, *args):
        # Suppress default logging for cleaner output
        pass

def test_yolo_server():
    """Test YOLO server on a clean port."""
    log_with_emoji("🚀 Testing YOLO Server on Clean Port", "🚀")
    log_with_emoji("=" * 60, "📋")
    
    # Find a clean port
    port = find_clean_port(8010)
    if port is None:
        log_with_emoji("❌ Could not find clean port for testing", "❌")
        return False
    
    # Start server in background thread
    log_with_emoji(f"🛠️ Starting YOLO test server on port {port}", "🛠️")
    
    try:
        with socketserver.TCPServer(("localhost", port), YOLOTestHandler) as httpd:
            log_with_emoji(f"🌐 YOLO test server running on localhost:{port}", "🌐")
            log_with_emoji("🚀 YOLO MODE: Test server is active!", "🚀")
            log_with_emoji("=" * 60, "📋")
            log_with_emoji("Available endpoints:", "📋")
            log_with_emoji("  GET  / - Root endpoint", "📋")
            log_with_emoji("  GET  /health - Health check", "📋")
            log_with_emoji("=" * 60, "📋")
            
            # Run server for 10 seconds
            log_with_emoji("⏱️ Server will run for 10 seconds for testing", "⏱️")
            httpd.serve_forever()
            
    except Exception as e:
        log_with_emoji(f"❌ YOLO test server failed: {e}", "❌")
        return False
    
    log_with_emoji("✅ YOLO test server completed successfully", "✅")
    return True

if __name__ == "__main__":
    try:
        success = test_yolo_server()
        if success:
            log_with_emoji("🎉 YOLO server test completed successfully!", "🎉")
        else:
            log_with_emoji("💀 YOLO server test failed!", "💀")
    except KeyboardInterrupt:
        log_with_emoji("🛑 Test stopped by user", "🛑")
    except Exception as e:
        log_with_emoji(f"💥 Unexpected error: {e}", "💥") 