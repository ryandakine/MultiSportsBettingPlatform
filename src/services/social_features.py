"""
Social Features Service - YOLO MODE!
==================================
Community features, shared predictions, and YOLO leaderboards.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class CommunityType(str, Enum):
    """Types of YOLO communities."""
    YOLO_MASTERS = "yolo_masters"
    SPORT_SPECIFIC = "sport_specific"
    RISK_TAKERS = "risk_takers"
    UNDERDOG_LOVERS = "underdog_lovers"
    HOME_TEAM_FANS = "home_team_fans"

@dataclass
class YOLOUser:
    """YOLO user profile."""
    user_id: str
    username: str
    yolo_score: float
    total_predictions: int
    successful_predictions: int
    favorite_sport: str
    yolo_level: str
    join_date: datetime
    last_active: datetime
    yolo_motto: str

@dataclass
class YOLOCommunity:
    """YOLO community."""
    community_id: str
    name: str
    description: str
    type: CommunityType
    members: List[str]
    total_predictions: int
    success_rate: float
    created_date: datetime
    yolo_energy: float

@dataclass
class SharedPrediction:
    """Shared prediction in community."""
    prediction_id: str
    user_id: str
    username: str
    sport: str
    prediction: str
    confidence: float
    reasoning: str
    community_id: str
    likes: int
    comments: List[Dict[str, Any]]
    timestamp: datetime
    yolo_factor: float

class SocialFeaturesService:
    """Social features service with YOLO enhancements."""
    
    def __init__(self):
        self.users: Dict[str, YOLOUser] = {}
        self.communities: Dict[str, YOLOCommunity] = {}
        self.shared_predictions: Dict[str, SharedPrediction] = {}
        self.user_communities: Dict[str, List[str]] = {}
        
        # Initialize with some YOLO data
        self._initialize_yolo_data()
    
    def _initialize_yolo_data(self):
        """Initialize with some YOLO data."""
        # Create some YOLO users
        yolo_users = [
            ("yolo_master_1", "YOLO_Master_Pro", 95.5, 150, 142, "basketball", "YOLO Legend", "YOLO or nothing! 🚀"),
            ("yolo_master_2", "UnderdogHunter", 88.2, 120, 108, "football", "YOLO Champion", "Underdogs are the way! 🎯"),
            ("yolo_master_3", "HomeCourtHero", 92.1, 200, 184, "basketball", "YOLO Master", "Home court advantage! 🏠"),
            ("yolo_master_4", "RiskTaker_Elite", 89.7, 180, 162, "baseball", "YOLO Expert", "High risk, high reward! 💰"),
            ("yolo_master_5", "HockeyYOLO", 87.3, 95, 83, "hockey", "YOLO Pro", "Hockey is unpredictable - perfect! 🏒")
        ]
        
        for user_id, username, score, total, success, sport, level, motto in yolo_users:
            self.users[user_id] = YOLOUser(
                user_id=user_id,
                username=username,
                yolo_score=score,
                total_predictions=total,
                successful_predictions=success,
                favorite_sport=sport,
                yolo_level=level,
                join_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                last_active=datetime.now() - timedelta(hours=random.randint(1, 24)),
                yolo_motto=motto
            )
        
        # Create YOLO communities
        communities = [
            ("yolo_masters", "YOLO Masters Elite", "The ultimate YOLO prediction community", CommunityType.YOLO_MASTERS),
            ("basketball_yolo", "Basketball YOLO Legends", "Basketball predictions with maximum YOLO", CommunityType.SPORT_SPECIFIC),
            ("underdog_army", "Underdog Army", "We bet on underdogs and win big!", CommunityType.UNDERDOG_LOVERS),
            ("risk_takers_united", "Risk Takers United", "High risk, high reward predictions", CommunityType.RISK_TAKERS),
            ("home_team_nation", "Home Team Nation", "Home court advantage believers", CommunityType.HOME_TEAM_FANS)
        ]
        
        for comm_id, name, desc, comm_type in communities:
            self.communities[comm_id] = YOLOCommunity(
                community_id=comm_id,
                name=name,
                description=desc,
                type=comm_type,
                members=list(self.users.keys())[:random.randint(3, 5)],
                total_predictions=random.randint(50, 200),
                success_rate=random.uniform(0.75, 0.95),
                created_date=datetime.now() - timedelta(days=random.randint(60, 180)),
                yolo_energy=random.uniform(0.8, 1.0)
            )
    
    async def create_user(self, user_id: str, username: str, favorite_sport: str) -> YOLOUser:
        """Create a new YOLO user."""
        yolo_mottos = [
            "YOLO or nothing! 🚀",
            "When in doubt, YOLO it out! 🎯",
            "High risk, high reward! 💰",
            "Trust the YOLO! 🏆",
            "YOLO mode activated! ⚡",
            "Bet with confidence! 🎲",
            "YOLO predictions never fail! 🎯",
            "Live life on the edge! 🚀"
        ]
        
        user = YOLOUser(
            user_id=user_id,
            username=username,
            yolo_score=50.0,  # Starting score
            total_predictions=0,
            successful_predictions=0,
            favorite_sport=favorite_sport,
            yolo_level="YOLO Rookie",
            join_date=datetime.now(),
            last_active=datetime.now(),
            yolo_motto=random.choice(yolo_mottos)
        )
        
        self.users[user_id] = user
        return user
    
    async def join_community(self, user_id: str, community_id: str) -> bool:
        """Join a YOLO community."""
        if user_id not in self.users or community_id not in self.communities:
            return False
        
        if user_id not in self.communities[community_id].members:
            self.communities[community_id].members.append(user_id)
        
        if user_id not in self.user_communities:
            self.user_communities[user_id] = []
        
        if community_id not in self.user_communities[user_id]:
            self.user_communities[user_id].append(community_id)
        
        return True
    
    async def share_prediction(self, user_id: str, community_id: str, sport: str, 
                             prediction: str, confidence: float, reasoning: str) -> SharedPrediction:
        """Share a prediction in a community."""
        if user_id not in self.users or community_id not in self.communities:
            raise ValueError("Invalid user or community")
        
        prediction_id = f"shared_pred_{int(datetime.now().timestamp())}"
        
        shared_pred = SharedPrediction(
            prediction_id=prediction_id,
            user_id=user_id,
            username=self.users[user_id].username,
            sport=sport,
            prediction=prediction,
            confidence=confidence,
            reasoning=reasoning,
            community_id=community_id,
            likes=0,
            comments=[],
            timestamp=datetime.now(),
            yolo_factor=random.uniform(1.0, 2.0)
        )
        
        self.shared_predictions[prediction_id] = shared_pred
        
        # Update user stats
        self.users[user_id].total_predictions += 1
        self.users[user_id].last_active = datetime.now()
        
        # Update community stats
        self.communities[community_id].total_predictions += 1
        
        return shared_pred
    
    async def like_prediction(self, prediction_id: str, user_id: str) -> bool:
        """Like a shared prediction."""
        if prediction_id not in self.shared_predictions:
            return False
        
        prediction = self.shared_predictions[prediction_id]
        prediction.likes += 1
        
        # Boost YOLO factor when liked
        prediction.yolo_factor *= 1.05
        
        return True
    
    async def comment_on_prediction(self, prediction_id: str, user_id: str, comment: str) -> bool:
        """Comment on a shared prediction."""
        if prediction_id not in self.shared_predictions or user_id not in self.users:
            return False
        
        prediction = self.shared_predictions[prediction_id]
        
        new_comment = {
            "comment_id": f"comment_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "username": self.users[user_id].username,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
            "yolo_energy": random.uniform(0.8, 1.2)
        }
        
        prediction.comments.append(new_comment)
        
        # Boost YOLO factor when commented
        prediction.yolo_factor *= 1.02
        
        return True
    
    async def get_leaderboard(self, community_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get YOLO leaderboard."""
        users_list = list(self.users.values())
        
        if community_id and community_id in self.communities:
            # Filter by community members
            community_members = self.communities[community_id].members
            users_list = [u for u in users_list if u.user_id in community_members]
        
        # Sort by YOLO score
        users_list.sort(key=lambda x: x.yolo_score, reverse=True)
        
        leaderboard = []
        for i, user in enumerate(users_list[:10]):  # Top 10
            leaderboard.append({
                "rank": i + 1,
                "user_id": user.user_id,
                "username": user.username,
                "yolo_score": user.yolo_score,
                "total_predictions": user.total_predictions,
                "success_rate": user.successful_predictions / max(user.total_predictions, 1),
                "yolo_level": user.yolo_level,
                "favorite_sport": user.favorite_sport,
                "yolo_motto": user.yolo_motto
            })
        
        return leaderboard
    
    async def get_community_predictions(self, community_id: str) -> List[Dict[str, Any]]:
        """Get recent predictions from a community."""
        if community_id not in self.communities:
            return []
        
        community_predictions = [
            p for p in self.shared_predictions.values() 
            if p.community_id == community_id
        ]
        
        # Sort by timestamp (newest first)
        community_predictions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "prediction_id": p.prediction_id,
                "user_id": p.user_id,
                "username": p.username,
                "sport": p.sport,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "reasoning": p.reasoning,
                "likes": p.likes,
                "comments_count": len(p.comments),
                "timestamp": p.timestamp.isoformat(),
                "yolo_factor": p.yolo_factor
            }
            for p in community_predictions[:20]  # Recent 20
        ]
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with YOLO stats."""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        user_communities = self.user_communities.get(user_id, [])
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "yolo_score": user.yolo_score,
            "total_predictions": user.total_predictions,
            "successful_predictions": user.successful_predictions,
            "success_rate": user.successful_predictions / max(user.total_predictions, 1),
            "favorite_sport": user.favorite_sport,
            "yolo_level": user.yolo_level,
            "join_date": user.join_date.isoformat(),
            "last_active": user.last_active.isoformat(),
            "yolo_motto": user.yolo_motto,
            "communities": [
                {
                    "community_id": comm_id,
                    "name": self.communities[comm_id].name,
                    "type": self.communities[comm_id].type.value
                }
                for comm_id in user_communities
                if comm_id in self.communities
            ]
        }
    
    async def get_communities(self) -> List[Dict[str, Any]]:
        """Get all YOLO communities."""
        return [
            {
                "community_id": comm.community_id,
                "name": comm.name,
                "description": comm.description,
                "type": comm.type.value,
                "member_count": len(comm.members),
                "total_predictions": comm.total_predictions,
                "success_rate": comm.success_rate,
                "created_date": comm.created_date.isoformat(),
                "yolo_energy": comm.yolo_energy
            }
            for comm in self.communities.values()
        ]

# Global instance
social_service = SocialFeaturesService() 