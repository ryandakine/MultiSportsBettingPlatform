#!/usr/bin/env python3
"""
Check Last Week's Pick Performance
==================================
Query and display betting performance from the last 7 days.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus, BetType
from src.db.models.parlay import ParlayLeg


async def get_last_week_performance():
    """Get performance metrics from the last 7 days."""
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    async with AsyncSessionLocal() as session:
        # Get all bets from last week
        result = await session.execute(
            select(Bet).where(
                Bet.placed_at >= seven_days_ago
            ).order_by(Bet.placed_at.desc())
        )
        bets = result.scalars().all()
        
        if not bets:
            print("📊 No bets found in the last 7 days.")
            return
        
        # Separate by bet type
        straight_bets = [b for b in bets if b.bet_type != BetType.PARLAY]
        parlay_bets = [b for b in bets if b.bet_type == BetType.PARLAY]
        
        # Filter settled bets
        settled_straight = [b for b in straight_bets if b.status != BetStatus.PENDING]
        settled_parlays = [b for b in parlay_bets if b.status != BetStatus.PENDING]
        
        # Calculate straight bet metrics
        straight_wins = [b for b in settled_straight if b.status == BetStatus.WON]
        straight_losses = [b for b in settled_straight if b.status == BetStatus.LOST]
        
        straight_wagered = sum(b.amount for b in settled_straight)
        straight_won = sum(b.payout or 0 for b in straight_wins)
        straight_lost = sum(b.amount for b in straight_losses)
        
        # Calculate parlay metrics
        parlay_wins = [b for b in settled_parlays if b.status == BetStatus.WON]
        parlay_losses = [b for b in settled_parlays if b.status == BetStatus.LOST]
        
        parlay_wagered = sum(b.amount for b in settled_parlays)
        parlay_won = sum(b.payout or 0 for b in parlay_wins)
        parlay_lost = sum(b.amount for b in parlay_losses)
        
        # Calculate totals
        total_bets = len(bets)
        total_settled = len(settled_straight) + len(settled_parlays)
        total_pending = total_bets - total_settled
        
        total_wagered = straight_wagered + parlay_wagered
        total_won = straight_won + parlay_won
        total_lost = straight_lost + parlay_lost
        net_profit = total_won - total_wagered
        
        # Calculate win rates
        straight_win_rate = (len(straight_wins) / len(settled_straight) * 100) if settled_straight else 0
        parlay_win_rate = (len(parlay_wins) / len(settled_parlays) * 100) if settled_parlays else 0
        overall_win_rate = ((len(straight_wins) + len(parlay_wins)) / total_settled * 100) if total_settled else 0
        
        # Calculate ROI
        straight_roi = ((straight_won - straight_wagered) / straight_wagered * 100) if straight_wagered > 0 else 0
        parlay_roi = ((parlay_won - parlay_wagered) / parlay_wagered * 100) if parlay_wagered > 0 else 0
        overall_roi = ((total_won - total_wagered) / total_wagered * 100) if total_wagered > 0 else 0
        
        # Print results
        print("=" * 80)
        print("📊 LAST 7 DAYS PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"Period: {seven_days_ago.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}")
        print()
        
        print("📈 OVERALL STATS")
        print("-" * 80)
        print(f"Total Bets Placed:     {total_bets}")
        print(f"  Settled:             {total_settled}")
        print(f"  Pending:             {total_pending}")
        print(f"Total Wagered:         ${total_wagered:,.2f}")
        print(f"Total Won:             ${total_won:,.2f}")
        print(f"Total Lost:            ${total_lost:,.2f}")
        print(f"Net Profit/Loss:       ${net_profit:,.2f} {'✅' if net_profit >= 0 else '❌'}")
        print(f"Overall ROI:           {overall_roi:.2f}%")
        print(f"Overall Win Rate:      {overall_win_rate:.2f}%")
        print()
        
        print("🎯 STRAIGHT BETS")
        print("-" * 80)
        print(f"Bets Placed:           {len(straight_bets)}")
        print(f"  Settled:             {len(settled_straight)}")
        print(f"  Pending:             {len(straight_bets) - len(settled_straight)}")
        print(f"Wins:                  {len(straight_wins)}")
        print(f"Losses:                {len(straight_losses)}")
        print(f"Win Rate:              {straight_win_rate:.2f}%")
        print(f"Amount Wagered:        ${straight_wagered:,.2f}")
        print(f"Amount Won:            ${straight_won:,.2f}")
        print(f"Net Profit/Loss:       ${straight_won - straight_wagered:,.2f} {'✅' if (straight_won - straight_wagered) >= 0 else '❌'}")
        print(f"ROI:                   {straight_roi:.2f}%")
        print()
        
        print("🎲 PARLAY BETS")
        print("-" * 80)
        print(f"Parlays Placed:        {len(parlay_bets)}")
        print(f"  Settled:             {len(settled_parlays)}")
        print(f"  Pending:             {len(parlay_bets) - len(settled_parlays)}")
        print(f"Wins:                  {len(parlay_wins)}")
        print(f"Losses:                {len(parlay_losses)}")
        print(f"Win Rate:              {parlay_win_rate:.2f}%")
        print(f"Amount Wagered:        ${parlay_wagered:,.2f}")
        print(f"Amount Won:            ${parlay_won:,.2f}")
        print(f"Net Profit/Loss:       ${parlay_won - parlay_wagered:,.2f} {'✅' if (parlay_won - parlay_wagered) >= 0 else '❌'}")
        print(f"ROI:                   {parlay_roi:.2f}%")
        print()
        
        # Show recent bets
        print("📋 RECENT BETS (Last 10)")
        print("-" * 80)
        recent_bets = sorted(bets, key=lambda x: x.placed_at or datetime.min, reverse=True)[:10]
        
        for bet in recent_bets:
            status_emoji = "✅" if bet.status == BetStatus.WON else "❌" if bet.status == BetStatus.LOST else "⏳"
            status_text = bet.status.value.upper() if bet.status else "UNKNOWN"
            bet_date = bet.placed_at.strftime('%Y-%m-%d %H:%M') if bet.placed_at else "N/A"
            
            print(f"{status_emoji} {bet_date} | {bet.sport.upper()} | {bet.bet_type.value.upper()}")
            if bet.team:
                print(f"   Pick: {bet.team}")
            if bet.line:
                print(f"   Line: {bet.line}")
            print(f"   Amount: ${bet.amount:.2f} @ {bet.odds}")
            print(f"   Status: {status_text}")
            if bet.payout:
                print(f"   Payout: ${bet.payout:.2f} | ROI: {bet.roi:.2f}%" if bet.roi else "")
            print()


async def main():
    """Main entry point."""
    try:
        await get_last_week_performance()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

