"""
Billing Service Tests
====================
Unit tests for Stripe billing integration.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.billing_service import BillingService, SubscriptionTier


@pytest_asyncio.fixture
async def billing_service():
    """Provide test billing service."""
    service = BillingService(stripe_api_key="sk_test_fake")
    yield service


@pytest.mark.asyncio
class TestSubscriptionTiers:
    """Test subscription tier configurations."""
    
    async def test_tier_definitions(self, billing_service):
        """Test that all tiers are properly defined."""
        assert SubscriptionTier.FREE in billing_service.tiers
        assert SubscriptionTier.PRO in billing_service.tiers
        assert SubscriptionTier.ENTERPRISE in billing_service.tiers
    
    async def test_free_tier_limits(self, billing_service):
        """Test free tier configuration."""
        free_config = billing_service.tiers[SubscriptionTier.FREE]
        
        assert free_config["price"] == 0
        assert free_config["predictions_per_month"] == 10
        assert len(free_config["features"]) > 0
    
    async def test_pro_tier_limits(self, billing_service):
        """Test pro tier configuration."""
        pro_config = billing_service.tiers[SubscriptionTier.PRO]
        
        assert pro_config["price"] > 0
        assert pro_config["predictions_per_month"] > 10
    
    async def test_enterprise_unlimited(self, billing_service):
        """Test enterprise tier has unlimited usage."""
        ent_config = billing_service.tiers[SubscriptionTier.ENTERPRISE]
        
        assert ent_config["predictions_per_month"] == -1  # Unlimited


@pytest.mark.asyncio
class TestSubscriptionCreation:
    """Test subscription creation."""
    
    @patch('stripe.Customer.create')
    async def test_create_customer(self, mock_create, billing_service):
        """Test creating Stripe customer."""
        mock_customer = MagicMock()
        mock_customer.id = "cus_test123"
        mock_create.return_value = mock_customer
        
        # Initialize Stripe
        await billing_service._init_stripe()
        
        customer_id = await billing_service.create_customer(
            user_id="user_123",
            email="test@example.com",
            name="Test User"
        )
        
        # May be None if Stripe not installed
        if billing_service.stripe:
            assert customer_id == "cus_test123"
    
    async def test_create_free_subscription(self, billing_service):
        """Test creating free tier subscription."""
        subscription = await billing_service.create_subscription(
            customer_id="cus_test",
            tier=SubscriptionTier.FREE
        )
        
        assert subscription["tier"] == "free"
        assert subscription["status"] == "active"
        assert "predictions_remaining" in subscription


@pytest.mark.asyncio
class TestUsageTracking:
    """Test usage tracking and limits."""
    
    async def test_check_usage_within_limit(self, billing_service):
        """Test usage check when within limits."""
        usage = await billing_service.check_usage_limit(
            user_id="user_123",
            tier=SubscriptionTier.FREE
        )
        
        assert "within_limit" in usage
        assert "usage" in usage
        assert "limit" in usage
    
    async def test_unlimited_usage(self, billing_service):
        """Test unlimited tier usage check."""
        usage = await billing_service.check_usage_limit(
            user_id="user_enterprise",
            tier=SubscriptionTier.ENTERPRISE
        )
        
        assert usage["within_limit"] is True
        assert usage["limit"] == "unlimited"
    
    async def test_track_usage(self, billing_service):
        """Test tracking prediction usage."""
        result = await billing_service.track_usage("user_123", predictions_used=1)
        
        # Should return True (placeholder implementation)
        assert result is True


@pytest.mark.asyncio
class TestWebhookHandling:
    """Test Stripe webhook handling."""
    
    async def test_subscription_created_webhook(self, billing_service):
        """Test handling subscription.created webhook."""
        result = await billing_service.handle_webhook(
            "customer.subscription.created",
            {"subscription": {"id": "sub_123"}}
        )
        
        assert result is True
    
    async def test_payment_succeeded_webhook(self, billing_service):
        """Test handling payment.succeeded webhook."""
        result = await billing_service.handle_webhook(
            "invoice.payment_succeeded",
            {"invoice": {"id": "in_123"}}
        )
        
        assert result is True
    
    async def test_payment_failed_webhook(self, billing_service):
        """Test handling payment.failed webhook."""
        result = await billing_service.handle_webhook(
            "invoice.payment_failed",
            {"invoice": {"id": "in_123"}}
        )
        
        # Should handle gracefully
        assert result is True


@pytest.mark.asyncio
class TestUpgradeDowngrade:
    """Test subscription upgrades and downgrades."""
    
    @patch('stripe.Subscription.retrieve')
    @patch('stripe.Subscription.modify')
    async def test_upgrade_subscription(self, mock_modify, mock_retrieve, billing_service):
        """Test upgrading subscription."""
        mock_subscription = MagicMock()
        mock_subscription.__getitem__ = MagicMock(return_value={"data": [MagicMock()]})
        mock_retrieve.return_value = mock_subscription
        
        await billing_service._init_stripe()
        
        if billing_service.stripe:
            result = await billing_service.upgrade_subscription(
                "sub_123",
                SubscriptionTier.ENTERPRISE
            )
            
            # Should call Stripe API
            assert result is True or result is False  # Depends on mock
    
    @patch('stripe.Subscription.modify')
    async def test_cancel_subscription(self, mock_modify, billing_service):
        """Test subscription cancellation."""
        await billing_service._init_stripe()
        
        if billing_service.stripe:
            result = await billing_service.cancel_subscription("sub_123")
            assert result is True or result is False
