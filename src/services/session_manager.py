"""
Session Management Service - YOLO MODE!
====================================
Redis-based session management with YOLO enhancements.
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class SessionStatus(str, Enum):
    """Session status types."""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    YOLO_MODE = "yolo_mode"

@dataclass
class UserSession:
    """User session data structure."""
    session_id: str
    user_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    status: SessionStatus
    yolo_level: str
    yolo_score: float
    active_predictions: List[str]
    preferences: Dict[str, Any]
    ip_address: str
    user_agent: str

class MockRedisClient:
    """Mock Redis client for development."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.expiry: Dict[str, float] = {}
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set a key-value pair."""
        self.data[key] = value
        if ex:
            self.expiry[key] = time.time() + ex
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        return self.data.get(key)
    
    async def delete(self, key: str):
        """Delete a key."""
        if key in self.data:
            del self.data[key]
        if key in self.expiry:
            del self.expiry[key]
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return False
        return key in self.data
    
    async def expire(self, key: str, seconds: int):
        """Set expiration for a key."""
        self.expiry[key] = time.time() + seconds

class SessionManager:
    """Session management service with YOLO enhancements."""
    
    def __init__(self):
        self.redis_client = MockRedisClient()
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.active_sessions: Dict[str, UserSession] = {}
        self.yolo_mode_active = True
    
    async def create_session(self, user_id: str, username: str, ip_address: str, 
                           user_agent: str, yolo_level: str = "YOLO Rookie") -> UserSession:
        """Create a new user session with YOLO enhancements."""
        
        session_id = f"yolo_session_{int(time.time())}_{random.randint(1000, 9999)}"
        now = datetime.now()
        expires_at = now + timedelta(hours=24)  # 24-hour session
        
        # Generate YOLO score for the session
        yolo_score = random.uniform(50.0, 100.0)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            status=SessionStatus.YOLO_MODE,
            yolo_level=yolo_level,
            yolo_score=yolo_score,
            active_predictions=[],
            preferences={
                "favorite_sports": ["basketball", "football"],
                "yolo_mode": True,
                "notifications": True,
                "theme": "yolo_dark"
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store in Redis
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "username": session.username,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "status": session.status.value,
            "yolo_level": session.yolo_level,
            "yolo_score": session.yolo_score,
            "active_predictions": session.active_predictions,
            "preferences": session.preferences,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent
        }
        
        await self.redis_client.set(
            f"{self.session_prefix}{session_id}",
            json.dumps(session_data),
            ex=86400  # 24 hours
        )
        
        # Store user session mapping
        await self.redis_client.set(
            f"{self.user_sessions_prefix}{user_id}",
            session_id,
            ex=86400
        )
        
        self.active_sessions[session_id] = session
        
        print(f"🔐 YOLO Session created: {session_id} for {username}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        session_data = await self.redis_client.get(f"{self.session_prefix}{session_id}")
        
        if not session_data:
            return None
        
        try:
            data = json.loads(session_data)
            session = UserSession(
                session_id=data["session_id"],
                user_id=data["user_id"],
                username=data["username"],
                created_at=datetime.fromisoformat(data["created_at"]),
                last_activity=datetime.fromisoformat(data["last_activity"]),
                expires_at=datetime.fromisoformat(data["expires_at"]),
                status=SessionStatus(data["status"]),
                yolo_level=data["yolo_level"],
                yolo_score=data["yolo_score"],
                active_predictions=data["active_predictions"],
                preferences=data["preferences"],
                ip_address=data["ip_address"],
                user_agent=data["user_agent"]
            )
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                await self.delete_session(session_id)
                return None
            
            return session
        except Exception as e:
            print(f"❌ Error loading session {session_id}: {e}")
            return None
    
    async def update_session_activity(self, session_id: str):
        """Update session last activity."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.last_activity = datetime.now()
        
        # Boost YOLO score for activity
        session.yolo_score = min(100.0, session.yolo_score + random.uniform(0.1, 0.5))
        
        # Update in Redis
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "username": session.username,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "status": session.status.value,
            "yolo_level": session.yolo_level,
            "yolo_score": session.yolo_score,
            "active_predictions": session.active_predictions,
            "preferences": session.preferences,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent
        }
        
        await self.redis_client.set(
            f"{self.session_prefix}{session_id}",
            json.dumps(session_data),
            ex=86400
        )
        
        return True
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        session = await self.get_session(session_id)
        if session:
            await self.redis_client.delete(f"{self.session_prefix}{session_id}")
            await self.redis_client.delete(f"{self.user_sessions_prefix}{session.user_id}")
            
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            print(f"🔐 YOLO Session deleted: {session_id}")
    
    async def get_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get session by user ID."""
        session_id = await self.redis_client.get(f"{self.user_sessions_prefix}{user_id}")
        if session_id:
            return await self.get_session(session_id)
        return None
    
    async def add_prediction_to_session(self, session_id: str, prediction_id: str):
        """Add a prediction to user's active predictions."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        if prediction_id not in session.active_predictions:
            session.active_predictions.append(prediction_id)
            
            # Boost YOLO score for making predictions
            session.yolo_score = min(100.0, session.yolo_score + random.uniform(1.0, 3.0))
            
            # Update in Redis
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "username": session.username,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "status": session.status.value,
                "yolo_level": session.yolo_level,
                "yolo_score": session.yolo_score,
                "active_predictions": session.active_predictions,
                "preferences": session.preferences,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent
            }
            
            await self.redis_client.set(
                f"{self.session_prefix}{session_id}",
                json.dumps(session_data),
                ex=86400
            )
        
        return True
    
    async def update_user_preferences(self, session_id: str, preferences: Dict[str, Any]):
        """Update user preferences."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session.preferences.update(preferences)
        
        # Update in Redis
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "username": session.username,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "status": session.status.value,
            "yolo_level": session.yolo_level,
            "yolo_score": session.yolo_score,
            "active_predictions": session.active_predictions,
            "preferences": session.preferences,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent
        }
        
        await self.redis_client.set(
            f"{self.session_prefix}{session_id}",
            json.dumps(session_data),
            ex=86400
        )
        
        return True
    
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions)
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.active_sessions)
        yolo_sessions = sum(1 for s in self.active_sessions.values() if s.status == SessionStatus.YOLO_MODE)
        
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "yolo_sessions": 0,
                "average_yolo_score": 0.0,
                "most_active_user": "None",
                "yolo_energy": "MINIMAL"
            }
        
        avg_yolo_score = sum(s.yolo_score for s in self.active_sessions.values()) / total_sessions
        
        # Find most active user
        most_active = max(self.active_sessions.values(), key=lambda s: len(s.active_predictions))
        
        return {
            "total_sessions": total_sessions,
            "yolo_sessions": yolo_sessions,
            "average_yolo_score": round(avg_yolo_score, 2),
            "most_active_user": most_active.username,
            "most_active_predictions": len(most_active.active_predictions),
            "yolo_energy": "MAXIMUM!" if yolo_sessions > 0 else "MINIMAL"
        }
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if datetime.now() > session.expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.delete_session(session_id)
        
        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired YOLO sessions")

# Global instance
session_manager = SessionManager() 