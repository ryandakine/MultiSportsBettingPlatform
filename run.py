#!/usr/bin/env python3
"""
YOLO MODE launcher for MultiSportsBettingPlatform with dynamic port finding
Bypasses Pydantic configuration errors with simplified server
"""

# Try to import uvicorn
try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False

import socket
import os
import datetime
import json
import typing
import socketserver
import logging
from typing import Optional

# ... (logging and helper functions remain same)

# Helper functions
def log_with_emoji(message: str, emoji: str = "ℹ️"):
    """Log a message with an emoji prefix."""
    print(f"{emoji} {message}")

def get_server_config():
    """Get host and port configuration."""
    return "0.0.0.0", 8000

# Import create_fastapi_app from src.main
from src.main import create_fastapi_app

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
    
    if app is not None and UVICORN_AVAILABLE:
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
        if not UVICORN_AVAILABLE:
             log_with_emoji("Uvicorn not found, cannot run FastAPI...", "⚠️")
        else:
             log_with_emoji("FastAPI creation failed...", "⚠️")
        
        log_with_emoji("Falling back to YOLO HTTP server...", "🛠️")
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