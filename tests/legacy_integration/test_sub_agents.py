#!/usr/bin/env python3
"""
Test script for Sub-Agent System functionality.
"""

import asyncio
import json
from datetime import datetime

from src.agents.head_agent import HeadAgent, SportType, UserQuery
from src.agents.sub_agents import BaseballAgent, BasketballAgent, FootballAgent, HockeyAgent

async def test_sub_agents():
    """Test the Sub-Agent System functionality."""
    print("🧪 Testing Sub-Agent System...")

    # Initialize Head Agent
    head_agent = HeadAgent()

    # Create and register real sub-agents
    sub_agents = [
        BaseballAgent("MLB Baseball Agent"),
        BasketballAgent("NBA/NCAAB Basketball Agent"),
        FootballAgent("NFL/NCAAF Football Agent"),
        HockeyAgent("NHL Hockey Agent")
    ]

    for agent in sub_agents:
        await head_agent.register_sub_agent(agent.sport, agent)
        print(f"✅ Registered {agent.name}")

    # Test 1: Get available sports
    print("\n📋 Test 1: Available Sports")
    available_sports = await head_agent.get_available_sports()
    print(f"Available sports: {[sport.value for sport in available_sports]}")

    # Test 2: Test each sub-agent individually
    print("\n🎯 Test 2: Individual Sub-Agent Testing")
    
    test_queries = {
        SportType.BASEBALL: "What are the best bets for Dodgers vs Yankees tonight?",
        SportType.BASKETBALL: "Lakers vs Warriors prediction for tonight's game",
        SportType.FOOTBALL: "Chiefs vs Bills NFL matchup analysis",
        SportType.HOCKEY: "Bruins vs Lightning NHL game prediction"
    }

    for sport, query in test_queries.items():
        print(f"\n--- Testing {sport.value.upper()} Agent ---")
        
        # Create user query for single sport
        user_query = UserQuery(
            user_id="test_user_123",
            sports=[sport],
            query_text=query,
            preferences={"risk_tolerance": "medium"},
            timestamp=datetime.now()
        )
        
        # Get prediction from specific agent
        result = await head_agent.aggregate_predictions(user_query)
        
        print(f"Query: {query}")
        print(f"Prediction: {result.get('predictions', {}).get(sport.value, {}).get('prediction', 'No prediction')}")
        print(f"Confidence: {result.get('predictions', {}).get(sport.value, {}).get('confidence', 'Unknown')}")
        print(f"Reasoning: {result.get('predictions', {}).get(sport.value, {}).get('reasoning', 'No reasoning')[:100]}...")

    # Test 3: Multi-sport aggregation
    print("\n🔮 Test 3: Multi-Sport Aggregation")
    multi_sport_query = UserQuery(
        user_id="test_user_456",
        sports=[SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL],
        query_text="What are the best bets across baseball, basketball, and football tonight?",
        preferences={"risk_tolerance": "high", "favorite_teams": ["Lakers", "Dodgers"]},
        timestamp=datetime.now()
    )

    result = await head_agent.aggregate_predictions(multi_sport_query)
    
    print("Multi-Sport Aggregation Result:")
    print(f"Sports analyzed: {result.get('sports_analyzed', [])}")
    print(f"Combined prediction: {result.get('combined_prediction', {}).get('recommendation', 'No recommendation')}")
    print(f"Overall confidence: {result.get('combined_prediction', {}).get('confidence', 'Unknown')}")
    
    # Show individual predictions
    for sport, prediction in result.get('predictions', {}).items():
        print(f"  {sport}: {prediction.get('prediction', 'No prediction')}")

    # Test 4: Sub-agent health status
    print("\n📊 Test 4: Sub-Agent Health Status")
    system_status = await head_agent.get_system_status()
    print(f"System status: {system_status['status']}")
    print(f"Active sports: {system_status['active_sports']}")
    
    for sport, status in system_status.get('agent_statuses', {}).items():
        print(f"  {sport}: {status.get('agent_name', 'Unknown')} - Healthy: {status.get('healthy', False)}")

    # Test 5: Sport-specific insights
    print("\n🔍 Test 5: Sport-Specific Insights")
    for agent in sub_agents:
        insights = await agent.get_sport_specific_insights()
        print(f"\n{insights.get('agent_name', 'Unknown Agent')}:")
        print(f"  Sport: {insights.get('sport', 'Unknown')}")
        print(f"  League: {insights.get('league', 'Unknown')}")
        print(f"  Prediction count: {insights.get('prediction_count', 0)}")
        print(f"  Recent accuracy: {insights.get('recent_accuracy', 0):.2%}")

    # Test 6: Learning and outcome reporting
    print("\n📈 Test 6: Learning and Outcome Reporting")
    
    # Simulate some outcomes for learning
    test_outcomes = [
        ("pred_123", True, "test_user_123"),
        ("pred_456", False, "test_user_123"),
        ("pred_789", True, "test_user_456"),
    ]
    
    for prediction_id, outcome, user_id in test_outcomes:
        await head_agent.report_outcome(prediction_id, outcome, user_id)
        print(f"✅ Reported outcome: {prediction_id} = {outcome}")

    print("\n🎉 Sub-Agent System testing completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_sub_agents()) 