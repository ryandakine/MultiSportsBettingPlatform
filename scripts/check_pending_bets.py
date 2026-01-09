#!/usr/bin/env python3
"""
Check Pending Bets
==================
See what bets are pending and why they might not be settled.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus
from sqlalchemy import select, and_


async def check_pending():
    """Check pending bets."""
    print("=" * 80)
    print("🔍 PENDING BETS ANALYSIS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get all pending bets
        result = await db.execute(
            select(Bet)
            .where(Bet.status == BetStatus.PENDING)
            .order_by(Bet.placed_at.desc())
        )
        pending_bets = result.scalars().all()
        
        print(f"📊 Total Pending Bets: {len(pending_bets)}")
        print()
        
        if not pending_bets:
            print("✅ No pending bets!")
            return
        
        # Group by date
        bets_by_date = {}
        for bet in pending_bets:
            date = bet.placed_at.date()
            if date not in bets_by_date:
                bets_by_date[date] = []
            bets_by_date[date].append(bet)
        
        print(f"📅 PENDING BETS BY DATE:")
        for date in sorted(bets_by_date.keys(), reverse=True):
            bets = bets_by_date[date]
            days_ago = (datetime.utcnow().date() - date).days
            print(f"\n   {date} ({days_ago} days ago): {len(bets)} bets")
            
            # Show sample of bets
            for bet in bets[:5]:
                game_date_str = bet.game_date.strftime('%Y-%m-%d') if bet.game_date else 'N/A'
                print(f"      - ${bet.amount:.2f} | {bet.sport} | {bet.bet_type.value} | Game Date: {game_date_str}")
            
            if len(bets) > 5:
                print(f"      ... and {len(bets) - 5} more")
        
        # Check game dates
        print(f"\n🎮 GAME DATES:")
        today = datetime.utcnow().date()
        future_games = [b for b in pending_bets if b.game_date and b.game_date.date() > today]
        past_games = [b for b in pending_bets if b.game_date and b.game_date.date() < today]
        today_games = [b for b in pending_bets if b.game_date and b.game_date.date() == today]
        no_date = [b for b in pending_bets if not b.game_date]
        
        print(f"   Future games: {len(future_games)}")
        print(f"   Past games (should be settled): {len(past_games)}")
        print(f"   Today's games: {len(today_games)}")
        print(f"   No game date: {len(no_date)}")
        
        if past_games:
            print(f"\n⚠️ {len(past_games)} bets have game dates in the past - these should be settled!")
            print(f"   Oldest game date: {min(b.game_date.date() for b in past_games if b.game_date)}")
            print(f"   Newest past game date: {max(b.game_date.date() for b in past_games if b.game_date)}")


if __name__ == "__main__":
    asyncio.run(check_pending())



