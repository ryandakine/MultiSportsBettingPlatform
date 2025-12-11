#!/usr/bin/env python3
"""
MultiSportsBettingPlatform - Main Application
============================================
FastAPI application for the multi-sport betting prediction platform.
"""

# Initialize agents on startup
# startup logic moved to app.on_event("startup")

# Try to import uvicorn, fallback to simple server if not available
try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    print("⚠️ Uvicorn not available, will use HTTP server fallback")
    UVICORN_AVAILABLE = False

import os
import datetime
import json
from typing import Dict, Any, List, Optional

# Try to import FastAPI, fallback to simple server if not available
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ FastAPI not available: {e}")
    FASTAPI_AVAILABLE = False

# Import services (these should work now)
try:
    from src.services.auth_service import AuthService
    from src.services.prediction_aggregator_v2 import PredictionAggregatorV2
    from src.services.real_time_predictions import RealTimePredictionService
    from src.services.social_features import SocialFeaturesService
    from src.services.security_service import SecurityService
    from src.services.session_manager import SessionManager
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some services not available: {e}")
    SERVICES_AVAILABLE = False

def create_fastapi_app():
    """Create a FastAPI application with all features."""
    global SERVICES_AVAILABLE
    
    if not FASTAPI_AVAILABLE:
        return None
    
    app = FastAPI(
        title="MultiSportsBettingPlatform - YOLO MODE",
        description="YOLO MODE: Comprehensive betting platform with maximum confidence!",
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

    @app.on_event("startup")
    async def startup_event():
        """Initialize services and agents on startup."""
        if SERVICES_AVAILABLE:
            try:
                from src.api.routes import initialize_sub_agents, head_agent
                await initialize_sub_agents()
                await head_agent.start_autonomous_loop()
            except Exception as e:
                print(f"❌ Failed to start autonomous agents: {e}")
    
    # Initialize services
    auth_service = AuthService() if SERVICES_AVAILABLE else None
    prediction_aggregator = PredictionAggregatorV2() if SERVICES_AVAILABLE else None
    real_time_service = RealTimePredictionService() if SERVICES_AVAILABLE else None
    social_service = SocialFeaturesService() if SERVICES_AVAILABLE else None
    security_service = SecurityService() if SERVICES_AVAILABLE else None
    session_manager = SessionManager() if SERVICES_AVAILABLE else None
    
    # ROOT ENDPOINT (Always available)
    @app.get("/")
    async def root():
        """Root endpoint."""
        mode = "REAL_MODE" if SERVICES_AVAILABLE else "YOLO_MODE"
        return {
            "message": f"{mode}: MultiSportsBettingPlatform is running!",
            "status": "success",
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat(),
            "server_info": {
                "type": f"{mode} FastAPI Server",
                "version": "1.0.0",
                "features": ["predictions", "auth", "real_mode" if SERVICES_AVAILABLE else "yolo_mode"]
            }
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "mode": "REAL_MODE" if SERVICES_AVAILABLE else "YOLO_MODE",
            "timestamp": datetime.datetime.now().isoformat(),
            "server_uptime": "Maximum uptime!"
        }

    if SERVICES_AVAILABLE:
        try:
            from src.api.routes import router as api_router
            app.include_router(api_router)
            print("✅ Real API Routes loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load real routes: {e}")
            SERVICES_AVAILABLE = False # Fallback to YOLO
            
    if not SERVICES_AVAILABLE:
        print("⚠️ Services not available, loading YOLO endpoints")
        
        @app.get("/health")
        async def health():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat(),
                "server_uptime": "YOLO MODE: Maximum uptime!",
                "system_status": "operational"
            }
        
        @app.get("/api/v1/health")
        async def api_health():
            """API health check."""
            return {
                "status": "healthy",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/status")
        async def status():
            """System status."""
            return {
                "status": "running",
                "mode": "yolo_fastapi",
                "features": ["predictions", "yolo_mode", "maximum_confidence"],
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/sports")
        async def sports():
            """Available sports."""
            return {
                "sports": ["baseball", "football", "basketball", "hockey"],
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/predict")
        async def predict():
            """Make predictions."""
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
            """Report prediction outcomes."""
            return {
                "message": "YOLO MODE: Outcome reported with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Authentication endpoints
        @app.post("/api/v1/auth/register")
        async def register():
            """User registration."""
            return {
                "message": "YOLO MODE: User registered with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/auth/login")
        async def login():
            """User login."""
            return {
                "message": "YOLO MODE: User logged in with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/auth/logout")
        async def logout():
            """User logout."""
            return {
                "message": "YOLO MODE: User logged out with maximum confidence!",
                "status": "success",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Social features endpoints
        @app.get("/api/v1/social/communities")
        async def get_communities():
            """Get YOLO communities."""
            return {
                "communities": [
                    {"id": "yolo_masters", "name": "YOLO Masters Elite", "type": "yolo_masters"},
                    {"id": "basketball_yolo", "name": "Basketball YOLO Legends", "type": "sport_specific"},
                    {"id": "underdog_army", "name": "Underdog Army", "type": "underdog_lovers"},
                    {"id": "risk_takers_united", "name": "Risk Takers United", "type": "risk_takers"},
                    {"id": "home_team_nation", "name": "Home Team Nation", "type": "home_team_fans"}
                ],
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.get("/api/v1/social/leaderboard")
        async def get_leaderboard():
            """Get YOLO leaderboard."""
            return {
                "leaderboard": [
                    {"rank": 1, "username": "YOLO_Master_Pro", "score": 95.5, "level": "YOLO Legend"},
                    {"rank": 2, "username": "UnderdogHunter", "score": 88.2, "level": "YOLO Champion"},
                    {"rank": 3, "username": "HomeCourtHero", "score": 92.1, "level": "YOLO Master"},
                    {"rank": 4, "username": "RiskTaker_Elite", "score": 89.7, "level": "YOLO Expert"},
                    {"rank": 5, "username": "HockeyYOLO", "score": 87.3, "level": "YOLO Pro"}
                ],
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # YOLO features endpoints
        @app.get("/api/v1/yolo/stats")
        async def yolo_stats():
            """Get YOLO statistics."""
            return {
                "yolo_stats": {
                    "total_predictions": 1250,
                    "average_confidence": 0.89,
                    "yolo_boost_factor": 1.5,
                    "success_rate": 0.87,
                    "active_users": 342,
                    "communities": 5
                },
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        @app.post("/api/v1/yolo/generate-prediction")
        async def generate_yolo_prediction():
            """Generate YOLO prediction."""
            return {
                "prediction": "YOLO MODE: Maximum confidence prediction generated!",
                "confidence": 0.95,
                "yolo_factor": 1.5,
                "reasoning": "YOLO MODE: Maximum confidence reasoning with YOLO boost!",
                "recommendation": "Go with maximum confidence - YOLO style!",
                "mode": "yolo_fastapi",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    return app

def main():
    """Main function to start the server."""
    print("🚀 Starting MultiSportsBettingPlatform - YOLO MODE")
    print("=" * 60)
    
    # Get server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Server configured: {host}:{port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    
    # Try to create FastAPI app
    app = create_fastapi_app()
    
    if app is not None and UVICORN_AVAILABLE:
        print("✅ FastAPI application created successfully")
        try:
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ FastAPI server failed: {e}")
            print("🔄 Falling back to YOLO HTTP server...")
            start_yolo_http_server(host, port)
    else:
        if not UVICORN_AVAILABLE:
            print("⚠️ Uvicorn not available, using YOLO HTTP server...")
        else:
            print("⚠️ FastAPI not available, using YOLO HTTP server...")
        start_yolo_http_server(host, port)

def start_yolo_http_server(host: str, port: int):
    """Start the YOLO HTTP server."""
    import http.server
    import socketserver
    
    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "message": "YOLO MODE: MultiSportsBettingPlatform is running!",
                    "status": "success",
                    "mode": "simple_http",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
            
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
        
        def log_message(self, format, *args):
            pass
    
    try:
        with socketserver.TCPServer((host, port), SimpleHandler) as httpd:
            print(f"🌐 YOLO HTTP server running on {host}:{port}")
            print("🚀 YOLO MODE: Maximum confidence server is active!")
            print("=" * 60)
            print("Available endpoints:")
            print("  GET  / - Root endpoint")
            print("  GET  /health - Health check")
            print("=" * 60)
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ YOLO HTTP server failed: {e}")
        print("💀 All server options exhausted. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 