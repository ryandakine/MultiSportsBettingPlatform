#!/usr/bin/env python3
"""
Analyze Bet Performance
========================
See how bets performed - wins, losses, ROI, etc.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta


async def analyze_performance():
    """Analyze betting performance."""
    print("=" * 80)
    print("💰 BET PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get all bets
        result = await db.execute(select(func.count(Bet.id)))
        total_bets = result.scalar()
        
        # Get bets by status
        result2 = await db.execute(
            select(func.count(Bet.id)).where(Bet.status == BetStatus.PENDING)
        )
        pending_bets = result2.scalar()
        
        result3 = await db.execute(
            select(func.count(Bet.id)).where(Bet.status == BetStatus.WON)
        )
        won_bets = result3.scalar()
        
        result4 = await db.execute(
            select(func.count(Bet.id)).where(Bet.status == BetStatus.LOST)
        )
        lost_bets = result4.scalar()
        
        result5 = await db.execute(
            select(func.count(Bet.id)).where(Bet.status == BetStatus.PUSHED)
        )
        pushed_bets = result5.scalar()
        
        # Get total amounts
        result6 = await db.execute(
            select(func.sum(Bet.amount)).where(Bet.status.in_([BetStatus.WON, BetStatus.LOST, BetStatus.PUSHED]))
        )
        total_wagered = result6.scalar() or 0
        
        result7 = await db.execute(
            select(func.sum(Bet.payout)).where(Bet.status == BetStatus.WON)
        )
        total_won = result7.scalar() or 0
        
        # Calculate ROI
        settled_bets = won_bets + lost_bets + pushed_bets
        net_profit = total_won - total_wagered if total_wagered > 0 else 0
        roi = (net_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        # Win rate
        win_rate = (won_bets / settled_bets * 100) if settled_bets > 0 else 0
        
        print(f"📊 OVERALL STATISTICS")
        print(f"   Total Bets: {total_bets}")
        print(f"   Pending: {pending_bets}")
        print(f"   Won: {won_bets}")
        print(f"   Lost: {lost_bets}")
        print(f"   Pushed: {pushed_bets}")
        print(f"   Settled: {settled_bets}")
        print()
        
        print(f"💰 FINANCIAL SUMMARY")
        print(f"   Total Wagered: ${total_wagered:,.2f}")
        print(f"   Total Won: ${total_won:,.2f}")
        print(f"   Net Profit/Loss: ${net_profit:,.2f}")
        print(f"   ROI: {roi:.2f}%")
        print(f"   Win Rate: {win_rate:.2f}%")
        print()
        
        # Get recent bets
        result8 = await db.execute(
            select(Bet)
            .order_by(Bet.placed_at.desc())
            .limit(20)
        )
        recent_bets = result8.scalars().all()
        
        print(f"📝 RECENT BETS (Last 20)")
        print("-" * 80)
        for bet in recent_bets:
            status_emoji = {
                BetStatus.PENDING: "⏳",
                BetStatus.WON: "✅",
                BetStatus.LOST: "❌",
                BetStatus.PUSHED: "➖"
            }.get(bet.status, "❓")
            
            payout_str = f" → ${bet.payout:.2f}" if bet.payout else ""
            print(f"{status_emoji} ${bet.amount:.2f} | {bet.sport} | {bet.status.value.upper()}{payout_str} | {bet.placed_at.strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # Get bets by sport
        result9 = await db.execute(
            select(Bet.sport, func.count(Bet.id).label('count'))
            .group_by(Bet.sport)
        )
        bets_by_sport = result9.all()
        
        print(f"🏀 BETS BY SPORT")
        for sport, count in bets_by_sport:
            print(f"   {sport}: {count} bets")
        print()
        
        # Get bets by date
        result10 = await db.execute(
            select(
                func.date(Bet.placed_at).label('date'),
                func.count(Bet.id).label('count')
            )
            .group_by(func.date(Bet.placed_at))
            .order_by(func.date(Bet.placed_at).desc())
            .limit(10)
        )
        bets_by_date = result10.all()
        
        print(f"📅 BETS BY DATE (Last 10 Days)")
        for date, count in bets_by_date:
            print(f"   {date}: {count} bets")
        print()


if __name__ == "__main__":
    asyncio.run(analyze_performance())



