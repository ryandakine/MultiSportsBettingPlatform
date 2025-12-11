"""
Agent Registry Service
=====================
Manages distributed sub-agent registration and discovery across multiple HeadAgent instances.
Enables horizontal scaling by externalizing agent state to Redis.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    sport: str
    instance_id: str
    agent_id: str
    registered_at: str
    last_heartbeat: str
    status: str = "healthy"  # healthy, unhealthy, stale
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AgentRegistry:
    """
    Distributed agent registry using Redis as backend.
    
    Supports:
    - Multi-instance agent registration
    - Agent discovery and load balancing
    - Automatic stale agent cleanup
    - Health monitoring
    """
    
    # Redis key patterns
    AGENTS_SET_KEY = "agents:{sport}"  # Set of agent_ids for a sport
    AGENT_INFO_KEY = "agent:{agent_id}"  # Hash of agent metadata
    INSTANCE_AGENTS_KEY = "instance:{instance_id}:agents"  # Set of agent_ids for an instance
    
    HEARTBEAT_INTERVAL = 30  # seconds
    STALE_THRESHOLD = 120  # seconds - consider agent stale if no heartbeat
    
    def __init__(self, redis_url: str = None):
        """Initialize the agent registry."""
        from src.config import settings
        self.redis_url = redis_url or settings.redis_url
        self.redis_client = None
        logger.info("✅ AgentRegistry initialized")
    
    async def _get_redis(self):
        """Lazy-initialize async Redis connection."""
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("✅ AgentRegistry: Redis connection established")
            except Exception as e:
                logger.error(f"❌ AgentRegistry: Redis connection failed: {e}")
                self.redis_client = False
        return self.redis_client if self.redis_client is not False else None
    
    async def register_agent(
        self,
        sport: str,
        instance_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Register a new agent.
        
        Args:
            sport: Sport type (e.g., "baseball", "basketball")
            instance_id: Unique identifier for the HeadAgent instance
            metadata: Optional metadata about the agent
        
        Returns:
            Agent ID if successful, None otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            logger.warning("⚠️ Cannot register agent: Redis not available")
            return None
        
        try:
            # Generate unique agent ID
            agent_id = f"{instance_id}:{sport}:{uuid.uuid4().hex[:8]}"
            
            # Create agent info
            now = datetime.utcnow().isoformat()
            agent_info = AgentInfo(
                sport=sport,
                instance_id=instance_id,
                agent_id=agent_id,
                registered_at=now,
                last_heartbeat=now,
                status="healthy",
                metadata=metadata or {}
            )
            
            # Store agent info
            agent_key = self.AGENT_INFO_KEY.format(agent_id=agent_id)
            await redis_client.hset(agent_key, mapping=self._serialize_agent_info(agent_info))
            await redis_client.expire(agent_key, self.STALE_THRESHOLD * 2)  # Auto-cleanup
            
            # Add to sport's agent set
            agents_set_key = self.AGENTS_SET_KEY.format(sport=sport)
            await redis_client.sadd(agents_set_key, agent_id)
            
            # Add to instance's agent set
            instance_key = self.INSTANCE_AGENTS_KEY.format(instance_id=instance_id)
            await redis_client.sadd(instance_key, agent_id)
            await redis_client.expire(instance_key, self.STALE_THRESHOLD * 2)
            
            logger.info(f"✅ Agent registered: {agent_id} (sport={sport}, instance={instance_id})")
            return agent_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register agent: {e}")
            return None
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            True if successful, False otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            return False
        
        try:
            # Get agent info
            agent_info = await self.get_agent_info(agent_id)
            if not agent_info:
                return False
            
            # Remove from sport's agent set
            agents_set_key = self.AGENTS_SET_KEY.format(sport=agent_info.sport)
            await redis_client.srem(agents_set_key, agent_id)
            
            # Remove from instance's agent set
            instance_key = self.INSTANCE_AGENTS_KEY.format(instance_id=agent_info.instance_id)
            await redis_client.srem(instance_key, agent_id)
            
            # Delete agent info
            agent_key = self.AGENT_INFO_KEY.format(agent_id=agent_id)
            await redis_client.delete(agent_key)
            
            logger.info(f"✅ Agent unregistered: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister agent: {e}")
            return False
    
    async def get_agent(self, sport: str) -> Optional[AgentInfo]:
        """
        Get a healthy agent for a sport (round-robin).
        
        Args:
            sport: Sport type
        
        Returns:
            AgentInfo if available, None otherwise
        """
        agents = await self.get_all_agents(sport)
        
        # Filter for healthy agents
        healthy_agents = [a for a in agents if a.status == "healthy"]
        
        if not healthy_agents:
            return None
        
        # Simple round-robin: return first (could enhance with true round-robin later)
        return healthy_agents[0]
    
    async def get_all_agents(self, sport: str) -> List[AgentInfo]:
        """
        Get all agents for a sport, with health status updated.
        
        Args:
            sport: Sport type
        
        Returns:
            List of AgentInfo objects
        """
        redis_client = await self._get_redis()
        if not redis_client:
            return []
        
        try:
            # Get all agent IDs for this sport
            agents_set_key = self.AGENTS_SET_KEY.format(sport=sport)
            agent_ids = await redis_client.smembers(agents_set_key)
            
            agents = []
            for agent_id in agent_ids:
                agent_info = await self.get_agent_info(agent_id)
                if agent_info:
                    agents.append(agent_info)
            
            return agents
            
        except Exception as e:
            logger.error(f"❌ Failed to get agents for {sport}: {e}")
            return []
    
    async def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent."""
        redis_client = await self._get_redis()
        if not redis_client:
            return None
        
        try:
            agent_key = self.AGENT_INFO_KEY.format(agent_id=agent_id)
            agent_data = await redis_client.hgetall(agent_key)
            
            if not agent_data:
                return None
            
            # Deserialize and update health status
            agent_info = self._deserialize_agent_info(agent_data)
            agent_info = self._update_agent_health(agent_info)
            
            return agent_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get agent info for {agent_id}: {e}")
            return None
    
    async def heartbeat(self, agent_id: str) -> bool:
        """
        Update agent's last heartbeat timestamp.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            True if successful, False otherwise
        """
        redis_client = await self._get_redis()
        if not redis_client:
            return False
        
        try:
            agent_key = self.AGENT_INFO_KEY.format(agent_id=agent_id)
            now = datetime.utcnow().isoformat()
            await redis_client.hset(agent_key, "last_heartbeat", now)
            await redis_client.hset(agent_key, "status", "healthy")
            
            # Refresh TTL
            await redis_client.expire(agent_key, self.STALE_THRESHOLD * 2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update heartbeat for {agent_id}: {e}")
            return False
    
    async def cleanup_stale_agents(self) -> int:
        """
        Remove agents that haven't sent heartbeat within STALE_THRESHOLD.
        
        Returns:
            Number of agents cleaned up
        """
        redis_client = await self._get_redis()
        if not redis_client:
            return 0
        
        try:
            cleaned = 0
            
            # Scan all agent info keys
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(
                    cursor, 
                    match="agent:*",
                    count=100
                )
                
                for agent_key in keys:
                    agent_data = await redis_client.hgetall(agent_key)
                    if not agent_data:
                        continue
                    
                    agent_info = self._deserialize_agent_info(agent_data)
                    agent_info = self._update_agent_health(agent_info)
                    
                    if agent_info.status == "stale":
                        await self.unregister_agent(agent_info.agent_id)
                        cleaned += 1
                
                if cursor == 0:
                    break
            
            if cleaned > 0:
                logger.info(f"🧹 Cleaned up {cleaned} stale agents")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup stale agents: {e}")
            return 0
    
    def _serialize_agent_info(self, agent_info: AgentInfo) -> Dict[str, str]:
        """Serialize AgentInfo to Redis hash."""
        data = asdict(agent_info)
        data['metadata'] = json.dumps(data.get('metadata', {}))
        return data
    
    def _deserialize_agent_info(self, data: Dict[str, str]) -> AgentInfo:
        """Deserialize Redis hash to AgentInfo."""
        data = dict(data)  # Copy to avoid mutation
        data['metadata'] = json.loads(data.get('metadata', '{}'))
        return AgentInfo(**data)
    
    def _update_agent_health(self, agent_info: AgentInfo) -> AgentInfo:
        """Update agent health status based on last heartbeat."""
        try:
            last_heartbeat = datetime.fromisoformat(agent_info.last_heartbeat)
            age = (datetime.utcnow() - last_heartbeat).total_seconds()
            
            if age > self.STALE_THRESHOLD:
                agent_info.status = "stale"
            elif age > self.HEARTBEAT_INTERVAL * 2:
                agent_info.status = "unhealthy"
            else:
                agent_info.status = "healthy"
                
        except Exception:
            agent_info.status = "unknown"
        
        return agent_info


# Global instance
agent_registry = AgentRegistry()
