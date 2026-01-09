#!/usr/bin/env python3
"""
Settle All Pending Bets (Direct Method)
========================================
Settle bets using direct SQL to bypass enum issues.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.services.bet_settlement_service import bet_settlement_service
from sqlalchemy import text


async def settle_all_direct():
    """Settle all pending bets by increasing the lookback period."""
    print("=" * 80)
    print("💰 SETTLING ALL PENDING BETS")
    print("=" * 80)
    print()
    
    # First check how many pending bets we have
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT COUNT(*) FROM bets WHERE status = 'pending'")
        )
        pending_count = result.scalar()
        print(f"Total pending bets: {pending_count}")
        
        if pending_count == 0:
            print("✅ No pending bets to settle!")
            return
        
        # Get date range of pending bets
        result2 = await db.execute(
            text("""
                SELECT 
                    MIN(DATE(placed_at)) as first_date,
                    MAX(DATE(placed_at)) as last_date
                FROM bets 
                WHERE status = 'pending'
            """)
        )
        row = result2.fetchone()
        first_date, last_date = row
        days_back = (datetime.utcnow().date() - first_date).days + 1
        
        print(f"Pending bets date range: {first_date} to {last_date}")
        print(f"Will look back {days_back} days for settlement")
        print()
    
    # Use the settlement service with a longer lookback
    print("Running settlement service...")
    try:
        # Use 60 days to catch all old bets
        result = await bet_settlement_service.settle_pending_bets(days_back=60)
        
        print()
        print("=" * 80)
        print("📊 SETTLEMENT RESULTS")
        print("=" * 80)
        print(f"Bets checked: {result.get('bets_checked', 0)}")
        print(f"Bets settled: {result.get('bets_settled', 0)}")
        print(f"  ✅ Won: {result.get('bets_won', 0)}")
        print(f"  ❌ Lost: {result.get('bets_lost', 0)}")
        print(f"  ➖ Pushed: {result.get('bets_pushed', 0)}")
        print(f"Skipped: {result.get('bets_skipped', 0)}")
        
        if result.get('errors'):
            print(f"\n⚠️ Errors: {len(result['errors'])}")
            for error in result['errors'][:5]:
                print(f"   - {error}")
                
        # Check remaining pending
        async with AsyncSessionLocal() as db:
            result3 = await db.execute(
                text("SELECT COUNT(*) FROM bets WHERE status = 'pending'")
            )
            still_pending = result3.scalar()
            print(f"\nRemaining pending bets: {still_pending}")
            
    except Exception as e:
        print(f"❌ Error during settlement: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(settle_all_direct())



