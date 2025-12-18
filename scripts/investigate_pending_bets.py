#!/usr/bin/env python3
"""
Investigate Pending Bets
========================
Check why bets are still pending and their details.
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


async def investigate_pending_bets():
    """Investigate why bets are still pending."""
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    async with AsyncSessionLocal() as session:
        # Get all pending bets from last week
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.placed_at >= seven_days_ago,
                    Bet.status == BetStatus.PENDING
                )
            ).order_by(Bet.placed_at.desc())
        )
        pending_bets = result.scalars().all()
        
        print("=" * 80)
        print(f"🔍 INVESTIGATING {len(pending_bets)} PENDING BETS")
        print("=" * 80)
        print()
        
        if not pending_bets:
            print("✅ No pending bets found!")
            return
        
        # Group by date
        by_date = {}
        for bet in pending_bets:
            date_key = bet.placed_at.strftime('%Y-%m-%d') if bet.placed_at else 'Unknown'
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(bet)
        
        print(f"📅 Pending bets by date:")
        print("-" * 80)
        for date, bets in sorted(by_date.items()):
            print(f"{date}: {len(bets)} bets")
        print()
        
        # Show details of all pending bets
        print("📋 DETAILS OF ALL PENDING BETS")
        print("=" * 80)
        
        for i, bet in enumerate(pending_bets, 1):
            placed_date = bet.placed_at.strftime('%Y-%m-%d %H:%M:%S') if bet.placed_at else "N/A"
            game_date = bet.game_date.strftime('%Y-%m-%d %H:%M:%S') if bet.game_date else "NOT SET"
            
            days_ago = (datetime.utcnow() - bet.placed_at).days if bet.placed_at else None
            
            print(f"\n{i}. Bet ID: {bet.id}")
            print(f"   Placed: {placed_date} ({days_ago} days ago)" if days_ago is not None else f"   Placed: {placed_date}")
            print(f"   Game Date: {game_date}")
            print(f"   Sport: {bet.sport}")
            print(f"   Bet Type: {bet.bet_type.value if bet.bet_type else 'N/A'}")
            if bet.home_team and bet.away_team:
                print(f"   Game: {bet.away_team} @ {bet.home_team}")
            if bet.team:
                print(f"   Pick: {bet.team}")
            if bet.line is not None:
                print(f"   Line: {bet.line}")
            print(f"   Amount: ${bet.amount:.2f}")
            print(f"   Odds: {bet.odds}")
            print(f"   Status: {bet.status.value if bet.status else 'UNKNOWN'}")
            print(f"   Settled At: {bet.settled_at if bet.settled_at else 'NOT SETTLED'}")
            print(f"   Game ID: {bet.game_id}")
            print(f"   Sportsbook: {bet.sportsbook}")
            print(f"   Sportsbook Bet ID: {bet.sportsbook_bet_id or 'NOT SET'}")
        
        # Check if there's a pattern
        print()
        print("=" * 80)
        print("🔍 ANALYSIS")
        print("=" * 80)
        
        # Check sportsbook bet IDs
        has_sportsbook_id = [b for b in pending_bets if b.sportsbook_bet_id]
        no_sportsbook_id = [b for b in pending_bets if not b.sportsbook_bet_id]
        
        print(f"Bets with Sportsbook ID: {len(has_sportsbook_id)}")
        print(f"Bets without Sportsbook ID: {len(no_sportsbook_id)}")
        print()
        
        # Check if game dates are set
        has_game_date = [b for b in pending_bets if b.game_date]
        no_game_date = [b for b in pending_bets if not b.game_date]
        
        print(f"Bets with Game Date: {len(has_game_date)}")
        print(f"Bets without Game Date: {len(no_game_date)}")
        print()
        
        # Check if these are paper trades or real bets
        autonomous = [b for b in pending_bets if b.is_autonomous]
        manual = [b for b in pending_bets if not b.is_autonomous]
        
        print(f"Autonomous bets: {len(autonomous)}")
        print(f"Manual bets: {len(manual)}")
        print()
        
        # Most recent pending bet
        if pending_bets:
            most_recent = max(pending_bets, key=lambda x: x.placed_at if x.placed_at else datetime.min)
            oldest = min(pending_bets, key=lambda x: x.placed_at if x.placed_at else datetime.max)
            
            print(f"Oldest pending bet: {oldest.placed_at.strftime('%Y-%m-%d %H:%M') if oldest.placed_at else 'N/A'}")
            print(f"Most recent pending bet: {most_recent.placed_at.strftime('%Y-%m-%d %H:%M') if most_recent.placed_at else 'N/A'}")


async def main():
    """Main entry point."""
    try:
        await investigate_pending_bets()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

