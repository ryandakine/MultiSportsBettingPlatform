"""
Unit Tests for HeadAgent
========================
Tests prediction aggregation, agent coordination, and distributed state management.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.agents.head_agent import HeadAgent
from src.agents import SportType


@pytest_asyncio.fixture
async def head_agent():
    """Provide a test HeadAgent instance."""
    agent = HeadAgent()
    yield agent
    
    # Cleanup: stop heartbeat
    if agent._heartbeat_running:
        await agent._stop_heartbeat_loop()


@pytest_asyncio.fixture
def mock_sub_agent():
    """Create a mock sub-agent."""
    agent = AsyncMock()
    agent.get_health_status = AsyncMock(return_value={"healthy": True})
    agent.get_prediction = AsyncMock(return_value=Prediction(
        prediction="Team A will win",
        confidence=ConfidenceLevel.HIGH,
        reasoning="Strong recent performance",
        metadata={}
    ))
    return agent


@pytest.mark.asyncio
class TestAgentRegistration:
    """Test agent registration functionality."""
    
    async def test_register_sub_agent(self, head_agent, mock_sub_agent):
        """Test registering a sub-agent."""
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        
        # Should be in local refs
        assert SportType.BASEBALL in head_agent._local_agent_refs
        assert head_agent._local_agent_refs[SportType.BASEBALL] == mock_sub_agent
        
        # Should have agent ID
        assert SportType.BASEBALL in head_agent._local_agent_ids
    
    async def test_register_multiple_agents(self, head_agent):
        """Test registering multiple sub-agents."""
        mock_baseball = AsyncMock()
        mock_basketball = AsyncMock()
        
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_baseball)
        await head_agent.register_sub_agent(SportType.BASKETBALL, mock_basketball)
        
        assert len(head_agent._local_agent_refs) == 2
        assert len(head_agent._local_agent_ids) == 2
    
    async def test_unregister_sub_agent(self, head_agent, mock_sub_agent):
        """Test unregistering a sub-agent."""
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        
        # Unregister
        await head_agent.unregister_sub_agent(SportType.BASEBALL)
        
        # Should be removed
        assert SportType.BASEBALL not in head_agent._local_agent_refs
        assert SportType.BASEBALL not in head_agent._local_agent_ids
    
    async def test_heartbeat_starts_on_first_registration(self, head_agent, mock_sub_agent):
        """Test that heartbeat loop starts when first agent is registered."""
        assert not head_agent._heartbeat_running
        
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        
        # Should start heartbeat
        assert head_agent._heartbeat_running
        assert head_agent._heartbeat_task is not None
    
    async def test_heartbeat_stops_when_all_agents_unregistered(self, head_agent, mock_sub_agent):
        """Test that heartbeat stops when all agents are unregistered."""
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        assert head_agent._heartbeat_running
        
        # Unregister all agents
        await head_agent.unregister_sub_agent(SportType.BASEBALL)
        
        # Should stop heartbeat
        assert not head_agent._heartbeat_running


@pytest.mark.asyncio
class TestAvailableSports:
    """Test getting available sports."""
    
    async def test_get_available_sports_local_only(self, head_agent):
        """Test getting sports with only local agents."""
        mock_baseball = AsyncMock()
        mock_basketball = AsyncMock()
        
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_baseball)
        await head_agent.register_sub_agent(SportType.BASKETBALL, mock_basketball)
        
        sports = await head_agent.get_available_sports()
        
        assert SportType.BASEBALL in sports
        assert SportType.BASKETBALL in sports
        assert len(sports) >= 2


@pytest.mark.asyncio
class TestPredictionAggregation:
    """Test prediction aggregation logic."""
    
    async def test_aggregate_predictions_single_sport(self, head_agent, mock_sub_agent):
        """Test aggregating predictions for a single sport."""
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        
        user_query = UserQuery(
            user_id="test_user",
            query_text="Who will win?",
            sports=[SportType.BASEBALL],
            preferences={},
            timestamp=datetime.utcnow()
        )
        
        result = await head_agent.aggregate_predictions(user_query)
        
        assert "baseball" in result
        assert result["baseball"]["prediction"] == "Team A will win"
    
    async def test_aggregate_predictions_multiple_sports(self, head_agent):
        """Test aggregating predictions for multiple sports."""
        mock_baseball = AsyncMock()
        mock_baseball.get_health_status = AsyncMock(return_value={"healthy": True})
        mock_baseball.get_prediction = AsyncMock(return_value=Prediction(
            prediction="Baseball prediction",
            confidence=ConfidenceLevel.HIGH,
            reasoning="Analysis",
            metadata={}
        ))
        
        mock_basketball = AsyncMock()
        mock_basketball.get_health_status = AsyncMock(return_value={"healthy": True})
        mock_basketball.get_prediction = AsyncMock(return_value=Prediction(
            prediction="Basketball prediction",
            confidence=ConfidenceLevel.MEDIUM,
            reasoning="Analysis",
            metadata={}
        ))
        
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_baseball)
        await head_agent.register_sub_agent(SportType.BASKETBALL, mock_basketball)
        
        user_query = UserQuery(
            user_id="test_user",
            query_text="Who will win?",
            sports=[SportType.BASEBALL, SportType.BASKETBALL],
            preferences={},
            timestamp=datetime.utcnow()
        )
        
        result = await head_agent.aggregate_predictions(user_query)
        
        assert "baseball" in result
        assert "basketball" in result
    
    async def test_aggregate_predictions_no_agents(self, head_agent):
        """Test aggregating when no agents are available."""
        user_query = UserQuery(
            user_id="test_user",
            query_text="Who will win?",
            sports=[SportType.BASEBALL],
            preferences={},
            timestamp=datetime.utcnow()
        )
        
        result = await head_agent.aggregate_predictions(user_query)
        
        assert "error" in result
    
    async def test_aggregate_predictions_unhealthy_agent(self, head_agent):
        """Test that un healthy agents are skipped."""
        mock_unhealthy = AsyncMock()
        mock_unhealthy.get_health_status = AsyncMock(return_value={"healthy": False})
        
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_unhealthy)
        
        user_query = UserQuery(
            user_id="test_user",
            query_text="Who will win?",
            sports=[SportType.BASEBALL],
            preferences={},
            timestamp=datetime.utcnow()
        )
        
        result = await head_agent.aggregate_predictions(user_query)
        
        # Should have no baseball prediction (agent unhealthy)
        assert "baseball" not in result or "error" in result


@pytest.mark.asyncio
class TestUserPreferences:
    """Test user preference management."""
    
    async def test_update_user_preferences(self, head_agent):
        """Test updating user preferences."""
        preferences = {
            "favorite_sports": ["baseball", "basketball"],
            "risk_tolerance": "medium"
        }
        
        # Should not raise exception
        await head_agent.update_user_preferences("test_user", preferences)
    
    async def test_get_user_session(self, head_agent):
        """Test getting user sessions."""
        sessions = await head_agent.get_user_session("test_user")
        
        # Should return list (even if empty)
        assert isinstance(sessions, list)


@pytest.mark.asyncio
class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    async def test_sub_agents_property(self, head_agent, mock_sub_agent):
        """Test that sub_agents property returns local refs."""
        await head_agent.register_sub_agent(SportType.BASEBALL, mock_sub_agent)
        
        # sub_agents should work
        assert SportType.BASEBALL in head_agent.sub_agents
        assert head_agent.sub_agents[SportType.BASEBALL] == mock_sub_agent
