"""
Authentication API Routes

This module provides FastAPI routes for user authentication, registration,
session management, and security features.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.services.auth_service import (
    AuthService, UserRegistration, UserLogin, PasswordChange,
    PasswordReset, AuthStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Authentication"])

# Initialize security
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    result = auth_service.validate_token(token)
    
    if result["status"] != AuthStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return result["user"]

@router.post("/register", response_model=Dict[str, Any])
async def register_user(registration: UserRegistration, request: Request):
    """Register a new user."""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        result = auth_service.register_user(registration)
        
        if result["status"] == AuthStatus.SUCCESS:
            logger.info(f"✅ User registered: {registration.username} from {client_ip}")
            return {
                "success": True,
                "message": result["message"],
                "user_id": result["user_id"],
                "username": result["username"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=Dict[str, Any])
async def login_user(login: UserLogin, request: Request):
    """Authenticate a user and create a session."""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        result = auth_service.login_user(login, client_ip, user_agent)
        
        if result["status"] == AuthStatus.SUCCESS:
            logger.info(f"✅ User logged in: {login.username} from {client_ip}")
            return {
                "success": True,
                "message": result["message"],
                "token": result["token"],
                "session_id": result["session_id"],
                "user": result["user"],
                "expires_in": result["expires_in"]
            }
        elif result["status"] == AuthStatus.ACCOUNT_LOCKED:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=result["message"]
            )
        elif result["status"] == AuthStatus.RATE_LIMITED:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/logout", response_model=Dict[str, Any])
async def logout_user(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout the current user."""
    try:
        # Get session ID from request headers or token
        session_id = request.headers.get("x-session-id")
        
        if session_id:
            result = auth_service.logout_user(session_id)
        else:
            # If no session ID, just return success (token will expire)
            result = {"status": AuthStatus.SUCCESS, "message": "Logout successful"}
        
        if result["status"] == AuthStatus.SUCCESS:
            logger.info(f"✅ User logged out: {current_user['username']}")
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    try:
        return {
            "success": True,
            "user": current_user,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/change-password", response_model=Dict[str, Any])
async def change_password(
    password_change: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change the current user's password."""
    try:
        result = auth_service.change_password(current_user["id"], password_change)
        
        if result["status"] == AuthStatus.SUCCESS:
            logger.info(f"✅ Password changed for user: {current_user['username']}")
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(reset_request: PasswordReset, request: Request):
    """Request a password reset."""
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"
        
        # TODO: Implement password reset logic
        # For now, just return a success message
        logger.info(f"📧 Password reset requested for: {reset_request.email} from {client_ip}")
        
        return {
            "success": True,
            "message": "If the email exists, a password reset link has been sent."
        }
        
    except Exception as e:
        logger.error(f"❌ Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.get("/sessions", response_model=Dict[str, Any])
async def get_user_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all active sessions for the current user."""
    try:
        sessions = auth_service.get_user_sessions(current_user["id"])
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"❌ Get sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user sessions"
        )

@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def revoke_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Revoke a specific session."""
    try:
        result = auth_service.logout_user(session_id)
        
        if result["status"] == AuthStatus.SUCCESS:
            logger.info(f"✅ Session revoked for user: {current_user['username']}")
            return {
                "success": True,
                "message": "Session revoked successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Revoke session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_auth_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get authentication service statistics (admin only)."""
    try:
        # Check if user is admin
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        stats = auth_service.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Clean up expired sessions (admin only)."""
    try:
        # Check if user is admin
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        cleaned_count = auth_service.cleanup_expired_sessions()
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_count": cleaned_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup sessions"
        )

@router.get("/health", response_model=Dict[str, Any])
async def auth_health_check():
    """Health check for authentication service."""
    try:
        stats = auth_service.get_stats()
        
        if "error" in stats:
            return {
                "status": "unhealthy",
                "message": "Redis connection failed",
                "error": stats["error"]
            }
        
        return {
            "status": "healthy",
            "message": "Authentication service is running",
            "redis_connected": stats.get("redis_connected", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {
            "status": "unhealthy",
            "message": "Authentication service error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 