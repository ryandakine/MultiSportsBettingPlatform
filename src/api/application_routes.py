"""
License Application API Routes
==============================
API endpoints for license applications from the marketing site.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.database import get_db
from src.db.models.application import LicenseApplication
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["License Applications"])

# Rate limiting: 3 applications per email per 24 hours
MAX_APPLICATIONS_PER_EMAIL = 3
RATE_LIMIT_WINDOW_HOURS = 24

# Disposable email domains (common ones - can be expanded)
DISPOSABLE_EMAIL_DOMAINS = {
    "tempmail.com", "10minutemail.com", "guerrillamail.com", "mailinator.com",
    "throwaway.email", "temp-mail.org", "yopmail.com", "getnada.com"
}


# Pydantic Models
class ApplicationSubmitRequest(BaseModel):
    """Request model for license application submission."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number (optional)")
    experience: Optional[str] = Field(None, max_length=1000, description="Betting experience and details (optional)")
    interest: Optional[str] = Field(None, max_length=1000, description="Interest in platform and additional info (optional)")
    monero_acknowledged: bool = Field(True, description="Monero payment acknowledgment (defaults to true for membership applications)")
    
    @validator('name')
    def validate_name(cls, v):
        """Sanitize name input."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        # Remove extra whitespace and validate
        sanitized = ' '.join(v.strip().split())
        if len(sanitized) < 2:
            raise ValueError("Name must be at least 2 characters")
        return sanitized
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone format (flexible)."""
        if not v:
            return v
        # Remove common separators and validate
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        # Allow digits, country codes, etc. - be flexible
        if not re.match(r'^\+?[\d]{7,15}$', cleaned):
            raise ValueError("Invalid phone number format")
        return v
    
    @validator('experience', 'interest')
    def validate_text_field(cls, v):
        """Sanitize text fields."""
        if not v:
            return v
        # Remove potential XSS patterns
        sanitized = v.strip()
        # Basic XSS prevention
        if '<script' in sanitized.lower() or 'javascript:' in sanitized.lower():
            raise ValueError("Invalid characters in text field")
        return sanitized
    
    @validator('monero_acknowledged')
    def validate_monero_acknowledgment(cls, v):
        """Ensure Monero acknowledgment is true for membership applications."""
        # For membership applications, we assume they understand payment method
        return True


class ApplicationSubmitResponse(BaseModel):
    """Response model for successful application submission."""
    
    success: bool
    application_id: str
    message: str
    status: str


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool
    error: str
    details: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# Helper Functions
def is_disposable_email(email: str) -> bool:
    """Check if email is from a disposable email service."""
    domain = email.split('@')[1].lower() if '@' in email else ''
    return domain in DISPOSABLE_EMAIL_DOMAINS


async def check_rate_limit(db: AsyncSession, email: str):
    """
    Check if email has exceeded rate limit.
    
    Returns:
        (is_allowed, error_message)
    """
    try:
        # Calculate cutoff time (24 hours ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
        
        # Count applications in the last 24 hours
        stmt = select(func.count(LicenseApplication.id)).where(
            LicenseApplication.email == email,
            LicenseApplication.created_at >= cutoff_time
        )
        
        result = await db.execute(stmt)
        count = result.scalar() or 0
        
        if count >= MAX_APPLICATIONS_PER_EMAIL:
            return False, f"Rate limit exceeded. Maximum {MAX_APPLICATIONS_PER_EMAIL} applications per {RATE_LIMIT_WINDOW_HOURS} hours."
        
        return True, None
        
    except Exception as e:
        logger.error(f"❌ Error checking rate limit: {e}")
        # On error, allow the request (fail open for availability)
        return True, None


async def check_duplicate_email(db: AsyncSession, email: str) -> bool:
    """Check if email already has a pending application."""
    try:
        stmt = select(LicenseApplication).where(
            LicenseApplication.email == email,
            LicenseApplication.status == "pending"
        ).limit(1)
        
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        return existing is not None
        
    except Exception as e:
        logger.error(f"❌ Error checking duplicate email: {e}")
        return False


async def send_application_email(application: LicenseApplication) -> bool:
    """
    Send email notifications to applicant and admin.
    
    TODO: Implement actual email sending service.
    For now, just log the email that would be sent.
    """
    try:
        logger.info(f"📧 [EMAIL] Would send application confirmation to: {application.email}")
        logger.info(f"   Application ID: {application.id}")
        logger.info(f"   Name: {application.name}")
        
        logger.info(f"📧 [EMAIL] Would send admin notification")
        logger.info(f"   New application from: {application.name} ({application.email})")
        logger.info(f"   Application ID: {application.id}")
        
        # In production, integrate with actual email service (SendGrid, AWS SES, etc.)
        # For now, this is a placeholder that logs what would be sent
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {e}")
        # Don't fail the application submission if email fails
        return False


# API Routes
@router.post(
    "/applications/submit",
    response_model=ApplicationSubmitResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def submit_application(
    request: ApplicationSubmitRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> ApplicationSubmitResponse:
    """
    Submit a license application.
    
    Validates input, checks rate limits, and stores the application.
    Sends email notifications to applicant and admin.
    """
    logger.info(f"📝 New license application received from: {request.email}")
    
    try:
        # Validate disposable email (warning only, don't block)
        if is_disposable_email(request.email):
            logger.warning(f"⚠️ Disposable email detected: {request.email}")
        
        # Check rate limit
        is_allowed, rate_limit_error = await check_rate_limit(db, request.email)
        if not is_allowed:
            logger.warning(f"⚠️ Rate limit exceeded for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": rate_limit_error
                }
            )
        
        # Check for duplicate pending applications (optional - allow multiple if needed)
        # For now, we allow multiple applications but log it
        has_pending = await check_duplicate_email(db, request.email)
        if has_pending:
            logger.info(f"ℹ️ Existing pending application found for: {request.email}")
        
        # Create application record
        application = LicenseApplication(
            name=request.name,
            email=request.email,
            phone=request.phone,
            experience=request.experience,
            interest=request.interest,
            monero_acknowledged=request.monero_acknowledged,
            status="pending",
            payment_status="not_started"
        )
        
        db.add(application)
        await db.commit()
        await db.refresh(application)
        
        logger.info(f"✅ Application created successfully: {application.id}")
        
        # Send email notifications (async, don't block)
        try:
            await send_application_email(application)
        except Exception as e:
            logger.error(f"❌ Email sending failed (non-critical): {e}")
        
        return ApplicationSubmitResponse(
            success=True,
            application_id=application.id,
            message="Application submitted successfully. We'll review within 48 hours.",
            status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting application: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Internal server error",
                "message": "Failed to submit application. Please try again."
            }
        )


@router.get("/applications/{application_id}", response_model=Dict[str, Any])
async def get_application_status(
    application_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get application status by ID.
    
    Note: In production, this should require authentication.
    """
    try:
        stmt = select(LicenseApplication).where(LicenseApplication.id == application_id)
        result = await db.execute(stmt)
        application = result.scalar_one_or_none()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return {
            "success": True,
            "application_id": application.id,
            "status": application.status,
            "payment_status": application.payment_status,
            "created_at": application.created_at.isoformat() if application.created_at else None,
            "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application"
        )

