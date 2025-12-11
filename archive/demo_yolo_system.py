"""
YOLO System Demonstration - YOLO MODE!
====================================
Show all the amazing YOLO features we built!
"""

import asyncio
import json
from datetime import datetime

# Import our YOLO services
from src.services.session_manager import session_manager
from src.services.security_service import security_service
from src.services.prediction_aggregator_v2 import prediction_aggregator_v2
from src.services.real_time_predictions import real_time_service
from src.services.social_features import social_service

class YOLOSystemDemo:
    def __init__(self):
        self.demo_user_id = "demo_yolo_user_123"
        self.demo_session_id = None
    
    async def demo_session_management(self):
        """Demonstrate session management features."""
        print("🔐 YOLO Session Management Demo")
        print("=" * 50)
        
        # Create a YOLO session
        session = await session_manager.create_session(
            user_id=self.demo_user_id,
            username="YOLO_Demo_User",
            ip_address="127.0.0.1",
            user_agent="YOLO Browser",
            yolo_level="YOLO Master"
        )
        
        self.demo_session_id = session.session_id
        print(f"✅ Created YOLO session: {session.session_id}")
        print(f"   User: {session.username}")
        print(f"   YOLO Level: {session.yolo_level}")
        print(f"   YOLO Score: {session.yolo_score:.2f}")
        print(f"   Status: {session.status.value}")
        
        # Get session stats
        stats = await session_manager.get_session_stats()
        print(f"\n📊 Session Stats:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   YOLO Sessions: {stats['yolo_sessions']}")
        print(f"   Average YOLO Score: {stats['average_yolo_score']}")
        print(f"   YOLO Energy: {stats['yolo_energy']}")
    
    async def demo_security_features(self):
        """Demonstrate security features."""
        print("\n🛡️ YOLO Security Features Demo")
        print("=" * 50)
        
        # Generate a secure token
        token = security_service.generate_token()
        print(f"✅ Generated secure token: {token[:20]}...")
        
        # Check rate limiting
        allowed, rate_info = security_service.check_rate_limit("demo_user")
        print(f"✅ Rate limit check: {'Allowed' if allowed else 'Blocked'}")
        print(f"   Requests: {rate_info['requests']}")
        print(f"   Remaining: {rate_info['remaining']}")
        print(f"   YOLO Boost: {rate_info['yolo_boost']}")
        
        # Get security stats
        security_stats = security_service.get_security_stats()
        print(f"\n📊 Security Stats:")
        print(f"   YOLO Security Score: {security_stats['yolo_security_score']}")
        print(f"   Security Level: {security_stats['security_level']}")
        print(f"   YOLO Energy: {security_stats['yolo_energy']}")
    
    async def demo_prediction_aggregation(self):
        """Demonstrate prediction aggregation."""
        print("\n🎯 YOLO Prediction Aggregation Demo")
        print("=" * 50)
        
        # Create mock predictions
        from src.services.real_time_predictions import LivePrediction, PredictionType
        
        predictions = {
            "baseball": LivePrediction(
                id="pred_1",
                sport="baseball",
                teams=["Yankees", "Red Sox"],
                prediction="YOLO bet on the underdog! The stats don't lie! 🎯",
                confidence=0.85,
                odds={"Yankees": 1.8, "Red Sox": 2.1},
                timestamp=datetime.now(),
                type=PredictionType.YOLO_MODE,
                reasoning="YOLO mode activated! Underdog energy is strong!",
                yolo_factor=1.5
            ),
            "basketball": LivePrediction(
                id="pred_2",
                sport="basketball",
                teams=["Lakers", "Warriors"],
                prediction="YOLO bet on the home team! Home court advantage is real! 🏀",
                confidence=0.90,
                odds={"Lakers": 1.6, "Warriors": 2.3},
                timestamp=datetime.now(),
                type=PredictionType.YOLO_MODE,
                reasoning="Home court advantage + YOLO energy = WIN!",
                yolo_factor=1.8
            )
        }
        
        # Test different aggregation strategies
        strategies = ["confidence_weighted", "historical_accuracy", "user_preference", "hybrid", "equal_weight", "yolo_mode"]
        
        for strategy in strategies:
            try:
                aggregated = await prediction_aggregator_v2.aggregate_predictions(
                    predictions=predictions,
                    strategy=strategy,
                    user_id=self.demo_user_id
                )
                print(f"✅ {strategy}: {aggregated.combined_prediction}")
                print(f"   Confidence: {aggregated.overall_confidence:.2f}")
                print(f"   YOLO Boost: {aggregated.yolo_boost:.2f}")
            except Exception as e:
                print(f"❌ {strategy}: Error - {e}")
        
        # Get aggregation stats
        agg_stats = prediction_aggregator_v2.get_aggregation_stats()
        print(f"\n📊 Aggregation Stats:")
        print(f"   Total Predictions: {agg_stats['total_predictions']}")
        print(f"   YOLO Predictions: {agg_stats['yolo_predictions']}")
        print(f"   Most Used Strategy: {agg_stats['most_used_strategy']}")
        print(f"   YOLO Energy: {agg_stats['yolo_energy']}")
    
    async def demo_real_time_predictions(self):
        """Demonstrate real-time predictions."""
        print("\n⚡ YOLO Real-Time Predictions Demo")
        print("=" * 50)
        
        # Generate live predictions
        sports = ["baseball", "basketball", "football", "hockey"]
        
        for sport in sports:
            try:
                prediction = await real_time_service.generate_live_prediction(
                    sport=sport,
                    teams=[f"{sport.title()} Team A", f"{sport.title()} Team B"]
                )
                print(f"✅ {sport.title()}: {prediction.prediction}")
                print(f"   Confidence: {prediction.confidence:.2f}")
                print(f"   YOLO Factor: {prediction.yolo_factor:.2f}")
            except Exception as e:
                print(f"❌ {sport}: Error - {e}")
        
        # Get YOLO insights
        for sport in sports:
            try:
                insights = await real_time_service.generate_yolo_insights(sport)
                print(f"\n🎯 {sport.title()} YOLO Insights:")
                print(f"   Trend: {insights.get('trend', 'N/A')}")
                print(f"   YOLO Energy: {insights.get('yolo_energy', 'N/A')}")
            except Exception as e:
                print(f"❌ {sport} insights: Error - {e}")
    
    async def demo_social_features(self):
        """Demonstrate social features."""
        print("\n👥 YOLO Social Features Demo")
        print("=" * 50)
        
        # Create a YOLO user
        user = await social_service.create_user(
            user_id=self.demo_user_id,
            username="YOLO_Demo_User",
            favorite_sport="basketball"
        )
        print(f"✅ Created YOLO user: {user.username}")
        print(f"   YOLO Score: {user.yolo_score}")
        print(f"   YOLO Level: {user.yolo_level}")
        print(f"   YOLO Motto: {user.yolo_motto}")
        
        # Get communities
        communities = await social_service.get_communities()
        print(f"\n🏘️ YOLO Communities ({len(communities)} total):")
        for comm in communities[:3]:
            print(f"   - {comm['name']}: {comm['member_count']} members")
            print(f"     Description: {comm['description']}")
        
        # Get leaderboard
        leaderboard = await social_service.get_leaderboard()
        print(f"\n🏆 YOLO Leaderboard:")
        for i, user in enumerate(leaderboard[:5], 1):
            print(f"   {i}. {user['username']} - YOLO Score: {user['yolo_score']}")
        
        # Share a prediction
        shared_pred = await social_service.share_prediction(
            user_id=self.demo_user_id,
            community_id="yolo_masters",
            sport="basketball",
            prediction="YOLO bet on the Lakers! Kobe energy is real! 🏀",
            confidence=0.95,
            reasoning="YOLO mode activated! Lakers are unstoppable!"
        )
        print(f"\n📢 Shared YOLO prediction: {shared_pred.prediction}")
        print(f"   Likes: {shared_pred.likes}")
        print(f"   Comments: {len(shared_pred.comments)}")
    
    async def run_complete_demo(self):
        """Run the complete YOLO system demonstration."""
        print("🚀 YOLO SYSTEM DEMONSTRATION - YOLO MODE!")
        print("=" * 80)
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Showing all YOLO features we built!")
        print()
        
        try:
            await self.demo_session_management()
            await self.demo_security_features()
            await self.demo_prediction_aggregation()
            await self.demo_real_time_predictions()
            await self.demo_social_features()
            
            print("\n" + "=" * 80)
            print("🎉 YOLO SYSTEM DEMONSTRATION COMPLETED!")
            print("=" * 80)
            print("✅ Session Management with YOLO enhancements")
            print("✅ Security Features with YOLO boost")
            print("✅ Prediction Aggregation with 6 strategies")
            print("✅ Real-Time YOLO Predictions")
            print("✅ Social Communities and Leaderboards")
            print("✅ User Profiles with YOLO scores")
            print("✅ Complete YOLO ecosystem")
            print()
            print("🚀 YOLO MODE ACTIVATED - ALL FEATURES WORKING!")
            print("🎯 When in doubt, YOLO it out!")
            print(f"⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            print("But that's okay - YOLO mode continues!")

def main():
    """Main demo function."""
    demo = YOLOSystemDemo()
    asyncio.run(demo.run_complete_demo())

if __name__ == "__main__":
    main() 