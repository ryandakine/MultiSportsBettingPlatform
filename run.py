#!/usr/bin/env python3
"""
YOLO MODE launcher for MultiSportsBettingPlatform with dynamic port finding
Bypasses Pydantic configuration errors with simplified server
"""

import uvicorn
import socket
import os
import datetime
import json
import typing
import socketserver
import logging
from typing import Optional

# Configure verbose logging as per .cursorrules
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

# Try to import dotenv, but continue without it if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
    log_with_emoji("Environment variables loaded from .env file", "✅")
except ImportError:
    log_with_emoji("python-dotenv not found, using default configuration", "⚠️")
    log_with_emoji("Run: pip install python-dotenv for full environment support", "💡")
    # Create a dummy load_dotenv function
    def load_dotenv():
        pass
except Exception as e:
    log_with_emoji(f"No .env file found, using default configuration: {e}", "⚠️")
    log_with_emoji("Create a .env file from env.example for custom configuration", "💡")
    # Create a dummy load_dotenv function
    def load_dotenv():
        pass

# Try to import port utilities, fallback to basic implementation if not available
try:
    from src.utils.port_utils import get_server_config
    log_with_emoji("Using advanced port utilities", "✅")
except ImportError:
    log_with_emoji("Port utilities not available, using basic port finding", "⚠️")
    
    def is_port_available(port: int, host: str = "localhost") -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            log_with_emoji(f"Port availability check failed: {e}", "❌")
            return False

    def find_available_port(start_port: int = 8000, max_attempts: int = 100, host: str = "localhost") -> Optional[int]:
        """Find an available port starting from start_port."""
        log_with_emoji(f"Searching for available port starting from {start_port}", "🔍")
        for port in range(start_port, start_port + max_attempts):
            if is_port_available(port, host):
                log_with_emoji(f"Found available port: {port}", "✅")
                return port
        log_with_emoji(f"No available ports found in range {start_port}-{start_port + max_attempts}", "❌")
        return None

    def get_server_config():
        """Get server configuration with dynamic port finding."""
        host = os.getenv("HOST", "0.0.0.0")
        preferred_port = int(os.getenv("PORT", 8000))
        
        log_with_emoji(f"Configuring server with host: {host}, preferred port: {preferred_port}", "⚙️")
        
        # Check if preferred port is available
        if is_port_available(preferred_port, "localhost"):
            port = preferred_port
            log_with_emoji(f"Using preferred port {port}", "✅")
        else:
            log_with_emoji(f"Port {preferred_port} is in use, searching for available port...", "⚠️")
            port = find_available_port(preferred_port)
            
            if port is None:
                log_with_emoji(f"Could not find available port in range {preferred_port}-{preferred_port + 100}", "❌")
                log_with_emoji("Please free up some ports or specify a different PORT in environment", "💡")
                return None, None
            else:
                log_with_emoji(f"Found available port: {port}", "✅")
        
        return host, port

def create_simple_server():
    """Create a simple HTTP server for YOLO mode."""
    import http.server
    
    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            log_with_emoji(f"GET request received: {self.path}", "📥")
            
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "message": "YOLO MODE: MultiSportsBettingPlatform is running!",
                    "status": "success",
                    "mode": "simple_http",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "server_info": {
                        "type": "YOLO HTTP Server",
                        "version": "1.0.0-yolo",
                        "features": ["predictions", "yolo_mode", "maximum_confidence"]
                    }
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                log_with_emoji("Root endpoint served successfully", "✅")
            
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy",
                    "mode": "yolo_simple",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "server_uptime": "YOLO MODE: Maximum uptime!",
                    "system_status": "operational"
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                log_with_emoji("Health check served successfully", "✅")
            
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "error": "YOLO MODE: Endpoint not found",
                    "path": self.path,
                    "mode": "simple_http",
                    "available_endpoints": ["/", "/health"],
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                log_with_emoji(f"404 error for path: {self.path}", "❌")
        
        def do_POST(self):
            log_with_emoji(f"POST request received: {self.path}", "📥")
            
            if self.path == '/api/v1/predict':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "prediction": "YOLO MODE: Maximum confidence prediction!",
                    "confidence": 0.95,
                    "yolo_factor": 1.5,
                    "mode": "yolo_simple",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "prediction_details": {
                        "reasoning": "YOLO MODE: Maximum confidence reasoning!",
                        "factors": ["yolo_boost", "maximum_confidence", "yolo_mode"],
                        "recommendation": "Go with maximum confidence!"
                    }
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                log_with_emoji("Prediction endpoint served successfully", "✅")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "error": "YOLO MODE: Endpoint not found",
                    "path": self.path,
                    "mode": "simple_http",
                    "available_endpoints": ["/", "/health", "/api/v1/predict"],
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                log_with_emoji(f"404 error for POST path: {self.path}", "❌")
        
        def log_message(self, format, *args):
            # Suppress default logging for cleaner output
            pass
    
    return SimpleHandler

def create_fastapi_app():
    """Create a simplified FastAPI app for YOLO mode."""
    log_with_emoji("Attempting to create FastAPI application", "🎯")
    
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
        
        app = FastAPI(
            title="MultiSportsBettingPlatform - YOLO MODE",
            description="YOLO MODE: Simplified betting platform with maximum confidence!",
            version="1.0.0-yolo"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            log_with_emoji("Root endpoint accessed", "📥")
            return {
                "message": "YOLO MODE: MultiSportsBettingPlatform is running!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_info": {
                    "type": "YOLO FastAPI Server",
                    "version": "1.0.0-yolo",
                    "features": ["predictions", "yolo_mode", "maximum_confidence", "fastapi"]
                }
            }
        
        @app.get("/health")
        async def health():
            log_with_emoji("Health check accessed", "📥")
            return {
                "status": "healthy",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_uptime": "YOLO MODE: Maximum uptime!",
                "system_status": "operational"
            }
        
        @app.get("/api/v1/health")
        async def api_health():
            log_with_emoji("API health check accessed", "📥")
            return {
                "status": "healthy",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/status")
        async def status():
            log_with_emoji("Status endpoint accessed", "📥")
            return {
                "status": "running",
                "mode": "yolo_fastapi",
                "features": ["predictions", "yolo_mode", "maximum_confidence"],
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/sports")
        async def sports():
            log_with_emoji("Sports endpoint accessed", "📥")
            return {
                "sports": ["baseball", "football", "basketball", "hockey"],
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/predict")
        async def predict():
            log_with_emoji("Prediction endpoint accessed", "📥")
            return {
                "prediction": "YOLO MODE: Maximum confidence prediction!",
                "confidence": 0.95,
                "yolo_factor": 1.5,
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat(),
                "prediction_details": {
                    "reasoning": "YOLO MODE: Maximum confidence reasoning!",
                    "factors": ["yolo_boost", "maximum_confidence", "yolo_mode"],
                    "recommendation": "Go with maximum confidence!"
                }
            }
        
        @app.post("/api/v1/report-outcome")
        async def report_outcome():
            log_with_emoji("Report outcome endpoint accessed", "📥")
            return {
                "message": "YOLO MODE: Outcome reported with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/auth/register")
        async def register():
            log_with_emoji("Register endpoint accessed", "📥")
            return {
                "message": "YOLO MODE: User registered with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/auth/login")
        async def login():
            log_with_emoji("Login endpoint accessed", "📥")
            return {
                "message": "YOLO MODE: User logged in with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        log_with_emoji("FastAPI application created successfully", "✅")
        return app
        
    except Exception as e:
        log_with_emoji(f"FastAPI creation failed: {e}", "❌")
        log_with_emoji("Falling back to YOLO HTTP server", "🔄")
        return None

def main():
    """Main function with comprehensive error handling and verbose logging."""
    log_with_emoji("🚀 Starting MultiSportsBettingPlatform - YOLO MODE", "🚀")
    log_with_emoji("=" * 60, "📋")
    
    # Get server configuration
    host, port = get_server_config()
    
    if host is None or port is None:
        log_with_emoji("Failed to configure server. Exiting.", "❌")
        return 1
    
    log_with_emoji(f"Server configured: {host}:{port}", "⚙️")
    log_with_emoji(f"API Documentation: http://localhost:{port}/docs", "📚")
    log_with_emoji(f"Health Check: http://localhost:{port}/health", "🔗")
    
    # Try to create FastAPI app first
    app = create_fastapi_app()
    
    if app is not None:
        log_with_emoji("Attempting to start FastAPI server...", "🎯")
        try:
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,  # Disable reload to avoid Pydantic issues
                log_level="info"
            )
        except Exception as e:
            log_with_emoji(f"FastAPI server failed: {e}", "❌")
            log_with_emoji("Falling back to YOLO HTTP server...", "🔄")
            start_yolo_http_server(host, port)
    else:
        log_with_emoji("FastAPI not available, using YOLO HTTP server...", "🛠️")
        start_yolo_http_server(host, port)
    
    return 0

def start_yolo_http_server(host: str, port: int):
    """Start the YOLO HTTP server with comprehensive logging."""
    try:
        log_with_emoji("Creating YOLO HTTP server...", "🛠️")
        SimpleHandler = create_simple_server()
        
        with socketserver.TCPServer((host, port), SimpleHandler) as httpd:
            log_with_emoji(f"🌐 YOLO HTTP server running on {host}:{port}", "🌐")
            log_with_emoji("🚀 YOLO MODE: Maximum confidence server is active!", "🚀")
            log_with_emoji("=" * 60, "📋")
            log_with_emoji("Available endpoints:", "📋")
            log_with_emoji("  GET  / - Root endpoint", "📋")
            log_with_emoji("  GET  /health - Health check", "📋")
            log_with_emoji("  POST /api/v1/predict - YOLO predictions", "📋")
            log_with_emoji("=" * 60, "📋")
            httpd.serve_forever()
            
    except Exception as e:
        log_with_emoji(f"YOLO HTTP server failed: {e}", "❌")
        log_with_emoji("All server options exhausted. Exiting.", "💀")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        if exit_code != 0:
            log_with_emoji(f"Server exited with code: {exit_code}", "💀")
    except KeyboardInterrupt:
        log_with_emoji("Server stopped by user", "🛑")
    except Exception as e:
        log_with_emoji(f"Unexpected error: {e}", "💥")
        log_with_emoji("Stack trace:", "📋")
        import traceback
        traceback.print_exc() 