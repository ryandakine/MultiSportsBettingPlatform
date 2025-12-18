#!/usr/bin/env python3
"""
Check Daily Picks System
========================
Verify that the daily picks system is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime, timedelta
from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction
from src.db.models.bet import Bet, BetType, BetStatus
from src.services.bet_tracker import bet_tracker
from src.services.autonomous_betting_engine import autonomous_engine
from sqlalchemy import select, and_, func


async def check_daily_picks():
    """Check the daily picks system status."""
    print("=" * 80)
    print("📊 DAILY PICKS SYSTEM CHECK")
    print("=" * 80)
    print()
    
    user_id = "demo_user"  # Default user
    
    # 1. Check for recent predictions with betting metadata
    print("1️⃣ Checking for predictions with betting metadata...")
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Prediction)
            .where(Prediction.timestamp >= cutoff)
            .order_by(Prediction.timestamp.desc())
        )
        predictions = result.scalars().all()
    
    print(f"   Found {len(predictions)} predictions in last 24 hours")
    
    eligible_predictions = []
    for pred in predictions:
        metadata = pred.metadata_json or {}
        if (metadata.get("game_id") and 
            metadata.get("odds") is not None and 
            metadata.get("probability") is not None):
            
            edge = metadata.get("edge", 0)
            confidence = pred.confidence
            
            # Convert confidence to float
            if isinstance(confidence, str):
                conf_map = {"low": 0.5, "medium": 0.65, "high": 0.85}
                confidence = conf_map.get(confidence.lower(), 0.65)
            elif isinstance(confidence, (int, float)):
                confidence = float(confidence) / 100.0 if confidence > 1 else float(confidence)
            else:
                confidence = 0.65
            
            if edge >= autonomous_engine.min_edge_threshold and confidence >= autonomous_engine.min_confidence:
                eligible_predictions.append({
                    "id": pred.id,
                    "sport": pred.sport,
                    "game_id": metadata.get("game_id"),
                    "team": metadata.get("team"),
                    "edge": edge,
                    "confidence": confidence,
                    "odds": metadata.get("odds")
                })
    
    print(f"   ✅ Found {len(eligible_predictions)} eligible predictions for daily picks")
    print(f"      (Edge >= {autonomous_engine.min_edge_threshold}, Confidence >= {autonomous_engine.min_confidence})")
    
    if eligible_predictions:
        print()
        print("   Top 5 eligible predictions:")
        sorted_preds = sorted(eligible_predictions, key=lambda x: x["confidence"] * x["edge"], reverse=True)
        for i, pred in enumerate(sorted_preds[:5], 1):
            print(f"      {i}. {pred['sport']} | {pred.get('team', 'N/A')} | Edge: {pred['edge']:.2%} | Conf: {pred['confidence']:.2%} | Odds: {pred['odds']}")
    print()
    
    # 2. Check bankroll
    print("2️⃣ Checking bankroll...")
    bankroll = await bet_tracker.get_bankroll(user_id)
    if bankroll:
        print(f"   ✅ Bankroll found: ${bankroll.get('current_balance', 0):.2f}")
        print(f"      Available: ${bankroll.get('available_balance', 0):.2f}")
    else:
        print(f"   ❌ No bankroll found for user {user_id}")
        print(f"      Run: python3 scripts/init_paper_trading.py")
    print()
    
    # 3. Check today's bets (daily picks)
    print("3️⃣ Checking today's bets (daily picks)...")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    async with AsyncSessionLocal() as session:
        # Count all bets today
        all_bets_result = await session.execute(
            select(func.count(Bet.id)).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start
                )
            )
        )
        all_bets_count = all_bets_result.scalar() or 0
        
        # Count daily picks (non-parlay bets)
        daily_picks_result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type != BetType.PARLAY,
                    Bet.is_autonomous == True
                )
            )
            .order_by(Bet.placed_at.desc())
        )
        daily_picks = daily_picks_result.scalars().all()
        
        # Count parlays
        parlays_result = await session.execute(
            select(func.count(Bet.id)).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type == BetType.PARLAY
                )
            )
        )
        parlays_count = parlays_result.scalar() or 0
    
    print(f"   Total bets today: {all_bets_count}")
    print(f"   Daily picks (straight bets): {len(daily_picks)}")
    print(f"   Parlays: {parlays_count}")
    
    if daily_picks:
        print()
        print("   Today's daily picks:")
        for i, bet in enumerate(daily_picks[:10], 1):
            status_emoji = "✅" if bet.status == BetStatus.WON else "❌" if bet.status == BetStatus.LOST else "⏳"
            print(f"      {i}. {status_emoji} {bet.sport} | {bet.team or 'N/A'} | ${bet.amount:.2f} @ {bet.odds} | {bet.status.value}")
    else:
        print("   ⚠️ No daily picks placed today")
    print()
    
    # 4. Check if autonomous engine is running
    print("4️⃣ Checking autonomous betting engine status...")
    print(f"   Enabled: {'✅ Yes' if autonomous_engine.enabled else '❌ No'}")
    print(f"   Running: {'✅ Yes' if autonomous_engine.running else '❌ No'}")
    print(f"   Paper Trading: {'✅ Yes' if autonomous_engine.paper_trading else '❌ No'}")
    print()
    
    # 5. Summary and recommendations
    print("=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    if not eligible_predictions:
        print("❌ ISSUE: No eligible predictions found")
        print("   → The head agent needs to generate predictions with betting metadata")
        print("   → Predictions need: game_id, odds, probability, and edge >= 5%")
    elif not bankroll:
        print("❌ ISSUE: No bankroll initialized")
        print("   → Run: python3 scripts/init_paper_trading.py")
    elif len(daily_picks) == 0 and all_bets_count == 0:
        print("⚠️  WARNING: No bets placed today")
        print("   → The autonomous betting engine may not have run yet today")
        print("   → Check if AUTO_BETTING_ENABLED is set in environment")
    elif len(daily_picks) == 0 and all_bets_count > 0:
        print("⚠️  WARNING: Parlays placed but no daily picks")
        print("   → This shouldn't happen - daily picks should be placed first")
    else:
        print("✅ Daily picks system appears to be working!")
        print(f"   → {len(daily_picks)} daily picks placed today")
    
    print()


async def main():
    """Main entry point."""
    try:
        await check_daily_picks()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

