"""
Unit Tests for AgentRegistry
============================
Tests distributed agent registration, discovery, health monitoring, and cleanup.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from src.services.agent_registry import AgentRegistry, AgentInfo


@pytest_asyncio.fixture
async def registry():
    """Provide a test AgentRegistry instance."""
    registry = AgentRegistry()
    yield registry
    
    # Cleanup
    redis_client = await registry._get_redis()
    if redis_client:
        # Clean up test data
        await redis_client.flushdb()


@pytest_asyncio.fixture
async def clean_redis(registry):
    """Clean Redis before each test."""
    redis_client = await registry._get_redis()
    if redis_client:
        await redis_client.flushdb()
    yield
    # Cleanup after
    if redis_client:
        await redis_client.flushdb()


@pytest.mark.asyncio
class TestAgentRegistration:
    """Test agent registration functionality."""
    
    async def test_register_agent_success(self, registry, clean_redis):
        """Test successful agent registration."""
        agent_id = await registry.register_agent(
            sport="baseball",
            instance_id="test_instance_1",
            metadata={"version": "1.0"}
        )
        
        assert agent_id is not None
        assert "test_instance_1" in agent_id
        assert "baseball" in agent_id
    
    async def test_register_multiple_agents(self, registry, clean_redis):
        """Test registering multiple agents for same sport."""
        agent1 = await registry.register_agent(
            sport="baseball",
            instance_id="instance_1"
        )
        agent2 = await registry.register_agent(
            sport="baseball",
            instance_id="instance_2"
        )
        
        assert agent1 != agent2
        
        agents = await registry.get_all_agents("baseball")
        assert len(agents) == 2
    
    async def test_register_different_sports(self, registry, clean_redis):
        """Test registering agents for different sports."""
        baseball_agent = await registry.register_agent(
            sport="baseball",
            instance_id="instance_1"
        )
        basketball_agent = await registry.register_agent(
            sport="basketball",
            instance_id="instance_1"
        )
        
        baseball_agents = await registry.get_all_agents("baseball")
        basketball_agents = await registry.get_all_agents("basketball")
        
        assert len(baseball_agents) == 1
        assert len(basketball_agents) == 1
        assert baseball_agents[0].sport == "baseball"
        assert basketball_agents[0].sport == "basketball"


@pytest.mark.asyncio
class TestAgentDiscovery:
    """Test agent discovery functionality."""
    
    async def test_get_agent_single(self, registry, clean_redis):
        """Test getting a single agent."""
        agent_id = await registry.register_agent(
            sport="baseball",
            instance_id="test_instance"
        )
        
        agent_info = await registry.get_agent("baseball")
        assert agent_info is not None
        assert agent_info.sport == "baseball"
        assert agent_info.status == "healthy"
    
    async def test_get_agent_no_agents(self, registry, clean_redis):
        """Test getting agent when none exist."""
        agent_info = await registry.get_agent("baseball")
        assert agent_info is None
    
    async def test_get_all_agents(self, registry, clean_redis):
        """Test getting all agents for a sport."""
        await registry.register_agent("baseball", "instance_1")
        await registry.register_agent("baseball", "instance_2")
        await registry.register_agent("baseball", "instance_3")
        
        agents = await registry.get_all_agents("baseball")
        assert len(agents) == 3
        assert all(a.sport == "baseball" for a in agents)
    
    async def test_get_agent_info(self, registry, clean_redis):
        """Test getting specific agent information."""
        agent_id = await registry.register_agent(
            sport="baseball",
            instance_id="test_instance",
            metadata={"model": "transformer-v2"}
        )
        
        agent_info = await registry.get_agent_info(agent_id)
        assert agent_info is not None
        assert agent_info.agent_id == agent_id
        assert agent_info.metadata["model"] == "transformer-v2"


@pytest.mark.asyncio
class TestAgentUnregistration:
    """Test agent unregistration functionality."""
    
    async def test_unregister_agent_success(self, registry, clean_redis):
        """Test successful agent unregistration."""
        agent_id = await registry.register_agent("baseball", "instance_1")
        
        success = await registry.unregister_agent(agent_id)
        assert success is True
        
        # Verify agent is removed
        agent_info = await registry.get_agent_info(agent_id)
        assert agent_info is None
    
    async def test_unregister_nonexistent_agent(self, registry, clean_redis):
        """Test unregistering non-existent agent."""
        success = await registry.unregister_agent("fake_agent_id")
        assert success is False
    
    async def test_unregister_removes_from_sport_set(self, registry, clean_redis):
        """Test that unregistration removes agent from sport set."""
        agent1 = await registry.register_agent("baseball", "instance_1")
        agent2 = await registry.register_agent("baseball", "instance_2")
        
        await registry.unregister_agent(agent1)
        
        agents = await registry.get_all_agents("baseball")
        assert len(agents) == 1
        assert agents[0].agent_id == agent2


@pytest.mark.asyncio
class TestAgentHealthMonitoring:
    """Test agent health monitoring functionality."""
    
    async def test_heartbeat_updates_timestamp(self, registry, clean_redis):
        """Test that heartbeat updates last_heartbeat timestamp."""
        agent_id = await registry.register_agent("baseball", "instance_1")
        
        # Get initial heartbeat
        agent_info1 = await registry.get_agent_info(agent_id)
        initial_heartbeat = agent_info1.last_heartbeat
        
        # Wait a bit and send heartbeat
        import asyncio
        await asyncio.sleep(0.1)
        await registry.heartbeat(agent_id)
        
        # Get updated heartbeat
        agent_info2 = await registry.get_agent_info(agent_id)
        updated_heartbeat = agent_info2.last_heartbeat
        
        assert updated_heartbeat > initial_heartbeat
    
    async def test_healthy_agent_status(self, registry, clean_redis):
        """Test that recently active agents are marked healthy."""
        agent_id = await registry.register_agent("baseball", "instance_1")
        await registry.heartbeat(agent_id)
        
        agent_info = await registry.get_agent_info(agent_id)
        assert agent_info.status == "healthy"
    
    async def test_stale_agent_detection(self, registry, clean_redis):
        """Test that stale agents are properly detected."""
        agent_id = await registry.register_agent("baseball", "instance_1")
        
        # Manually set old heartbeat
        redis_client = await registry._get_redis()
        old_time = (datetime.utcnow() - timedelta(seconds=200)).isoformat()
        agent_key = registry.AGENT_INFO_KEY.format(agent_id=agent_id)
        await redis_client.hset(agent_key, "last_heartbeat", old_time)
        
        agent_info = await registry.get_agent_info(agent_id)
        assert agent_info.status == "stale"
    
    async def test_get_agent_filters_stale(self, registry, clean_redis):
        """Test that get_agent returns only healthy agents."""
        # Register two agents
        agent1 = await registry.register_agent("baseball", "instance_1")
        agent2 = await registry.register_agent("baseball", "instance_2")
        
        # Make agent1 stale
        redis_client = await registry._get_redis()
        old_time = (datetime.utcnow() - timedelta(seconds=200)).isoformat()
        agent_key = registry.AGENT_INFO_KEY.format(agent_id=agent1)
        await redis_client.hset(agent_key, "last_heartbeat", old_time)
        
        # Should return agent2 (healthy)
        agent_info = await registry.get_agent("baseball")
        assert agent_info is not None
        assert agent_info.agent_id == agent2


@pytest.mark.asyncio
class TestStaleAgentCleanup:
    """Test automatic stale agent cleanup."""
    
    async def test_cleanup_removes_stale_agents(self, registry, clean_redis):
        """Test that cleanup removes stale agents."""
        # Register agents
        agent1 = await registry.register_agent("baseball", "instance_1")
        agent2 = await registry.register_agent("baseball", "instance_2")
        
        # Make agent1 stale
        redis_client = await registry._get_redis()
        old_time = (datetime.utcnow() - timedelta(seconds=200)).isoformat()
        agent_key = registry.AGENT_INFO_KEY.format(agent_id=agent1)
        await redis_client.hset(agent_key, "last_heartbeat", old_time)
        
        # Run cleanup
        cleaned = await registry.cleanup_stale_agents()
        assert cleaned == 1
        
        # Verify agent1 removed, agent2 remains
        all_agents = await registry.get_all_agents("baseball")
        assert len(all_agents) == 1
        assert all_agents[0].agent_id == agent2
    
    async def test_cleanup_no_stale_agents(self, registry, clean_redis):
        """Test cleanup when no stale agents exist."""
        await registry.register_agent("baseball", "instance_1")
        await registry.register_agent("baseball", "instance_2")
        
        cleaned = await registry.cleanup_stale_agents()
        assert cleaned == 0
        
        all_agents = await registry.get_all_agents("baseball")
        assert len(all_agents) == 2


@pytest.mark.asyncio
class TestRedisFailure:
    """Test graceful degradation when Redis is unavailable."""
    
    async def test_register_agent_redis_unavailable(self):
        """Test registration fails gracefully without Redis."""
        registry = AgentRegistry(redis_url="redis://invalid:9999")
        agent_id = await registry.register_agent("baseball", "instance_1")
        assert agent_id is None
    
    async def test_get_agent_redis_unavailable(self):
        """Test getting agent fails gracefully without Redis."""
        registry = AgentRegistry(redis_url="redis://invalid:9999")
        agent_info = await registry.get_agent("baseball")
        assert agent_info is None
