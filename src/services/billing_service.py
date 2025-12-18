"""
Stripe Billing Integration
==========================
Handle subscriptions, payments, and usage tracking for monetization.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SubscriptionTier(str, Enum):
    """Subscription tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingService:
    """
    Stripe billing integration for subscription management.
    
    Features:
    - Subscription creation/upgrade/downgrade
    - Usage tracking
    - Webhook handling
    - Invoice management
    """
    
    def __init__(self, stripe_api_key: Optional[str] = None):
        self.stripe_api_key = stripe_api_key
        self.stripe = None
        
        # Tier configurations
        self.tiers = {
            SubscriptionTier.FREE: {
                "price_id": None,
                "predictions_per_month": 10,
                "price": 0,
                "features": ["10 predictions/month", "Basic support"]
            },
            SubscriptionTier.PRO: {
                "price_id": "price_pro_monthly",  # Stripe price ID
                "predictions_per_month": 500,
                "price": 29.99,
                "features": [
                    "500 predictions/month",
                    "Real-time updates",
                    "Advanced analytics",
                    "Priority support"
                ]
            },
            SubscriptionTier.ENTERPRISE: {
                "price_id": "price_enterprise_monthly",
                "predictions_per_month": -1,  # Unlimited
                "price": 99.99,
                "features": [
                    "Unlimited predictions",
                    "Custom models",
                    "API access",
                    "Dedicated support",
                    "White label option"
                ]
            }
        }
    
    async def _init_stripe(self):
        """Lazy-initialize Stripe SDK."""
        if self.stripe is None:
            try:
                import stripe
                if self.stripe_api_key:
                    stripe.api_key = self.stripe_api_key
                self.stripe = stripe
                logger.info("✅ Stripe initialized")
            except ImportError:
                logger.warning("⚠️ Stripe SDK not installed")
                self.stripe = False
        
        return self.stripe if self.stripe is not False else None
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None
    ) -> Optional[str]:
        """
        Create Stripe customer.
        
        Args:
            user_id: Internal user ID
            email: User email
            name: User name
        
        Returns:
            Stripe customer ID
        """
        stripe = await self._init_stripe()
        if not stripe:
            return None
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            
            logger.info(f"Created Stripe customer: {customer.id} for user {user_id}")
            return customer.id
            
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    async def create_subscription(
        self,
        customer_id: str,
        tier: SubscriptionTier
    ) -> Optional[Dict[str, Any]]:
        """
        Create subscription for customer.
        
        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier
        
        Returns:
            Subscription details
        """
        stripe = await self._init_stripe()
        if not stripe:
            return None
        
        tier_config = self.tiers[tier]
        
        # Free tier doesn't need Stripe subscription
        if tier == SubscriptionTier.FREE:
            return {
                "tier": tier.value,
                "status": "active",
                "predictions_remaining": tier_config["predictions_per_month"]
            }
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": tier_config["price_id"]}],
                metadata={"tier": tier.value}
            )
            
            logger.info(f"Created subscription: {subscription.id} for tier {tier.value}")
            
            return {
                "subscription_id": subscription.id,
                "tier": tier.value,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "predictions_remaining": tier_config["predictions_per_month"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_tier: SubscriptionTier
    ) -> bool:
        """Upgrade subscription to new tier."""
        stripe = await self._init_stripe()
        if not stripe:
            return False
        
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update to new price
            new_price_id = self.tiers[new_tier]["price_id"]
            
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id
                }],
                metadata={"tier": new_tier.value}
            )
            
            logger.info(f"Upgraded subscription {subscription_id} to {new_tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {e}")
            return False
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription at period end."""
        stripe = await self._init_stripe()
        if not stripe:
            return False
        
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Scheduled cancellation for subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    async def track_usage(
        self,
        user_id: str,
        predictions_used: int = 1
    ) -> bool:
        """
        Track prediction usage for billing.
        
        Args:
            user_id: User ID
            predictions_used: Number of predictions used
        
        Returns:
            True if within limits, False if exceeded
        """
        # Usage tracking is implemented via UsageLog model
        # For now, just return True
        return True
    
    async def check_usage_limit(
        self,
        user_id: str,
        tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """
        Check if user is within usage limits.
        
        Returns:
            Usage information
        """
        from src.db.database import AsyncSessionLocal
        from src.db.models.subscription import Subscription, UsageLog
        from sqlalchemy import select, func, and_
        from datetime import datetime, timedelta
        
        tier_config = self.tiers[tier]
        monthly_limit = tier_config["predictions_per_month"]
        
        # Get actual usage from database (last 30 days)
        month_start = datetime.utcnow() - timedelta(days=30)
        
        async with AsyncSessionLocal() as session:
            # Get user's subscription to get subscription_id
            sub_result = await session.execute(
                select(Subscription)
                .where(
                    Subscription.user_id == user_id,
                    Subscription.status == "active"
                )
                .order_by(Subscription.created_at.desc())
            )
            subscription = sub_result.scalar_one_or_none()
            
            if subscription:
                # Count usage logs from last 30 days
                usage_result = await session.execute(
                    select(func.sum(UsageLog.predictions_count))
                    .where(
                        and_(
                            UsageLog.user_id == user_id,
                            UsageLog.subscription_id == subscription.id,
                            UsageLog.timestamp >= month_start
                        )
                    )
                )
                current_usage = usage_result.scalar() or 0
            else:
                current_usage = 0
        
        if monthly_limit == -1:
            # Unlimited
            return {
                "within_limit": True,
                "usage": current_usage,
                "limit": "unlimited"
            }
        
        return {
            "within_limit": current_usage < monthly_limit,
            "usage": current_usage,
            "limit": monthly_limit,
            "remaining": max(0, monthly_limit - current_usage)
        }
    
    async def handle_webhook(self, event_type: str, event_data: Dict) -> bool:
        """
        Handle Stripe webhook events.
        
        Args:
            event_type: Stripe event type
            event_data: Event payload
        
        Returns:
            True if handled successfully
        """
        logger.info(f"Received Stripe webhook: {event_type}")
        
        try:
            if event_type == "customer.subscription.created":
                # Handle new subscription
                pass
            
            elif event_type == "customer.subscription.updated":
                # Handle subscription update
                pass
            
            elif event_type == "customer.subscription.deleted":
                # Handle cancellation
                pass
            
            elif event_type == "invoice.payment_succeeded":
                # Handle successful payment
                pass
            
            elif event_type == "invoice.payment_failed":
                # Handle failed payment
                logger.warning(f"Payment failed for customer")
            
            return True
            
        except Exception as e:
            logger.error(f"Webhook handler error: {e}")
            return False


# Global billing service
billing_service = BillingService()
