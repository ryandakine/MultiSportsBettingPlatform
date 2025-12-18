#!/usr/bin/env python3
"""
Test Daily Picks Placement
==========================
Manually trigger the daily picks placement to verify it works.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from src.services.autonomous_betting_engine import autonomous_engine
from src.services.bet_tracker import bet_tracker


async def test_daily_picks():
    """Test placing daily picks."""
    print("=" * 80)
    print("🎯 TESTING DAILY PICKS PLACEMENT")
    print("=" * 80)
    print()
    
    user_id = "demo_user"
    
    # 1. Get bankroll
    print("1️⃣ Checking bankroll...")
    bankroll = await bet_tracker.get_bankroll(user_id)
    if not bankroll:
        print("   ❌ No bankroll found")
        return
    
    print(f"   ✅ Bankroll: ${bankroll.get('current_balance', 0):.2f}")
    print(f"      Available: ${bankroll.get('available_balance', 0):.2f}")
    print()
    
    # 2. Get predictions
    print("2️⃣ Fetching predictions...")
    predictions = await autonomous_engine._get_predictions(user_id)
    print(f"   ✅ Found {len(predictions)} total predictions")
    
    # Filter eligible predictions
    eligible = []
    for pred in predictions:
        edge = pred.get("edge", 0)
        confidence = pred.get("confidence", 0)
        if edge >= autonomous_engine.min_edge_threshold and confidence >= autonomous_engine.min_confidence:
            eligible.append(pred)
    
    print(f"   ✅ Found {len(eligible)} eligible predictions")
    print()
    
    if not eligible:
        print("   ❌ No eligible predictions found")
        return
    
    # 3. Process predictions (this will place daily picks)
    print("3️⃣ Processing predictions to place daily picks...")
    print(f"   Will place up to {min(10, len(eligible))} daily picks")
    print()
    
    # Test a single bet first
    print("   Testing single bet placement...")
    test_pred = eligible[0]
    print(f"   Test prediction: {test_pred.get('sport')} | {test_pred.get('team')} | Edge: {test_pred.get('edge'):.2%}")
    
    # Calculate bet size
    bet_amount = autonomous_engine._calculate_bet_size(test_pred, bankroll["available_balance"])
    print(f"   Calculated bet size: ${bet_amount:.2f}")
    
    if bet_amount < 1:
        print(f"   ⚠️ Bet amount too small (${bet_amount:.2f} < $1 minimum)")
    else:
        print(f"   ✅ Bet amount is valid")
    
    print()
    
    # Now process all predictions
    bets_placed = await autonomous_engine._process_predictions(user_id, eligible, bankroll)
    
    print()
    print("=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    print(f"✅ Total bets placed: {bets_placed}")
    print()
    
    # 4. Verify bets were placed
    from src.db.database import AsyncSessionLocal
    from src.db.models.bet import Bet, BetType
    from sqlalchemy import select, and_
    from datetime import datetime
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type != BetType.PARLAY
                )
            )
            .order_by(Bet.placed_at.desc())
            .limit(10)
        )
        daily_picks = result.scalars().all()
    
    if daily_picks:
        print("📋 Daily picks placed:")
        for i, bet in enumerate(daily_picks, 1):
            print(f"   {i}. {bet.sport} | {bet.team or 'N/A'} | ${bet.amount:.2f} @ {bet.odds} | {bet.bet_type.value}")
    else:
        print("⚠️ No daily picks found in database")
    
    print()


async def main():
    """Main entry point."""
    try:
        await test_daily_picks()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

