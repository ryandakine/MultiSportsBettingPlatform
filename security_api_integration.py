#!/usr/bin/env python3
"""
Security API Integration System - YOLO MODE!
============================================
RESTful API endpoints for authentication, user management, and security monitoring
for the sports betting platform
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict, deque
import uuid
import re

# Import our security system
from advanced_security_authentication_system import AdvancedSecuritySystem, User, SecurityEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    timestamp: str = ""

@dataclass
class APIRequest:
    """API request wrapper"""
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class EndpointConfig:
    """API endpoint configuration"""
    path: str
    method: str
    requires_auth: bool = False
    required_permissions: List[str] = None
    rate_limit: Optional[str] = None

class SecurityAPIServer:
    """Security API server with comprehensive endpoints"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.security_system = AdvancedSecuritySystem()
        
        # API endpoints configuration
        self.endpoints = {
            # Authentication endpoints
            ("POST", "/api/auth/register"): EndpointConfig("/api/auth/register", "POST", requires_auth=False, rate_limit="register"),
            ("POST", "/api/auth/login"): EndpointConfig("/api/auth/login", "POST", requires_auth=False, rate_limit="login"),
            ("POST", "/api/auth/logout"): EndpointConfig("/api/auth/logout", "POST", requires_auth=True),
            ("POST", "/api/auth/refresh"): EndpointConfig("/api/auth/refresh", "POST", requires_auth=False),
            ("POST", "/api/auth/verify"): EndpointConfig("/api/auth/verify", "POST", requires_auth=False),
            
            # User management endpoints
            ("GET", "/api/users/profile"): EndpointConfig("/api/users/profile", "GET", requires_auth=True),
            ("PUT", "/api/users/profile"): EndpointConfig("/api/users/profile", "PUT", requires_auth=True),
            ("POST", "/api/users/change-password"): EndpointConfig("/api/users/change-password", "POST", requires_auth=True),
            ("POST", "/api/users/enable-2fa"): EndpointConfig("/api/users/enable-2fa", "POST", requires_auth=True),
            ("POST", "/api/users/verify-2fa"): EndpointConfig("/api/users/verify-2fa", "POST", requires_auth=True),
            
            # Admin endpoints
            ("GET", "/api/admin/users"): EndpointConfig("/api/admin/users", "GET", requires_auth=True, required_permissions=["manage_users"]),
            ("GET", "/api/admin/security-logs"): EndpointConfig("/api/admin/security-logs", "GET", requires_auth=True, required_permissions=["view_security_logs"]),
            ("POST", "/api/admin/block-user"): EndpointConfig("/api/admin/block-user", "POST", requires_auth=True, required_permissions=["manage_users"]),
            ("POST", "/api/admin/unblock-user"): EndpointConfig("/api/admin/unblock-user", "POST", requires_auth=True, required_permissions=["manage_users"]),
            
            # System endpoints
            ("GET", "/api/system/health"): EndpointConfig("/api/system/health", "GET", requires_auth=False),
            ("GET", "/api/system/status"): EndpointConfig("/api/system/status", "GET", requires_auth=True, required_permissions=["system_configuration"]),
        }
        
        # Request tracking
        self.request_log = deque(maxlen=1000)
        self.active_sessions = {}
        
        logger.info("🚀 Security API Server initialized - YOLO MODE!")
    
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """Handle incoming API request"""
        start_time = time.time()
        
        try:
            # Log request
            self._log_request(request)
            
            # Check rate limiting
            rate_limit_check = await self._check_rate_limits(request)
            if not rate_limit_check["allowed"]:
                return APIResponse(
                    success=False,
                    message="Rate limit exceeded",
                    error_code="RATE_LIMIT_EXCEEDED",
                    timestamp=datetime.now().isoformat()
                )
            
            # Find endpoint
            endpoint_key = (request.method, request.path)
            if endpoint_key not in self.endpoints:
                return APIResponse(
                    success=False,
                    message="Endpoint not found",
                    error_code="ENDPOINT_NOT_FOUND",
                    timestamp=datetime.now().isoformat()
                )
            
            endpoint = self.endpoints[endpoint_key]
            
            # Check authentication
            if endpoint.requires_auth:
                auth_result = await self._authenticate_request(request)
                if not auth_result["authenticated"]:
                    return APIResponse(
                        success=False,
                        message="Authentication required",
                        error_code="AUTHENTICATION_REQUIRED",
                        timestamp=datetime.now().isoformat()
                    )
                
                # Check permissions
                if endpoint.required_permissions:
                    user_data = auth_result["user_data"]
                    for permission in endpoint.required_permissions:
                        if not self.security_system.has_permission(user_data["role"], permission):
                            return APIResponse(
                                success=False,
                                message="Insufficient permissions",
                                error_code="INSUFFICIENT_PERMISSIONS",
                                timestamp=datetime.now().isoformat()
                            )
            
            # Route to handler
            handler_name = f"_handle_{request.method.lower()}_{request.path.replace('/', '_').replace('-', '_').lstrip('_')}"
            handler = getattr(self, handler_name, None)
            
            if handler:
                result = await handler(request)
                processing_time = (time.time() - start_time) * 1000
                
                # Add processing time to response
                if result.data is None:
                    result.data = {}
                result.data["processing_time_ms"] = processing_time
                result.timestamp = datetime.now().isoformat()
                
                return result
            else:
                return APIResponse(
                    success=False,
                    message="Handler not implemented",
                    error_code="HANDLER_NOT_IMPLEMENTED",
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"❌ Request handling error: {e}")
            return APIResponse(
                success=False,
                message="Internal server error",
                error_code="INTERNAL_ERROR",
                timestamp=datetime.now().isoformat()
            )
    
    async def _check_rate_limits(self, request: APIRequest) -> Dict[str, Any]:
        """Check rate limits for request"""
        endpoint_key = (request.method, request.path)
        if endpoint_key not in self.endpoints:
            return {"allowed": True}
        
        endpoint = self.endpoints[endpoint_key]
        if not endpoint.rate_limit:
            return {"allowed": True}
        
        # Use security system's rate limiter
        allowed, rate_info = self.security_system.rate_limiter.is_allowed(
            endpoint.path, 
            ip_address=request.ip_address
        )
        
        return {
            "allowed": allowed,
            "rate_info": rate_info
        }
    
    async def _authenticate_request(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate request using JWT token"""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"authenticated": False}
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        is_valid, user_data = await self.security_system.verify_token(token)
        
        return {
            "authenticated": is_valid,
            "user_data": user_data
        }
    
    def _log_request(self, request: APIRequest):
        """Log API request"""
        self.request_log.append({
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.path,
            "ip_address": request.ip_address,
            "user_agent": request.user_agent
        })
    
    # Authentication handlers
    async def _handle_post_api_auth_register(self, request: APIRequest) -> APIResponse:
        """Handle user registration"""
        try:
            body = request.body or {}
            username = body.get("username", "")
            email = body.get("email", "")
            password = body.get("password", "")
            
            if not username or not email or not password:
                return APIResponse(
                    success=False,
                    message="Username, email, and password are required",
                    error_code="MISSING_FIELDS"
                )
            
            success, message, user = await self.security_system.register_user(
                username=username,
                email=email,
                password=password,
                ip_address=request.ip_address,
                user_agent=request.user_agent
            )
            
            if success:
                return APIResponse(
                    success=True,
                    message=message,
                    data={
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                )
            else:
                return APIResponse(
                    success=False,
                    message=message,
                    error_code="REGISTRATION_FAILED"
                )
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return APIResponse(
                success=False,
                message="Registration failed",
                error_code="REGISTRATION_ERROR"
            )
    
    async def _handle_post_api_auth_login(self, request: APIRequest) -> APIResponse:
        """Handle user login"""
        try:
            body = request.body or {}
            username = body.get("username", "")
            password = body.get("password", "")
            totp_code = body.get("totp_code")
            
            if not username or not password:
                return APIResponse(
                    success=False,
                    message="Username and password are required",
                    error_code="MISSING_FIELDS"
                )
            
            success, message, auth_data = await self.security_system.authenticate_user(
                username=username,
                password=password,
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                totp_code=totp_code
            )
            
            if success:
                return APIResponse(
                    success=True,
                    message=message,
                    data=auth_data
                )
            else:
                return APIResponse(
                    success=False,
                    message=message,
                    error_code="AUTHENTICATION_FAILED"
                )
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return APIResponse(
                success=False,
                message="Login failed",
                error_code="LOGIN_ERROR"
            )
    
    async def _handle_post_api_auth_logout(self, request: APIRequest) -> APIResponse:
        """Handle user logout"""
        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return APIResponse(
                    success=False,
                    message="Authorization header required",
                    error_code="MISSING_AUTH_HEADER"
                )
            
            token = auth_header[7:]
            success = await self.security_system.logout(token)
            
            if success:
                return APIResponse(
                    success=True,
                    message="Logout successful"
                )
            else:
                return APIResponse(
                    success=False,
                    message="Logout failed",
                    error_code="LOGOUT_FAILED"
                )
                
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return APIResponse(
                success=False,
                message="Logout failed",
                error_code="LOGOUT_ERROR"
            )
    
    async def _handle_post_api_auth_refresh(self, request: APIRequest) -> APIResponse:
        """Handle token refresh"""
        try:
            body = request.body or {}
            refresh_token = body.get("refresh_token", "")
            
            if not refresh_token:
                return APIResponse(
                    success=False,
                    message="Refresh token is required",
                    error_code="MISSING_REFRESH_TOKEN"
                )
            
            success, message, token_data = await self.security_system.refresh_token(refresh_token)
            
            if success:
                return APIResponse(
                    success=True,
                    message=message,
                    data=token_data
                )
            else:
                return APIResponse(
                    success=False,
                    message=message,
                    error_code="REFRESH_FAILED"
                )
                
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return APIResponse(
                success=False,
                message="Token refresh failed",
                error_code="REFRESH_ERROR"
            )
    
    async def _handle_post_api_auth_verify(self, request: APIRequest) -> APIResponse:
        """Handle token verification"""
        try:
            body = request.body or {}
            token = body.get("token", "")
            
            if not token:
                return APIResponse(
                    success=False,
                    message="Token is required",
                    error_code="MISSING_TOKEN"
                )
            
            is_valid, user_data = await self.security_system.verify_token(token)
            
            if is_valid:
                return APIResponse(
                    success=True,
                    message="Token is valid",
                    data=user_data
                )
            else:
                return APIResponse(
                    success=False,
                    message="Token is invalid or expired",
                    error_code="INVALID_TOKEN"
                )
                
        except Exception as e:
            logger.error(f"❌ Token verification error: {e}")
            return APIResponse(
                success=False,
                message="Token verification failed",
                error_code="VERIFICATION_ERROR"
            )
    
    # User management handlers
    async def _handle_get_api_users_profile(self, request: APIRequest) -> APIResponse:
        """Get user profile"""
        try:
            auth_result = await self._authenticate_request(request)
            user_data = auth_result["user_data"]
            
            user_id = user_data["user_id"]
            user = self.security_system.users.get(user_id)
            
            if user:
                return APIResponse(
                    success=True,
                    message="Profile retrieved successfully",
                    data={
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "created_at": user.created_at,
                        "last_login": user.last_login,
                        "two_factor_enabled": user.two_factor_enabled
                    }
                )
            else:
                return APIResponse(
                    success=False,
                    message="User not found",
                    error_code="USER_NOT_FOUND"
                )
                
        except Exception as e:
            logger.error(f"❌ Get profile error: {e}")
            return APIResponse(
                success=False,
                message="Failed to retrieve profile",
                error_code="PROFILE_ERROR"
            )
    
    # Admin handlers
    async def _handle_get_api_admin_users(self, request: APIRequest) -> APIResponse:
        """Get all users (admin only)"""
        try:
            users_data = []
            for user in self.security_system.users.values():
                users_data.append({
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "failed_login_attempts": user.failed_login_attempts,
                    "two_factor_enabled": user.two_factor_enabled
                })
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(users_data)} users",
                data={"users": users_data}
            )
            
        except Exception as e:
            logger.error(f"❌ Get users error: {e}")
            return APIResponse(
                success=False,
                message="Failed to retrieve users",
                error_code="USERS_ERROR"
            )
    
    async def _handle_get_api_admin_security_logs(self, request: APIRequest) -> APIResponse:
        """Get security logs (admin only)"""
        try:
            recent_events = self.security_system.security_monitor.get_recent_events(100)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(recent_events)} security events",
                data={"events": recent_events}
            )
            
        except Exception as e:
            logger.error(f"❌ Get security logs error: {e}")
            return APIResponse(
                success=False,
                message="Failed to retrieve security logs",
                error_code="SECURITY_LOGS_ERROR"
            )
    
    # System handlers
    async def _handle_get_api_system_health(self, request: APIRequest) -> APIResponse:
        """Get system health status"""
        try:
            security_status = self.security_system.get_security_status()
            
            return APIResponse(
                success=True,
                message="System is healthy",
                data={
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "security": security_status,
                    "uptime": time.time() - self.security_system.start_time if hasattr(self.security_system, 'start_time') else 0
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return APIResponse(
                success=False,
                message="System health check failed",
                error_code="HEALTH_CHECK_ERROR"
            )
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        return {
            "total_requests": len(self.request_log),
            "active_sessions": len(self.active_sessions),
            "endpoints": len(self.endpoints),
            "recent_requests": list(self.request_log)[-10:] if self.request_log else []
        }

async def main():
    """Test the security API integration system"""
    print("🚀 Testing Security API Integration System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize API server
    api_server = SecurityAPIServer()
    
    try:
        # Test user registration
        print("\n📝 Testing User Registration API:")
        print("-" * 40)
        
        register_request = APIRequest(
            method="POST",
            path="/api/auth/register",
            headers={"Content-Type": "application/json"},
            body={
                "username": "apiuser",
                "email": "api@example.com",
                "password": "SecurePass123!"
            },
            ip_address="192.168.1.101",
            user_agent="API-Test-Client/1.0"
        )
        
        register_response = await api_server.handle_request(register_request)
        print(f"✅ Registration: {register_response.success}")
        print(f"   Message: {register_response.message}")
        if register_response.success:
            print(f"   User ID: {register_response.data['user_id']}")
        
        # Test user login
        print("\n🔐 Testing User Login API:")
        print("-" * 40)
        
        login_request = APIRequest(
            method="POST",
            path="/api/auth/login",
            headers={"Content-Type": "application/json"},
            body={
                "username": "apiuser",
                "password": "SecurePass123!"
            },
            ip_address="192.168.1.101",
            user_agent="API-Test-Client/1.0"
        )
        
        login_response = await api_server.handle_request(login_request)
        print(f"✅ Login: {login_response.success}")
        print(f"   Message: {login_response.message}")
        
        if login_response.success:
            access_token = login_response.data['access_token']
            print(f"   Access Token: {access_token[:50]}...")
            print(f"   User Role: {login_response.data['user']['role']}")
            
            # Test token verification
            print("\n🔍 Testing Token Verification API:")
            print("-" * 40)
            
            verify_request = APIRequest(
                method="POST",
                path="/api/auth/verify",
                headers={"Content-Type": "application/json"},
                body={"token": access_token},
                ip_address="192.168.1.101"
            )
            
            verify_response = await api_server.handle_request(verify_request)
            print(f"✅ Token Verification: {verify_response.success}")
            print(f"   Message: {verify_response.message}")
            
            # Test profile retrieval
            print("\n👤 Testing Profile Retrieval API:")
            print("-" * 40)
            
            profile_request = APIRequest(
                method="GET",
                path="/api/users/profile",
                headers={"Authorization": f"Bearer {access_token}"},
                ip_address="192.168.1.101"
            )
            
            profile_response = await api_server.handle_request(profile_request)
            print(f"✅ Profile Retrieval: {profile_response.success}")
            print(f"   Message: {profile_response.message}")
            if profile_response.success:
                print(f"   Username: {profile_response.data['username']}")
                print(f"   Email: {profile_response.data['email']}")
                print(f"   2FA Enabled: {profile_response.data['two_factor_enabled']}")
        
        # Test system health
        print("\n🏥 Testing System Health API:")
        print("-" * 40)
        
        health_request = APIRequest(
            method="GET",
            path="/api/system/health",
            headers={},
            ip_address="192.168.1.101"
        )
        
        health_response = await api_server.handle_request(health_request)
        print(f"✅ System Health: {health_response.success}")
        print(f"   Message: {health_response.message}")
        if health_response.success:
            print(f"   Status: {health_response.data['status']}")
            print(f"   Total Users: {health_response.data['security']['total_users']}")
            print(f"   Active Tokens: {health_response.data['security']['active_tokens']}")
        
        # Test API statistics
        print("\n📊 API Statistics:")
        print("-" * 40)
        api_stats = api_server.get_api_stats()
        print(f"✅ Total Requests: {api_stats['total_requests']}")
        print(f"✅ Active Sessions: {api_stats['active_sessions']}")
        print(f"✅ Endpoints: {api_stats['endpoints']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Security API Integration System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 