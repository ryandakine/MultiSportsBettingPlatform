#!/usr/bin/env python3
"""
Fix Bankroll
============
Initialize or fix bankroll for demo_user
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bankroll
from src.services.bet_tracker import bet_tracker
from sqlalchemy import select


async def fix_bankroll():
    """Initialize or fix bankroll."""
    user_id = "demo_user"
    
    # Check if bankroll exists
    bankroll = await bet_tracker.get_bankroll(user_id)
    
    if not bankroll:
        print(f"Creating bankroll for {user_id}...")
        async with AsyncSessionLocal() as db:
            new_bankroll = Bankroll(
                user_id=user_id,
                balance=1000.0,
                total_wagered=0.0,
                total_won=0.0,
                updated_at=datetime.utcnow()
            )
            db.add(new_bankroll)
            await db.commit()
            print(f"✅ Bankroll created: $1,000.00")
    else:
        current_balance = bankroll.get("balance", 0)
        print(f"Bankroll exists: ${current_balance:,.2f}")
        
        if current_balance <= 0:
            print(f"Updating bankroll to $1,000...")
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Bankroll).where(Bankroll.user_id == user_id)
                )
                br = result.scalar_one()
                br.balance = 1000.0
                await db.commit()
                print(f"✅ Bankroll updated to $1,000.00")
        else:
            print(f"✅ Bankroll is fine: ${current_balance:,.2f}")


if __name__ == "__main__":
    asyncio.run(fix_bankroll())



