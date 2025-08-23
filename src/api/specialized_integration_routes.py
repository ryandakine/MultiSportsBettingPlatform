"""
Specialized System Integration API Routes - YOLO MODE!
===================================================
API endpoints for coordinating with MLB and CFL_NFL_Gold systems.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException

from src.services.specialized_system_integration import specialized_integration, SystemType

router = APIRouter()

@router.get("/api/v1/specialized/status")
async def get_all_system_statuses():
    """Get status of all specialized systems."""
    try:
        statuses = await specialized_integration.get_all_system_statuses()
        return {
            "status": "success",
            "message": "Specialized system statuses retrieved",
            "data": statuses,
            "timestamp": datetime.now().isoformat(),
            "yolo_mode": specialized_integration.yolo_mode_active
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system statuses: {str(e)}")

@router.get("/api/v1/specialized/statistics")
async def get_integration_statistics():
    """Get integration statistics."""
    try:
        stats = await specialized_integration.get_integration_statistics()
        return {
            "status": "success",
            "message": "Integration statistics retrieved",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/api/v1/specialized/predict")
async def create_cross_system_prediction(request: Dict[str, Any]):
    """Create a prediction using all available specialized systems."""
    try:
        sport = request.get("sport", "")
        teams = request.get("teams", [])
        query_params = request.get("query_params", {})
        
        if not sport or not teams:
            raise HTTPException(status_code=400, detail="Sport and teams are required")
        
        prediction = await specialized_integration.create_cross_system_prediction(
            sport=sport,
            teams=teams,
            query_params=query_params
        )
        
        return {
            "status": "success",
            "message": "Cross-system prediction created",
            "data": {
                "id": prediction.id,
                "sport": prediction.sport,
                "teams": prediction.teams,
                "mlb_prediction": prediction.mlb_prediction,
                "football_prediction": prediction.football_prediction,
                "head_agent_prediction": prediction.head_agent_prediction,
                "combined_prediction": prediction.combined_prediction,
                "overall_confidence": prediction.overall_confidence,
                "yolo_boost": prediction.yolo_boost,
                "timestamp": prediction.timestamp.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create prediction: {str(e)}")

@router.get("/api/v1/specialized/predictions/recent")
async def get_recent_predictions(limit: int = 10):
    """Get recent cross-system predictions."""
    try:
        predictions = await specialized_integration.get_recent_predictions(limit=limit)
        return {
            "status": "success",
            "message": f"Retrieved {len(predictions)} recent predictions",
            "data": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent predictions: {str(e)}")

@router.post("/api/v1/specialized/yolo-mode")
async def toggle_yolo_mode(request: Dict[str, Any]):
    """Enable or disable YOLO mode for specialized systems."""
    try:
        enabled = request.get("enabled", True)
        await specialized_integration.enable_yolo_mode(enabled)
        
        return {
            "status": "success",
            "message": f"YOLO mode {'enabled' if enabled else 'disabled'}",
            "data": {
                "yolo_mode_active": specialized_integration.yolo_mode_active
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle YOLO mode: {str(e)}")

@router.get("/api/v1/specialized/system/{system_type}/status")
async def get_system_status(system_type: str):
    """Get detailed status of a specific system."""
    try:
        try:
            system_enum = SystemType(system_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid system type: {system_type}")
        
        status = await specialized_integration.get_system_status(system_enum)
        
        return {
            "status": "success",
            "message": f"Status retrieved for {system_type}",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.post("/api/v1/specialized/system/{system_type}/predict")
async def get_system_prediction(system_type: str, request: Dict[str, Any]):
    """Get prediction from a specific system."""
    try:
        try:
            system_enum = SystemType(system_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid system type: {system_type}")
        
        query_params = request.get("query_params", {})
        prediction = await specialized_integration.get_prediction_from_system(system_enum, query_params)
        
        if prediction is None:
            raise HTTPException(status_code=503, detail=f"{system_type} system is unavailable")
        
        return {
            "status": "success",
            "message": f"Prediction retrieved from {system_type}",
            "data": prediction,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prediction: {str(e)}")

@router.get("/api/v1/specialized/health")
async def get_integration_health():
    """Get overall integration health status."""
    try:
        statuses = await specialized_integration.get_all_system_statuses()
        stats = await specialized_integration.get_integration_statistics()
        
        online_systems = stats["online_systems"]
        total_systems = stats["total_systems"]
        health_percentage = (online_systems / total_systems) * 100
        
        health_status = "healthy" if health_percentage >= 66 else "degraded" if health_percentage >= 33 else "critical"
        
        return {
            "status": "success",
            "message": "Integration health check completed",
            "data": {
                "health_status": health_status,
                "health_percentage": health_percentage,
                "online_systems": online_systems,
                "total_systems": total_systems,
                "yolo_mode_active": specialized_integration.yolo_mode_active,
                "system_statuses": statuses
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")

@router.get("/api/v1/specialized/systems")
async def get_available_systems():
    """Get list of available specialized systems."""
    try:
        systems = []
        for system_type in SystemType:
            systems.append({
                "type": system_type.value,
                "name": system_type.value.replace("_", " ").title(),
                "port": specialized_integration._get_system_port(system_type),
                "base_url": specialized_integration.system_configs[system_type]["base_url"]
            })
        
        return {
            "status": "success",
            "message": "Available systems retrieved",
            "data": {
                "systems": systems,
                "total_systems": len(systems)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available systems: {str(e)}")

@router.get("/api/v1/specialized/yolo-stats")
async def get_yolo_statistics():
    """Get YOLO mode statistics."""
    try:
        stats = await specialized_integration.get_integration_statistics()
        recent_predictions = await specialized_integration.get_recent_predictions(limit=5)
        
        yolo_predictions = [p for p in recent_predictions if p.get("yolo_boost", 1.0) > 1.0]
        
        return {
            "status": "success",
            "message": "YOLO statistics retrieved",
            "data": {
                "yolo_mode_active": specialized_integration.yolo_mode_active,
                "average_yolo_boost": stats["average_yolo_boost"],
                "total_predictions": stats["total_cross_predictions"],
                "yolo_predictions_count": len(yolo_predictions),
                "recent_yolo_predictions": yolo_predictions
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get YOLO statistics: {str(e)}") 