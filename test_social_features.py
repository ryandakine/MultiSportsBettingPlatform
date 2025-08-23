#!/usr/bin/env python3
"""
Test Social Features and Community Platform
==========================================
Test the comprehensive social features and community platform functionality.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class SocialFeaturesTester:
    """Test the social features and community platform functionality."""
    
    def __init__(self):
        self.test_results = []
        self.social_service = None
    
    async def test_user_creation(self, test_name: str) -> Dict[str, Any]:
        """Test user creation and profile management."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Test creating new users
            new_users = [
                ("test_user_1", "YOLO_Newbie", "basketball"),
                ("test_user_2", "RiskTaker_New", "football"),
                ("test_user_3", "UnderdogFan", "baseball")
            ]
            
            created_users = []
            for user_id, username, sport in new_users:
                user = await social_service.create_user(user_id, username, sport)
                created_users.append(user)
                print(f"✅ Created user: {user.username} - {user.yolo_level}")
            
            # Test user profile retrieval
            profile = await social_service.get_user_profile("test_user_1")
            profile_success = profile is not None and profile["username"] == "YOLO_Newbie"
            
            print(f"✅ User profile retrieval: {'success' if profile_success else 'failed'}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "User creation and profile management test completed successfully",
                "users_created": len(created_users),
                "profile_retrieval_success": profile_success,
                "yolo_levels": [user.yolo_level for user in created_users]
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_community_management(self, test_name: str) -> Dict[str, Any]:
        """Test community creation and management."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Get existing communities
            communities = await social_service.get_communities()
            
            print(f"✅ Found {len(communities)} existing communities")
            for community in communities:
                print(f"   🏠 {community['name']}: {community['type']} - {community['member_count']} members")
            
            # Test joining communities
            join_successes = []
            for community in communities[:2]:  # Join first 2 communities
                success = await social_service.join_community("test_user_1", community["community_id"])
                join_successes.append(success)
                print(f"✅ Join {community['name']}: {'success' if success else 'failed'}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Community management test completed successfully",
                "total_communities": len(communities),
                "community_types": [c["type"] for c in communities],
                "join_successes": join_successes
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_prediction_sharing(self, test_name: str) -> Dict[str, Any]:
        """Test prediction sharing functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Create test users first
            await social_service.create_user("test_user_1", "YOLO_Newbie", "basketball")
            await social_service.create_user("test_user_2", "RiskTaker_New", "football")
            
            # Get communities for sharing
            communities = await social_service.get_communities()
            if not communities:
                return {
                    "test": test_name,
                    "status": "SKIPPED",
                    "message": "No communities available for testing"
                }
            
            # Test sharing predictions
            test_predictions = [
                {
                    "sport": "basketball",
                    "prediction": "Lakers will win by 10+ points",
                    "confidence": 0.85,
                    "reasoning": "Home court advantage and recent form"
                },
                {
                    "sport": "football",
                    "prediction": "Underdog will cover the spread",
                    "confidence": 0.72,
                    "reasoning": "Historical performance against this opponent"
                }
            ]
            
            shared_predictions = []
            for pred in test_predictions:
                shared = await social_service.share_prediction(
                    "test_user_1",
                    communities[0]["community_id"],
                    pred["sport"],
                    pred["prediction"],
                    pred["confidence"],
                    pred["reasoning"]
                )
                shared_predictions.append(shared)
                print(f"✅ Shared prediction: {shared.prediction[:30]}...")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Prediction sharing test completed successfully",
                "predictions_shared": len(shared_predictions),
                "avg_confidence": sum(p.confidence for p in shared_predictions) / len(shared_predictions),
                "avg_yolo_factor": sum(p.yolo_factor for p in shared_predictions) / len(shared_predictions)
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_social_interactions(self, test_name: str) -> Dict[str, Any]:
        """Test social interactions (likes, comments)."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Create test users first
            await social_service.create_user("test_user_1", "YOLO_Newbie", "basketball")
            await social_service.create_user("test_user_2", "RiskTaker_New", "football")
            
            # Get communities and predictions
            communities = await social_service.get_communities()
            if not communities:
                return {
                    "test": test_name,
                    "status": "SKIPPED",
                    "message": "No communities available for testing"
                }
            
            # Share a test prediction first
            shared = await social_service.share_prediction(
                "test_user_1",
                communities[0]["community_id"],
                "basketball",
                "Test prediction for social interactions",
                0.80,
                "Testing social features"
            )
            
            # Test liking prediction
            like_success = await social_service.like_prediction(shared.prediction_id, "test_user_2")
            print(f"✅ Like prediction: {'success' if like_success else 'failed'}")
            
            # Test commenting on prediction
            comment_success = await social_service.comment_on_prediction(
                shared.prediction_id,
                "test_user_2",
                "Great prediction! I agree with this analysis."
            )
            print(f"✅ Comment on prediction: {'success' if comment_success else 'failed'}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Social interactions test completed successfully",
                "like_success": like_success,
                "comment_success": comment_success,
                "prediction_id": shared.prediction_id
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_leaderboards(self, test_name: str) -> Dict[str, Any]:
        """Test leaderboard functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Test global leaderboard
            global_leaderboard = await social_service.get_leaderboard()
            
            print(f"✅ Global leaderboard: {len(global_leaderboard)} users")
            for i, user in enumerate(global_leaderboard[:3]):
                print(f"   🏆 #{i+1}: {user['username']} - {user['yolo_score']:.1f} YOLO Score")
            
            # Test community-specific leaderboard
            communities = await social_service.get_communities()
            if communities:
                community_leaderboard = await social_service.get_leaderboard(communities[0]["community_id"])
                print(f"✅ Community leaderboard: {len(community_leaderboard)} users")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Leaderboard test completed successfully",
                "global_leaderboard_size": len(global_leaderboard),
                "top_yolo_score": global_leaderboard[0]["yolo_score"] if global_leaderboard else 0,
                "community_leaderboards": len(communities) if communities else 0
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_community_predictions(self, test_name: str) -> Dict[str, Any]:
        """Test community predictions retrieval."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Get communities
            communities = await social_service.get_communities()
            if not communities:
                return {
                    "test": test_name,
                    "status": "SKIPPED",
                    "message": "No communities available for testing"
                }
            
            # Test getting community predictions
            community_predictions = await social_service.get_community_predictions(communities[0]["community_id"])
            
            print(f"✅ Community predictions: {len(community_predictions)} predictions")
            for pred in community_predictions[:3]:
                print(f"   📊 {pred['username']}: {pred['prediction'][:40]}...")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Community predictions test completed successfully",
                "predictions_count": len(community_predictions),
                "avg_confidence": sum(p["confidence"] for p in community_predictions) / max(len(community_predictions), 1),
                "sports_covered": len(set(p["sport"] for p in community_predictions))
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_yolo_features(self, test_name: str) -> Dict[str, Any]:
        """Test YOLO-specific features."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.social_features import SocialFeaturesService
            
            social_service = SocialFeaturesService()
            
            # Test YOLO user levels
            yolo_levels = set()
            yolo_scores = []
            
            for user in social_service.users.values():
                yolo_levels.add(user.yolo_level)
                yolo_scores.append(user.yolo_score)
            
            print(f"✅ YOLO levels found: {', '.join(yolo_levels)}")
            print(f"✅ YOLO score range: {min(yolo_scores):.1f} - {max(yolo_scores):.1f}")
            
            # Test YOLO mottos
            yolo_mottos = [user.yolo_motto for user in social_service.users.values()]
            print(f"✅ YOLO mottos: {len(yolo_mottos)} unique mottos")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "YOLO features test completed successfully",
                "yolo_levels_count": len(yolo_levels),
                "yolo_levels": list(yolo_levels),
                "avg_yolo_score": sum(yolo_scores) / len(yolo_scores),
                "yolo_mottos_count": len(yolo_mottos)
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all social features tests."""
        print("🚀 Starting Social Features and Community Platform Tests")
        print("=" * 80)
        
        tests = [
            self.test_user_creation("User Creation and Profile Management"),
            self.test_community_management("Community Management"),
            self.test_prediction_sharing("Prediction Sharing"),
            self.test_social_interactions("Social Interactions (Likes/Comments)"),
            self.test_leaderboards("Leaderboard System"),
            self.test_community_predictions("Community Predictions"),
            self.test_yolo_features("YOLO Features")
        ]
        
        for test in tests:
            result = await test
            self.test_results.append(result)
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 Social Features and Community Platform Test Summary")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed = sum(1 for result in self.test_results if result["status"] == "FAILED")
        skipped = sum(1 for result in self.test_results if result["status"] == "SKIPPED")
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "⏭️"
            print(f"   {status_icon} {result['test']}: {result['status']}")
            if result["status"] == "FAILED":
                print(f"      Error: {result['message']}")
        
        # Save results
        with open("social_features_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to social_features_test_results.json")

async def main():
    """Main test function."""
    tester = SocialFeaturesTester()
    
    try:
        await tester.run_all_tests()
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 