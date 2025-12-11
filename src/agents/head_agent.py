#!/usr/bin/env python3
"""
Head Agent for MultiSportsBettingPlatform
=========================================
Central coordinator that manages user interactions, aggregates picks from sub-agents,
and handles global learning across all sports.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Protocol, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from src.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import AsyncSessionLocal
from sqlalchemy import select, func
from src.db.models.prediction import Prediction as PredictionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportType(Enum):
    """Supported sports."""
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    HOCKEY = "hockey"

class PredictionConfidence(Enum):
    """Prediction confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Prediction:
    """Prediction data structure."""
    sport: SportType
    prediction: str
    confidence: PredictionConfidence
    reasoning: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class UserQuery:
    """User query data structure."""
    user_id: str
    sports: List[SportType]
    query_text: str
    preferences: Dict[str, Any]
    timestamp: datetime

class SubAgentInterface(Protocol):
    """Protocol for sub-agent interface."""
    
    async def get_prediction(self, query_params: dict) -> Prediction:
        """Get prediction from sub-agent."""
        ...
    
    async def report_outcome(self, prediction_id: str, outcome: bool) -> None:
        """Report prediction outcome for learning."""
        ...
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get sub-agent health status."""
        ...

class HeadAgent:
    """Head Agent - Central coordinator for multi-sport betting predictions.
    
    Sub-agent registration is persisted to Redis to support horizontal scaling.
    Local instance keeps references to agent objects for actual communication.
    """
    
    # Redis key for sub-agent registry
    REDIS_AGENT_KEY = "head_agent:sub_agents"
    
    def __init__(self, redis_client=None):
        # Local agent instances (for fast access within this process)
        # These are actual agent object references
        self._local_agent_refs: Dict[SportType, SubAgentInterface] = {}
        
        # Agent IDs for agents registered by this instance
        self._local_agent_ids: Dict[SportType, str] = {}
        
        self.global_model = None
        
        # Initialize services for state management
        from src.services.auth_service import AuthService
        from src.services.user_preferences import UserPreferencesService
        from src.services.feature_flags import feature_flags
        from src.services.agent_registry import agent_registry
        from src.config import settings
        
        self.auth_service = AuthService()
        self.preferences_service = UserPreferencesService()
        self.feature_flags = feature_flags
        self.agent_registry = agent_registry
        
        # Generate unique instance ID
        import socket
        self.instance_id = f"{socket.gethostname()}:{id(self)}"
        
        # Redis client for shared state (optional - graceful degradation)
        self._redis_client = redis_client
        self._redis_url = settings.redis_url
        
        logger.info(f"Head Agent initialized (instance={self.instance_id})")
        
        # Start heartbeat loop
        self._heartbeat_task = None
        self._heartbeat_running = False
    
    async def _get_redis(self):
        """Lazy-initialize Redis connection."""
        if self._redis_client is None:
            try:
                import redis.asyncio as aioredis
                self._redis_client = await aioredis.from_url(
                    self._redis_url, 
                    decode_responses=True
                )
            except Exception as e:
                logger.warning(f"Redis connection failed (agent state will be local only): {e}")
        return self._redis_client
    
    @property
    def sub_agents(self) -> Dict[SportType, SubAgentInterface]:
        """Return local agent instances (backward compatibility).
        
        Note: This only returns agents registered on THIS instance.
        For distributed queries, use agent_registry.get_all_agents()
        """
        return self._local_agent_refs
    
    async def register_sub_agent(self, sport: SportType, agent: SubAgentInterface) -> None:
        """Register a sub-agent for a specific sport.
        
        Registers the agent both locally (for fast access) and in the
        distributed registry (for multi-instance coordination).
        """
        # Store local reference for fast access
        self._local_agent_refs[sport] = agent
        
        # Register in distributed registry
        agent_id = await self.agent_registry.register_agent(
            sport=sport.value,
            instance_id=self.instance_id,
            metadata={
                "agent_type": type(agent).__name__,
                "capabilities": getattr(agent, 'capabilities', [])
            }
        )
        
        if agent_id:
            self._local_agent_ids[sport] = agent_id
            logger.info(f"✅ Registered sub-agent for {sport.value} (agent_id={agent_id})")
            
            # Start heartbeat loop if not already running
            if not self._heartbeat_running:
                await self._start_heartbeat_loop()
        else:
            logger.warning(f"⚠️ Failed to register {sport.value} in distributed registry (local only)")
    
    async def unregister_sub_agent(self, sport: SportType) -> None:
        """Unregister a sub-agent."""
        # Remove local reference
        if sport in self._local_agent_refs:
            del self._local_agent_refs[sport]
        
        # Unregister from distributed registry
        if sport in self._local_agent_ids:
            agent_id = self._local_agent_ids[sport]
            await self.agent_registry.unregister_agent(agent_id)
            del self._local_agent_ids[sport]
            logger.info(f"✅ Unregistered sub-agent for {sport.value}")
        
        # Stop heartbeat if no more agents
        if not self._local_agent_ids and self._heartbeat_running:
            await self._stop_heartbeat_loop()
    
    async def get_available_sports(self) -> List[SportType]:
        """Get all available sports across all instances."""
        # Get sports from local instance
        local_sports = set(self._local_agent_refs.keys())
        
        # Get sports from distributed registry
        try:
            redis_client = await self._get_redis()
            if redis_client:
                # Scan for all agent registrations
                all_sports = set()
                cursor = 0
                while True:
                    cursor, keys = await redis_client.scan(
                        cursor,
                        match="agents:*",
                        count=100
                    )
                    for key in keys:
                        # Extract sport from key pattern "agents:{sport}"
                        sport_name = key.replace("agents:", "")
                        try:
                            sport = SportType(sport_name)
                            all_sports.add(sport)
                        except ValueError:
                            pass
                    
                    if cursor == 0:
                        break
                
                return list(local_sports | all_sports)
        except Exception as e:
            logger.warning(f"Failed to get sports from registry: {e}")
        
        # Fallback to local only
        return list(local_sports)
    
    async def aggregate_predictions(self, user_query: UserQuery) -> Dict[str, Any]:
        """Aggregate predictions from relevant sub-agents."""
        logger.info(f"Aggregating predictions for user {user_query.user_id}")
        
        predictions = {}
        relevant_sports = []
        
        # Determine which sports are relevant to the query
        for sport in user_query.sports:
            if sport in self.sub_agents:
                relevant_sports.append(sport)
            else:
                logger.warning(f"No sub-agent available for {sport.value}")
        
        if not relevant_sports:
            return {
                "error": "No relevant sub-agents available",
                "available_sports": await self.get_available_sports()
            }
        
        # Collect predictions from relevant sub-agents
        for sport in relevant_sports:
            try:
                # First try local agent (fast path)
                if sport in self._local_agent_refs:
                    agent = self._local_agent_refs[sport]
                    
                    # Check agent health
                    health = await agent.get_health_status()
                    if not health.get("healthy", False):
                        logger.warning(f"Sub-agent for {sport.value} is unhealthy: {health}")
                        continue
                    
                    # Get prediction from local agent
                    query_params = {
                        "user_id": user_query.user_id,
                        "query_text": user_query.query_text,
                        "preferences": user_query.preferences,
                        "timestamp": user_query.timestamp.isoformat()
                    }
                    
                    prediction = await agent.get_prediction(query_params)
                    predictions[sport.value] = prediction
                else:
                    # Try to get agent from registry (remote instance)
                    agent_info = await self.agent_registry.get_agent(sport.value)
                    if not agent_info:
                        logger.warning(f"No agent available for {sport.value}")
                        continue
                    
                    # Invoke remote agent via HTTP
                    prediction = await self._invoke_remote_agent(
                        agent_info,
                        user_query
                    )
                    
                    if prediction:
                        predictions[sport.value] = prediction
                    else:
                        logger.warning(f"Remote agent invocation failed for {sport.value}")
                        continue
                
                # Store in database
                async with AsyncSessionLocal() as db:
                    try:
                        db_prediction = PredictionModel(
                            id=f"pred_{sport.value}_{uuid.uuid4()}", # Unique ID
                            user_id=user_query.user_id,
                            sport=sport.value,
                            prediction_text=prediction.prediction,
                            confidence=prediction.confidence.value,
                            reasoning=prediction.reasoning,
                            timestamp=datetime.utcnow(),
                            metadata_json=prediction.metadata
                        )
                        db.add(db_prediction)
                        await db.commit()
                    except Exception as db_err:
                        logger.error(f"Failed to save prediction to DB: {db_err}")
                        await db.rollback()
                
            except Exception as e:
                logger.error(f"Error getting prediction from {sport.value} agent: {e}")
                predictions[sport.value] = {
                    "error": f"Failed to get prediction: {str(e)}"
                }
        
        # Combine predictions using weighting algorithm
        combined_prediction = await self._combine_predictions(predictions, user_query)
        
        return {
            "user_id": user_query.user_id,
            "query": user_query.query_text,
            "predictions": predictions,
            "combined_prediction": combined_prediction,
            "timestamp": datetime.now().isoformat(),
            "sports_analyzed": [s.value for s in relevant_sports]
        }
    
    async def _combine_predictions(self, predictions: Dict[str, Any], user_query: UserQuery) -> Dict[str, Any]:
        """Combine predictions using intelligent weighting."""
        if not predictions:
            return {"error": "No predictions to combine"}
        
        # Simple weighting based on confidence levels
        confidence_weights = {
            PredictionConfidence.HIGH: 0.5,
            PredictionConfidence.MEDIUM: 0.3,
            PredictionConfidence.LOW: 0.2
        }
        
        weighted_predictions = []
        total_weight = 0
        
        for sport, prediction in predictions.items():
            if isinstance(prediction, Prediction):
                weight = confidence_weights.get(prediction.confidence, 0.2)
                weighted_predictions.append({
                    "sport": sport,
                    "prediction": prediction.prediction,
                    "confidence": prediction.confidence.value,
                    "weight": weight,
                    "reasoning": prediction.reasoning
                })
                total_weight += weight
        
        if not weighted_predictions:
            return {"error": "No valid predictions to combine"}
        
        # Calculate weighted average (simplified)
        combined_reasoning = " | ".join([wp["reasoning"] for wp in weighted_predictions])
        
        return {
            "recommendation": "Combined prediction based on multiple sports",
            "confidence": "medium",  # Could be calculated based on individual confidences
            "reasoning": combined_reasoning,
            "sports_contributing": len(weighted_predictions),
            "total_weight": total_weight,
            "individual_predictions": weighted_predictions
        }
    
    async def report_outcome(self, prediction_id: str, outcome: bool, user_id: str) -> None:
        """Report prediction outcome for learning."""
        logger.info(f"Reporting outcome for prediction {prediction_id}: {outcome}")
        
        # Update prediction in DB
        async with AsyncSessionLocal() as db:
            try:
                query = select(PredictionModel).where(PredictionModel.id == prediction_id)
                result = await db.execute(query)
                prediction = result.scalar_one_or_none()
                
                if prediction:
                    prediction.outcome = outcome
                    prediction.outcome_reported_at = datetime.utcnow()
                    await db.commit()
                    
                    # Report to relevant sub-agent
                    sport_enum = None
                    try:
                        sport_enum = SportType(prediction.sport)
                    except ValueError:
                        pass
                        
                    if sport_enum and sport_enum in self.sub_agents:
                        try:
                            await self.sub_agents[sport_enum].report_outcome(prediction_id, outcome)
                        except Exception as e:
                            logger.error(f"Error reporting outcome to {sport_enum.value} agent: {e}")
                else:
                    logger.warning(f"Prediction {prediction_id} not found in DB for outcome reporting")
            except Exception as e:
                logger.error(f"Error updating outcome: {e}")
                await db.rollback()
        
        # Update global learning model (placeholder)
        await self._update_global_model(prediction_id, outcome, user_id)
    
    async def _update_global_model(self, prediction_id: str, outcome: bool, user_id: str) -> None:
        """Update global learning model (placeholder for future implementation)."""
        # TODO: Implement global learning across sports
        logger.info(f"Global model update: prediction {prediction_id} outcome {outcome}")
    
    async def start_autonomous_loop(self) -> None:
        """Start the autonomous operation loop."""
        logger.info("🚀 Starting Head Agent Autonomous Loop")
        asyncio.create_task(self._run_autonomous_loop())
    
    async def _run_autonomous_loop(self) -> None:
        """Main autonomous loop."""
        while True:
            try:
                # Check if autonomous scanning is enabled
                if await self.feature_flags.is_enabled("autonomous_scanning"):
                    logger.info("🤖 Head Agent: Scanning for betting opportunities...")
                    await self.scan_market()
                else:
                    logger.debug("⏸️ Autonomous scanning disabled via feature flag")
            except Exception as e:
                logger.error(f"❌ Error in autonomous loop: {e}")
            
            # Sleep for a bit (e.g., 60 seconds)
            await asyncio.sleep(60)
    
    async def _start_heartbeat_loop(self) -> None:
        """Start the background heartbeat task."""
        if self._heartbeat_running:
            return
        
        self._heartbeat_running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("💓 Heartbeat loop started")
    
    async def _stop_heartbeat_loop(self) -> None:
        """Stop the background heartbeat task."""
        if not self._heartbeat_running:
            return
        
        self._heartbeat_running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info("💔 Heartbeat loop stopped")
    
    async def _heartbeat_loop(self) -> None:
        """Background task to send heartbeats for all registered agents."""
        while self._heartbeat_running:
            try:
                # Send heartbeat for each registered agent
                for sport, agent_id in list(self._local_agent_ids.items()):
                    try:
                        success = await self.agent_registry.heartbeat(agent_id)
                        if not success:
                            logger.warning(f"⚠️ Failed to send heartbeat for {sport.value}")
                    except Exception as e:
                        logger.error(f"❌ Heartbeat error for {sport.value}: {e}")
                
                # Sleep for heartbeat interval (30 seconds)
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Heartbeat loop error: {e}")
                await asyncio.sleep(30)  # Continue despite errors

    async def scan_market(self) -> None:
        """Scan active sub-agents for betting opportunities."""
        for sport, agent in self.sub_agents.items():
            try:
                # Find opportunities
                opportunities = await agent.find_betting_opportunities()
                
                if opportunities:
                    logger.info(f"🔎 Found {len(opportunities)} opportunities for {sport.value}")
                    
                    for opp in opportunities:
                        # Generate prediction automatically
                        user_query = UserQuery(
                            user_id="autonomous_agent",
                            sports=[sport],
                            query_text=opp.get("query_text", ""),
                            preferences={"autonomous": True},
                            timestamp=datetime.now()
                        )
                        
                        # Use existing aggregation logic to generate and store prediction
                        result = await self.aggregate_predictions(user_query)
                        
                        # Broadcast if a prediction was made
                        if "combined_prediction" in result and "error" not in result:
                            # Here we would broadcast to websocket users
                            # For now, just log it
                            logger.info(f"📢 Autonomous Prediction Generated: {result['combined_prediction'].get('recommendation')}")
                            
            except Exception as e:
                logger.error(f"Error scanning market for {sport.value}: {e}")
    
    async def get_user_session(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user session information."""
        return await self.auth_service.get_user_sessions(user_id)
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        # This simplifies to updating betting preferences for now, but could be more granular
        self.preferences_service.update_betting_preferences(user_id, preferences)
        logger.info(f"Updated preferences for user {user_id}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = {}
        
        for sport, agent in self.sub_agents.items():
            try:
                health = await agent.get_health_status()
                agent_statuses[sport.value] = health
            except Exception as e:
                agent_statuses[sport.value] = {"error": str(e)}
        
        # Get active sessions count from Redis
        try:
            stats = await self.auth_service.get_stats()
            active_sessions = stats.get("active_sessions", 0)
        except Exception:
            active_sessions = 0
        
        return {
            "status": "operational",
            "active_sports": len(self.sub_agents),
            "active_sessions": active_sessions,
            "prediction_history_count": await self._get_prediction_count(),
            "agent_statuses": agent_statuses,
            "timestamp": datetime.now().isoformat()
        }

    async def get_prediction_history(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get paginated prediction history for a user."""
        async with AsyncSessionLocal() as db:
            try:
                query = (
                    select(PredictionModel)
                    .where(PredictionModel.user_id == user_id)
                    .order_by(PredictionModel.timestamp.desc())
                    .limit(limit)
                    .offset(offset)
                )
                result = await db.execute(query)
                predictions = result.scalars().all()
                
                return [
                    {
                        "id": p.id,
                        "sport": p.sport,
                        "prediction": p.prediction_text,
                        "confidence": p.confidence,
                        "reasoning": p.reasoning,
                        "timestamp": p.timestamp.isoformat(),
                        "outcome": p.outcome,
                        "metadata": p.metadata_json
                    }
                    for p in predictions
                ]
            except Exception as e:
                logger.error(f"Failed to get prediction history: {e}")
                return []

    async def _get_prediction_count(self) -> int:
        """Get total number of predictions from DB."""
        async with AsyncSessionLocal() as db:
            try:
                query = select(func.count()).select_from(PredictionModel)
                result = await db.execute(query)
                return result.scalar()
            except Exception:
                return 0 