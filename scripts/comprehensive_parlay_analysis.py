#!/usr/bin/env python3
"""
Comprehensive Parlay Analysis - Check all parlays including dates
"""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from sqlalchemy import text


async def analyze_all_parlays():
    """Analyze all parlays in detail."""
    print("=" * 80)
    print("🎲 COMPREHENSIVE PARLAY ANALYSIS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get all parlays with full details
        result = await db.execute(text('''
            SELECT 
                b.id,
                b.status,
                b.amount,
                b.odds,
                b.payout,
                b.placed_at,
                COUNT(pl.id) as leg_count
            FROM bets b
            LEFT JOIN parlay_legs pl ON b.id = pl.parlay_bet_id
            WHERE b.bet_type = 'parlay'
            GROUP BY b.id
            ORDER BY b.placed_at DESC
        '''))
        
        all_parlays = result.fetchall()
        print(f"📊 Total Parlays Found: {len(all_parlays)}")
        print()
        
        # Group by leg count
        by_legs = defaultdict(list)
        for parlay_id, status, amount, odds, payout, placed_at, leg_count in all_parlays:
            by_legs[leg_count].append({
                'id': parlay_id,
                'status': status,
                'amount': amount,
                'odds': odds,
                'payout': payout,
                'placed_at': placed_at
            })
        
        # Show breakdown by leg count
        print("📈 PARLAYS BY LEG COUNT:")
        print("-" * 80)
        for leg_count in sorted(by_legs.keys(), reverse=True):
            parlays = by_legs[leg_count]
            print(f"\n{leg_count}-LEG PARLAYS: {len(parlays)} total")
            
            # Group by date
            by_date = defaultdict(list)
            for p in parlays:
                date_str = str(p['placed_at'])[:10] if p['placed_at'] else 'Unknown'
                by_date[date_str].append(p)
            
            print(f"   Dates: {len(by_date)} unique dates")
            for date_str in sorted(by_date.keys(), reverse=True):
                date_parlays = by_date[date_str]
                print(f"   📅 {date_str}: {len(date_parlays)} parlay(s)")
                
                # Show status breakdown for this date
                status_counts = defaultdict(int)
                for p in date_parlays:
                    status_counts[p['status']] += 1
                
                status_str = ", ".join([f"{count} {status}" for status, count in status_counts.items()])
                print(f"      Status: {status_str}")
                
                # Show details
                for p in date_parlays[:3]:  # Show first 3 per date
                    emoji = "✅" if p['status'] == 'won' else "❌" if p['status'] == 'lost' else "⏳"
                    payout_str = f" → ${p['payout']:.2f}" if p['payout'] else ""
                    time_str = str(p['placed_at'])[11:16] if p['placed_at'] else ""
                    print(f"      {emoji} ${p['amount']:.2f} @ {p['odds']:+.0f} {payout_str} [{time_str}]")
                
                if len(date_parlays) > 3:
                    print(f"      ... and {len(date_parlays) - 3} more on this date")
        
        # Analysis
        print("\n" + "=" * 80)
        print("💡 ANALYSIS")
        print("-" * 80)
        
        if 6 in by_legs:
            six_leg_count = len(by_legs[6])
            six_leg_dates = len(set(str(p['placed_at'])[:10] for p in by_legs[6] if p['placed_at']))
            
            print(f"🚀 6-LEG PARLAYS:")
            print(f"   Total: {six_leg_count}")
            print(f"   Unique dates: {six_leg_dates}")
            
            if six_leg_dates > 0:
                expected = six_leg_dates  # One per day
                if six_leg_count < expected:
                    print(f"   ⚠️  Expected ~{expected} parlays (one per day), but only have {six_leg_count}")
                    print(f"      → Some 6-leg parlays may have failed to build/place")
                elif six_leg_count == expected:
                    print(f"   ✅ Exactly {six_leg_count} parlays across {six_leg_dates} days (one per day)")
                else:
                    print(f"   ⚠️  More parlays ({six_leg_count}) than days ({six_leg_dates}) - unexpected!")
                    print(f"      → Check if multiple 6-leg parlays were placed on some days")
        
        # Check if parlays are being placed daily
        all_dates = set()
        for leg_count in by_legs.keys():
            for p in by_legs[leg_count]:
                if p['placed_at']:
                    all_dates.add(str(p['placed_at'])[:10])
        
        if all_dates:
            print(f"\n📅 SYSTEM ACTIVITY:")
            print(f"   Parlays placed on {len(all_dates)} unique dates")
            print(f"   Date range: {min(all_dates)} to {max(all_dates)}")
            
            if 6 in by_legs and len(by_legs[6]) < len(all_dates):
                missing_days = len(all_dates) - len(by_legs[6])
                print(f"   ⚠️  6-leg parlays missing on {missing_days} day(s)")
                print(f"      → 6-leg parlays may be failing to build on some days")


if __name__ == "__main__":
    asyncio.run(analyze_all_parlays())


