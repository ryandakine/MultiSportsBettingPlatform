#!/usr/bin/env python3
"""
Test script for Enhanced AI System (Claude + Perplexity Pro).
"""

import asyncio
import json
from datetime import datetime

from src.agents.head_agent import HeadAgent, SportType, UserQuery
from src.agents.sub_agents import BaseballAgent, BasketballAgent, FootballAgent, HockeyAgent
from src.services.claude_service import ClaudeService
from src.services.perplexity_service import PerplexityService

async def test_enhanced_ai_system():
    """Test the Enhanced AI System with Claude and Perplexity Pro."""
    print("🧪 Testing Enhanced AI System (Claude + Perplexity Pro)...")

    # Test AI services directly
    print("\n🔍 Test 1: AI Services Connection")
    
    # Test Claude service
    claude_service = ClaudeService()
    if claude_service.enabled:
        print("✅ Claude AI service is enabled")
        claude_connection = await claude_service.test_connection()
        print(f"🔗 Claude API connection: {'✅ Connected' if claude_connection else '❌ Failed'}")
    else:
        print("⚠️  Claude AI service is disabled (no API key)")
    
    # Test Perplexity service
    perplexity_service = PerplexityService()
    if perplexity_service.enabled:
        print("✅ Perplexity Pro AI service is enabled")
        perplexity_connection = await perplexity_service.test_connection()
        print(f"🔗 Perplexity API connection: {'✅ Connected' if perplexity_connection else '❌ Failed'}")
    else:
        print("⚠️  Perplexity Pro AI service is disabled (no API key)")

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
        print(f"✅ Registered {agent.name}")
        print(f"   Claude AI: {'Enabled' if agent.use_claude else 'Disabled'}")
        print(f"   Perplexity Pro: {'Enabled' if agent.use_perplexity else 'Disabled'}")

    # Test 2: Enhanced predictions with both AI services
    print("\n🎯 Test 2: Enhanced Predictions with Claude + Perplexity")
    
    test_queries = {
        SportType.BASEBALL: "Analyze the Dodgers vs Yankees matchup tonight. Consider recent form, pitching matchups, and provide a detailed betting recommendation.",
        SportType.BASKETBALL: "Lakers vs Warriors tonight - analyze star power, recent performance, and give me the best betting strategy.",
        SportType.FOOTBALL: "Chiefs vs Bills this weekend - evaluate weather impact, home field advantage, and provide comprehensive betting analysis.",
        SportType.HOCKEY: "Bruins vs Lightning tonight - analyze goalie matchups, special teams, and give detailed betting insights."
    }

    for sport, query in test_queries.items():
        print(f"\n--- Testing {sport.value.upper()} Agent with Enhanced AI ---")
        
        # Create user query
        user_query = UserQuery(
            user_id="enhanced_ai_test_user",
            sports=[sport],
            query_text=query,
            preferences={"risk_tolerance": "medium", "ai_enhanced": True, "research_required": True},
            timestamp=datetime.now()
        )
        
        # Get prediction
        result = await head_agent.aggregate_predictions(user_query)
        
        prediction_data = result.get('predictions', {}).get(sport.value, {})
        metadata = prediction_data.get('metadata', {})
        
        print(f"Query: {query}")
        print(f"Prediction: {prediction_data.get('prediction', 'No prediction')}")
        print(f"Confidence: {prediction_data.get('confidence', 'Unknown')}")
        print(f"Claude Enhanced: {metadata.get('claude_enhanced', False)}")
        print(f"Perplexity Research: {metadata.get('perplexity_research', False)}")
        
        # Show AI services status
        ai_services = metadata.get('ai_services', {})
        print(f"AI Services: Claude={ai_services.get('claude', False)}, Perplexity={ai_services.get('perplexity', False)}")
        
        # Show reasoning (truncated)
        reasoning = prediction_data.get('reasoning', 'No reasoning')
        print(f"Reasoning: {reasoning[:150]}..." if len(reasoning) > 150 else f"Reasoning: {reasoning}")

    # Test 3: Multi-sport aggregation with enhanced AI
    print("\n🔮 Test 3: Multi-Sport Aggregation with Enhanced AI")
    multi_sport_query = UserQuery(
        user_id="enhanced_multi_user",
        sports=[SportType.BASEBALL, SportType.BASKETBALL, SportType.FOOTBALL],
        query_text="Give me comprehensive betting analysis across baseball, basketball, and football tonight. Use AI to research teams, analyze patterns, and provide detailed recommendations.",
        preferences={"risk_tolerance": "high", "ai_enhanced": True, "research_required": True, "favorite_teams": ["Lakers", "Dodgers", "Chiefs"]},
        timestamp=datetime.now()
    )

    result = await head_agent.aggregate_predictions(multi_sport_query)
    
    print("Multi-Sport Aggregation Result:")
    print(f"Sports analyzed: {result.get('sports_analyzed', [])}")
    print(f"Combined prediction: {result.get('combined_prediction', {}).get('recommendation', 'No recommendation')}")
    print(f"Overall confidence: {result.get('combined_prediction', {}).get('confidence', 'Unknown')}")
    
    # Show individual predictions with AI status
    for sport, prediction in result.get('predictions', {}).items():
        metadata = prediction.get('metadata', {})
        claude_enhanced = metadata.get('claude_enhanced', False)
        perplexity_research = metadata.get('perplexity_research', False)
        
        ai_indicators = []
        if claude_enhanced:
            ai_indicators.append("🤖")
        if perplexity_research:
            ai_indicators.append("🔍")
        
        ai_status = " ".join(ai_indicators) if ai_indicators else "📊"
        print(f"  {sport}: {prediction.get('prediction', 'No prediction')} {ai_status}")

    # Test 4: Health status with enhanced AI information
    print("\n📊 Test 4: Health Status with Enhanced AI Information")
    system_status = await head_agent.get_system_status()
    print(f"System status: {system_status['status']}")
    print(f"Active sports: {system_status['active_sports']}")
    
    for sport, status in system_status.get('agent_statuses', {}).items():
        claude_info = status.get('claude_ai', {})
        perplexity_info = status.get('perplexity_pro', {})
        
        print(f"  {sport}: {status.get('agent_name', 'Unknown')}")
        print(f"    Healthy: {status.get('healthy', False)}")
        print(f"    Claude AI: {claude_info.get('enabled', False)} ({claude_info.get('status', 'unknown')})")
        print(f"    Perplexity Pro: {perplexity_info.get('enabled', False)} ({perplexity_info.get('status', 'unknown')})")

    # Test 5: Sport-specific insights with enhanced AI capabilities
    print("\n🔍 Test 5: Sport-Specific Insights with Enhanced AI Capabilities")
    for agent in sub_agents:
        insights = await agent.get_sport_specific_insights()
        print(f"\n{insights.get('agent_name', 'Unknown Agent')}:")
        print(f"  Sport: {insights.get('sport', 'Unknown')}")
        print(f"  AI Capabilities: {insights.get('ai_capabilities', 'Unknown')}")
        print(f"  Claude Enhanced: {insights.get('claude_ai_enhanced', False)}")
        print(f"  Perplexity Enhanced: {insights.get('perplexity_pro_enhanced', False)}")
        print(f"  Prediction count: {insights.get('prediction_count', 0)}")

    # Test 6: Direct AI service testing
    print("\n🧠 Test 6: Direct AI Service Testing")
    
    # Test Perplexity research
    if perplexity_service.enabled:
        print("\n--- Testing Perplexity Pro Research ---")
        try:
            research_result = await perplexity_service.get_research_insights(
                sport="baseball",
                teams=["Dodgers", "Yankees"],
                query="Recent performance and betting analysis",
                include_recent_data=True
            )
            print(f"Research insights: {len(research_result.get('insights', ''))} characters")
            print(f"Sources found: {len(research_result.get('sources', []))}")
            print(f"Recent data: {'Available' if research_result.get('recent_data') else 'None'}")
        except Exception as e:
            print(f"Perplexity research test failed: {e}")
    
    # Test Claude enhanced prediction
    if claude_service.enabled:
        print("\n--- Testing Claude AI Enhanced Prediction ---")
        try:
            test_analysis = {
                "teams_analyzed": ["Dodgers", "Yankees"],
                "offensive_analysis": {"offensive_advantage": "Dodgers", "total_points_expected": 8.5},
                "defensive_analysis": {"defensive_advantage": "Yankees"},
                "key_metrics": {"team1_era": 3.45, "team2_era": 3.78}
            }
            
            claude_result = await claude_service.get_enhanced_prediction(
                sport="baseball",
                analysis=test_analysis,
                query_text="Dodgers vs Yankees prediction",
                context="Test prediction"
            )
            print(f"Claude prediction: {claude_result.get('prediction', 'No prediction')}")
            print(f"Confidence: {claude_result.get('confidence', 'Unknown')}")
        except Exception as e:
            print(f"Claude prediction test failed: {e}")

    print("\n🎉 Enhanced AI System testing completed!")
    
    # Summary
    claude_enabled_count = sum(1 for agent in sub_agents if agent.use_claude)
    perplexity_enabled_count = sum(1 for agent in sub_agents if agent.use_perplexity)
    
    print(f"\n📋 Summary:")
    print(f"  Total agents: {len(sub_agents)}")
    print(f"  Claude AI enabled: {claude_enabled_count}")
    print(f"  Perplexity Pro enabled: {perplexity_enabled_count}")
    print(f"  Both AI services: {sum(1 for agent in sub_agents if agent.use_claude and agent.use_perplexity)}")
    
    if claude_enabled_count > 0 or perplexity_enabled_count > 0:
        print("✅ Enhanced AI integration is working!")
    else:
        print("⚠️  AI services are not enabled. Set API keys to enable enhanced predictions.")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_enhanced_ai_system()) 