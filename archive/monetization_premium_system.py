#!/usr/bin/env python3
"""
Monetization & Premium Features System - YOLO MODE!
===================================================
Subscription tiers, payment processing, premium analytics, revenue tracking,
and exclusive features for profitable sports betting platform
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
import hashlib
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SubscriptionTier:
    """Subscription tier configuration"""
    tier_id: str
    name: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    max_predictions_per_day: int
    max_portfolio_size: float
    premium_analytics: bool
    priority_support: bool
    exclusive_content: bool
    api_access: bool
    custom_alerts: bool
    advanced_charts: bool
    risk_management: bool
    is_active: bool = True

@dataclass
class UserSubscription:
    """User subscription information"""
    user_id: str
    tier_id: str
    status: str  # 'active', 'cancelled', 'expired', 'trial'
    start_date: str
    end_date: str
    auto_renew: bool
    payment_method: str
    last_payment_date: str
    next_payment_date: str
    total_paid: float
    trial_used: bool

@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    status: str  # 'pending', 'completed', 'failed', 'refunded'
    description: str
    timestamp: str
    gateway_response: Dict[str, Any]
    subscription_tier: str

@dataclass
class PremiumFeature:
    """Premium feature configuration"""
    feature_id: str
    name: str
    description: str
    tier_required: str
    is_active: bool
    usage_limits: Dict[str, Any]
    pricing: Dict[str, Any]

@dataclass
class RevenueMetrics:
    """Revenue tracking metrics"""
    total_revenue: float
    monthly_recurring_revenue: float
    annual_recurring_revenue: float
    active_subscriptions: int
    churn_rate: float
    average_revenue_per_user: float
    conversion_rate: float
    trial_conversion_rate: float
    revenue_by_tier: Dict[str, float]
    revenue_by_month: Dict[str, float]

@dataclass
class PremiumAnalytics:
    """Premium analytics features"""
    user_id: str
    advanced_portfolio_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    performance_benchmarks: Dict[str, Any]
    predictive_insights: Dict[str, Any]
    market_intelligence: Dict[str, Any]
    custom_reports: List[Dict[str, Any]]

class SubscriptionManager:
    """Subscription management system"""
    
    def __init__(self):
        self.subscription_tiers = {}
        self.user_subscriptions = {}
        self.payment_transactions = []
        
        # Initialize default subscription tiers
        self._initialize_subscription_tiers()
        
        logger.info("🚀 Subscription Manager initialized - YOLO MODE!")
    
    def _initialize_subscription_tiers(self):
        """Initialize default subscription tiers"""
        self.subscription_tiers = {
            "free": SubscriptionTier(
                tier_id="free",
                name="Free",
                price_monthly=0.0,
                price_yearly=0.0,
                features=[
                    "Basic predictions (5/day)",
                    "Standard portfolio tracking",
                    "Basic charts",
                    "Community access"
                ],
                max_predictions_per_day=5,
                max_portfolio_size=1000.0,
                premium_analytics=False,
                priority_support=False,
                exclusive_content=False,
                api_access=False,
                custom_alerts=False,
                advanced_charts=False,
                risk_management=False
            ),
            "pro": SubscriptionTier(
                tier_id="pro",
                name="Pro",
                price_monthly=19.99,
                price_yearly=199.99,
                features=[
                    "Advanced predictions (25/day)",
                    "Enhanced portfolio tracking",
                    "Premium analytics",
                    "Advanced charts",
                    "Custom alerts",
                    "Priority support",
                    "Risk management tools"
                ],
                max_predictions_per_day=25,
                max_portfolio_size=10000.0,
                premium_analytics=True,
                priority_support=True,
                exclusive_content=False,
                api_access=False,
                custom_alerts=True,
                advanced_charts=True,
                risk_management=True
            ),
            "premium": SubscriptionTier(
                tier_id="premium",
                name="Premium",
                price_monthly=49.99,
                price_yearly=499.99,
                features=[
                    "Unlimited predictions",
                    "Unlimited portfolio size",
                    "Premium analytics",
                    "Advanced charts",
                    "Custom alerts",
                    "Priority support",
                    "Risk management tools",
                    "Exclusive content",
                    "API access",
                    "Personal betting advisor"
                ],
                max_predictions_per_day=999999,
                max_portfolio_size=999999.0,
                premium_analytics=True,
                priority_support=True,
                exclusive_content=True,
                api_access=True,
                custom_alerts=True,
                advanced_charts=True,
                risk_management=True
            ),
            "enterprise": SubscriptionTier(
                tier_id="enterprise",
                name="Enterprise",
                price_monthly=199.99,
                price_yearly=1999.99,
                features=[
                    "Everything in Premium",
                    "White-label solution",
                    "Custom integrations",
                    "Dedicated support",
                    "Advanced reporting",
                    "Team management",
                    "Custom features"
                ],
                max_predictions_per_day=999999,
                max_portfolio_size=999999.0,
                premium_analytics=True,
                priority_support=True,
                exclusive_content=True,
                api_access=True,
                custom_alerts=True,
                advanced_charts=True,
                risk_management=True
            )
        }
    
    def get_subscription_tier(self, tier_id: str) -> Optional[SubscriptionTier]:
        """Get subscription tier by ID"""
        return self.subscription_tiers.get(tier_id)
    
    def get_all_tiers(self) -> List[SubscriptionTier]:
        """Get all active subscription tiers"""
        return [tier for tier in self.subscription_tiers.values() if tier.is_active]
    
    def create_user_subscription(self, user_id: str, tier_id: str, payment_method: str = "credit_card") -> UserSubscription:
        """Create new user subscription"""
        tier = self.get_subscription_tier(tier_id)
        if not tier:
            raise ValueError(f"Invalid tier ID: {tier_id}")
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)  # Monthly subscription
        
        subscription = UserSubscription(
            user_id=user_id,
            tier_id=tier_id,
            status="active",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            auto_renew=True,
            payment_method=payment_method,
            last_payment_date=start_date.isoformat(),
            next_payment_date=end_date.isoformat(),
            total_paid=tier.price_monthly,
            trial_used=False
        )
        
        self.user_subscriptions[user_id] = subscription
        
        # Create payment transaction
        self._create_payment_transaction(user_id, tier.price_monthly, "subscription", tier_id)
        
        return subscription
    
    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user subscription"""
        return self.user_subscriptions.get(user_id)
    
    def upgrade_subscription(self, user_id: str, new_tier_id: str) -> UserSubscription:
        """Upgrade user subscription"""
        current_sub = self.get_user_subscription(user_id)
        new_tier = self.get_subscription_tier(new_tier_id)
        
        if not current_sub or not new_tier:
            raise ValueError("Invalid subscription or tier")
        
        # Calculate prorated amount
        days_remaining = (datetime.fromisoformat(current_sub.end_date) - datetime.now()).days
        if days_remaining > 0:
            current_tier = self.get_subscription_tier(current_sub.tier_id)
            refund_amount = (current_tier.price_monthly / 30) * days_remaining
            upgrade_cost = new_tier.price_monthly - refund_amount
        else:
            upgrade_cost = new_tier.price_monthly
        
        # Update subscription
        current_sub.tier_id = new_tier_id
        current_sub.total_paid += upgrade_cost
        current_sub.last_payment_date = datetime.now().isoformat()
        
        # Create payment transaction
        self._create_payment_transaction(user_id, upgrade_cost, "upgrade", new_tier_id)
        
        return current_sub
    
    def cancel_subscription(self, user_id: str) -> UserSubscription:
        """Cancel user subscription"""
        subscription = self.get_user_subscription(user_id)
        if subscription:
            subscription.status = "cancelled"
            subscription.auto_renew = False
        return subscription
    
    def _create_payment_transaction(self, user_id: str, amount: float, description: str, tier_id: str):
        """Create payment transaction record"""
        transaction = PaymentTransaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            currency="USD",
            payment_method="credit_card",
            status="completed",
            description=description,
            timestamp=datetime.now().isoformat(),
            gateway_response={"status": "success", "transaction_id": str(uuid.uuid4())},
            subscription_tier=tier_id
        )
        
        self.payment_transactions.append(transaction)

class PremiumFeaturesManager:
    """Premium features management system"""
    
    def __init__(self):
        self.premium_features = {}
        self.user_feature_access = defaultdict(set)
        
        # Initialize premium features
        self._initialize_premium_features()
        
        logger.info("🚀 Premium Features Manager initialized - YOLO MODE!")
    
    def _initialize_premium_features(self):
        """Initialize premium features"""
        self.premium_features = {
            "advanced_analytics": PremiumFeature(
                feature_id="advanced_analytics",
                name="Advanced Analytics",
                description="Deep portfolio analysis with predictive insights",
                tier_required="pro",
                is_active=True,
                usage_limits={"daily_queries": 100},
                pricing={"one_time": 29.99, "monthly": 9.99}
            ),
            "risk_management": PremiumFeature(
                feature_id="risk_management",
                name="Risk Management Tools",
                description="Advanced risk assessment and portfolio protection",
                tier_required="pro",
                is_active=True,
                usage_limits={"daily_assessments": 50},
                pricing={"one_time": 19.99, "monthly": 4.99}
            ),
            "custom_alerts": PremiumFeature(
                feature_id="custom_alerts",
                name="Custom Alerts",
                description="Personalized betting alerts and notifications",
                tier_required="pro",
                is_active=True,
                usage_limits={"max_alerts": 20},
                pricing={"one_time": 14.99, "monthly": 2.99}
            ),
            "api_access": PremiumFeature(
                feature_id="api_access",
                name="API Access",
                description="Programmatic access to betting data and predictions",
                tier_required="premium",
                is_active=True,
                usage_limits={"daily_requests": 1000},
                pricing={"one_time": 99.99, "monthly": 19.99}
            ),
            "personal_advisor": PremiumFeature(
                feature_id="personal_advisor",
                name="Personal Betting Advisor",
                description="AI-powered personal betting recommendations",
                tier_required="premium",
                is_active=True,
                usage_limits={"daily_recommendations": 10},
                pricing={"one_time": 149.99, "monthly": 29.99}
            ),
            "exclusive_content": PremiumFeature(
                feature_id="exclusive_content",
                name="Exclusive Content",
                description="Premium betting insights and expert analysis",
                tier_required="premium",
                is_active=True,
                usage_limits={"daily_content": 50},
                pricing={"one_time": 49.99, "monthly": 9.99}
            )
        }
    
    def get_user_features(self, user_id: str, subscription_tier: str) -> List[PremiumFeature]:
        """Get features available to user based on subscription tier"""
        available_features = []
        
        for feature in self.premium_features.values():
            if feature.is_active and self._tier_has_access(subscription_tier, feature.tier_required):
                available_features.append(feature)
        
        return available_features
    
    def _tier_has_access(self, user_tier: str, required_tier: str) -> bool:
        """Check if user tier has access to required tier"""
        tier_hierarchy = ["free", "pro", "premium", "enterprise"]
        
        try:
            user_index = tier_hierarchy.index(user_tier)
            required_index = tier_hierarchy.index(required_tier)
            return user_index >= required_index
        except ValueError:
            return False
    
    def check_feature_access(self, user_id: str, feature_id: str, subscription_tier: str) -> bool:
        """Check if user has access to specific feature"""
        feature = self.premium_features.get(feature_id)
        if not feature or not feature.is_active:
            return False
        
        return self._tier_has_access(subscription_tier, feature.tier_required)

class RevenueTracker:
    """Revenue tracking and analytics system"""
    
    def __init__(self):
        self.revenue_data = []
        self.subscription_manager = None
        
        logger.info("🚀 Revenue Tracker initialized - YOLO MODE!")
    
    def set_subscription_manager(self, subscription_manager: SubscriptionManager):
        """Set subscription manager reference"""
        self.subscription_manager = subscription_manager
    
    def add_revenue(self, amount: float, source: str, user_id: str = None):
        """Add revenue entry"""
        revenue_entry = {
            "id": str(uuid.uuid4()),
            "amount": amount,
            "source": source,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "month": datetime.now().strftime("%Y-%m")
        }
        
        self.revenue_data.append(revenue_entry)
    
    def get_revenue_metrics(self) -> RevenueMetrics:
        """Calculate revenue metrics"""
        if not self.subscription_manager:
            return RevenueMetrics(
                total_revenue=0.0,
                monthly_recurring_revenue=0.0,
                annual_recurring_revenue=0.0,
                active_subscriptions=0,
                churn_rate=0.0,
                average_revenue_per_user=0.0,
                conversion_rate=0.0,
                trial_conversion_rate=0.0,
                revenue_by_tier={},
                revenue_by_month={}
            )
        
        # Calculate basic metrics
        total_revenue = sum(entry["amount"] for entry in self.revenue_data)
        
        # Calculate MRR (Monthly Recurring Revenue)
        current_month = datetime.now().strftime("%Y-%m")
        monthly_revenue = sum(
            entry["amount"] for entry in self.revenue_data 
            if entry["month"] == current_month
        )
        
        # Calculate ARR (Annual Recurring Revenue)
        annual_recurring_revenue = monthly_revenue * 12
        
        # Calculate active subscriptions
        active_subscriptions = len([
            sub for sub in self.subscription_manager.user_subscriptions.values()
            if sub.status == "active"
        ])
        
        # Calculate revenue by tier
        revenue_by_tier = defaultdict(float)
        for sub in self.subscription_manager.user_subscriptions.values():
            if sub.status == "active":
                tier = self.subscription_manager.get_subscription_tier(sub.tier_id)
                if tier:
                    revenue_by_tier[sub.tier_id] += tier.price_monthly
        
        # Calculate revenue by month
        revenue_by_month = defaultdict(float)
        for entry in self.revenue_data:
            revenue_by_month[entry["month"]] += entry["amount"]
        
        # Calculate average revenue per user
        avg_revenue_per_user = total_revenue / max(active_subscriptions, 1)
        
        return RevenueMetrics(
            total_revenue=total_revenue,
            monthly_recurring_revenue=monthly_revenue,
            annual_recurring_revenue=annual_recurring_revenue,
            active_subscriptions=active_subscriptions,
            churn_rate=0.05,  # Placeholder - would need historical data
            average_revenue_per_user=avg_revenue_per_user,
            conversion_rate=0.15,  # Placeholder
            trial_conversion_rate=0.25,  # Placeholder
            revenue_by_tier=dict(revenue_by_tier),
            revenue_by_month=dict(revenue_by_month)
        )

class PremiumAnalyticsEngine:
    """Premium analytics engine for advanced insights"""
    
    def __init__(self):
        logger.info("🚀 Premium Analytics Engine initialized - YOLO MODE!")
    
    def generate_advanced_portfolio_analysis(self, user_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced portfolio analysis"""
        # Simulate advanced analysis
        total_value = portfolio_data.get("total_value", 0)
        total_profit = portfolio_data.get("total_profit", 0)
        roi = portfolio_data.get("roi_percentage", 0)
        
        # Risk assessment
        risk_score = self._calculate_risk_score(portfolio_data)
        volatility = self._calculate_volatility(portfolio_data)
        
        # Performance benchmarks
        benchmarks = {
            "market_average": 8.5,
            "top_performers": 15.2,
            "risk_adjusted_return": roi / max(risk_score, 1)
        }
        
        # Predictive insights
        predictions = {
            "projected_roi_30d": roi * 1.1,
            "projected_roi_90d": roi * 1.25,
            "risk_level": "medium" if risk_score < 0.5 else "high",
            "recommended_actions": self._generate_recommendations(portfolio_data)
        }
        
        return {
            "risk_assessment": {
                "risk_score": risk_score,
                "volatility": volatility,
                "risk_level": "medium" if risk_score < 0.5 else "high"
            },
            "performance_benchmarks": benchmarks,
            "predictive_insights": predictions,
            "recommendations": self._generate_recommendations(portfolio_data)
        }
    
    def _calculate_risk_score(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate portfolio risk score"""
        # Simulate risk calculation
        win_rate = portfolio_data.get("win_rate", 50)
        roi = portfolio_data.get("roi_percentage", 0)
        total_bets = portfolio_data.get("total_bets", 1)
        
        # Risk factors
        win_rate_risk = max(0, (50 - win_rate) / 50)
        roi_risk = max(0, (-roi) / 100)
        sample_size_risk = max(0, (10 - total_bets) / 10)
        
        return (win_rate_risk + roi_risk + sample_size_risk) / 3
    
    def _calculate_volatility(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate portfolio volatility"""
        # Simulate volatility calculation
        return random.uniform(0.1, 0.3)
    
    def _generate_recommendations(self, portfolio_data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        roi = portfolio_data.get("roi_percentage", 0)
        win_rate = portfolio_data.get("win_rate", 50)
        
        if roi < 0:
            recommendations.append("Consider reducing bet sizes to minimize losses")
            recommendations.append("Review your betting strategy and focus on higher confidence picks")
        
        if win_rate < 45:
            recommendations.append("Focus on sports where you have better historical performance")
            recommendations.append("Consider using more conservative betting strategies")
        
        if roi > 10:
            recommendations.append("Your strategy is working well - consider increasing position sizes gradually")
            recommendations.append("Diversify across more sports to spread risk")
        
        return recommendations

class MonetizationSystem:
    """Complete monetization system"""
    
    def __init__(self):
        self.subscription_manager = SubscriptionManager()
        self.premium_features_manager = PremiumFeaturesManager()
        self.revenue_tracker = RevenueTracker()
        self.premium_analytics = PremiumAnalyticsEngine()
        
        # Connect components
        self.revenue_tracker.set_subscription_manager(self.subscription_manager)
        
        logger.info("🚀 Monetization System initialized - YOLO MODE!")
    
    def get_subscription_tiers(self) -> List[SubscriptionTier]:
        """Get all subscription tiers"""
        return self.subscription_manager.get_all_tiers()
    
    def create_subscription(self, user_id: str, tier_id: str, payment_method: str = "credit_card") -> UserSubscription:
        """Create new subscription"""
        subscription = self.subscription_manager.create_user_subscription(user_id, tier_id, payment_method)
        
        # Add revenue tracking
        tier = self.subscription_manager.get_subscription_tier(tier_id)
        if tier:
            self.revenue_tracker.add_revenue(tier.price_monthly, "subscription", user_id)
        
        return subscription
    
    def get_user_features(self, user_id: str) -> List[PremiumFeature]:
        """Get features available to user"""
        subscription = self.subscription_manager.get_user_subscription(user_id)
        if not subscription:
            return self.premium_features_manager.get_user_features(user_id, "free")
        
        return self.premium_features_manager.get_user_features(user_id, subscription.tier_id)
    
    def check_feature_access(self, user_id: str, feature_id: str) -> bool:
        """Check if user has access to feature"""
        subscription = self.subscription_manager.get_user_subscription(user_id)
        tier_id = subscription.tier_id if subscription else "free"
        
        return self.premium_features_manager.check_feature_access(user_id, feature_id, tier_id)
    
    def generate_premium_analytics(self, user_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate premium analytics for user"""
        if not self.check_feature_access(user_id, "advanced_analytics"):
            return {"error": "Premium analytics not available for your subscription tier"}
        
        return self.premium_analytics.generate_advanced_portfolio_analysis(user_id, portfolio_data)
    
    def get_revenue_metrics(self) -> RevenueMetrics:
        """Get revenue metrics"""
        return self.revenue_tracker.get_revenue_metrics()
    
    def upgrade_user(self, user_id: str, new_tier_id: str) -> UserSubscription:
        """Upgrade user subscription"""
        return self.subscription_manager.upgrade_subscription(user_id, new_tier_id)
    
    def cancel_user_subscription(self, user_id: str) -> UserSubscription:
        """Cancel user subscription"""
        return self.subscription_manager.cancel_subscription(user_id)

async def main():
    """Test the monetization and premium features system"""
    print("🚀 Testing Monetization & Premium Features System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize monetization system
    monetization = MonetizationSystem()
    
    try:
        # Test subscription tiers
        print("\n💰 Testing Subscription Tiers:")
        print("-" * 40)
        
        tiers = monetization.get_subscription_tiers()
        for tier in tiers:
            print(f"✅ {tier.name}: ${tier.price_monthly}/month")
            print(f"   Features: {len(tier.features)} premium features")
            print(f"   Max predictions: {tier.max_predictions_per_day}/day")
            print(f"   Premium analytics: {'✅' if tier.premium_analytics else '❌'}")
            print(f"   API access: {'✅' if tier.api_access else '❌'}")
            print()
        
        # Test user subscriptions
        print("\n👤 Testing User Subscriptions:")
        print("-" * 40)
        
        # Create test subscriptions
        user1_sub = monetization.create_subscription("user1", "pro")
        user2_sub = monetization.create_subscription("user2", "premium")
        user3_sub = monetization.create_subscription("user3", "enterprise")
        
        print(f"✅ User1 (Pro): ${user1_sub.total_paid} - Status: {user1_sub.status}")
        print(f"✅ User2 (Premium): ${user2_sub.total_paid} - Status: {user2_sub.status}")
        print(f"✅ User3 (Enterprise): ${user3_sub.total_paid} - Status: {user3_sub.status}")
        
        # Test premium features
        print("\n⭐ Testing Premium Features:")
        print("-" * 40)
        
        for user_id in ["user1", "user2", "user3"]:
            features = monetization.get_user_features(user_id)
            print(f"👤 {user_id} has access to {len(features)} premium features:")
            for feature in features:
                print(f"   - {feature.name}: {feature.description}")
            print()
        
        # Test feature access
        print("\n🔐 Testing Feature Access:")
        print("-" * 40)
        
        test_features = ["advanced_analytics", "api_access", "personal_advisor"]
        for user_id in ["user1", "user2", "user3"]:
            print(f"👤 {user_id} feature access:")
            for feature in test_features:
                has_access = monetization.check_feature_access(user_id, feature)
                print(f"   - {feature}: {'✅' if has_access else '❌'}")
            print()
        
        # Test premium analytics
        print("\n📊 Testing Premium Analytics:")
        print("-" * 40)
        
        sample_portfolio = {
            "total_value": 1059.05,
            "total_profit": 34.05,
            "roi_percentage": 3.3,
            "win_rate": 62.5,
            "total_bets": 8,
            "winning_bets": 5,
            "losing_bets": 3
        }
        
        analytics = monetization.generate_premium_analytics("user2", sample_portfolio)
        print(f"✅ Premium analytics generated for user2")
        print(f"   Risk assessment: {analytics.get('risk_assessment', {}).get('risk_level', 'N/A')}")
        print(f"   Recommendations: {len(analytics.get('recommendations', []))} suggestions")
        
        # Test revenue tracking
        print("\n💰 Testing Revenue Tracking:")
        print("-" * 40)
        
        revenue_metrics = monetization.get_revenue_metrics()
        print(f"✅ Total Revenue: ${revenue_metrics.total_revenue:.2f}")
        print(f"✅ Monthly Recurring Revenue: ${revenue_metrics.monthly_recurring_revenue:.2f}")
        print(f"✅ Annual Recurring Revenue: ${revenue_metrics.annual_recurring_revenue:.2f}")
        print(f"✅ Active Subscriptions: {revenue_metrics.active_subscriptions}")
        print(f"✅ Average Revenue Per User: ${revenue_metrics.average_revenue_per_user:.2f}")
        
        # Test subscription upgrades
        print("\n⬆️ Testing Subscription Upgrades:")
        print("-" * 40)
        
        upgraded_sub = monetization.upgrade_user("user1", "premium")
        print(f"✅ User1 upgraded to Premium: ${upgraded_sub.total_paid} total paid")
        
        # Test subscription cancellation
        print("\n❌ Testing Subscription Cancellation:")
        print("-" * 40)
        
        cancelled_sub = monetization.cancel_user_subscription("user3")
        print(f"✅ User3 subscription cancelled: Status = {cancelled_sub.status}")
        
        # Final revenue metrics
        print("\n📈 Final Revenue Metrics:")
        print("-" * 40)
        
        final_metrics = monetization.get_revenue_metrics()
        print(f"✅ Total Revenue: ${final_metrics.total_revenue:.2f}")
        print(f"✅ Active Subscriptions: {final_metrics.active_subscriptions}")
        print(f"✅ Revenue by Tier: {final_metrics.revenue_by_tier}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Monetization & Premium Features System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 