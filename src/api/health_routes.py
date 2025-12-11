"""
Health & Readiness Endpoints
============================
Production-grade health monitoring for load balancers and orchestrators.
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime
import asyncio

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Liveness probe - is the application running?
    
    Used by Kubernetes/Docker for liveness checks.
    Should ONLY check if the process is alive, not dependencies.
    
    Returns:
        Simple status indicating app is alive
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MultiSportsBettingPlatform"
    }


@router.get("/ready", status_code=status.HTTP_200_OK) 
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe - is the application ready to serve traffic?
    
    Used by load balancers to determine if instance should receive traffic.
    Checks all critical dependencies.
    
    Returns:
        Detailed status of all dependencies
    """
    checks = {}
    overall_ready = True
    
    # Check Database
    db_status = await check_database()
    checks["database"] = db_status
    if not db_status["healthy"]:
        overall_ready = False
    
    # Check Redis
    redis_status = await check_redis()
    checks["redis"] = redis_status
    if not redis_status["healthy"]:
        overall_ready = False
    
    # Check AgentRegistry
    registry_status = await check_agent_registry()
    checks["agent_registry"] = registry_status
    # Don't fail readiness if agents not registered yet
    
    response = {
        "status": "ready" if overall_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
    
    if not overall_ready:
        return response, status.HTTP_503_SERVICE_UNAVAILABLE
    
    return response


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """
    Prometheus-compatible metrics endpoint.
    
    Returns key application metrics in a format Prometheus can scrape.
    """
    from src.api.routes import head_agent
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        
        # Application metrics
        "agents_registered": len(head_agent._local_agent_refs) if head_agent else 0,
        "heartbeat_running": head_agent._heartbeat_running if head_agent else False,
        
        # Will be populated by actual metrics collection
        "predictions_total": 0,  # TODO: Implement counter
        "predictions_per_minute": 0,  # TODO: Implement gauge
        "active_users": 0,  # TODO: Implement from sessions
        "websocket_connections": 0,  # TODO: Implement
        
        # System metrics
        "uptime_seconds": 0,  # TODO: Track startup time
    }
    
    return metrics


async def check_database() -> Dict[str, Any]:
    """Check if database is accessible."""
    try:
        from src.db.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # Simple query to verify DB is up
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
        return {
            "healthy": True,
            "message": "Database connection successful",
            "latency_ms": 0  # TODO: Measure actual latency
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Database connection failed: {str(e)}",
            "error": type(e).__name__
        }


async def check_redis() -> Dict[str, Any]:
    """Check if Redis is accessible."""
    try:
        from src.services.feature_flags import feature_flags
        
        # Try to access Redis
        redis_client = await feature_flags._get_redis()
        
        if not redis_client:
            return {
                "healthy": False,
                "message": "Redis not available"
            }
        
        # Ping Redis
        await redis_client.ping()
        
        return {
            "healthy": True,
            "message": "Redis connection successful"
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Redis connection failed: {str(e)}",
            "error": type(e).__name__
        }


async def check_agent_registry() -> Dict[str, Any]:
    """Check if AgentRegistry is functioning."""
    try:
        from src.services.agent_registry import agent_registry
        
        # Check if registry can access Redis
        redis_client = await agent_registry._get_redis()
        
        if not redis_client:
            return {
                "healthy": False,
                "message": "AgentRegistry Redis unavailable",
                "warning": "Will function in degraded mode"
            }
        
        return {
            "healthy": True,
            "message": "AgentRegistry operational"
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"AgentRegistry check failed: {str(e)}",
            "error": type(e).__name__
        }
