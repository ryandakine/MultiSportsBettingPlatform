"""
Subscription Database Model
===========================
Track user subscriptions and usage.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from src.db.models import Base


class Subscription(Base):
    """User subscription model."""
    
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Stripe integration
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Subscription details
    tier = Column(String, nullable=False, default="free")  # free, pro, enterprise
    status = Column(String, nullable=False, default="active")  # active, cancelled, past_due
    
    # Billing
    price_monthly = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="usd")
    
    # Usage tracking
    predictions_used = Column(Integer, nullable=False, default=0)
    predictions_limit = Column(Integer, nullable=False, default=10)  # -1 = unlimited
    
    # Period
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)


class UsageLog(Base):
    """Track prediction usage for billing."""
    
    __tablename__ = "usage_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    subscription_id = Column(String, nullable=False)
    
    # Usage details
    predictions_count = Column(Integer, nullable=False, default=1)
    endpoint = Column(String, nullable=True)  # Which API endpoint
    
    # Timestamps
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)
