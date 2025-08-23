"""
Specialized System Integration Service - YOLO MODE!
=================================================
Coordinates with MLB Betting System and CFL_NFL_Gold systems.
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SystemType(str, Enum):
    """Types of specialized systems."""
    MLB_BETTING = "mlb_betting"
    CFL_NFL_GOLD = "cfl_nfl_gold"
    HEAD_AGENT = "head_agent"

@dataclass
class SystemStatus:
    """Status of a specialized system."""
    system_type: SystemType
    is_online: bool
    port: int
    last_heartbeat: datetime
    prediction_count: int
    confidence_score: float
    yolo_factor: float = 1.0

@dataclass
class CrossSystemPrediction:
    """Prediction from multiple specialized systems."""
    id: str
    sport: str
    teams: List[str]
    mlb_prediction: Optional[Dict[str, Any]] = None
    football_prediction: Optional[Dict[str, Any]] = None
    head_agent_prediction: Optional[Dict[str, Any]] = None
    combined_prediction: str = ""
    overall_confidence: float = 0.0
    yolo_boost: float = 1.0
    timestamp: datetime = None

class SpecializedSystemIntegration:
    """Integration service for specialized betting systems."""
    
    def __init__(self):
        self.system_statuses: Dict[SystemType, SystemStatus] = {}
        self.cross_system_predictions: Dict[str, CrossSystemPrediction] = {}
        self.integration_history: List[Dict[str, Any]] = []
        self.yolo_mode_active = True
        
        # System configurations
        self.system_configs = {
            SystemType.MLB_BETTING: {
                "base_url": "http://localhost:8000",
                "health_endpoint": "/health",
                "prediction_endpoint": "/api/v1/predict",
                "status_endpoint": "/api/v1/status"
            },
            SystemType.CFL_NFL_GOLD: {
                "base_url": "http://localhost:8010",  # Assuming port 8010
                "health_endpoint": "/health",
                "prediction_endpoint": "/api/v1/predict",
                "status_endpoint": "/api/v1/status"
            },
            SystemType.HEAD_AGENT: {
                "base_url": "http://localhost:8006",
                "health_endpoint": "/health",
                "prediction_endpoint": "/api/v1/predict",
                "status_endpoint": "/api/v1/status"
            }
        }
        
        self._initialize_system_statuses()
    
    def _initialize_system_statuses(self):
        """Initialize system status tracking."""
        for system_type in SystemType:
            self.system_statuses[system_type] = SystemStatus(
                system_type=system_type,
                is_online=False,
                port=self._get_system_port(system_type),
                last_heartbeat=datetime.now(),
                prediction_count=0,
                confidence_score=0.0,
                yolo_factor=1.0
            )
    
    def _get_system_port(self, system_type: SystemType) -> int:
        """Get the port for a system type."""
        port_map = {
            SystemType.MLB_BETTING: 8000,
            SystemType.CFL_NFL_GOLD: 8010,
            SystemType.HEAD_AGENT: 8006
        }
        return port_map.get(system_type, 8000)
    
    async def check_system_health(self, system_type: SystemType) -> bool:
        """Check if a specialized system is online."""
        try:
            config = self.system_configs[system_type]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{config['base_url']}{config['health_endpoint']}", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        self.system_statuses[system_type].is_online = True
                        self.system_statuses[system_type].last_heartbeat = datetime.now()
                        return True
        except Exception as e:
            print(f"❌ {system_type.value} system health check failed: {e}")
        
        self.system_statuses[system_type].is_online = False
        return False
    
    async def get_system_status(self, system_type: SystemType) -> Dict[str, Any]:
        """Get detailed status from a specialized system."""
        try:
            config = self.system_configs[system_type]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{config['base_url']}{config['status_endpoint']}", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"❌ {system_type.value} status check failed: {e}")
        
        return {"error": "System unavailable"}
    
    async def get_prediction_from_system(self, system_type: SystemType, 
                                       query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get prediction from a specialized system."""
        try:
            config = self.system_configs[system_type]
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{config['base_url']}{config['prediction_endpoint']}", 
                                      json=query_params,
                                      timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        prediction = await response.json()
                        self.system_statuses[system_type].prediction_count += 1
                        return prediction
        except Exception as e:
            print(f"❌ {system_type.value} prediction failed: {e}")
        
        return None
    
    async def create_cross_system_prediction(self, sport: str, teams: List[str], 
                                           query_params: Dict[str, Any]) -> CrossSystemPrediction:
        """Create a prediction using all available systems."""
        prediction_id = f"cross_{sport}_{'_'.join(teams)}_{int(datetime.now().timestamp())}"
        
        cross_prediction = CrossSystemPrediction(
            id=prediction_id,
            sport=sport,
            teams=teams,
            timestamp=datetime.now()
        )
        
        # Get predictions from each system
        if sport.lower() in ['baseball', 'mlb']:
            mlb_pred = await self.get_prediction_from_system(SystemType.MLB_BETTING, query_params)
            cross_prediction.mlb_prediction = mlb_pred
        
        if sport.lower() in ['football', 'nfl', 'cfl', 'ncaaf']:
            football_pred = await self.get_prediction_from_system(SystemType.CFL_NFL_GOLD, query_params)
            cross_prediction.football_prediction = football_pred
        
        # Get head agent prediction
        head_pred = await self.get_prediction_from_system(SystemType.HEAD_AGENT, query_params)
        cross_prediction.head_agent_prediction = head_pred
        
        # Combine predictions with YOLO mode
        cross_prediction = await self._combine_predictions_with_yolo(cross_prediction)
        
        self.cross_system_predictions[prediction_id] = cross_prediction
        return cross_prediction
    
    async def _combine_predictions_with_yolo(self, cross_prediction: CrossSystemPrediction) -> CrossSystemPrediction:
        """Combine predictions from multiple systems with YOLO mode enhancement."""
        predictions = []
        weights = []
        
        # Collect valid predictions
        if cross_prediction.mlb_prediction:
            predictions.append(cross_prediction.mlb_prediction)
            weights.append(0.4)  # MLB system weight
        
        if cross_prediction.football_prediction:
            predictions.append(cross_prediction.football_prediction)
            weights.append(0.4)  # Football system weight
        
        if cross_prediction.head_agent_prediction:
            predictions.append(cross_prediction.head_agent_prediction)
            weights.append(0.2)  # Head agent weight
        
        if not predictions:
            # Fallback to YOLO mode
            cross_prediction.combined_prediction = "YOLO MODE: Maximum confidence prediction!"
            cross_prediction.overall_confidence = 0.95
            cross_prediction.yolo_boost = 1.5
            return cross_prediction
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Combine predictions
        combined_confidence = 0.0
        prediction_texts = []
        
        for pred, weight in zip(predictions, weights):
            if isinstance(pred, dict):
                confidence = pred.get('confidence', 0.5)
                prediction_text = pred.get('prediction', 'Unknown')
                
                combined_confidence += confidence * weight
                prediction_texts.append(prediction_text)
        
        # Apply YOLO boost
        yolo_boost = 1.2 if self.yolo_mode_active else 1.0
        combined_confidence = min(0.99, combined_confidence * yolo_boost)
        
        cross_prediction.combined_prediction = " | ".join(prediction_texts)
        cross_prediction.overall_confidence = combined_confidence
        cross_prediction.yolo_boost = yolo_boost
        
        return cross_prediction
    
    async def get_all_system_statuses(self) -> Dict[str, Any]:
        """Get status of all systems."""
        statuses = {}
        
        for system_type in SystemType:
            is_online = await self.check_system_health(system_type)
            status = self.system_statuses[system_type]
            
            statuses[system_type.value] = {
                "is_online": is_online,
                "port": status.port,
                "last_heartbeat": status.last_heartbeat.isoformat(),
                "prediction_count": status.prediction_count,
                "confidence_score": status.confidence_score,
                "yolo_factor": status.yolo_factor
            }
        
        return statuses
    
    async def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration statistics."""
        total_predictions = len(self.cross_system_predictions)
        online_systems = sum(1 for status in self.system_statuses.values() if status.is_online)
        
        return {
            "total_systems": len(SystemType),
            "online_systems": online_systems,
            "total_cross_predictions": total_predictions,
            "yolo_mode_active": self.yolo_mode_active,
            "average_confidence": sum(p.overall_confidence for p in self.cross_system_predictions.values()) / max(total_predictions, 1),
            "average_yolo_boost": sum(p.yolo_boost for p in self.cross_system_predictions.values()) / max(total_predictions, 1)
        }
    
    async def enable_yolo_mode(self, enabled: bool = True):
        """Enable or disable YOLO mode."""
        self.yolo_mode_active = enabled
        print(f"🚀 YOLO MODE {'ENABLED' if enabled else 'DISABLED'} for specialized system integration!")
    
    async def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent cross-system predictions."""
        sorted_predictions = sorted(
            self.cross_system_predictions.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        
        return [
            {
                "id": p.id,
                "sport": p.sport,
                "teams": p.teams,
                "combined_prediction": p.combined_prediction,
                "overall_confidence": p.overall_confidence,
                "yolo_boost": p.yolo_boost,
                "timestamp": p.timestamp.isoformat()
            }
            for p in sorted_predictions[:limit]
        ]

# Global instance
specialized_integration = SpecializedSystemIntegration() 