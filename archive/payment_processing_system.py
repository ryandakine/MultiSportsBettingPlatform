#!/usr/bin/env python3
"""
Payment Processing System - YOLO MODE!
=====================================
Multiple payment gateways, subscription billing, transaction management,
and secure payment processing for sports betting platform
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
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaymentMethod:
    """Payment method information"""
    payment_id: str
    user_id: str
    method_type: str  # 'credit_card', 'debit_card', 'paypal', 'stripe', 'crypto'
    card_type: str = ""  # 'visa', 'mastercard', 'amex', 'discover'
    last_four: str = ""
    expiry_month: int = 0
    expiry_year: int = 0
    is_default: bool = False
    is_active: bool = True
    created_at: str = ""

@dataclass
class PaymentRequest:
    """Payment request data"""
    request_id: str
    user_id: str
    amount: float
    currency: str
    description: str
    payment_method_id: str
    gateway: str  # 'stripe', 'paypal', 'square', 'crypto'
    metadata: Dict[str, Any]
    created_at: str

@dataclass
class PaymentResponse:
    """Payment response data"""
    success: bool
    transaction_id: str
    amount: float
    currency: str
    gateway: str
    status: str  # 'pending', 'completed', 'failed', 'refunded'
    error_message: str = ""
    gateway_response: Dict[str, Any] = None
    processing_time: float = 0.0

@dataclass
class BillingCycle:
    """Billing cycle information"""
    cycle_id: str
    user_id: str
    subscription_id: str
    start_date: str
    end_date: str
    amount: float
    status: str  # 'pending', 'billed', 'paid', 'failed', 'cancelled'
    payment_method_id: str
    invoice_url: str = ""
    created_at: str = ""

@dataclass
class RefundRequest:
    """Refund request data"""
    refund_id: str
    transaction_id: str
    user_id: str
    amount: float
    reason: str
    status: str  # 'pending', 'approved', 'completed', 'rejected'
    processed_at: str = ""
    created_at: str = ""

class PaymentGateway:
    """Base payment gateway class"""
    
    def __init__(self, gateway_name: str, api_key: str, secret_key: str = ""):
        self.gateway_name = gateway_name
        self.api_key = api_key
        self.secret_key = secret_key
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Connect to payment gateway"""
        # Simulate connection
        await asyncio.sleep(0.1)
        self.is_connected = True
        return True
    
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment (to be implemented by subclasses)"""
        raise NotImplementedError
    
    async def refund_payment(self, transaction_id: str, amount: float, reason: str) -> PaymentResponse:
        """Refund payment (to be implemented by subclasses)"""
        raise NotImplementedError
    
    def validate_payment_method(self, payment_method: PaymentMethod) -> bool:
        """Validate payment method"""
        # Basic validation
        if payment_method.method_type == "credit_card":
            return (
                len(payment_method.last_four) == 4 and
                payment_method.expiry_month in range(1, 13) and
                payment_method.expiry_year >= datetime.now().year
            )
        return True

class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation"""
    
    def __init__(self, api_key: str):
        super().__init__("stripe", api_key)
    
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment via Stripe"""
        start_time = time.time()
        
        try:
            # Simulate Stripe API call
            await asyncio.sleep(0.5)
            
            # Simulate success/failure
            success = random.random() > 0.1  # 90% success rate
            
            if success:
                transaction_id = f"stripe_{uuid.uuid4().hex[:16]}"
                return PaymentResponse(
                    success=True,
                    transaction_id=transaction_id,
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="stripe",
                    status="completed",
                    gateway_response={
                        "stripe_transaction_id": transaction_id,
                        "status": "succeeded",
                        "amount": payment_request.amount,
                        "currency": payment_request.currency
                    },
                    processing_time=time.time() - start_time
                )
            else:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="stripe",
                    status="failed",
                    error_message="Payment declined by bank",
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            return PaymentResponse(
                success=False,
                transaction_id="",
                amount=payment_request.amount,
                currency=payment_request.currency,
                gateway="stripe",
                status="failed",
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def refund_payment(self, transaction_id: str, amount: float, reason: str) -> PaymentResponse:
        """Refund payment via Stripe"""
        start_time = time.time()
        
        try:
            # Simulate Stripe refund API call
            await asyncio.sleep(0.3)
            
            refund_id = f"stripe_refund_{uuid.uuid4().hex[:16]}"
            return PaymentResponse(
                success=True,
                transaction_id=refund_id,
                amount=amount,
                currency="USD",
                gateway="stripe",
                status="completed",
                gateway_response={
                    "stripe_refund_id": refund_id,
                    "status": "succeeded",
                    "amount": amount
                },
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return PaymentResponse(
                success=False,
                transaction_id="",
                amount=amount,
                currency="USD",
                gateway="stripe",
                status="failed",
                error_message=str(e),
                processing_time=time.time() - start_time
            )

class PayPalGateway(PaymentGateway):
    """PayPal payment gateway implementation"""
    
    def __init__(self, client_id: str, client_secret: str):
        super().__init__("paypal", client_id, client_secret)
    
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment via PayPal"""
        start_time = time.time()
        
        try:
            # Simulate PayPal API call
            await asyncio.sleep(0.4)
            
            # Simulate success/failure
            success = random.random() > 0.05  # 95% success rate
            
            if success:
                transaction_id = f"paypal_{uuid.uuid4().hex[:16]}"
                return PaymentResponse(
                    success=True,
                    transaction_id=transaction_id,
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="paypal",
                    status="completed",
                    gateway_response={
                        "paypal_transaction_id": transaction_id,
                        "status": "completed",
                        "amount": payment_request.amount,
                        "currency": payment_request.currency
                    },
                    processing_time=time.time() - start_time
                )
            else:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="paypal",
                    status="failed",
                    error_message="PayPal payment failed",
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            return PaymentResponse(
                success=False,
                transaction_id="",
                amount=payment_request.amount,
                currency=payment_request.currency,
                gateway="paypal",
                status="failed",
                error_message=str(e),
                processing_time=time.time() - start_time
            )

class CryptoGateway(PaymentGateway):
    """Cryptocurrency payment gateway implementation"""
    
    def __init__(self, api_key: str):
        super().__init__("crypto", api_key)
    
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment via cryptocurrency"""
        start_time = time.time()
        
        try:
            # Simulate crypto payment processing
            await asyncio.sleep(1.0)  # Crypto payments take longer
            
            # Simulate success/failure
            success = random.random() > 0.15  # 85% success rate
            
            if success:
                transaction_id = f"crypto_{uuid.uuid4().hex[:16]}"
                return PaymentResponse(
                    success=True,
                    transaction_id=transaction_id,
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="crypto",
                    status="completed",
                    gateway_response={
                        "crypto_transaction_id": transaction_id,
                        "status": "confirmed",
                        "amount": payment_request.amount,
                        "currency": payment_request.currency,
                        "blockchain": "ethereum"
                    },
                    processing_time=time.time() - start_time
                )
            else:
                return PaymentResponse(
                    success=False,
                    transaction_id="",
                    amount=payment_request.amount,
                    currency=payment_request.currency,
                    gateway="crypto",
                    status="failed",
                    error_message="Crypto transaction failed",
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            return PaymentResponse(
                success=False,
                transaction_id="",
                amount=payment_request.amount,
                currency=payment_request.currency,
                gateway="crypto",
                status="failed",
                error_message=str(e),
                processing_time=time.time() - start_time
            )

class PaymentProcessor:
    """Main payment processing system"""
    
    def __init__(self):
        self.gateways = {}
        self.payment_methods = {}
        self.transactions = []
        self.billing_cycles = []
        self.refund_requests = []
        
        # Initialize payment gateways
        self._initialize_gateways()
        
        logger.info("🚀 Payment Processor initialized - YOLO MODE!")
    
    def _initialize_gateways(self):
        """Initialize payment gateways"""
        # Initialize with test keys
        self.gateways["stripe"] = StripeGateway("sk_test_stripe_key_12345")
        self.gateways["paypal"] = PayPalGateway("paypal_client_id", "paypal_secret")
        self.gateways["crypto"] = CryptoGateway("crypto_api_key_12345")
        
        # Connect to gateways
        for gateway in self.gateways.values():
            asyncio.create_task(gateway.connect())
    
    async def add_payment_method(self, user_id: str, method_data: Dict[str, Any]) -> PaymentMethod:
        """Add payment method for user"""
        payment_method = PaymentMethod(
            payment_id=str(uuid.uuid4()),
            user_id=user_id,
            method_type=method_data.get("method_type", "credit_card"),
            card_type=method_data.get("card_type", ""),
            last_four=method_data.get("last_four", ""),
            expiry_month=method_data.get("expiry_month", 0),
            expiry_year=method_data.get("expiry_year", 0),
            is_default=method_data.get("is_default", False),
            created_at=datetime.now().isoformat()
        )
        
        # Validate payment method
        gateway = self.gateways.get("stripe")  # Use Stripe for validation
        if not gateway.validate_payment_method(payment_method):
            raise ValueError("Invalid payment method")
        
        # Store payment method
        if user_id not in self.payment_methods:
            self.payment_methods[user_id] = []
        
        self.payment_methods[user_id].append(payment_method)
        
        return payment_method
    
    def get_user_payment_methods(self, user_id: str) -> List[PaymentMethod]:
        """Get user's payment methods"""
        return self.payment_methods.get(user_id, [])
    
    async def process_payment(self, user_id: str, amount: float, description: str, 
                            payment_method_id: str, gateway: str = "stripe") -> PaymentResponse:
        """Process payment"""
        # Create payment request
        payment_request = PaymentRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            currency="USD",
            description=description,
            payment_method_id=payment_method_id,
            gateway=gateway,
            metadata={"user_id": user_id, "description": description},
            created_at=datetime.now().isoformat()
        )
        
        # Get gateway
        payment_gateway = self.gateways.get(gateway)
        if not payment_gateway:
            return PaymentResponse(
                success=False,
                transaction_id="",
                amount=amount,
                currency="USD",
                gateway=gateway,
                status="failed",
                error_message=f"Gateway {gateway} not available"
            )
        
        # Process payment
        response = await payment_gateway.process_payment(payment_request)
        
        # Store transaction
        if response.success:
            self.transactions.append({
                "transaction_id": response.transaction_id,
                "user_id": user_id,
                "amount": amount,
                "gateway": gateway,
                "status": response.status,
                "timestamp": datetime.now().isoformat()
            })
        
        return response
    
    async def create_subscription_billing(self, user_id: str, subscription_id: str, 
                                        amount: float, payment_method_id: str) -> BillingCycle:
        """Create subscription billing cycle"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        billing_cycle = BillingCycle(
            cycle_id=str(uuid.uuid4()),
            user_id=user_id,
            subscription_id=subscription_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            amount=amount,
            status="pending",
            payment_method_id=payment_method_id,
            created_at=datetime.now().isoformat()
        )
        
        self.billing_cycles.append(billing_cycle)
        
        # Process payment
        response = await self.process_payment(
            user_id, amount, f"Subscription billing for {subscription_id}", 
            payment_method_id, "stripe"
        )
        
        if response.success:
            billing_cycle.status = "paid"
        else:
            billing_cycle.status = "failed"
        
        return billing_cycle
    
    async def request_refund(self, transaction_id: str, user_id: str, 
                           amount: float, reason: str) -> RefundRequest:
        """Request refund for transaction"""
        refund_request = RefundRequest(
            refund_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            user_id=user_id,
            amount=amount,
            reason=reason,
            status="pending",
            created_at=datetime.now().isoformat()
        )
        
        self.refund_requests.append(refund_request)
        
        # Process refund
        gateway = self.gateways.get("stripe")  # Use Stripe for refunds
        if gateway:
            response = await gateway.refund_payment(transaction_id, amount, reason)
            
            if response.success:
                refund_request.status = "completed"
                refund_request.processed_at = datetime.now().isoformat()
            else:
                refund_request.status = "rejected"
        
        return refund_request
    
    def get_transaction_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's transaction history"""
        user_transactions = [
            tx for tx in self.transactions 
            if tx["user_id"] == user_id
        ]
        
        # Sort by timestamp (newest first)
        user_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return user_transactions[:limit]
    
    def get_billing_history(self, user_id: str) -> List[BillingCycle]:
        """Get user's billing history"""
        return [
            cycle for cycle in self.billing_cycles 
            if cycle.user_id == user_id
        ]
    
    def get_payment_statistics(self) -> Dict[str, Any]:
        """Get payment processing statistics"""
        total_transactions = len(self.transactions)
        successful_transactions = len([tx for tx in self.transactions if tx["status"] == "completed"])
        failed_transactions = total_transactions - successful_transactions
        
        total_amount = sum(tx["amount"] for tx in self.transactions if tx["status"] == "completed")
        
        gateway_stats = defaultdict(lambda: {"count": 0, "amount": 0})
        for tx in self.transactions:
            if tx["status"] == "completed":
                gateway_stats[tx["gateway"]]["count"] += 1
                gateway_stats[tx["gateway"]]["amount"] += tx["amount"]
        
        return {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate": (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            "total_amount": total_amount,
            "gateway_statistics": dict(gateway_stats),
            "active_gateways": list(self.gateways.keys())
        }

async def main():
    """Test the payment processing system"""
    print("🚀 Testing Payment Processing System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize payment processor
    payment_processor = PaymentProcessor()
    
    try:
        # Wait for gateways to connect
        await asyncio.sleep(1)
        
        # Test payment methods
        print("\n💳 Testing Payment Methods:")
        print("-" * 40)
        
        # Add payment methods for test users
        payment_methods = []
        for user_id in ["user1", "user2", "user3"]:
            method_data = {
                "method_type": "credit_card",
                "card_type": "visa",
                "last_four": "1234",
                "expiry_month": 12,
                "expiry_year": 2025,
                "is_default": True
            }
            
            payment_method = await payment_processor.add_payment_method(user_id, method_data)
            payment_methods.append(payment_method)
            print(f"✅ Added payment method for {user_id}: {payment_method.card_type} ****{payment_method.last_four}")
        
        # Test payment processing
        print("\n💸 Testing Payment Processing:")
        print("-" * 40)
        
        # Test different gateways
        gateways = ["stripe", "paypal", "crypto"]
        payments = []
        
        for i, gateway in enumerate(gateways):
            user_id = f"user{i+1}"
            amount = 19.99 + (i * 10)
            
            response = await payment_processor.process_payment(
                user_id, amount, f"Test payment via {gateway}", 
                payment_methods[i].payment_id, gateway
            )
            
            payments.append(response)
            status_emoji = "✅" if response.success else "❌"
            print(f"{status_emoji} {gateway.title()} payment: ${amount} - {response.status}")
            if not response.success:
                print(f"   Error: {response.error_message}")
        
        # Test subscription billing
        print("\n📅 Testing Subscription Billing:")
        print("-" * 40)
        
        billing_cycles = []
        for i, user_id in enumerate(["user1", "user2", "user3"]):
            amount = 19.99 + (i * 15)
            subscription_id = f"sub_{user_id}"
            
            billing_cycle = await payment_processor.create_subscription_billing(
                user_id, subscription_id, amount, payment_methods[i].payment_id
            )
            
            billing_cycles.append(billing_cycle)
            status_emoji = "✅" if billing_cycle.status == "paid" else "❌"
            print(f"{status_emoji} Billing cycle for {user_id}: ${amount} - {billing_cycle.status}")
        
        # Test refund processing
        print("\n🔄 Testing Refund Processing:")
        print("-" * 40)
        
        # Request refund for first payment
        if payments[0].success:
            refund_request = await payment_processor.request_refund(
                payments[0].transaction_id, "user1", 19.99, "Customer requested refund"
            )
            
            status_emoji = "✅" if refund_request.status == "completed" else "❌"
            print(f"{status_emoji} Refund request: ${refund_request.amount} - {refund_request.status}")
            print(f"   Reason: {refund_request.reason}")
        
        # Test transaction history
        print("\n📊 Testing Transaction History:")
        print("-" * 40)
        
        for user_id in ["user1", "user2", "user3"]:
            transactions = payment_processor.get_transaction_history(user_id)
            print(f"👤 {user_id}: {len(transactions)} transactions")
            for tx in transactions[:2]:  # Show first 2 transactions
                print(f"   - ${tx['amount']} via {tx['gateway']} ({tx['status']})")
        
        # Test billing history
        print("\n📋 Testing Billing History:")
        print("-" * 40)
        
        for user_id in ["user1", "user2", "user3"]:
            billing_history = payment_processor.get_billing_history(user_id)
            print(f"👤 {user_id}: {len(billing_history)} billing cycles")
            for cycle in billing_history:
                print(f"   - ${cycle.amount} ({cycle.status}) - {cycle.subscription_id}")
        
        # Test payment statistics
        print("\n📈 Testing Payment Statistics:")
        print("-" * 40)
        
        stats = payment_processor.get_payment_statistics()
        print(f"✅ Total Transactions: {stats['total_transactions']}")
        print(f"✅ Successful Transactions: {stats['successful_transactions']}")
        print(f"✅ Failed Transactions: {stats['failed_transactions']}")
        print(f"✅ Success Rate: {stats['success_rate']:.1f}%")
        print(f"✅ Total Amount: ${stats['total_amount']:.2f}")
        print(f"✅ Active Gateways: {', '.join(stats['active_gateways'])}")
        
        # Show gateway statistics
        print(f"\n🔌 Gateway Statistics:")
        for gateway, data in stats['gateway_statistics'].items():
            print(f"   {gateway.title()}: {data['count']} transactions, ${data['amount']:.2f}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Payment Processing System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 