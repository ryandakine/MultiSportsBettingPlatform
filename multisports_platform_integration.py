#!/usr/bin/env python3
"""
MultiSports Betting Platform Integration - YOLO MODE!
====================================================
Unified platform that coordinates all sports betting systems:
- Baseball (MLB) - Port 8000
- Football (CFL/NFL) - Port 8002  
- Hockey (NHL) - Port 8005
- Basketball (NBA) - Port 8006
"""

import asyncio
import aiohttp
import json
import random
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

class SportType(str, Enum):
    """Supported sports in the platform - YOLO MODE!"""
    BASEBALL = "baseball"
    FOOTBALL = "football"
    HOCKEY = "hockey"
    BASKETBALL = "basketball"

@dataclass
class SportSystem:
    """Individual sport system configuration - YOLO MODE!"""
    sport: SportType
    name: str
    port: int
    base_url: str
    status: str = "unknown"
    council_members: int = 5
    teams_count: int = 0
    yolo_factor: float = 1.5

@dataclass
class CrossSportPrediction:
    """Prediction from multiple sports systems - YOLO MODE!"""
    id: str
    sport_type: SportType
    teams: List[str]
    prediction: str
    confidence: float
    yolo_factor: float
    timestamp: datetime.datetime
    system_port: int
    council_analysis: Optional[List[Dict[str, Any]]] = None

@dataclass
class PlatformStatus:
    """Overall platform status - YOLO MODE!"""
    total_sports: int
    active_systems: int
    total_predictions: int
    yolo_mode: bool
    systems_status: Dict[str, str]
    timestamp: datetime.datetime

class MultiSportsBettingPlatform:
    """Unified platform coordinating all sports betting systems - YOLO MODE!"""
    
    def __init__(self):
        self.platform_name = "MultiSports Betting Platform - YOLO MODE!"
        self.version = "2.0.0-yolo"
        self.yolo_mode_active = True
        
        # Configure all sport systems
        self.sport_systems = {
            SportType.BASEBALL: SportSystem(
                sport=SportType.BASEBALL,
                name="MLB Betting System",
                port=8000,
                base_url="http://localhost:8000",
                council_members=5,
                teams_count=30,
                yolo_factor=1.6
            ),
            SportType.FOOTBALL: SportSystem(
                sport=SportType.FOOTBALL,
                name="CFL/NFL Gold System",
                port=8002,
                base_url="http://localhost:8002",
                council_members=5,
                teams_count=32,
                yolo_factor=1.7
            ),
            SportType.HOCKEY: SportSystem(
                sport=SportType.HOCKEY,
                name="NHL Hockey System",
                port=8005,
                base_url="http://localhost:8005",
                council_members=5,
                teams_count=16,
                yolo_factor=1.8
            ),
            SportType.BASKETBALL: SportSystem(
                sport=SportType.BASKETBALL,
                name="NBA Basketball System",
                port=8006,
                base_url="http://localhost:8006",
                council_members=5,
                teams_count=15,
                yolo_factor=1.9
            )
        }
        
        # Prediction history across all sports
        self.cross_sport_predictions: List[CrossSportPrediction] = []
        
        # Platform statistics
        self.platform_stats = {
            "total_predictions": 0,
            "sport_predictions": {sport.value: 0 for sport in SportType},
            "successful_predictions": 0,
            "yolo_boosts_applied": 0
        }

    async def check_system_health(self, sport: SportType) -> bool:
        """Check if a sport system is healthy - YOLO MODE!"""
        system = self.sport_systems[sport]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{system.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        system.status = "healthy"
                        return True
                    else:
                        system.status = "unhealthy"
                        return False
        except Exception as e:
            system.status = "offline"
            return False

    async def get_system_status(self, sport: SportType) -> Dict[str, Any]:
        """Get detailed status of a sport system - YOLO MODE!"""
        system = self.sport_systems[sport]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{system.base_url}/api/v1/status", timeout=5) as response:
                    if response.status == 200:
                        status_data = await response.json()
                        system.status = "healthy"
                        return {
                            "sport": sport.value,
                            "name": system.name,
                            "port": system.port,
                            "status": "healthy",
                            "yolo_mode": status_data.get("yolo_mode", True),
                            "council_members": status_data.get("council_members", 5),
                            "teams_count": status_data.get("teams_in_database", system.teams_count),
                            "predictions_count": status_data.get("total_predictions", 0),
                            "yolo_factor": system.yolo_factor
                        }
                    else:
                        system.status = "unhealthy"
                        return {
                            "sport": sport.value,
                            "name": system.name,
                            "port": system.port,
                            "status": "unhealthy",
                            "error": "Status endpoint failed"
                        }
        except Exception as e:
            system.status = "offline"
            return {
                "sport": sport.value,
                "name": system.name,
                "port": system.port,
                "status": "offline",
                "error": str(e)
            }

    async def get_sport_teams(self, sport: SportType) -> List[str]:
        """Get teams for a specific sport - YOLO MODE!"""
        system = self.sport_systems[sport]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{system.base_url}/api/v1/teams", timeout=5) as response:
                    if response.status == 200:
                        teams_data = await response.json()
                        return teams_data.get("teams", [])
                    else:
                        return []
        except Exception as e:
            return []

    async def create_sport_prediction(self, sport: SportType, team1: str, team2: str, prediction_type: str = "moneyline") -> Optional[CrossSportPrediction]:
        """Create prediction for a specific sport - YOLO MODE!"""
        system = self.sport_systems[sport]
        
        try:
            async with aiohttp.ClientSession() as session:
                prediction_data = {
                    "team1": team1,
                    "team2": team2,
                    "prediction_type": prediction_type
                }
                
                async with session.post(f"{system.base_url}/api/v1/predict", json=prediction_data, timeout=10) as response:
                    if response.status == 200:
                        prediction_result = await response.json()
                        
                        prediction = CrossSportPrediction(
                            id=prediction_result.get("prediction_id", f"{sport.value}_yolo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"),
                            sport_type=sport,
                            teams=[team1, team2],
                            prediction=prediction_result.get("prediction", f"{sport.value.title()} YOLO prediction"),
                            confidence=prediction_result.get("confidence", 0.8),
                            yolo_factor=prediction_result.get("yolo_factor", system.yolo_factor),
                            timestamp=datetime.datetime.now(),
                            system_port=system.port,
                            council_analysis=prediction_result.get("council_analysis", [])
                        )
                        
                        # Update platform statistics
                        self.platform_stats["total_predictions"] += 1
                        self.platform_stats["sport_predictions"][sport.value] += 1
                        self.cross_sport_predictions.append(prediction)
                        
                        return prediction
                    else:
                        return None
        except Exception as e:
            return None

    async def get_platform_status(self) -> PlatformStatus:
        """Get overall platform status - YOLO MODE!"""
        systems_status = {}
        active_systems = 0
        
        for sport in SportType:
            is_healthy = await self.check_system_health(sport)
            systems_status[sport.value] = self.sport_systems[sport].status
            if is_healthy:
                active_systems += 1
        
        return PlatformStatus(
            total_sports=len(SportType),
            active_systems=active_systems,
            total_predictions=self.platform_stats["total_predictions"],
            yolo_mode=self.yolo_mode_active,
            systems_status=systems_status,
            timestamp=datetime.datetime.now()
        )

    async def get_all_sport_teams(self) -> Dict[str, List[str]]:
        """Get teams from all sports - YOLO MODE!"""
        all_teams = {}
        
        for sport in SportType:
            teams = await self.get_sport_teams(sport)
            all_teams[sport.value] = teams
        
        return all_teams

    async def get_recent_predictions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent predictions from all sports - YOLO MODE!"""
        recent = self.cross_sport_predictions[-limit:] if self.cross_sport_predictions else []
        return [
            {
                "id": p.id,
                "sport": p.sport_type.value,
                "teams": p.teams,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "yolo_factor": p.yolo_factor,
                "timestamp": p.timestamp.isoformat(),
                "system_port": p.system_port
            }
            for p in recent
        ]

    async def create_cross_sport_analysis(self, team1: str, team2: str) -> Dict[str, Any]:
        """Create analysis across all sports - YOLO MODE!"""
        cross_sport_results = {}
        
        for sport in SportType:
            # Get teams for this sport
            sport_teams = await self.get_sport_teams(sport)
            
            # Check if teams exist in this sport
            if team1 in sport_teams and team2 in sport_teams:
                prediction = await self.create_sport_prediction(sport, team1, team2, "moneyline")
                if prediction:
                    cross_sport_results[sport.value] = {
                        "prediction": prediction.prediction,
                        "confidence": prediction.confidence,
                        "yolo_factor": prediction.yolo_factor,
                        "council_analysis": prediction.council_analysis
                    }
            else:
                cross_sport_results[sport.value] = {
                    "status": "teams_not_found",
                    "available_teams": sport_teams
                }
        
        return cross_sport_results

# Create platform instance
multisports_platform = MultiSportsBettingPlatform()

async def root(request: Request):
    """Root endpoint - YOLO MODE!"""
    return JSONResponse({
        "message": "MultiSports Betting Platform - YOLO MODE!",
        "platform": multisports_platform.platform_name,
        "version": multisports_platform.version,
        "sports": [sport.value for sport in SportType],
        "status": "operational",
        "yolo_mode": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def health(request: Request):
    """Health check endpoint - YOLO MODE!"""
    return JSONResponse({
        "status": "healthy",
        "platform": "multisports_betting_platform",
        "yolo_mode": multisports_platform.yolo_mode_active,
        "yolo_factor": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

async def platform_status(request: Request):
    """Platform status endpoint - YOLO MODE!"""
    status = await multisports_platform.get_platform_status()
    return JSONResponse({
        "platform_name": multisports_platform.platform_name,
        "version": multisports_platform.version,
        "total_sports": status.total_sports,
        "active_systems": status.active_systems,
        "total_predictions": status.total_predictions,
        "yolo_mode": status.yolo_mode,
        "systems_status": status.systems_status,
        "timestamp": status.timestamp.isoformat()
    })

async def sport_status(request: Request):
    """Individual sport system status - YOLO MODE!"""
    sport_param = request.query_params.get("sport", "baseball")
    
    try:
        sport = SportType(sport_param)
        status_data = await multisports_platform.get_system_status(sport)
        return JSONResponse(status_data)
    except ValueError:
        return JSONResponse({
            "error": f"Invalid sport: {sport_param}",
            "available_sports": [sport.value for sport in SportType]
        }, status_code=400)

async def all_teams(request: Request):
    """Get teams from all sports - YOLO MODE!"""
    all_teams = await multisports_platform.get_all_sport_teams()
    return JSONResponse({
        "teams": all_teams,
        "total_sports": len(all_teams),
        "yolo_mode": "MAXIMUM CONFIDENCE!"
    })

async def predict(request: Request):
    """Create prediction for specific sport - YOLO MODE!"""
    try:
        body = await request.json()
        sport_param = body.get("sport", "baseball")
        team1 = body.get("team1", "default_team1")
        team2 = body.get("team2", "default_team2")
        prediction_type = body.get("prediction_type", "moneyline")
        
        try:
            sport = SportType(sport_param)
        except ValueError:
            return JSONResponse({
                "error": f"Invalid sport: {sport_param}",
                "available_sports": [sport.value for sport in SportType]
            }, status_code=400)
        
        prediction = await multisports_platform.create_sport_prediction(sport, team1, team2, prediction_type)
        
        if prediction:
            return JSONResponse({
                "prediction_id": prediction.id,
                "sport": prediction.sport_type.value,
                "teams": prediction.teams,
                "prediction": prediction.prediction,
                "confidence": prediction.confidence,
                "yolo_factor": prediction.yolo_factor,
                "council_analysis": prediction.council_analysis,
                "timestamp": prediction.timestamp.isoformat()
            })
        else:
            return JSONResponse({
                "error": f"Failed to create prediction for {sport.value}",
                "sport": sport.value,
                "teams": [team1, team2]
            }, status_code=500)
        
    except Exception as e:
        return JSONResponse({
            "error": f"Prediction failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def cross_sport_analysis(request: Request):
    """Create analysis across all sports - YOLO MODE!"""
    try:
        body = await request.json()
        team1 = body.get("team1", "default_team1")
        team2 = body.get("team2", "default_team2")
        
        cross_sport_results = await multisports_platform.create_cross_sport_analysis(team1, team2)
        
        return JSONResponse({
            "team1": team1,
            "team2": team2,
            "cross_sport_analysis": cross_sport_results,
            "yolo_mode": "MAXIMUM CONFIDENCE!",
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Cross-sport analysis failed: {str(e)}",
            "yolo_mode": "MAXIMUM CONFIDENCE!"
        }, status_code=500)

async def recent_predictions(request: Request):
    """Get recent predictions from all sports - YOLO MODE!"""
    limit = int(request.query_params.get("limit", 20))
    predictions = await multisports_platform.get_recent_predictions(limit)
    return JSONResponse({
        "predictions": predictions,
        "count": len(predictions),
        "yolo_mode": "MAXIMUM CONFIDENCE!"
    })

async def platform_stats(request: Request):
    """Get platform statistics - YOLO MODE!"""
    return JSONResponse({
        "platform_stats": multisports_platform.platform_stats,
        "yolo_mode": "MAXIMUM CONFIDENCE!",
        "timestamp": datetime.datetime.now().isoformat()
    })

# Create Starlette app
app = Starlette(routes=[
    Route("/", root, methods=["GET"]),
    Route("/health", health, methods=["GET"]),
    Route("/api/v1/status", platform_status, methods=["GET"]),
    Route("/api/v1/sport-status", sport_status, methods=["GET"]),
    Route("/api/v1/teams", all_teams, methods=["GET"]),
    Route("/api/v1/predict", predict, methods=["POST"]),
    Route("/api/v1/cross-sport-analysis", cross_sport_analysis, methods=["POST"]),
    Route("/api/v1/recent-predictions", recent_predictions, methods=["GET"]),
    Route("/api/v1/stats", platform_stats, methods=["GET"])
])

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

def main():
    """Main function to start the multisports betting platform - YOLO MODE!"""
    print("🚀 Starting MultiSports Betting Platform - YOLO MODE!")
    print("=" * 70)
    print(f"Platform: {multisports_platform.platform_name}")
    print(f"Version: {multisports_platform.version}")
    print(f"Sports: {len(SportType)}")
    print("YOLO MODE: MAXIMUM CONFIDENCE!")
    print("=" * 70)
    
    # Display sport systems
    for sport, system in multisports_platform.sport_systems.items():
        print(f"🏈 {sport.value.title()}: {system.name} (Port {system.port})")
    
    print("=" * 70)
    
    host = "0.0.0.0"
    port = 8007  # Main platform port
    
    print(f"Platform Server: {host}:{port}")
    print(f"Health: http://localhost:{port}/health")
    print(f"Status: http://localhost:{port}/api/v1/status")
    print(f"Teams: http://localhost:{port}/api/v1/teams")
    print(f"Predict: http://localhost:{port}/api/v1/predict")
    print(f"Cross-Sport: http://localhost:{port}/api/v1/cross-sport-analysis")
    print("YOLO MODE: MAXIMUM CONFIDENCE!")
    print("=" * 70)
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main() 