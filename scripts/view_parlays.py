#!/usr/bin/env python3
"""
View Parlays Script
===================
View parlay bets and their legs from the database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus, BetType
from src.services.parlay_tracker import parlay_tracker


async def view_parlays(days_back: int = 30, status_filter: str = None):
    """View parlay bets from the last N days."""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    async with AsyncSessionLocal() as session:
        query = select(Bet).where(
            and_(
                Bet.bet_type == BetType.PARLAY,
                Bet.placed_at >= cutoff_date
            )
        )
        
        if status_filter:
            query = query.where(Bet.status == BetStatus[status_filter.upper()])
        
        query = query.order_by(Bet.placed_at.desc())
        
        result = await session.execute(query)
        parlay_bets = result.scalars().all()
        
        if not parlay_bets:
            print(f"📊 No parlay bets found in the last {days_back} days")
            return
        
        print("=" * 80)
        print(f"📊 PARLAY BETS (Last {days_back} days)")
        print("=" * 80)
        print()
        
        for i, bet in enumerate(parlay_bets, 1):
            placed_date = bet.placed_at.strftime('%Y-%m-%d %H:%M:%S') if bet.placed_at else "N/A"
            status_emoji = "✅" if bet.status == BetStatus.WON else "❌" if bet.status == BetStatus.LOST else "⏳"
            
            print(f"{i}. {status_emoji} Parlay ID: {bet.id}")
            print(f"   Placed: {placed_date}")
            print(f"   Amount: ${bet.amount:.2f}")
            print(f"   Combined Odds: {bet.odds}")
            print(f"   Status: {bet.status.value.upper()}")
            if bet.payout:
                print(f"   Payout: ${bet.payout:.2f} | ROI: {bet.roi:.2f}%" if bet.roi else "")
            
            # Get legs
            legs = await parlay_tracker.get_parlay_legs(bet.id)
            print(f"   Legs ({len(legs)}):")
            for j, leg in enumerate(legs, 1):
                leg_result = leg.get('result', 'pending')
                leg_emoji = "✅" if leg_result == "won" else "❌" if leg_result == "lost" else "⏳"
                print(f"      {j}. {leg_emoji} {leg['sport'].upper()} | {leg['team']} ({leg['bet_type']})")
                if leg.get('line'):
                    print(f"         Line: {leg['line']} | Odds: {leg['odds']}")
                print(f"         Result: {leg_result}")
            print()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View parlay bets")
    parser.add_argument("--days", type=int, default=30, help="Days to look back (default: 30)")
    parser.add_argument("--status", type=str, choices=['pending', 'won', 'lost', 'pushed'], 
                       help="Filter by status")
    
    args = parser.parse_args()
    
    try:
        await view_parlays(days_back=args.days, status_filter=args.status)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

