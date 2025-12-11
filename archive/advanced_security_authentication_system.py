#!/usr/bin/env python3
"""
Advanced Security & Authentication System - YOLO MODE!
======================================================
OAuth2, JWT tokens, role-based access control, encryption, and security monitoring
for ultra-secure sports betting platform
"""

import asyncio
import json
import time
import math
import random
import hashlib
import hmac
import base64
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict, deque
import uuid
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """User account information"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: str  # 'user', 'premium', 'admin'
    is_active: bool = True
    is_verified: bool = False
    created_at: str = ""
    last_login: str = ""
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None

@dataclass
class JWTToken:
    """JWT token information"""
    token_id: str
    user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: str = ""
    created_at: str = ""
    is_revoked: bool = False
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class SecurityEvent:
    """Security event log"""
    event_id: str
    timestamp: str
    event_type: str  # 'login', 'logout', 'failed_login', 'password_change', 'suspicious_activity'
    user_id: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    severity: str = "low"  # 'low', 'medium', 'high', 'critical'
    description: str = ""
    metadata: Dict[str, Any] = None

@dataclass
class RolePermission:
    """Role-based permission"""
    role: str
    permissions: List[str]
    description: str = ""

@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    endpoint: str
    max_requests: int
    time_window: int  # seconds
    user_type: str = "all"  # 'all', 'user', 'premium', 'admin'

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str
    jwt_expiry_hours: int = 24
    refresh_token_expiry_days: int = 30
    password_min_length: int = 8
    password_require_special: bool = True
    max_failed_logins: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    require_2fa_for_admin: bool = True

class PasswordManager:
    """Advanced password management"""
    
    def __init__(self):
        self.salt_length = 32
        self.hash_iterations = 100000
        self.hash_algorithm = 'sha256'
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(self.salt_length)
        hash_obj = hashlib.pbkdf2_hmac(
            self.hash_algorithm,
            password.encode('utf-8'),
            salt.encode('utf-8'),
            self.hash_iterations
        )
        return f"{salt}:{hash_obj.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            hash_obj = hashlib.pbkdf2_hmac(
                self.hash_algorithm,
                password.encode('utf-8'),
                salt.encode('utf-8'),
                self.hash_iterations
            )
            return hmac.compare_digest(hash_obj.hex(), hash_hex)
        except:
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors

class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret: str):
        self.secret = secret
        self.algorithm = "HS256"
    
    def create_access_token(self, user_id: str, role: str, expires_in_hours: int = 24) -> str:
        """Create JWT access token"""
        payload = {
            "user_id": user_id,
            "role": role,
            "type": "access",
            "exp": int(time.time()) + (expires_in_hours * 3600),
            "iat": int(time.time()),
            "jti": str(uuid.uuid4())
        }
        
        # Simple JWT encoding (in production, use proper JWT library)
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    def create_refresh_token(self, user_id: str, expires_in_days: int = 30) -> str:
        """Create JWT refresh token"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": int(time.time()) + (expires_in_days * 24 * 3600),
            "iat": int(time.time()),
            "jti": str(uuid.uuid4())
        }
        
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self.secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).rstrip(b'=').decode()
            
            if not hmac.compare_digest(signature_b64, expected_signature_b64):
                return None
            
            # Decode payload
            payload_json = base64.urlsafe_b64decode(payload_b64 + '=' * (4 - len(payload_b64) % 4))
            payload = json.loads(payload_json)
            
            # Check expiration
            if payload.get('exp', 0) < time.time():
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

class TwoFactorAuth:
    """Two-factor authentication"""
    
    def __init__(self):
        self.secret_length = 32
    
    def generate_secret(self) -> str:
        """Generate TOTP secret"""
        return base64.b32encode(secrets.token_bytes(self.secret_length)).decode()
    
    def generate_totp(self, secret: str, time_step: int = 30) -> str:
        """Generate TOTP code"""
        # Simplified TOTP generation
        current_time = int(time.time()) // time_step
        time_bytes = current_time.to_bytes(8, 'big')
        
        # Create HMAC
        hmac_obj = hmac.new(
            base64.b32decode(secret),
            time_bytes,
            hashlib.sha1
        )
        
        # Generate 6-digit code
        hmac_result = hmac_obj.digest()
        offset = hmac_result[-1] & 0xf
        code = ((hmac_result[offset] & 0x7f) << 24 |
                (hmac_result[offset + 1] & 0xff) << 16 |
                (hmac_result[offset + 2] & 0xff) << 8 |
                (hmac_result[offset + 3] & 0xff))
        
        return f"{code % 1000000:06d}"
    
    def verify_totp(self, secret: str, code: str, time_step: int = 30, window: int = 1) -> bool:
        """Verify TOTP code"""
        current_time = int(time.time()) // time_step
        
        for i in range(-window, window + 1):
            expected_code = self.generate_totp(secret, time_step)
            if code == expected_code:
                return True
        
        return False

class RateLimiter:
    """Rate limiting system"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.rules = {
            "/api/auth/login": RateLimitRule("/api/auth/login", 5, 300),  # 5 requests per 5 minutes
            "/api/auth/register": RateLimitRule("/api/auth/register", 3, 3600),  # 3 requests per hour
            "/api/predictions": RateLimitRule("/api/predictions", 100, 3600),  # 100 requests per hour
            "/api/admin": RateLimitRule("/api/admin", 50, 3600),  # 50 requests per hour
        }
    
    def is_allowed(self, endpoint: str, user_id: str = None, ip_address: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed"""
        if endpoint not in self.rules:
            return True, {}
        
        rule = self.rules[endpoint]
        key = f"{endpoint}:{user_id or ip_address}"
        
        current_time = time.time()
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if current_time - req_time < rule.time_window]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= rule.max_requests:
            return False, {
                "limit_exceeded": True,
                "max_requests": rule.max_requests,
                "time_window": rule.time_window,
                "reset_time": self.requests[key][0] + rule.time_window
            }
        
        # Add current request
        self.requests[key].append(current_time)
        
        return True, {
            "limit_exceeded": False,
            "requests_remaining": rule.max_requests - len(self.requests[key]),
            "reset_time": current_time + rule.time_window
        }

class SecurityMonitor:
    """Security monitoring and alerting"""
    
    def __init__(self):
        self.security_events = deque(maxlen=10000)
        self.suspicious_patterns = {
            "multiple_failed_logins": {"threshold": 3, "time_window": 300},
            "rapid_requests": {"threshold": 50, "time_window": 60},
            "unusual_ip": {"threshold": 1, "time_window": 3600},
            "admin_access": {"threshold": 1, "time_window": 300}
        }
        self.blocked_ips = set()
        self.blocked_users = set()
    
    def log_event(self, event: SecurityEvent):
        """Log security event"""
        self.security_events.append(event)
        logger.info(f"🔒 Security Event: {event.event_type} - {event.description}")
        
        # Check for suspicious patterns
        self._check_suspicious_patterns(event)
    
    def _check_suspicious_patterns(self, event: SecurityEvent):
        """Check for suspicious activity patterns"""
        current_time = time.time()
        
        # Check for multiple failed logins
        if event.event_type == "failed_login":
            recent_failures = [
                e for e in self.security_events
                if e.event_type == "failed_login" and 
                e.user_id == event.user_id and
                current_time - time.mktime(datetime.fromisoformat(e.timestamp).timetuple()) < 300
            ]
            
            if len(recent_failures) >= 3:
                self._create_alert("multiple_failed_logins", event.user_id, event.ip_address)
        
        # Check for rapid requests
        recent_requests = [
            e for e in self.security_events
            if e.ip_address == event.ip_address and
            current_time - time.mktime(datetime.fromisoformat(e.timestamp).timetuple()) < 60
        ]
        
        if len(recent_requests) >= 50:
            self._create_alert("rapid_requests", None, event.ip_address)
    
    def _create_alert(self, alert_type: str, user_id: str = None, ip_address: str = None):
        """Create security alert"""
        alert = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            event_type="suspicious_activity",
            user_id=user_id,
            ip_address=ip_address or "",
            severity="high",
            description=f"Suspicious activity detected: {alert_type}",
            metadata={"alert_type": alert_type}
        )
        
        self.security_events.append(alert)
        logger.warning(f"🚨 Security Alert: {alert_type} - User: {user_id}, IP: {ip_address}")
        
        # Block IP if necessary
        if ip_address and alert_type in ["rapid_requests", "multiple_failed_logins"]:
            self.blocked_ips.add(ip_address)
            logger.warning(f"🚫 IP {ip_address} blocked due to {alert_type}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is blocked"""
        return user_id in self.blocked_users
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events"""
        return [asdict(event) for event in list(self.security_events)[-limit:]]

class AdvancedSecuritySystem:
    """Advanced security and authentication system"""
    
    def __init__(self):
        # Initialize components
        self.config = SecurityConfig(
            jwt_secret=secrets.token_hex(32),
            jwt_expiry_hours=24,
            refresh_token_expiry_days=30,
            password_min_length=8,
            password_require_special=True,
            max_failed_logins=5,
            lockout_duration_minutes=30,
            session_timeout_minutes=60,
            require_2fa_for_admin=True
        )
        
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager(self.config.jwt_secret)
        self.two_factor_auth = TwoFactorAuth()
        self.rate_limiter = RateLimiter()
        self.security_monitor = SecurityMonitor()
        
        # User storage (in production, use database)
        self.users = {}
        self.tokens = {}
        
        # Role permissions
        self.role_permissions = {
            "user": RolePermission("user", [
                "read_predictions", "place_bets", "view_history", "update_profile"
            ], "Standard user permissions"),
            "premium": RolePermission("premium", [
                "read_predictions", "place_bets", "view_history", "update_profile",
                "advanced_analytics", "priority_support", "exclusive_predictions"
            ], "Premium user permissions"),
            "admin": RolePermission("admin", [
                "read_predictions", "place_bets", "view_history", "update_profile",
                "advanced_analytics", "priority_support", "exclusive_predictions",
                "manage_users", "view_security_logs", "system_configuration"
            ], "Administrator permissions")
        }
        
        logger.info("🚀 Advanced Security & Authentication System initialized - YOLO MODE!")
    
    async def register_user(self, username: str, email: str, password: str, 
                          ip_address: str = "", user_agent: str = "") -> Tuple[bool, str, Optional[User]]:
        """Register new user"""
        try:
            # Rate limiting
            allowed, rate_info = self.rate_limiter.is_allowed("/api/auth/register", ip_address=ip_address)
            if not allowed:
                return False, "Rate limit exceeded. Please try again later.", None
            
            # Validate input
            if not username or not email or not password:
                return False, "All fields are required", None
            
            # Check if user already exists
            if any(u.username == username for u in self.users.values()):
                return False, "Username already exists", None
            
            if any(u.email == email for u in self.users.values()):
                return False, "Email already registered", None
            
            # Validate password strength
            is_valid, errors = self.password_manager.validate_password_strength(password)
            if not is_valid:
                return False, f"Password validation failed: {'; '.join(errors)}", None
            
            # Create user
            user_id = str(uuid.uuid4())
            password_hash = self.password_manager.hash_password(password)
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role="user",
                created_at=datetime.now().isoformat()
            )
            
            self.users[user_id] = user
            
            # Log security event
            self.security_monitor.log_event(SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                event_type="user_registration",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                severity="low",
                description=f"New user registered: {username}"
            ))
            
            logger.info(f"✅ User registered: {username}")
            return True, "User registered successfully", user
            
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False, "Registration failed", None
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = "", user_agent: str = "",
                              totp_code: str = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticate user"""
        try:
            # Rate limiting
            allowed, rate_info = self.rate_limiter.is_allowed("/api/auth/login", ip_address=ip_address)
            if not allowed:
                return False, "Rate limit exceeded. Please try again later.", None
            
            # Check if IP is blocked
            if self.security_monitor.is_ip_blocked(ip_address):
                return False, "Access denied from this IP address", None
            
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                self._log_failed_login(None, ip_address, user_agent, "User not found")
                return False, "Invalid credentials", None
            
            # Check if user is locked
            if user.locked_until:
                lock_time = datetime.fromisoformat(user.locked_until)
                if datetime.now() < lock_time:
                    remaining = (lock_time - datetime.now()).seconds // 60
                    return False, f"Account locked. Try again in {remaining} minutes", None
                else:
                    user.locked_until = None
                    user.failed_login_attempts = 0
            
            # Check if user is blocked
            if self.security_monitor.is_user_blocked(user.user_id):
                return False, "Account has been suspended", None
            
            # Verify password
            if not self.password_manager.verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Check if account should be locked
                if user.failed_login_attempts >= self.config.max_failed_logins:
                    lock_until = datetime.now() + timedelta(minutes=self.config.lockout_duration_minutes)
                    user.locked_until = lock_until.isoformat()
                    self._log_failed_login(user.user_id, ip_address, user_agent, "Account locked")
                    return False, f"Account locked due to multiple failed attempts. Try again in {self.config.lockout_duration_minutes} minutes", None
                
                self._log_failed_login(user.user_id, ip_address, user_agent, "Invalid password")
                return False, "Invalid credentials", None
            
            # Check 2FA if enabled
            if user.two_factor_enabled:
                if not totp_code:
                    return False, "Two-factor authentication code required", None
                
                if not self.two_factor_auth.verify_totp(user.two_factor_secret, totp_code):
                    self._log_failed_login(user.user_id, ip_address, user_agent, "Invalid 2FA code")
                    return False, "Invalid two-factor authentication code", None
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now().isoformat()
            
            # Generate tokens
            access_token = self.jwt_manager.create_access_token(user.user_id, user.role)
            refresh_token = self.jwt_manager.create_refresh_token(user.user_id)
            
            # Store token
            token_id = str(uuid.uuid4())
            token = JWTToken(
                token_id=token_id,
                user_id=user.user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=(datetime.now() + timedelta(hours=self.config.jwt_expiry_hours)).isoformat(),
                created_at=datetime.now().isoformat(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.tokens[token_id] = token
            
            # Log successful login
            self.security_monitor.log_event(SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                event_type="login",
                user_id=user.user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                severity="low",
                description=f"User logged in: {user.username}"
            ))
            
            logger.info(f"✅ User authenticated: {user.username}")
            
            return True, "Authentication successful", {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": self.config.jwt_expiry_hours * 3600,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "two_factor_enabled": user.two_factor_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False, "Authentication failed", None
    
    def _log_failed_login(self, user_id: str, ip_address: str, user_agent: str, reason: str):
        """Log failed login attempt"""
        self.security_monitor.log_event(SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            event_type="failed_login",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity="medium",
            description=f"Failed login attempt: {reason}"
        ))
    
    async def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify JWT token"""
        try:
            payload = self.jwt_manager.verify_token(token)
            if not payload:
                return False, None
            
            # Check if token is revoked
            token_id = payload.get('jti')
            if token_id in self.tokens and self.tokens[token_id].is_revoked:
                return False, None
            
            # Get user
            user_id = payload.get('user_id')
            if user_id not in self.users:
                return False, None
            
            user = self.users[user_id]
            if not user.is_active:
                return False, None
            
            return True, {
                "user_id": user_id,
                "role": user.role,
                "username": user.username,
                "permissions": self.role_permissions[user.role].permissions
            }
            
        except Exception as e:
            logger.error(f"❌ Token verification error: {e}")
            return False, None
    
    async def refresh_token(self, refresh_token: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Refresh access token"""
        try:
            payload = self.jwt_manager.verify_token(refresh_token)
            if not payload or payload.get('type') != 'refresh':
                return False, "Invalid refresh token", None
            
            user_id = payload.get('user_id')
            if user_id not in self.users:
                return False, "User not found", None
            
            user = self.users[user_id]
            if not user.is_active:
                return False, "User account inactive", None
            
            # Generate new tokens
            access_token = self.jwt_manager.create_access_token(user.user_id, user.role)
            new_refresh_token = self.jwt_manager.create_refresh_token(user.user_id)
            
            # Revoke old refresh token
            token_id = payload.get('jti')
            if token_id in self.tokens:
                self.tokens[token_id].is_revoked = True
            
            # Store new token
            new_token_id = str(uuid.uuid4())
            token = JWTToken(
                token_id=new_token_id,
                user_id=user.user_id,
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_at=(datetime.now() + timedelta(hours=self.config.jwt_expiry_hours)).isoformat(),
                created_at=datetime.now().isoformat()
            )
            self.tokens[new_token_id] = token
            
            return True, "Token refreshed successfully", {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer",
                "expires_in": self.config.jwt_expiry_hours * 3600
            }
            
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False, "Token refresh failed", None
    
    async def logout(self, token: str) -> bool:
        """Logout user and revoke token"""
        try:
            payload = self.jwt_manager.verify_token(token)
            if payload:
                token_id = payload.get('jti')
                if token_id in self.tokens:
                    self.tokens[token_id].is_revoked = True
                
                # Log logout event
                self.security_monitor.log_event(SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    event_type="logout",
                    user_id=payload.get('user_id'),
                    severity="low",
                    description="User logged out"
                ))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Check if user has permission"""
        if user_role not in self.role_permissions:
            return False
        
        return permission in self.role_permissions[user_role].permissions
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security system status"""
        return {
            "total_users": len(self.users),
            "active_tokens": len([t for t in self.tokens.values() if not t.is_revoked]),
            "blocked_ips": len(self.security_monitor.blocked_ips),
            "blocked_users": len(self.security_monitor.blocked_users),
            "recent_events": len(self.security_monitor.security_events),
            "rate_limits": {endpoint: asdict(rule) for endpoint, rule in self.rate_limiter.rules.items()},
            "role_permissions": {role: asdict(perm) for role, perm in self.role_permissions.items()}
        }

async def main():
    """Test the advanced security and authentication system"""
    print("🚀 Testing Advanced Security & Authentication System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize security system
    security = AdvancedSecuritySystem()
    
    try:
        # Test user registration
        print("\n📝 Testing User Registration:")
        print("-" * 40)
        
        success, message, user = await security.register_user(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        
        if success:
            print(f"✅ Registration: {message}")
            print(f"   User ID: {user.user_id}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
        else:
            print(f"❌ Registration failed: {message}")
        
        # Test authentication
        print("\n🔐 Testing User Authentication:")
        print("-" * 40)
        
        success, message, auth_data = await security.authenticate_user(
            username="testuser",
            password="SecurePass123!",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        
        if success:
            print(f"✅ Authentication: {message}")
            print(f"   Access Token: {auth_data['access_token'][:50]}...")
            print(f"   Refresh Token: {auth_data['refresh_token'][:50]}...")
            print(f"   User Role: {auth_data['user']['role']}")
            print(f"   2FA Enabled: {auth_data['user']['two_factor_enabled']}")
        else:
            print(f"❌ Authentication failed: {message}")
        
        # Test token verification
        if success:
            print("\n🔍 Testing Token Verification:")
            print("-" * 40)
            
            is_valid, user_data = await security.verify_token(auth_data['access_token'])
            
            if is_valid:
                print(f"✅ Token verification successful")
                print(f"   User ID: {user_data['user_id']}")
                print(f"   Role: {user_data['role']}")
                print(f"   Permissions: {user_data['permissions']}")
            else:
                print(f"❌ Token verification failed")
        
        # Test permission checking
        print("\n🔒 Testing Permission System:")
        print("-" * 40)
        
        permissions_to_test = ["read_predictions", "place_bets", "manage_users", "system_configuration"]
        
        for permission in permissions_to_test:
            has_perm = security.has_permission("user", permission)
            print(f"   User permission '{permission}': {'✅' if has_perm else '❌'}")
        
        for permission in permissions_to_test:
            has_perm = security.has_permission("admin", permission)
            print(f"   Admin permission '{permission}': {'✅' if has_perm else '❌'}")
        
        # Test security monitoring
        print("\n🛡️ Testing Security Monitoring:")
        print("-" * 40)
        
        # Simulate failed login attempts
        for i in range(3):
            await security.authenticate_user(
                username="testuser",
                password="wrongpassword",
                ip_address="192.168.1.100"
            )
        
        # Get security status
        security_status = security.get_security_status()
        print(f"✅ Total Users: {security_status['total_users']}")
        print(f"✅ Active Tokens: {security_status['active_tokens']}")
        print(f"✅ Blocked IPs: {security_status['blocked_ips']}")
        print(f"✅ Recent Events: {security_status['recent_events']}")
        
        # Get recent security events
        recent_events = security.security_monitor.get_recent_events(5)
        print(f"\n📋 Recent Security Events:")
        for event in recent_events:
            print(f"   {event['event_type']}: {event['description']} ({event['severity']})")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Advanced Security & Authentication System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 