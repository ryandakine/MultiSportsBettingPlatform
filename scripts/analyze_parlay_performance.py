#!/usr/bin/env python3
"""
Comprehensive Parlay Performance Analysis
=========================================
Analyzes parlay bet performance, especially focusing on 6-leg parlays
and comparing them to straight bets.
"""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus, BetType
from src.db.models.parlay import ParlayLeg
from sqlalchemy import select, func, and_, or_


async def analyze_parlay_performance():
    """Comprehensive parlay performance analysis."""
    print("=" * 80)
    print("🎯 COMPREHENSIVE PARLAY PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # ===== OVERALL BET ANALYSIS =====
        print("📊 OVERALL BET PERFORMANCE")
        print("-" * 80)
        
        # Get all straight bets (non-parlays)
        straight_bets = await db.execute(
            select(Bet)
            .where(Bet.bet_type != BetType.PARLAY)
            .where(Bet.status.in_([BetStatus.WON, BetStatus.LOST, BetStatus.PUSHED]))
        )
        straight_bets_list = straight_bets.scalars().all()
        
        # Get all parlay bets
        parlay_bets = await db.execute(
            select(Bet)
            .where(Bet.bet_type == BetType.PARLAY)
            .where(Bet.status.in_([BetStatus.WON, BetStatus.LOST, BetStatus.PUSHED]))
        )
        parlay_bets_list = parlay_bets.scalars().all()
        
        # Calculate straight bet stats
        straight_won = sum(1 for b in straight_bets_list if b.status == BetStatus.WON)
        straight_lost = sum(1 for b in straight_bets_list if b.status == BetStatus.LOST)
        straight_settled = len(straight_bets_list)
        straight_wagered = sum(b.amount for b in straight_bets_list)
        straight_won_amount = sum(b.payout or 0 for b in straight_bets_list if b.status == BetStatus.WON)
        straight_win_rate = (straight_won / straight_settled * 100) if straight_settled > 0 else 0
        straight_roi = ((straight_won_amount - straight_wagered) / straight_wagered * 100) if straight_wagered > 0 else 0
        
        # Calculate parlay bet stats
        parlay_won = sum(1 for b in parlay_bets_list if b.status == BetStatus.WON)
        parlay_lost = sum(1 for b in parlay_bets_list if b.status == BetStatus.LOST)
        parlay_settled = len(parlay_bets_list)
        parlay_wagered = sum(b.amount for b in parlay_bets_list)
        parlay_won_amount = sum(b.payout or 0 for b in parlay_bets_list if b.status == BetStatus.WON)
        parlay_win_rate = (parlay_won / parlay_settled * 100) if parlay_settled > 0 else 0
        parlay_roi = ((parlay_won_amount - parlay_wagered) / parlay_wagered * 100) if parlay_wagered > 0 else 0
        
        print(f"📈 STRAIGHT BETS:")
        print(f"   Settled: {straight_settled}")
        print(f"   Won: {straight_won} | Lost: {straight_lost}")
        print(f"   Win Rate: {straight_win_rate:.1f}%")
        print(f"   Wagered: ${straight_wagered:,.2f}")
        print(f"   Won: ${straight_won_amount:,.2f}")
        print(f"   ROI: {straight_roi:+.1f}%")
        print()
        
        print(f"🎲 PARLAY BETS:")
        print(f"   Settled: {parlay_settled}")
        print(f"   Won: {parlay_won} | Lost: {parlay_lost}")
        print(f"   Win Rate: {parlay_win_rate:.1f}%")
        print(f"   Wagered: ${parlay_wagered:,.2f}")
        print(f"   Won: ${parlay_won_amount:,.2f}")
        print(f"   ROI: {parlay_roi:+.1f}%")
        print()
        
        # ===== PARLAY ANALYSIS BY LEG COUNT =====
        print("=" * 80)
        print("🎯 PARLAY PERFORMANCE BY LEG COUNT")
        print("-" * 80)
        
        # Get all parlay legs to count legs per parlay
        all_legs_result = await db.execute(
            select(ParlayLeg.parlay_bet_id, func.count(ParlayLeg.id).label('leg_count'))
            .group_by(ParlayLeg.parlay_bet_id)
        )
        legs_by_parlay = {parlay_id: leg_count for parlay_id, leg_count in all_legs_result.all()}
        
        # Group parlays by leg count
        parlays_by_legs = defaultdict(list)
        for parlay in parlay_bets_list:
            leg_count = legs_by_parlay.get(parlay.id, 0)
            parlays_by_legs[leg_count].append(parlay)
        
        # Analyze each leg count
        for leg_count in sorted(parlays_by_legs.keys()):
            parlays = parlays_by_legs[leg_count]
            won = sum(1 for p in parlays if p.status == BetStatus.WON)
            lost = sum(1 for p in parlays if p.status == BetStatus.LOST)
            settled = len(parlays)
            wagered = sum(p.amount for p in parlays)
            won_amount = sum(p.payout or 0 for p in parlays if p.status == BetStatus.WON)
            win_rate = (won / settled * 100) if settled > 0 else 0
            roi = ((won_amount - wagered) / wagered * 100) if wagered > 0 else 0
            
            emoji = "🚀" if leg_count == 6 else "💰" if win_rate > 40 else "📊"
            highlight = " ⭐ BIG MONEY MAKER" if leg_count == 6 and win_rate > 30 else ""
            
            print(f"{emoji} {leg_count}-LEG PARLAYS{highlight}:")
            print(f"   Settled: {settled}")
            print(f"   Won: {won} | Lost: {lost}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Wagered: ${wagered:,.2f}")
            print(f"   Won: ${won_amount:,.2f}")
            print(f"   ROI: {roi:+.1f}%")
            
            if settled > 0:
                avg_wager = wagered / settled
                avg_payout = won_amount / won if won > 0 else 0
                print(f"   Avg Wager: ${avg_wager:.2f}")
                if won > 0:
                    print(f"   Avg Payout (when won): ${avg_payout:.2f}")
            print()
        
        # ===== DETAILED 6-LEG PARLAY ANALYSIS =====
        if 6 in parlays_by_legs:
            print("=" * 80)
            print("🚀 DETAILED 6-LEG PARLAY ANALYSIS")
            print("-" * 80)
            
            six_leg_parlays = parlays_by_legs[6]
            
            # Get all legs for 6-leg parlays
            six_leg_parlay_ids = [p.id for p in six_leg_parlays]
            legs_result = await db.execute(
                select(ParlayLeg)
                .where(ParlayLeg.parlay_bet_id.in_(six_leg_parlay_ids))
            )
            all_legs = legs_result.scalars().all()
            
            # Analyze legs by bet type
            leg_stats_by_type = defaultdict(lambda: {'won': 0, 'lost': 0, 'pending': 0, 'pushed': 0})
            leg_stats_by_sport = defaultdict(lambda: {'won': 0, 'lost': 0, 'pending': 0, 'pushed': 0})
            
            for leg in all_legs:
                result = leg.result or 'pending'
                leg_stats_by_type[leg.bet_type][result] += 1
                leg_stats_by_sport[leg.sport][result] += 1
            
            print(f"📊 LEG PERFORMANCE BY BET TYPE:")
            for bet_type, stats in sorted(leg_stats_by_type.items()):
                total = sum(stats.values())
                won = stats.get('won', 0)
                win_rate = (won / total * 100) if total > 0 else 0
                print(f"   {bet_type.upper()}: {won}/{total} won ({win_rate:.1f}%)")
            print()
            
            print(f"🏀 LEG PERFORMANCE BY SPORT:")
            for sport, stats in sorted(leg_stats_by_sport.items()):
                total = sum(stats.values())
                won = stats.get('won', 0)
                win_rate = (won / total * 100) if total > 0 else 0
                print(f"   {sport}: {won}/{total} won ({win_rate:.1f}%)")
            print()
            
            # Show individual 6-leg parlays
            print(f"📝 INDIVIDUAL 6-LEG PARLAYS:")
            for parlay in sorted(six_leg_parlays, key=lambda x: x.placed_at, reverse=True)[:10]:
                status_emoji = "✅" if parlay.status == BetStatus.WON else "❌" if parlay.status == BetStatus.LOST else "⏳"
                payout_str = f" → ${parlay.payout:.2f}" if parlay.payout else ""
                print(f"   {status_emoji} ${parlay.amount:.2f} @ {parlay.odds:+.0f} odds | {parlay.status.value.upper()}{payout_str} | {parlay.placed_at.strftime('%Y-%m-%d')}")
            print()
            
            # Analyze winning 6-leg parlays
            winning_six_leg = [p for p in six_leg_parlays if p.status == BetStatus.WON]
            if winning_six_leg:
                print(f"✅ WINNING 6-LEG PARLAY INSIGHTS:")
                avg_odds = sum(p.odds for p in winning_six_leg) / len(winning_six_leg)
                avg_amount = sum(p.amount for p in winning_six_leg) / len(winning_six_leg)
                avg_payout = sum(p.payout or 0 for p in winning_six_leg) / len(winning_six_leg)
                print(f"   Average Odds: {avg_odds:+.0f}")
                print(f"   Average Wager: ${avg_amount:.2f}")
                print(f"   Average Payout: ${avg_payout:.2f}")
                print(f"   Average Profit: ${avg_payout - avg_amount:.2f}")
                print()
        
        # ===== RECOMMENDATIONS =====
        print("=" * 80)
        print("💡 RECOMMENDATIONS")
        print("-" * 80)
        
        if parlay_settled > 0:
            if parlay_win_rate > straight_win_rate:
                print(f"✅ Parlays are outperforming straight bets ({parlay_win_rate:.1f}% vs {straight_win_rate:.1f}%)")
                print(f"   → Continue placing parlays, especially high-performing leg counts")
            else:
                print(f"⚠️  Straight bets outperform parlays ({straight_win_rate:.1f}% vs {parlay_win_rate:.1f}%)")
                print(f"   → Consider focusing more on straight bets or improving parlay selection")
            print()
            
            if 6 in parlays_by_legs:
                six_leg_win_rate = (sum(1 for p in parlays_by_legs[6] if p.status == BetStatus.WON) / 
                                   len(parlays_by_legs[6]) * 100)
                if six_leg_win_rate > 30:
                    print(f"🚀 6-leg parlays showing strong performance ({six_leg_win_rate:.1f}% win rate)")
                    print(f"   → These could be your big money makers!")
                    print(f"   → Consider increasing frequency or bet sizes for 6-leg parlays")
                elif six_leg_win_rate > 20:
                    print(f"💰 6-leg parlays showing decent performance ({six_leg_win_rate:.1f}% win rate)")
                    print(f"   → With high payouts, even 20%+ win rate can be very profitable")
                    print(f"   → Continue monitoring and optimizing leg selection")
                else:
                    print(f"⚠️  6-leg parlays need improvement ({six_leg_win_rate:.1f}% win rate)")
                    print(f"   → Review leg selection criteria")
                    print(f"   → Check if certain bet types or sports underperform in 6-leg parlays")
                print()
        
        # Overall win rate
        total_settled = straight_settled + parlay_settled
        total_won = straight_won + parlay_won
        overall_win_rate = (total_won / total_settled * 100) if total_settled > 0 else 0
        
        print(f"📈 OVERALL PERFORMANCE:")
        print(f"   Total Settled Bets: {total_settled}")
        print(f"   Overall Win Rate: {overall_win_rate:.1f}%")
        print()
        
        if overall_win_rate < 50:
            print(f"💡 To improve from {overall_win_rate:.1f}% to 50%+ win rate:")
            print(f"   1. Focus on bet types with highest win rates")
            print(f"   2. Improve over/under bet quality (currently 9.1% win rate)")
            print(f"   3. Optimize parlay leg selection based on performance data")
            print(f"   4. Review edge thresholds - may need higher minimum edge")
        else:
            print(f"✅ Win rate above 50% - system is performing well!")
            print(f"   Continue optimizing and scaling successful strategies")
        print()


if __name__ == "__main__":
    asyncio.run(analyze_parlay_performance())


