#!/usr/bin/env python3
"""
Check All Bet Dates
===================
See when bets were actually placed to understand the timeline.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from sqlalchemy import text, func


async def check_dates():
    """Check all bet dates."""
    print("=" * 80)
    print("📅 ALL BETS BY DATE")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get all bets grouped by date placed
        result = await db.execute(
            text("""
                SELECT 
                    DATE(placed_at) as bet_date,
                    status,
                    COUNT(*) as count
                FROM bets
                GROUP BY DATE(placed_at), status
                ORDER BY bet_date DESC, status
            """)
        )
        
        rows = result.fetchall()
        
        if not rows:
            print("No bets found!")
            return
        
        print("BETS BY DATE PLACED:")
        print("-" * 80)
        current_date = None
        for row in rows:
            bet_date, status, count = row
            if current_date != bet_date:
                if current_date is not None:
                    print()
                current_date = bet_date
                if isinstance(bet_date, str):
                    bet_date_obj = datetime.strptime(bet_date, '%Y-%m-%d').date()
                else:
                    bet_date_obj = bet_date
                days_ago = (datetime.utcnow().date() - bet_date_obj).days
                print(f"\n{bet_date} ({days_ago} days ago):")
            print(f"   {status}: {count} bets")
        
        print()
        print("=" * 80)
        print("SUMMARY BY STATUS:")
        print("-" * 80)
        
        result2 = await db.execute(
            text("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    MIN(DATE(placed_at)) as first_date,
                    MAX(DATE(placed_at)) as last_date
                FROM bets
                GROUP BY status
            """)
        )
        
        for row in result2.fetchall():
            status, count, first_date, last_date = row
            print(f"{status.upper()}: {count} bets (from {first_date} to {last_date})")
        
        print()
        print("=" * 80)
        print("TIMELINE ANALYSIS:")
        print("-" * 80)
        
        result3 = await db.execute(
            text("""
                SELECT 
                    DATE(placed_at) as bet_date,
                    COUNT(*) as count
                FROM bets
                GROUP BY DATE(placed_at)
                ORDER BY bet_date DESC
            """)
        )
        
        dates_with_bets = [(row[0], row[1]) for row in result3.fetchall()]
        print(f"Days with bets: {len(dates_with_bets)}")
        print(f"Date range: {dates_with_bets[-1][0]} to {dates_with_bets[0][0]}")
        
        # Check for gaps
        if len(dates_with_bets) > 1:
            gaps = []
            for i in range(len(dates_with_bets) - 1):
                date1 = dates_with_bets[i][0]
                date2 = dates_with_bets[i+1][0]
                days_diff = (date1 - date2).days
                if days_diff > 1:
                    gaps.append((date2, date1, days_diff - 1))
            
            if gaps:
                print(f"\n⚠️ GAPS IN BETTING:")
                for gap_start, gap_end, gap_days in gaps:
                    print(f"   No bets between {gap_start} and {gap_end} ({gap_days} days)")


if __name__ == "__main__":
    asyncio.run(check_dates())

