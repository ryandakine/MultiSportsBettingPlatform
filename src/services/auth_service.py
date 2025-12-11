"""
Authentication and Session Management Service

This module provides comprehensive user authentication, session management,
and security features for the MultiSportsBettingPlatform.
"""

import os
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import bcrypt
import redis
from pydantic import BaseModel, EmailStr, validator
import logging
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.db.models.user import User as UserModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for access control."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    ANALYST = "analyst"

class AuthStatus(Enum):
    """Authentication status codes."""
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    ACCOUNT_LOCKED = "account_locked"
    TOKEN_EXPIRED = "token_expired"
    INVALID_TOKEN = "invalid_token"
    RATE_LIMITED = "rate_limited"

@dataclass
class User:
    """User data model."""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = None
    last_login: datetime = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.preferences is None:
            self.preferences = {}

@dataclass
class Session:
    """Session data model."""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class UserRegistration(BaseModel):
    """User registration request model."""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be between 3 and 30 characters')
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str
    remember_me: bool = False

class PasswordReset(BaseModel):
    """Password reset request model."""
    email: EmailStr

class PasswordChange(BaseModel):
    """Password change request model."""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class AuthService:
    """Authentication and session management service."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 jwt_secret: str = None, jwt_algorithm: str = "HS256"):
        """Initialize the authentication service."""
        self.redis_url = redis_url
        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.jwt_algorithm = jwt_algorithm
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = 15  # minutes
        self.session_timeout = 24  # hours
        self.remember_me_timeout = 30  # days
        self.password_reset_timeout = 1  # hour
        
        # Rate limiting settings
        self.rate_limit_requests = 100  # requests per hour
        self.rate_limit_window = 3600  # seconds
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
    
    def _generate_user_id(self) -> str:
        """Generate a unique user ID."""
        return f"user_{int(time.time())}_{secrets.token_hex(8)}"
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{int(time.time())}_{secrets.token_hex(16)}"
    
    def _create_jwt_token(self, user_id: str, role: str, expires_in: int = None) -> str:
        """Create a JWT token for the user."""
        if expires_in is None:
            expires_in = self.session_timeout * 3600  # Convert hours to seconds
        
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _decode_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def _is_rate_limited(self, identifier: str, limit_type: str = "auth") -> bool:
        """Check if a request is rate limited."""
        if not self.redis_client:
            return False
        
        key = f"rate_limit:{limit_type}:{identifier}"
        current_count = self.redis_client.get(key)
        
        if current_count is None:
            self.redis_client.setex(key, self.rate_limit_window, 1)
            return False
        
        count = int(current_count)
        if count >= self.rate_limit_requests:
            return True
        
        self.redis_client.incr(key)
        return False
    
    def _increment_login_attempts(self, username: str) -> int:
        """Increment failed login attempts for a user."""
        if not self.redis_client:
            return 0
        
        key = f"login_attempts:{username}"
        attempts = self.redis_client.incr(key)
        self.redis_client.expire(key, self.lockout_duration * 60)
        return attempts
    
    def _check_account_locked(self, username: str) -> bool:
        """Check if an account is locked due to too many failed attempts."""
        if not self.redis_client:
            return False
        
        key = f"login_attempts:{username}"
        attempts = self.redis_client.get(key)
        
        if attempts and int(attempts) >= self.max_login_attempts:
            return True
        
        return False
    
    def _reset_login_attempts(self, username: str):
        """Reset failed login attempts for a user."""
        if self.redis_client:
            key = f"login_attempts:{username}"
            self.redis_client.delete(key)
    
    def register_user(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register a new user."""
        db = SessionLocal()
        try:
            # Check rate limiting (keep Redis for this)
            if self._is_rate_limited("registration", "registration"):
                return {
                    "status": AuthStatus.RATE_LIMITED,
                    "message": "Too many registration attempts. Please try again later."
                }
            
            # Check if username or email already exists
            existing_user = db.query(UserModel).filter(
                (UserModel.username == registration.username) | 
                (UserModel.email == registration.email)
            ).first()
            
            if existing_user:
                if existing_user.username == registration.username:
                    return {"status": AuthStatus.INVALID_CREDENTIALS, "message": "Username already exists"}
                return {"status": AuthStatus.INVALID_CREDENTIALS, "message": "Email already registered"}
            
            # Create new user
            import uuid
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(registration.password)
            
            user = UserModel(
                id=user_id,
                username=registration.username,
                email=registration.email,
                password_hash=password_hash,
                role=UserRole.USER.value,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"✅ User registered successfully: {user.username}")
            
            return {
                "status": AuthStatus.SUCCESS,
                "message": "User registered successfully",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Registration failed: {e}")
            return {
                "status": AuthStatus.INVALID_CREDENTIALS,
                "message": "Registration failed. Please try again."
            }
        finally:
            db.close()
    
    def login_user(self, login: UserLogin, ip_address: str = None, 
                   user_agent: str = None) -> Dict[str, Any]:
        """Authenticate a user and create a session."""
        db = SessionLocal()
        try:
            # Keep Redis for rate limiting / account locking if available
            if self._is_rate_limited(login.username, "login"):
                return {
                    "status": AuthStatus.RATE_LIMITED,
                    "message": "Too many login attempts. Please try again later."
                }
            
            if self._check_account_locked(login.username):
                return {
                    "status": AuthStatus.ACCOUNT_LOCKED,
                    "message": f"Account locked. Try again in {self.lockout_duration} minutes."
                }
            
            # Get user from DB
            user = db.query(UserModel).filter(UserModel.username == login.username).first()
            if not user:
                self._increment_login_attempts(login.username)
                return {
                    "status": AuthStatus.USER_NOT_FOUND,
                    "message": "Invalid username or password"
                }
            
            # Verify password
            if not self._verify_password(login.password, user.password_hash):
                attempts = self._increment_login_attempts(login.username)
                return {
                    "status": AuthStatus.INVALID_CREDENTIALS,
                    "message": f"Invalid username or password."
                }
            
            # Reset login attempts
            self._reset_login_attempts(login.username)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create session (Keep sessions in Redis for simple fast expiry)
            session_timeout = self.remember_me_timeout if login.remember_me else self.session_timeout
            session = self._create_session(user.id, ip_address, user_agent, session_timeout)
            
            # Create JWT token
            token = self._create_jwt_token(user.id, user.role, session_timeout * 3600)
            
            logger.info(f"✅ User logged in successfully: {user.username}")
            
            return {
                "status": AuthStatus.SUCCESS,
                "message": "Login successful",
                "token": token,
                "session_id": session.session_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_verified": user.is_verified
                },
                "expires_in": session_timeout * 3600
            }
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return {
                "status": AuthStatus.INVALID_CREDENTIALS,
                "message": "Login failed. Please try again."
            }
        finally:
            db.close()
    
    def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout a user by invalidating their session."""
        try:
            if self._invalidate_session(session_id):
                return {
                    "status": AuthStatus.SUCCESS,
                    "message": "Logout successful"
                }
            else:
                return {
                    "status": AuthStatus.INVALID_TOKEN,
                    "message": "Invalid session"
                }
        except Exception as e:
            logger.error(f"❌ Logout failed: {e}")
            return {
                "status": AuthStatus.INVALID_TOKEN,
                "message": "Logout failed"
            }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return user information."""
        try:
            payload = self._decode_jwt_token(token)
            if not payload:
                return {
                    "status": AuthStatus.INVALID_TOKEN,
                    "message": "Invalid or expired token"
                }
            
            user_id = payload.get('user_id')
            user = self._get_user_by_id(user_id)
            
            if not user or not user.is_active:
                return {
                    "status": AuthStatus.USER_NOT_FOUND,
                    "message": "User not found or inactive"
                }
            
            return {
                "status": AuthStatus.SUCCESS,
                "message": "Token valid",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_verified": user.is_verified
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Token validation failed: {e}")
            return {
                "status": AuthStatus.INVALID_TOKEN,
                "message": "Token validation failed"
            }
    
    def change_password(self, user_id: str, password_change: PasswordChange) -> Dict[str, Any]:
        """Change a user's password."""
        db = SessionLocal()
        try:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return {
                    "status": AuthStatus.USER_NOT_FOUND,
                    "message": "User not found"
                }
            
            # Verify current password
            if not self._verify_password(password_change.current_password, user.password_hash):
                return {
                    "status": AuthStatus.INVALID_CREDENTIALS,
                    "message": "Current password is incorrect"
                }
            
            # Hash new password
            new_password_hash = self._hash_password(password_change.new_password)
            user.password_hash = new_password_hash
            
            # Commit changes
            db.commit()
            
            # Invalidate all sessions for this user
            self._invalidate_user_sessions(user_id)
            
            logger.info(f"✅ Password changed successfully for user: {user.username}")
            
            return {
                "status": AuthStatus.SUCCESS,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Password change failed: {e}")
            return {
                "status": AuthStatus.INVALID_CREDENTIALS,
                "message": "Password change failed"
            }
        finally:
            db.close()
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user."""
        try:
            if not self.redis_client:
                return []
            
            pattern = f"session:*:user:{user_id}"
            session_keys = self.redis_client.keys(pattern)
            
            sessions = []
            for key in session_keys:
                session_data = self.redis_client.hgetall(key)
                if session_data and session_data.get('is_active') == 'True':
                    sessions.append({
                        "session_id": session_data.get('session_id'),
                        "created_at": session_data.get('created_at'),
                        "expires_at": session_data.get('expires_at'),
                        "ip_address": session_data.get('ip_address'),
                        "user_agent": session_data.get('user_agent')
                    })
            
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Failed to get user sessions: {e}")
            return []
    
    def _user_exists_by_username(self, username: str) -> bool:
        """Check if a user exists by username."""
        if not self.redis_client:
            return False
        
        key = f"user:username:{username}"
        return self.redis_client.exists(key) > 0
    
    def _user_exists_by_email(self, email: str) -> bool:
        """Check if a user exists by email."""
        if not self.redis_client:
            return False
        
        key = f"user:email:{email}"
        return self.redis_client.exists(key) > 0
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        db = SessionLocal()
        try:
            db_user = db.query(UserModel).filter(UserModel.username == username).first()
            if not db_user:
                return None
            
            return User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                password_hash=db_user.password_hash,
                role=UserRole(db_user.role),
                is_active=db_user.is_active,
                is_verified=db_user.is_verified,
                created_at=db_user.created_at,
                last_login=db_user.last_login,
                login_attempts=db_user.login_attempts['count'] if isinstance(db_user.login_attempts, dict) else 0,
                locked_until=db_user.locked_until,
                preferences=db_user.preferences or {}
            )
        except Exception:
            return None
        finally:
            db.close()
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        if not self.redis_client:
            return None
        
        key = f"user:email:{email}"
        user_id = self.redis_client.get(key)
        
        if user_id:
            return self._get_user_by_id(user_id)
        
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        db = SessionLocal()
        try:
            db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not db_user:
                return None
            
            # Convert to User dataclass
            return User(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                password_hash=db_user.password_hash,
                role=UserRole(db_user.role),
                is_active=db_user.is_active,
                is_verified=db_user.is_verified,
                created_at=db_user.created_at,
                last_login=db_user.last_login,
                login_attempts=db_user.login_attempts['count'] if isinstance(db_user.login_attempts, dict) else 0,
                locked_until=db_user.locked_until,
                preferences=db_user.preferences or {}
            )
        except Exception as e:
            logger.error(f"❌ Failed to get user by ID: {e}")
            return None
        finally:
            db.close()
    
    def _store_user(self, user: User):
        """Store a user in Redis."""
        if not self.redis_client:
            return
        
        # Store user data
        user_key = f"user:{user.id}"
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'role': user.role.value,
            'is_active': str(user.is_active),
            'is_verified': str(user.is_verified),
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else '',
            'login_attempts': str(user.login_attempts),
            'locked_until': user.locked_until.isoformat() if user.locked_until else '',
            'preferences': str(user.preferences)
        }
        
        self.redis_client.hset(user_key, mapping=user_data)
        self.redis_client.expire(user_key, 86400 * 30)  # 30 days
        
        # Store username and email indexes
        self.redis_client.set(f"user:username:{user.username}", user.id)
        self.redis_client.set(f"user:email:{user.email}", user.id)
        self.redis_client.expire(f"user:username:{user.username}", 86400 * 30)
        self.redis_client.expire(f"user:email:{user.email}", 86400 * 30)
    
    def _create_session(self, user_id: str, ip_address: str = None, 
                       user_agent: str = None, timeout_hours: int = None) -> Session:
        """Create a new session for a user."""
        if timeout_hours is None:
            timeout_hours = self.session_timeout
        
        session_id = self._generate_session_id()
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=timeout_hours)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown"
        )
        
        if self.redis_client:
            session_key = f"session:{session_id}"
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': str(session.is_active)
            }
            
            self.redis_client.hset(session_key, mapping=session_data)
            self.redis_client.expire(session_key, timeout_hours * 3600)
            
            # Store session reference for user
            user_sessions_key = f"user_sessions:{user_id}"
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, timeout_hours * 3600)
        
        return session
    
    def _invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        if not self.redis_client:
            return False
        
        session_key = f"session:{session_id}"
        session_data = self.redis_client.hgetall(session_key)
        
        if session_data:
            user_id = session_data.get('user_id')
            
            # Mark session as inactive
            self.redis_client.hset(session_key, 'is_active', 'False')
            
            # Remove from user sessions
            if user_id:
                user_sessions_key = f"user_sessions:{user_id}"
                self.redis_client.srem(user_sessions_key, session_id)
            
            return True
        
        return False
    
    def _invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user."""
        if not self.redis_client:
            return
        
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = self.redis_client.smembers(user_sessions_key)
        
        for session_id in session_ids:
            self._invalidate_session(session_id)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        if not self.redis_client:
            return 0
        
        cleaned_count = 0
        pattern = "session:*"
        session_keys = self.redis_client.keys(pattern)
        
        for key in session_keys:
            session_data = self.redis_client.hgetall(key)
            if session_data:
                expires_at_str = session_data.get('expires_at')
                if expires_at_str:
                    try:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        if expires_at < datetime.utcnow():
                            self.redis_client.delete(key)
                            cleaned_count += 1
                    except Exception:
                        # If we can't parse the date, delete the session
                        self.redis_client.delete(key)
                        cleaned_count += 1
        
        logger.info(f"🧹 Cleaned up {cleaned_count} expired sessions")
        return cleaned_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get authentication service statistics."""
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            total_users = len(self.redis_client.keys("user:*"))
            active_sessions = len(self.redis_client.keys("session:*"))
            locked_accounts = len(self.redis_client.keys("login_attempts:*"))
            
            return {
                "total_users": total_users,
                "active_sessions": active_sessions,
                "locked_accounts": locked_accounts,
                "redis_connected": True
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {"error": str(e)} 