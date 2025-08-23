#!/usr/bin/env python3
"""
Test script for Head Agent functionality.
"""

import asyncio
import json
from datetime import datetime

from src.agents.head_agent import HeadAgent, SportType, UserQuery
from src.agents.mock_sub_agent import MockSubAgent

async def test_head_agent():
    """Test the Head Agent functionality."""
    print("🧪 Testing Head Agent Architecture...")
    
    # Initialize Head Agent
    head_agent = HeadAgent()
    
    # Create and register mock sub-agents
    mock_agents = [
        MockSubAgent(SportType.BASEBALL, "Mock Baseball Agent"),
        MockSubAgent(SportType.BASKETBALL, "Mock Basketball Agent"),
        MockSubAgent(SportType.FOOTBALL, "Mock Football Agent"),
        MockSubAgent(SportType.HOCKEY, "Mock Hockey Agent")
    ]
    
    for agent in mock_agents:
        await head_agent.register_sub_agent(agent.sport, agent)
        print(f"✅ Registered {agent.name}")
    
    # Test 1: Get available sports
    print("\n📋 Test 1: Available Sports")
    available_sports = await head_agent.get_available_sports()
    print(f"Available sports: {[sport.value for sport in available_sports]}")
    
    # Test 2: Create a user query
    print("\n🎯 Test 2: User Query")
    user_query = UserQuery(
        user_id="test_user_123",
        sports=[SportType.BASEBALL, SportType.BASKETBALL],
        query_text="What are the best bets for tonight's games?",
        preferences={"risk_tolerance": "medium"},
        timestamp=datetime.now()
    )
    print(f"User query: {user_query.query_text}")
    print(f"Sports requested: {[sport.value for sport in user_query.sports]}")
    
    # Test 3: Get aggregated predictions
    print("\n🔮 Test 3: Aggregated Predictions")
    result = await head_agent.aggregate_predictions(user_query)
    
    print("Aggregation Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Test 4: System status
    print("\n📊 Test 4: System Status")
    status = await head_agent.get_system_status()
    print(f"System status: {status['status']}")
    print(f"Active sports: {status['active_sports']}")
    print(f"Prediction history count: {status['prediction_history_count']}")
    
    # Test 5: Report outcome
    print("\n📈 Test 5: Report Outcome")
    if result.get('predictions'):
        # Get first prediction ID from metadata
        first_prediction = None
        for sport, pred in result['predictions'].items():
            if hasattr(pred, 'metadata') and pred.metadata:
                first_prediction = pred.metadata.get('prediction_id')
                break
        
        if first_prediction:
            await head_agent.report_outcome(first_prediction, True, "test_user_123")
            print(f"✅ Reported outcome for prediction: {first_prediction}")
    
    print("\n🎉 Head Agent testing completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_head_agent()) 