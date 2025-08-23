"""
Security Service - YOLO MODE!
===========================
Rate limiting, account lockout, and security features with YOLO enhancements.
"""

import time
import hashlib
import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(str, Enum):
    """Security level types."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    YOLO_MODE = "yolo_mode"

class AccountStatus(str, Enum):
    """Account status types."""
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    YOLO_VERIFIED = "yolo_verified"

@dataclass
class SecurityEvent:
    """Security event data structure."""
    event_id: str
    user_id: str
    event_type: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    severity: str
    yolo_factor: float
    details: Dict[str, Any]

@dataclass
class RateLimitInfo:
    """Rate limit information."""
    key: str
    requests: int
    window_start: datetime
    limit: int
    window_seconds: int
    yolo_boost: bool

class SecurityService:
    """Security service with YOLO enhancements."""
    
    def __init__(self):
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        self.security_events: List[SecurityEvent] = []
        self.yolo_mode_active = True
        
        # Security thresholds
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.rate_limit_window = 3600  # 1 hour
        self.max_requests_per_hour = 1000
        
    def generate_salt(self) -> str:
        """Generate a random salt for password hashing."""
        return secrets.token_hex(16)
    
    def hash_password(self, password: str, salt: str) -> str:
        """Hash a password with salt using SHA-256."""
        combined = password + salt
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_password(self, password: str, salt: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.hash_password(password, salt) == hashed_password
    
    def generate_token(self) -> str:
        """Generate a secure token."""
        return secrets.token_urlsafe(32)
    
    def check_rate_limit(self, key: str, limit: int = None, window_seconds: int = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits."""
        if limit is None:
            limit = self.max_requests_per_hour
        if window_seconds is None:
            window_seconds = self.rate_limit_window
        
        now = datetime.now()
        
        # Check if key exists and window is still valid
        if key in self.rate_limits:
            rate_info = self.rate_limits[key]
            
            # Check if window has expired
            if (now - rate_info.window_start).total_seconds() > window_seconds:
                # Reset window
                rate_info.requests = 1
                rate_info.window_start = now
                rate_info.yolo_boost = random.choice([True, False])  # Random YOLO boost
            else:
                # Increment requests
                rate_info.requests += 1
        else:
            # Create new rate limit entry
            self.rate_limits[key] = RateLimitInfo(
                key=key,
                requests=1,
                window_start=now,
                limit=limit,
                window_seconds=window_seconds,
                yolo_boost=random.choice([True, False])
            )
        
        rate_info = self.rate_limits[key]
        allowed = rate_info.requests <= limit
        
        # YOLO boost: sometimes allow extra requests
        if not allowed and rate_info.yolo_boost and random.random() < 0.1:
            allowed = True
            print(f"🚀 YOLO boost activated for {key} - extra request allowed!")
        
        return allowed, {
            "allowed": allowed,
            "requests": rate_info.requests,
            "limit": limit,
            "remaining": max(0, limit - rate_info.requests),
            "reset_time": (rate_info.window_start + timedelta(seconds=window_seconds)).isoformat(),
            "yolo_boost": rate_info.yolo_boost
        }
    
    def record_failed_attempt(self, user_id: str, ip_address: str, user_agent: str):
        """Record a failed login attempt."""
        now = datetime.now()
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        
        self.failed_attempts[user_id].append(now)
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id]
            if (now - attempt).total_seconds() < 3600
        ]
        
        # Check if account should be locked
        if len(self.failed_attempts[user_id]) >= self.max_failed_attempts:
            self.locked_accounts[user_id] = now
            print(f"🔒 Account locked: {user_id} due to too many failed attempts")
        
        # Record security event
        self.record_security_event(
            user_id=user_id,
            event_type="failed_login",
            ip_address=ip_address,
            user_agent=user_agent,
            severity="medium",
            details={"attempt_count": len(self.failed_attempts[user_id])}
        )
    
    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked."""
        if user_id not in self.locked_accounts:
            return False
        
        lock_time = self.locked_accounts[user_id]
        now = datetime.now()
        
        # Check if lockout period has expired
        if (now - lock_time).total_seconds() > self.lockout_duration:
            del self.locked_accounts[user_id]
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            return False
        
        return True
    
    def unlock_account(self, user_id: str):
        """Manually unlock an account."""
        if user_id in self.locked_accounts:
            del self.locked_accounts[user_id]
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        print(f"🔓 Account unlocked: {user_id}")
    
    def record_security_event(self, user_id: str, event_type: str, ip_address: str, 
                            user_agent: str, severity: str, details: Dict[str, Any]):
        """Record a security event."""
        event = SecurityEvent(
            event_id=f"sec_event_{int(time.time())}_{random.randint(1000, 9999)}",
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            severity=severity,
            yolo_factor=random.uniform(0.5, 2.0),
            details=details
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        now = datetime.now()
        
        # Count recent events
        recent_events = [
            event for event in self.security_events
            if (now - event.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        failed_logins = len([e for e in recent_events if e.event_type == "failed_login"])
        locked_accounts = len(self.locked_accounts)
        
        # Calculate YOLO security score
        yolo_security_score = 100.0 - (failed_logins * 5) - (locked_accounts * 10)
        yolo_security_score = max(0.0, yolo_security_score)
        
        return {
            "total_security_events": len(self.security_events),
            "recent_events_last_hour": len(recent_events),
            "failed_logins_last_hour": failed_logins,
            "locked_accounts": locked_accounts,
            "active_rate_limits": len(self.rate_limits),
            "yolo_security_score": round(yolo_security_score, 2),
            "security_level": "YOLO_MODE" if yolo_security_score > 80 else "HIGH" if yolo_security_score > 60 else "MEDIUM",
            "yolo_energy": "MAXIMUM!" if yolo_security_score > 90 else "HIGH" if yolo_security_score > 70 else "MEDIUM"
        }
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Basic IP address validation."""
        if not ip_address:
            return False
        
        # Simple validation - could be enhanced
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
        except ValueError:
            return False
        
        return True
    
    def validate_user_agent(self, user_agent: str) -> bool:
        """Basic user agent validation."""
        if not user_agent:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "bot", "crawler", "spider", "scraper", "curl", "wget"
        ]
        
        user_agent_lower = user_agent.lower()
        for pattern in suspicious_patterns:
            if pattern in user_agent_lower:
                return False
        
        return True
    
    def get_suspicious_activity(self) -> List[Dict[str, Any]]:
        """Get list of suspicious activities."""
        now = datetime.now()
        suspicious = []
        
        # Check for accounts with many failed attempts
        for user_id, attempts in self.failed_attempts.items():
            if len(attempts) >= 3:
                suspicious.append({
                    "type": "multiple_failed_attempts",
                    "user_id": user_id,
                    "attempt_count": len(attempts),
                    "last_attempt": attempts[-1].isoformat(),
                    "severity": "medium"
                })
        
        # Check for high rate limit usage
        for key, rate_info in self.rate_limits.items():
            if rate_info.requests > rate_info.limit * 0.8:  # 80% of limit
                suspicious.append({
                    "type": "high_rate_limit_usage",
                    "key": key,
                    "requests": rate_info.requests,
                    "limit": rate_info.limit,
                    "severity": "low"
                })
        
        # Check for recent security events
        recent_events = [
            event for event in self.security_events
            if (now - event.timestamp).total_seconds() < 300  # Last 5 minutes
        ]
        
        for event in recent_events:
            if event.severity in ["high", "critical"]:
                suspicious.append({
                    "type": "recent_security_event",
                    "event_id": event.event_id,
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "timestamp": event.timestamp.isoformat()
                })
        
        return suspicious
    
    def cleanup_old_data(self):
        """Clean up old security data."""
        now = datetime.now()
        
        # Clean old rate limits
        expired_keys = []
        for key, rate_info in self.rate_limits.items():
            if (now - rate_info.window_start).total_seconds() > rate_info.window_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.rate_limits[key]
        
        # Clean old security events (older than 24 hours)
        self.security_events = [
            event for event in self.security_events
            if (now - event.timestamp).total_seconds() < 86400
        ]
        
        if expired_keys:
            print(f"🧹 Cleaned up {len(expired_keys)} expired rate limits")

# Global instance
security_service = SecurityService() 