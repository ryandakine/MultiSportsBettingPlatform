"""
Paper Trading Initialization Script
====================================
Set up paper trading with fake bankroll and start tracking bets.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy import select

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bankroll


async def initialize_paper_trading(user_id: str, initial_balance: float = 10000.0):
    """
    Initialize paper trading bankroll.
    
    Args:
        user_id: User ID
        initial_balance: Starting fake money (default $10,000)
    """
    async with AsyncSessionLocal() as session:
        # Check if bankroll already exists
        result = await session.execute(
            select(Bankroll).where(Bankroll.user_id == user_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✅ Bankroll already exists for user {user_id}")
            print(f"   Current balance: ${existing.current_balance:.2f}")
            return existing.id
        
        # Create new bankroll
        bankroll = Bankroll(
            id=str(uuid.uuid4()),
            user_id=user_id,
            sportsbook="paper_trading",
            current_balance=initial_balance,
            initial_deposit=initial_balance,
            available_balance=initial_balance,
            max_bet_amount=initial_balance * 0.05,  # 5% max
            daily_loss_limit=initial_balance * 0.10  # 10% daily loss limit
        )
        
        session.add(bankroll)
        await session.commit()
        
        print(f"✅ Paper trading initialized!")
        print(f"   User ID: {user_id}")
        print(f"   Starting balance: ${initial_balance:,.2f}")
        print(f"   Max bet size: ${bankroll.max_bet_amount:.2f}")
        print(f"   Daily loss limit: ${bankroll.daily_loss_limit:.2f}")
        print(f"\n🎯 Ready to start paper trading!")
        
        return bankroll.id


async def main():
    """Initialize paper trading for demo user."""
    user_id = "demo_user"
    await initialize_paper_trading(user_id, initial_balance=10000.0)


if __name__ == "__main__":
    asyncio.run(main())
