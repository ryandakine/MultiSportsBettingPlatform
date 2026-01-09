#!/usr/bin/env python3
"""
Performance Analysis using Raw SQL to bypass enum issues
"""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from sqlalchemy import text


async def analyze_performance():
    """Analyze performance using raw SQL."""
    print("=" * 80)
    print("💰 COMPREHENSIVE BET PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get all settled bets
        result = await db.execute(text("""
            SELECT 
                bet_type,
                status,
                COUNT(*) as count,
                SUM(amount) as total_wagered,
                SUM(CASE WHEN status = 'won' THEN (payout - amount) ELSE -amount END) as net_profit,
                SUM(CASE WHEN status = 'won' THEN payout ELSE 0 END) as total_won
            FROM bets
            WHERE status IN ('won', 'lost', 'pushed')
            GROUP BY bet_type, status
            ORDER BY bet_type, status
        """))
        
        rows = result.fetchall()
        
        # Organize data
        stats = defaultdict(lambda: {'won': 0, 'lost': 0, 'pushed': 0, 'wagered': 0.0, 'won_amount': 0.0})
        
        for row in rows:
            bet_type, status, count, wagered, net_profit, won_amount = row
            stats[bet_type][status] = count
            stats[bet_type]['wagered'] += wagered or 0
            stats[bet_type]['won_amount'] += won_amount or 0
        
        # Overall stats
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(amount) as wagered,
                SUM(CASE WHEN status = 'won' THEN payout ELSE 0 END) as won,
                SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as losses
            FROM bets
            WHERE status IN ('won', 'lost', 'pushed')
        """))
        
        overall = result.fetchone()
        total_settled, total_wagered, total_won, total_wins, total_losses = overall
        
        if total_settled == 0:
            print("⚠️  No settled bets found. All bets may still be pending.")
            return
        
        overall_win_rate = (total_wins / total_settled * 100) if total_settled > 0 else 0
        overall_roi = ((total_won - total_wagered) / total_wagered * 100) if total_wagered > 0 else 0
        
        print(f"📊 OVERALL PERFORMANCE")
        print("-" * 80)
        print(f"   Total Settled Bets: {total_settled}")
        print(f"   Wins: {total_wins} | Losses: {total_losses}")
        print(f"   Win Rate: {overall_win_rate:.1f}%")
        print(f"   Total Wagered: ${total_wagered:,.2f}")
        print(f"   Total Won: ${total_won:,.2f}")
        print(f"   Net Profit: ${total_won - total_wagered:,.2f}")
        print(f"   ROI: {overall_roi:+.1f}%")
        print()
        
        # By bet type
        print(f"📈 PERFORMANCE BY BET TYPE")
        print("-" * 80)
        for bet_type in sorted(stats.keys()):
            data = stats[bet_type]
            settled = data['won'] + data['lost'] + data['pushed']
            if settled == 0:
                continue
                
            win_rate = (data['won'] / settled * 100) if settled > 0 else 0
            roi = ((data['won_amount'] - data['wagered']) / data['wagered'] * 100) if data['wagered'] > 0 else 0
            
            emoji = "✅" if win_rate >= 50 else "⚠️" if win_rate >= 40 else "❌"
            
            print(f"{emoji} {bet_type.upper()}:")
            print(f"   Settled: {settled} (Won: {data['won']}, Lost: {data['lost']})")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Wagered: ${data['wagered']:,.2f}")
            print(f"   Won: ${data['won_amount']:,.2f}")
            print(f"   ROI: {roi:+.1f}%")
            print()
        
        # Check for parlays
        result = await db.execute(text("""
            SELECT COUNT(*) FROM bets WHERE bet_type = 'parlay'
        """))
        parlay_count = result.scalar()
        
        if parlay_count > 0:
            # Get parlay details
            result = await db.execute(text("""
                SELECT 
                    b.id,
                    b.status,
                    b.amount,
                    b.odds,
                    b.payout,
                    COUNT(pl.id) as leg_count
                FROM bets b
                LEFT JOIN parlay_legs pl ON b.id = pl.parlay_bet_id
                WHERE b.bet_type = 'parlay'
                GROUP BY b.id
                ORDER BY leg_count DESC, b.placed_at DESC
            """))
            
            parlays = result.fetchall()
            
            print("=" * 80)
            print("🎲 PARLAY ANALYSIS")
            print("-" * 80)
            
            # Group by leg count
            parlays_by_legs = defaultdict(list)
            for parlay_id, status, amount, odds, payout, leg_count in parlays:
                parlays_by_legs[leg_count].append((status, amount, odds, payout))
            
            for leg_count in sorted(parlays_by_legs.keys()):
                parlay_list = parlays_by_legs[leg_count]
                won = sum(1 for s, _, _, _ in parlay_list if s == 'won')
                lost = sum(1 for s, _, _, _ in parlay_list if s == 'lost')
                settled = won + lost
                
                if settled == 0:
                    print(f"📊 {leg_count}-LEG PARLAYS: {len(parlay_list)} total (all pending)")
                    continue
                
                wagered = sum(a for _, a, _, _ in parlay_list if settled > 0)
                won_amount = sum(p or 0 for _, _, _, p in parlay_list if settled > 0)
                win_rate = (won / settled * 100) if settled > 0 else 0
                roi = ((won_amount - wagered) / wagered * 100) if wagered > 0 else 0
                
                emoji = "🚀" if leg_count == 6 else "💰"
                highlight = " ⭐ BIG MONEY MAKER" if leg_count == 6 and win_rate > 25 else ""
                
                print(f"{emoji} {leg_count}-LEG PARLAYS{highlight}:")
                print(f"   Total: {len(parlay_list)}")
                print(f"   Settled: {settled} (Won: {won}, Lost: {lost})")
                print(f"   Win Rate: {win_rate:.1f}%")
                if wagered > 0:
                    print(f"   Wagered: ${wagered:,.2f}")
                    print(f"   Won: ${won_amount:,.2f}")
                    print(f"   ROI: {roi:+.1f}%")
                    
                    if won > 0:
                        avg_payout = won_amount / won
                        print(f"   Avg Payout (when won): ${avg_payout:,.2f}")
                print()
            
            # Show recent 6-leg parlays
            if 6 in parlays_by_legs:
                print("🚀 RECENT 6-LEG PARLAYS:")
                six_leg = parlays_by_legs[6][:10]  # Show first 10
                for status, amount, odds, payout in six_leg:
                    emoji = "✅" if status == 'won' else "❌" if status == 'lost' else "⏳"
                    payout_str = f" → ${payout:.2f}" if payout else ""
                    print(f"   {emoji} ${amount:.2f} @ {odds:+.0f} odds | {status.upper()}{payout_str}")
                print()
        
        # Recommendations
        print("=" * 80)
        print("💡 RECOMMENDATIONS")
        print("-" * 80)
        
        if overall_win_rate < 50:
            print(f"📊 Current win rate: {overall_win_rate:.1f}%")
            print(f"   Target: 50%+ for profitability")
            print()
            print("🎯 To improve:")
            
            best_type = max(stats.items(), key=lambda x: (stats[x[0]]['won'] / max(1, stats[x[0]]['won'] + stats[x[0]]['lost'])) if (stats[x[0]]['won'] + stats[x[0]]['lost']) > 0 else 0)
            if best_type[1]['won'] + best_type[1]['lost'] > 0:
                best_win_rate = (best_type[1]['won'] / (best_type[1]['won'] + best_type[1]['lost']) * 100)
                print(f"   1. Focus on {best_type[0].upper()} bets ({best_win_rate:.1f}% win rate)")
            
            if 6 in parlays_by_legs:
                six_leg_data = parlays_by_legs[6]
                six_won = sum(1 for s, _, _, _ in six_leg_data if s == 'won')
                six_lost = sum(1 for s, _, _, _ in six_leg_data if s == 'lost')
                six_settled = six_won + six_lost
                if six_settled > 0:
                    six_win_rate = (six_won / six_settled * 100)
                    print(f"   2. 6-leg parlays: {six_win_rate:.1f}% win rate")
                    if six_win_rate > 20:
                        print(f"      → Even {six_win_rate:.1f}% can be very profitable with high payouts!")
                        print(f"      → Consider increasing frequency or bet sizes")
        else:
            print(f"✅ Win rate at {overall_win_rate:.1f}% - performing well!")
            print(f"   Continue optimizing and scaling successful strategies")


if __name__ == "__main__":
    asyncio.run(analyze_performance())


