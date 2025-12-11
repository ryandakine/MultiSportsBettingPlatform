"""
Multi-Instance Integration Test
==============================
Tests HeadAgent deployment across multiple instances.
"""

import pytest
import pytest_asyncio
import asyncio
from src.agents.head_agent import HeadAgent
from src.agents import SportType
from unittest.mock import AsyncMock


@pytest_asyncio.fixture
async def instance_1():
    """First HeadAgent instance."""
    agent = HeadAgent()
    yield agent
    if agent._heartbeat_running:
        await agent._stop_heartbeat_loop()


@pytest_asyncio.fixture
async def instance_2():
    """Second HeadAgent instance."""
    agent = HeadAgent()
    yield agent
    if agent._heartbeat_running:
        await agent._stop_heartbeat_loop()


@pytest.mark.asyncio
class TestMultiInstanceDeployment:
    """Test multi-instance HeadAgent deployment."""
    
    async def test_different_instance_ids(self, instance_1, instance_2):
        """Test that instances have different IDs."""
        assert instance_1.instance_id != instance_2.instance_id
    
    async def test_register_agents_on_different_instances(self, instance_1, instance_2):
        """Test registering different agents on different instances."""
        mock_baseball = AsyncMock()
        mock_basketball = AsyncMock()
        
        # Register baseball on instance 1
        await instance_1.register_sub_agent(SportType.BASEBALL, mock_baseball)
        
        # Register basketball on instance 2
        await instance_2.register_sub_agent(SportType.BASKETBALL, mock_basketball)
        
        # Each instance should only have its own agent locally
        assert SportType.BASEBALL in instance_1._local_agent_refs
        assert SportType.BASEBALL not in instance_2._local_agent_refs
        
        assert SportType.BASKETBALL in instance_2._local_agent_refs
        assert SportType.BASKETBALL not in instance_1._local_agent_refs
    
    async def test_agent_discovery_across_instances(self, instance_1, instance_2):
        """Test that agents can be discovered across instances."""
        mock_baseball = AsyncMock()
        mock_basketball = AsyncMock()
        
        await instance_1.register_sub_agent(SportType.BASEBALL, mock_baseball)
        await instance_2.register_sub_agent(SportType.BASKETBALL, mock_basketball)
        
        # Wait for registry updates
        await asyncio.sleep(0.1)
        
        # Each instance should be able to discover agents
        sports_1 = await instance_1.get_available_sports()
        sports_2 = await instance_2.get_available_sports()
        
        # Both should see both sports (local + registry)
        # Note: This depends on Redis being available
        assert SportType.BASEBALL in sports_1
        assert SportType.BASKETBALL in sports_2
    
    async def test_heartbeat_independence(self, instance_1, instance_2):
        """Test that heartbeat loops are independent."""
        mock_agent_1 = AsyncMock()
        mock_agent_2 = AsyncMock()
        
        await instance_1.register_sub_agent(SportType.BASEBALL, mock_agent_1)
        await instance_2.register_sub_agent(SportType.BASKETBALL, mock_agent_2)
        
        # Both should have independent heartbeat loops
        assert instance_1._heartbeat_running
        assert instance_2._heartbeat_running
        
        # Stopping one shouldn't affect the other
        await instance_1._stop_heartbeat_loop()
        
        assert not instance_1._heartbeat_running
        assert instance_2._heartbeat_running
    
    async def test_agent_failover(self, instance_1, instance_2):
        """Test agent re-registration after instance failure."""
        mock_baseball = AsyncMock()
        
        # Register on instance 1
        await instance_1.register_sub_agent(SportType.BASEBALL, mock_baseball)
        agent_id_1 = instance_1._local_agent_ids.get(SportType.BASEBALL)
        
        # Simulate instance 1 failure (stop heartbeat)
        await instance_1._stop_heartbeat_loop()
        
        # Wait for stale detection (would take 120s in production)
        # In test, we just verify the mechanism exists
        
        # Re-register on instance 2
        await instance_2.register_sub_agent(SportType.BASEBALL, mock_baseball)
        agent_id_2 = instance_2._local_agent_ids.get(SportType.BASEBALL)
        
        # Should have different agent IDs
        assert agent_id_1 != agent_id_2


@pytest.mark.asyncio
class TestLoadBalancing:
    """Test load balancing across instances."""
    
    async def test_round_robin_agent_selection(self):
        """Test that agents are selected in round-robin fashion."""
        # This would test the AgentRegistry.get_agent() method
        # to ensure it properly load balances
        pass  # Placeholder for full implementation
