#!/usr/bin/env python3
"""
Settle Old Pending Bets
========================
Manually settle all pending bets, bypassing enum issues.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.services.bet_settlement_service import bet_settlement_service
from sqlalchemy import text


async def settle_old_bets():
    """Settle all pending bets using raw SQL to avoid enum issues."""
    print("=" * 80)
    print("💰 SETTLING ALL PENDING BETS (including old ones)")
    print("=" * 80)
    print()
    
    # First, let's try the normal settlement service with 30 days lookback
    print("Attempting to settle bets from last 30 days...")
    try:
        result = await bet_settlement_service.settle_pending_bets(days_back=30)
        print(f"✅ Settled {result['bets_settled']} bets")
        print(f"   Won: {result['bets_won']}, Lost: {result['bets_lost']}, Pushed: {result['bets_pushed']}")
        
        if result['bets_settled'] > 0:
            print("\n✅ Settlement successful!")
            return
    except Exception as e:
        print(f"❌ Settlement service failed: {e}")
        print("Trying alternative method...")
    
    # Alternative: Check how many pending bets there are
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT COUNT(*) FROM bets WHERE status = 'pending'")
        )
        pending_count = result.scalar()
        print(f"\nTotal pending bets in database: {pending_count}")
        
        if pending_count == 0:
            print("✅ No pending bets to settle!")
            return
        
        # Get oldest pending bet
        result2 = await db.execute(
            text("SELECT MIN(placed_at) FROM bets WHERE status = 'pending'")
        )
        oldest = result2.scalar()
        if oldest:
            days_old = (datetime.utcnow() - oldest).days
            print(f"Oldest pending bet is {days_old} days old")
        
        print("\n⚠️ Settlement service encountered an error.")
        print("The bets may have enum value mismatches in the database.")
        print("You may need to manually check and fix bet_type values.")
        print("\nCurrent bet_type values in pending bets:")
        
        result3 = await db.execute(
            text("SELECT DISTINCT bet_type FROM bets WHERE status = 'pending' LIMIT 10")
        )
        bet_types = [row[0] for row in result3]
        for bt in bet_types:
            print(f"   - {bt}")


if __name__ == "__main__":
    asyncio.run(settle_old_bets())



