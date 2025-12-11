"""
Feature Flag Management API Routes
==================================
Admin endpoints for managing feature flags at runtime.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from src.services.feature_flags import feature_flags
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/feature-flags", tags=["Feature Flags"])

auth_service = AuthService()


# Request/Response Models
class SetFlagRequest(BaseModel):
    """Request to set a feature flag."""
    flag: str
    enabled: bool


class SetUserFlagRequest(BaseModel):
    """Request to set a user-specific flag."""
    user_id: str
    flag: str
    enabled: bool


class DeleteUserFlagRequest(BaseModel):
    """Request to delete a user-specific flag."""
    user_id: str
    flag: str


# Admin authentication dependency (simplified - enhance in production)
async def require_admin(authorization: Optional[str] = None):
    """Require admin role for feature flag management."""
    # In production, use proper JWT validation
    # For now, this is a placeholder
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # TODO: Validate admin token
    return True


@router.get("/")
async def get_all_flags() -> Dict[str, bool]:
    """
    Get all global feature flags.
    
    Returns:
        Dictionary of flag names to enabled status
    """
    try:
        flags = await feature_flags.get_all_flags()
        return flags
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flags: {str(e)}")


@router.get("/{flag}")
async def get_flag(flag: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a specific feature flag status.
    
    Args:
        flag: Flag name
        user_id: Optional user ID for user-specific override
    
    Returns:
        Flag status and metadata
    """
    try:
        enabled = await feature_flags.is_enabled(flag, user_id=user_id)
        return {
            "flag": flag,
            "enabled": enabled,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flag: {str(e)}")


@router.post("/set", dependencies=[Depends(require_admin)])
async def set_flag(request: SetFlagRequest) -> Dict[str, Any]:
    """
    Set a global feature flag.
    
    Requires admin authentication.
    
    Args:
        request: Flag name and enabled status
    
    Returns:
        Success message
    """
    try:
        success = await feature_flags.set_global_flag(request.flag, request.enabled)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set flag (Redis unavailable?)")
        
        return {
            "message": f"Flag '{request.flag}' set to {request.enabled}",
            "flag": request.flag,
            "enabled": request.enabled
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set flag: {str(e)}")


@router.post("/set-user", dependencies=[Depends(require_admin)])
async def set_user_flag(request: SetUserFlagRequest) -> Dict[str, Any]:
    """
    Set a user-specific feature flag override.
    
    Requires admin authentication.
    
    Args:
        request: User ID, flag name, and enabled status
    
    Returns:
        Success message
    """
    try:
        success = await feature_flags.set_user_flag(request.user_id, request.flag, request.enabled)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set user flag (Redis unavailable?)")
        
        return {
            "message": f"User flag '{request.flag}' set to {request.enabled} for user {request.user_id}",
            "user_id": request.user_id,
            "flag": request.flag,
            "enabled": request.enabled
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set user flag: {str(e)}")


@router.delete("/delete-user", dependencies=[Depends(require_admin)])
async def delete_user_flag(request: DeleteUserFlagRequest) -> Dict[str, Any]:
    """
    Delete a user-specific flag override (reverts to global/default).
    
    Requires admin authentication.
    
    Args:
        request: User ID and flag name
    
    Returns:
        Success message
    """
    try:
        success = await feature_flags.delete_user_flag(request.user_id, request.flag)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user flag (Redis unavailable?)")
        
        return {
            "message": f"User flag '{request.flag}' deleted for user {request.user_id}",
            "user_id": request.user_id,
            "flag": request.flag
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user flag: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_flags(user_id: str) -> Dict[str, bool]:
    """
    Get all feature flags for a specific user (including overrides).
    
    Args:
        user_id: User ID
    
    Returns:
        Dictionary of flag names to enabled status
    """
    try:
        flags = await feature_flags.get_all_flags(user_id=user_id)
        return flags
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user flags: {str(e)}")
