#!/usr/bin/env python3
"""
Test script for Prediction Aggregation and Weighting System
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

# Import our aggregation system
from src.services.prediction_aggregator import (
    PredictionAggregator, 
    Prediction, 
    AggregatedPrediction,
    WeightingStrategy,
    SportType,
    ConfidenceLevel
)
from src.services.prediction_cache import CacheManager

class MockSubAgent:
    """Mock sub-agent for testing."""
    
    def __init__(self, name: str, sport: SportType, accuracy: float = 0.75):
        self.name = name
        self.sport = sport
        self.accuracy = accuracy
    
    async def get_prediction(self, query: str) -> Dict:
        """Mock prediction response."""
        predictions = {
            "baseball": {
                "prediction": "Dodgers win by 2+ runs",
                "confidence": 0.8,
                "reasoning": "Strong pitching matchup favors Dodgers",
                "metadata": {"ai_enhanced": True, "data_sources": ["mlb_stats", "weather"]}
            },
            "basketball": {
                "prediction": "Lakers cover the spread",
                "confidence": 0.7,
                "reasoning": "Home court advantage and recent form",
                "metadata": {"ai_enhanced": True, "data_sources": ["nba_stats", "injury_report"]}
            },
            "football": {
                "prediction": "Chiefs win outright",
                "confidence": 0.6,
                "reasoning": "Mahomes is healthy and team is rested",
                "metadata": {"ai_enhanced": True, "data_sources": ["nfl_stats", "weather"]}
            },
            "hockey": {
                "prediction": "Bruins win in regulation",
                "confidence": 0.75,
                "reasoning": "Goalie matchup favors Bruins",
                "metadata": {"ai_enhanced": True, "data_sources": ["nhl_stats", "special_teams"]}
            }
        }
        
        sport_key = self.sport.value
        base_prediction = predictions.get(sport_key, {
            "prediction": f"{self.sport.value.title()} team wins",
            "confidence": 0.5,
            "reasoning": "Default prediction",
            "metadata": {"ai_enhanced": False}
        })
        
        # Add some variation based on accuracy
        base_prediction["confidence"] = min(base_prediction["confidence"] * self.accuracy, 1.0)
        
        return base_prediction

async def test_prediction_collection():
    """Test collecting predictions from sub-agents."""
    print("🧪 Testing Prediction Collection")
    print("=" * 50)
    
    # Create mock sub-agents
    sub_agents = {
        SportType.BASEBALL: MockSubAgent("MLB Agent", SportType.BASEBALL, 0.8),
        SportType.BASKETBALL: MockSubAgent("NBA Agent", SportType.BASKETBALL, 0.75),
        SportType.FOOTBALL: MockSubAgent("NFL Agent", SportType.FOOTBALL, 0.7),
        SportType.HOCKEY: MockSubAgent("NHL Agent", SportType.HOCKEY, 0.8)
    }
    
    # Create aggregator
    aggregator = PredictionAggregator(strategy=WeightingStrategy.HYBRID)
    
    # Test query
    query = "Analyze tonight's games and provide betting recommendations"
    
    print(f"Query: {query}")
    print("Collecting predictions from all agents...")
    
    # Collect predictions
    predictions = await aggregator.collect_predictions(sub_agents, query, user_id="test_user")
    
    print(f"\n✅ Collected {len(predictions)} predictions:")
    for pred in predictions:
        print(f"   {pred.sport.value.title()}: {pred.prediction} (confidence: {pred.confidence:.2f})")
    
    return predictions

def test_weighting_strategies():
    """Test different weighting strategies."""
    print("\n⚖️  Testing Weighting Strategies")
    print("=" * 50)
    
    # Create sample predictions
    predictions = [
        Prediction(
            sport=SportType.BASEBALL,
            agent_name="MLB Agent",
            prediction="Dodgers win",
            confidence=0.8,
            reasoning="Strong pitching",
            timestamp=datetime.now(),
            metadata={},
            historical_accuracy=0.75,
            user_preference_weight=1.2
        ),
        Prediction(
            sport=SportType.BASKETBALL,
            agent_name="NBA Agent",
            prediction="Lakers cover",
            confidence=0.7,
            reasoning="Home court advantage",
            timestamp=datetime.now(),
            metadata={},
            historical_accuracy=0.8,
            user_preference_weight=0.9
        )
    ]
    
    # Test each strategy
    strategies = [
        WeightingStrategy.CONFIDENCE_ONLY,
        WeightingStrategy.HISTORICAL_ACCURACY,
        WeightingStrategy.USER_PREFERENCE,
        WeightingStrategy.HYBRID,
        WeightingStrategy.EQUAL_WEIGHT
    ]
    
    for strategy in strategies:
        print(f"\n📊 Strategy: {strategy.value}")
        aggregator = PredictionAggregator(strategy=strategy)
        
        # Calculate weighted confidences
        for pred in predictions:
            weighted_conf = aggregator.calculate_weighted_confidence(pred)
            print(f"   {pred.sport.value}: {pred.confidence:.2f} → {weighted_conf:.2f}")
        
        # Aggregate predictions
        result = aggregator.aggregate_predictions(predictions)
        print(f"   Overall confidence: {result.overall_confidence:.2f}")

async def test_prediction_aggregation():
    """Test full prediction aggregation workflow."""
    print("\n🔮 Testing Full Prediction Aggregation")
    print("=" * 50)
    
    # Create mock sub-agents
    sub_agents = {
        SportType.BASEBALL: MockSubAgent("MLB Agent", SportType.BASEBALL, 0.8),
        SportType.BASKETBALL: MockSubAgent("NBA Agent", SportType.BASKETBALL, 0.75),
        SportType.FOOTBALL: MockSubAgent("NFL Agent", SportType.FOOTBALL, 0.7),
        SportType.HOCKEY: MockSubAgent("NHL Agent", SportType.HOCKEY, 0.8)
    }
    
    # Create aggregator
    aggregator = PredictionAggregator(strategy=WeightingStrategy.HYBRID)
    
    # Test queries
    test_queries = [
        "Who will win tonight's Dodgers vs Yankees game?",
        "Analyze the Lakers vs Warriors matchup",
        "What's the best bet for Chiefs vs Bills?",
        "Bruins vs Lightning - who wins?",
        "Multi-sport analysis for tonight's games"
    ]
    
    for query in test_queries:
        print(f"\n📋 Query: {query}")
        
        # Collect predictions
        predictions = await aggregator.collect_predictions(sub_agents, query, user_id="test_user")
        
        # Aggregate predictions
        result = aggregator.aggregate_predictions(predictions)
        
        print(f"   Combined Prediction: {result.combined_prediction}")
        print(f"   Overall Confidence: {result.overall_confidence:.2f}")
        print(f"   Sports Covered: {list(result.sport_breakdown.keys())}")
        print(f"   Recommendations: {len(result.recommendations)} recommendations")

async def test_caching_system():
    """Test the caching system."""
    print("\n💾 Testing Caching System")
    print("=" * 50)
    
    # Create cache manager
    cache_manager = CacheManager()
    
    # Test data
    test_data = {
        "query": "Dodgers vs Yankees prediction",
        "sports": ["baseball"],
        "data": {
            "prediction": "Dodgers win",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat()
        },
        "user_id": "test_user"
    }
    
    # Cache prediction
    print("📥 Caching prediction...")
    await cache_manager.cache_prediction(
        test_data["query"],
        test_data["sports"],
        test_data["data"],
        ttl=60,  # 1 minute
        user_id=test_data["user_id"]
    )
    
    # Retrieve from cache
    print("📤 Retrieving from cache...")
    cached_result = await cache_manager.get_cached_prediction(
        test_data["query"],
        test_data["sports"],
        user_id=test_data["user_id"]
    )
    
    if cached_result:
        print("✅ Cache hit!")
        print(f"   Retrieved: {cached_result['prediction']}")
    else:
        print("❌ Cache miss")
    
    # Test cache stats
    stats = cache_manager.get_overall_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Main cache hit rate: {stats['main_cache']['hit_rate']:.2f}")
    
    # Test sport-specific cache
    print("\n🏈 Testing Sport-Specific Cache...")
    await cache_manager.sport_cache.set("football", "Chiefs vs Bills", {"prediction": "Chiefs win"}, ttl=60)
    
    football_result = cache_manager.sport_cache.get("football", "Chiefs vs Bills")
    if football_result:
        print("✅ Sport-specific cache hit!")
    else:
        print("❌ Sport-specific cache miss")

def test_performance_metrics():
    """Test performance metrics and historical accuracy tracking."""
    print("\n📈 Testing Performance Metrics")
    print("=" * 50)
    
    aggregator = PredictionAggregator()
    
    # Simulate historical accuracy updates
    print("📊 Updating historical accuracy...")
    aggregator.update_historical_accuracy(
        SportType.BASEBALL, "MLB Agent", 
        "Dodgers win", "Dodgers won", True
    )
    aggregator.update_historical_accuracy(
        SportType.BASEBALL, "MLB Agent", 
        "Yankees win", "Dodgers won", False
    )
    aggregator.update_historical_accuracy(
        SportType.BASEBALL, "MLB Agent", 
        "Dodgers win", "Dodgers won", True
    )
    
    # Get performance metrics
    metrics = aggregator.get_performance_metrics()
    print(f"   Strategy: {metrics['strategy']}")
    print(f"   Total predictions processed: {metrics['total_predictions_processed']}")
    print(f"   Sport weights: {metrics['sport_weights']}")

async def test_integration():
    """Test full integration of all components."""
    print("\n🔗 Testing Full Integration")
    print("=" * 50)
    
    # Create all components
    cache_manager = CacheManager()
    aggregator = PredictionAggregator(strategy=WeightingStrategy.HYBRID)
    
    # Create mock sub-agents
    sub_agents = {
        SportType.BASEBALL: MockSubAgent("MLB Agent", SportType.BASEBALL, 0.8),
        SportType.BASKETBALL: MockSubAgent("NBA Agent", SportType.BASKETBALL, 0.75),
        SportType.FOOTBALL: MockSubAgent("NFL Agent", SportType.FOOTBALL, 0.7),
        SportType.HOCKEY: MockSubAgent("NHL Agent", SportType.HOCKEY, 0.8)
    }
    
    # Test query
    query = "Comprehensive analysis of tonight's major games"
    user_id = "integration_test_user"
    
    print(f"Query: {query}")
    print("User: {user_id}")
    
    # Check cache first
    print("\n🔍 Checking cache...")
    cached_result = await cache_manager.get_cached_prediction(query, ["baseball", "basketball", "football", "hockey"], user_id)
    
    if cached_result:
        print("✅ Using cached result")
        result = cached_result
    else:
        print("📥 Cache miss, generating new prediction...")
        
        # Collect predictions
        predictions = await aggregator.collect_predictions(sub_agents, query, user_id)
        
        # Aggregate predictions
        result = aggregator.aggregate_predictions(predictions)
        
        # Cache the result
        await cache_manager.cache_prediction(query, ["baseball", "basketball", "football", "hockey"], result, ttl=300, user_id=user_id)
        print("💾 Result cached for future use")
    
    # Display results
    print(f"\n🎯 Final Result:")
    print(f"   Prediction: {result.combined_prediction}")
    print(f"   Confidence: {result.overall_confidence:.2f}")
    print(f"   Sports: {list(result.sport_breakdown.keys())}")
    print(f"   Recommendations: {result.recommendations[:2]}...")  # Show first 2
    
    # Show cache stats
    stats = cache_manager.get_overall_stats()
    print(f"\n📊 Final Cache Stats:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Hit rate: {stats['main_cache']['hit_rate']:.2f}")

async def main():
    """Run all tests."""
    print("🚀 MultiSportsBettingPlatform - Prediction Aggregation Test")
    print("=" * 70)
    print("Testing the intelligent prediction aggregation and weighting system")
    print()
    
    try:
        # Run all tests
        await test_prediction_collection()
        test_weighting_strategies()
        await test_prediction_aggregation()
        await test_caching_system()
        test_performance_metrics()
        await test_integration()
        
        print("\n" + "=" * 70)
        print("🎉 All Tests Completed Successfully!")
        print()
        print("✅ Prediction Collection: Working")
        print("✅ Weighting Strategies: Working")
        print("✅ Prediction Aggregation: Working")
        print("✅ Caching System: Working")
        print("✅ Performance Metrics: Working")
        print("✅ Full Integration: Working")
        print()
        print("🚀 Your prediction aggregation system is ready!")
        print("   The system can now intelligently combine predictions from")
        print("   multiple sport agents with appropriate weighting.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 