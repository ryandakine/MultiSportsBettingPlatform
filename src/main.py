#!/usr/bin/env python3
"""
MultiSportsBettingPlatform - Main Application
============================================
FastAPI application for the multi-sport betting prediction platform.
"""

import os
import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import middleware
from src.middleware.error_handler import ErrorHandlerMiddleware, add_error_handlers
from src.middleware.rate_limiter import RateLimitMiddleware, rate_limiters

from src.config import settings

# Services
from src.services.auth_service import AuthService
from src.services.real_time_predictions import RealTimePredictionService
from src.services.social_features import SocialFeaturesService
from src.services.security_service import SecurityService
from src.services.session_manager import SessionManager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifelong(app: FastAPI):
    """Lifecycle events."""
    # Startup
    try:
        from src.api.routes import initialize_sub_agents, head_agent
        from src.services.websocket_service import websocket_manager
        from src.services.notification_service import initialize_notification_service
        
        logger.info("🚀 Initializing services...")
        await websocket_manager.initialize()
        redis_client = await websocket_manager.redis_manager.get_redis()
        await initialize_notification_service(redis_client, websocket_manager)
        
        logger.info("🚀 Initializing autonomous agents...")
        await initialize_sub_agents()
        await head_agent.start_autonomous_loop()
        logger.info("✅ Autonomous agents started")
    except Exception as e:
        logger.error(f"❌ Failed to start autonomous agents: {e}")
    
    yield
    
    # Shutdown logic (if any)
    logger.info("🛑 Shutting down...")

def create_fastapi_app():
    """Create a FastAPI application with all features."""
    
    app = FastAPI(
        title="MultiSportsBettingPlatform",
        description="Professional AI-Powered Sports Betting Platform",
        version="1.0.0",
        lifespan=lifelong
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add error handling middleware
    add_error_handlers(app)
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Add rate limiting middleware
    # app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
    # Note: Commented out for now, uncomment when Redis is configured

    # Initialize services
    # We maintain singletons or initialize here if needed for dependency injection
    auth_service = AuthService()
    # prediction_aggregator = PredictionAggregator() # Uses new HeadAgent logic instead
    real_time_service = RealTimePredictionService()
    social_service = SocialFeaturesService()
    security_service = SecurityService()
    session_manager = SessionManager()
    
    # ROOT ENDPOINT
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "MultiSportsBettingPlatform is running",
            "status": "operational",
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat()
        }

    # Include API Routes
    try:
        from src.api import routes, websocket_routes, auth_routes
        from src.api import feature_flag_routes, agent_query_routes, health_routes
        
        # Core routes
        app.include_router(health_routes.router)  # Health checks first
        app.include_router(routes.router)
        app.include_router(websocket_routes.router)
        app.include_router(auth_routes.router)
        
        # New production routes
        app.include_router(feature_flag_routes.router)
        app.include_router(agent_query_routes.router)
        
        logger.info("✅ API Routes loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load routes: {e}")
        # In production, we might want to raise this to fail startup
        raise e

    return app

# Initialize app
app = create_fastapi_app()

# Global reference for agent query API
from src.api.routes import head_agent as head_agent_instance

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)