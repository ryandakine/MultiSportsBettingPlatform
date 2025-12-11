"""
Billing API Routes
=================
Subscription management and billing endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from src.services.billing_service import billing_service, SubscriptionTier
from src.api.auth_routes import get_current_user

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


class CreateSubscriptionRequest(BaseModel):
    """Request to create subscription."""
    tier: str  # "pro" or "enterprise"
    payment_method_id: Optional[str] = None


class UpgradeRequest(BaseModel):
    """Request to upgrade subscription."""
    new_tier: str


@router.post("/subscribe")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create new subscription for user.
    
    Requires:
    - User must not have active subscription
    - Payment method must be provided
    """
    user_id = current_user.get("user_id")
    
    # Validate tier
    try:
        tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Create Stripe customer if needed
    customer_id = await billing_service.create_customer(
        user_id=user_id,
        email=current_user.get("email"),
        name=current_user.get("username")
    )
    
    if not customer_id:
        raise HTTPException(status_code=500, detail="Failed to create customer")
    
    # Create subscription
    subscription = await billing_service.create_subscription(customer_id, tier)
    
    if not subscription:
        raise HTTPException(status_code=500, detail="Failed to create subscription")
    
    return {
        "success": True,
        "subscription": subscription,
        "message": f"Successfully subscribed to {tier.value} tier"
    }


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Upgrade existing subscription."""
    # TODO: Get user's current subscription from database
    subscription_id = "sub_xxx"  # Placeholder
    
    try:
        new_tier = SubscriptionTier(request.new_tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    success = await billing_service.upgrade_subscription(subscription_id, new_tier)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upgrade subscription")
    
    return {
        "success": True,
        "message": f"Upgraded to {new_tier.value} tier"
    }


@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """Cancel subscription at period end."""
    # TODO: Get user's subscription from database
    subscription_id = "sub_xxx"  # Placeholder
    
    success = await billing_service.cancel_subscription(subscription_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    return {
        "success": True,
        "message": "Subscription will cancel at period end"
    }


@router.get("/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    """Get current usage and limits."""
    user_id = current_user.get("user_id")
    
    # TODO: Get user's tier from database
    tier = SubscriptionTier.FREE  # Placeholder
    
    usage = await billing_service.check_usage_limit(user_id, tier)
    
    return {
        "tier": tier.value,
        **usage
    }


@router.get("/tiers")
async def get_subscription_tiers():
    """Get available subscription tiers and pricing."""
    tiers = {}
    
    for tier, config in billing_service.tiers.items():
        tiers[tier.value] = {
            "price": config["price"],
            "predictions_per_month": config["predictions_per_month"],
            "features": config["features"]
        }
    
    return {"tiers": tiers}


@router.post("/webhook")
async def stripe_webhook(
    stripe_signature: Optional[str] = Header(None)
):
    """
    Handle Stripe webhooks.
    
    Stripe sends events like:
    - customer.subscription.created
    - customer.subscription.updated
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    # TODO: Verify webhook signature
    # TODO: Parse webhook payload
    
    event_type = "customer.subscription.updated"  # Placeholder
    event_data = {}  # Placeholder
    
    success = await billing_service.handle_webhook(event_type, event_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return {"received": True}
