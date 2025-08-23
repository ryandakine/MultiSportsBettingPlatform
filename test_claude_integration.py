#!/usr/bin/env python3
"""
Test script for Claude AI integration with Sub-Agents.
"""

import asyncio
import json
from datetime import datetime

from src.agents.head_agent import HeadAgent, SportType, UserQuery
from src.agents.sub_agents import BaseballAgent, BasketballAgent, FootballAgent, HockeyAgent
from src.services.claude_service import ClaudeService

async def test_claude_integration():
    """Test Claude AI integration with sub-agents."""
    print("🧪 Testing Claude AI Integration with Sub-Agents...")

    # Test Claude service directly
    print("\n🔍 Test 1: Claude Service Connection")
    claude_service = ClaudeService()
    
    if claude_service.enabled:
        print("✅ Claude AI service is enabled")
        
        # Test connection
        connection_test = await claude_service.test_connection()
        print(f"🔗 Claude API connection: {'✅ Connected' if connection_test else '❌ Failed'}")
    else:
        print("⚠️  Claude AI service is disabled (no API key)")
        print("   Set ANTHROPIC_API_KEY in your environment to enable Claude AI")

    # Initialize Head Agent
    head_agent = HeadAgent()

    # Create and register sub-agents
    sub_agents = [
        BaseballAgent("MLB Baseball Agent"),
        BasketballAgent("NBA/NCAAB Basketball Agent"),
        FootballAgent("NFL/NCAAF Football Agent"),
        HockeyAgent("NHL Hockey Agent")
    ]

    for agent in sub_agents:
        await head_agent.register_sub_agent(agent.sport, agent)
        print(f"✅ Registered {agent.name} (Claude: {'Enabled' if agent.use_claude else 'Disabled'})")

    # Test 2: Individual agent predictions with Claude
    print("\n🎯 Test 2: Individual Agent Predictions with Claude AI")
    
    test_queries = {
        SportType.BASEBALL: "What's the best bet for Dodgers vs Yankees tonight? Consider pitching matchups and recent form.",
        SportType.BASKETBALL: "Lakers vs Warriors tonight - who covers the spread? Analyze star power and recent performance.",
        SportType.FOOTBALL: "Chiefs vs Bills this weekend - what's the smartest bet? Consider weather and home field advantage.",
        SportType.HOCKEY: "Bruins vs Lightning tonight - who wins? Analyze goalie matchups and special teams."
    }

    for sport, query in test_queries.items():
        print(f"\n--- Testing {sport.value.upper()} Agent with Claude AI ---")
        
        # Create user query
        user_query = UserQuery(
            user_id="claude_test_user",
            sports=[sport],
            query_text=query,
            preferences={"risk_tolerance": "medium", "ai_enhanced": True},
            timestamp=datetime.now()
        )
        
        # Get prediction
        result = await head_agent.aggregate_predictions(user_query)
        
        prediction_data = result.get('predictions', {}).get(sport.value, {})
        
        print(f"Query: {query}")
        print(f"Prediction: {prediction_data.get('prediction', 'No prediction')}")
        print(f"Confidence: {prediction_data.get('confidence', 'Unknown')}")
        print(f"Claude Enhanced: {result.get('predictions', {}).get(sport.value, {}).get('metadata', {}).get('claude_enhanced', False)}")
        
        # Show reasoning (truncated)
        reasoning = prediction_data.get('reasoning', 'No reasoning')
        print(f"Reasoning: {reasoning[:150]}..." if len(reasoning) > 150 else f"Reasoning: {reasoning}")

    # Test 3: Multi-sport aggregation with Claude
    print("\n🔮 Test 3: Multi-Sport Aggregation with Claude AI")
    multi_sport_query = UserQuery(
        user_id="claude_multi_user",
        sports=[SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL],
        query_text="Give me the best bets across baseball, basketball, and football tonight. Use AI to analyze patterns and provide detailed reasoning.",
        preferences={"risk_tolerance": "high", "ai_enhanced": True, "favorite_teams": ["Lakers", "Dodgers", "Chiefs"]},
        timestamp=datetime.now()
    )

    result = await head_agent.aggregate_predictions(multi_sport_query)
    
    print("Multi-Sport Aggregation Result:")
    print(f"Sports analyzed: {result.get('sports_analyzed', [])}")
    print(f"Combined prediction: {result.get('combined_prediction', {}).get('recommendation', 'No recommendation')}")
    print(f"Overall confidence: {result.get('combined_prediction', {}).get('confidence', 'Unknown')}")
    
    # Show individual predictions with Claude status
    for sport, prediction in result.get('predictions', {}).items():
        claude_enhanced = prediction.get('metadata', {}).get('claude_enhanced', False)
        print(f"  {sport}: {prediction.get('prediction', 'No prediction')} {'🤖' if claude_enhanced else '📊'}")

    # Test 4: Health status with Claude information
    print("\n📊 Test 4: Health Status with Claude AI Information")
    system_status = await head_agent.get_system_status()
    print(f"System status: {system_status['status']}")
    print(f"Active sports: {system_status['active_sports']}")
    
    for sport, status in system_status.get('agent_statuses', {}).items():
        claude_info = status.get('claude_ai', {})
        print(f"  {sport}: {status.get('agent_name', 'Unknown')}")
        print(f"    Healthy: {status.get('healthy', False)}")
        print(f"    Claude AI: {claude_info.get('enabled', False)} ({claude_info.get('status', 'unknown')})")

    # Test 5: Sport-specific insights with AI capabilities
    print("\n🔍 Test 5: Sport-Specific Insights with AI Capabilities")
    for agent in sub_agents:
        insights = await agent.get_sport_specific_insights()
        print(f"\n{insights.get('agent_name', 'Unknown Agent')}:")
        print(f"  Sport: {insights.get('sport', 'Unknown')}")
        print(f"  AI Capabilities: {insights.get('ai_capabilities', 'Unknown')}")
        print(f"  Claude Enhanced: {insights.get('claude_ai_enhanced', False)}")
        print(f"  Prediction count: {insights.get('prediction_count', 0)}")

    print("\n🎉 Claude AI Integration testing completed!")
    
    # Summary
    claude_enabled_count = sum(1 for agent in sub_agents if agent.use_claude)
    print(f"\n📋 Summary:")
    print(f"  Total agents: {len(sub_agents)}")
    print(f"  Claude AI enabled: {claude_enabled_count}")
    print(f"  Claude AI disabled: {len(sub_agents) - claude_enabled_count}")
    
    if claude_enabled_count > 0:
        print("✅ Claude AI integration is working!")
    else:
        print("⚠️  Claude AI is not enabled. Set ANTHROPIC_API_KEY to enable AI-enhanced predictions.")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_claude_integration()) 