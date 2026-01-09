#!/usr/bin/env python3
"""
Diagnose Why Betting Stopped
============================
Check why autonomous betting isn't placing bets.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.autonomous_betting_engine import autonomous_engine
from src.services.bet_tracker import bet_tracker
from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet
from sqlalchemy import select, and_, func


async def diagnose():
    """Diagnose betting issues."""
    print("=" * 80)
    print("🔍 DIAGNOSING WHY BETTING STOPPED")
    print("=" * 80)
    print()
    
    user_id = "demo_user"
    
    # Check 1: Is autonomous engine enabled/running?
    print("1️⃣ AUTONOMOUS ENGINE STATUS")
    print(f"   Enabled: {autonomous_engine.enabled}")
    print(f"   Running: {autonomous_engine.running}")
    if not autonomous_engine.enabled:
        print("   ❌ PROBLEM: Autonomous engine is NOT enabled!")
    print()
    
    # Check 2: Bankroll exists?
    print("2️⃣ BANKROLL STATUS")
    bankroll = await bet_tracker.get_bankroll(user_id)
    if bankroll:
        balance = bankroll.get("balance", 0)
        print(f"   ✅ Bankroll exists: ${balance:,.2f}")
        if balance <= 0:
            print("   ⚠️ WARNING: Bankroll is $0 or negative!")
    else:
        print("   ❌ PROBLEM: No bankroll found for demo_user!")
    print()
    
    # Check 3: Predictions available?
    print("3️⃣ PREDICTIONS STATUS")
    try:
        predictions = await autonomous_engine._get_predictions(user_id)
        print(f"   Total predictions found: {len(predictions)}")
        
        if predictions:
            print(f"   ✅ Predictions available")
            # Check how many are for today
            today = datetime.utcnow().date()
            today_predictions = [
                p for p in predictions 
                if p.get("game_date") and datetime.fromisoformat(p["game_date"].replace('Z', '+00:00')).date() == today
            ]
            print(f"   Predictions for today: {len(today_predictions)}")
            if today_predictions:
                print(f"   ✅ Has predictions for today")
            else:
                print(f"   ⚠️ WARNING: No predictions for today's date!")
        else:
            print("   ❌ PROBLEM: No predictions available!")
    except Exception as e:
        print(f"   ❌ ERROR getting predictions: {e}")
    print()
    
    # Check 4: Bets placed today?
    print("4️⃣ TODAY'S BETTING STATUS")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count(Bet.id)).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start
                )
            )
        )
        bets_today = result.scalar()
        print(f"   Bets placed today: {bets_today}")
        if bets_today > 0:
            print("   ℹ️ Note: Engine waits until tomorrow if bets already placed today")
    print()
    
    # Check 5: Last bet date
    print("5️⃣ LAST BET DATE")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Bet.placed_at)
            .where(Bet.user_id == user_id)
            .order_by(Bet.placed_at.desc())
            .limit(1)
        )
        last_bet = result.scalar_one_or_none()
        if last_bet:
            days_ago = (datetime.utcnow() - last_bet).days
            print(f"   Last bet placed: {last_bet.strftime('%Y-%m-%d %H:%M')} ({days_ago} days ago)")
        else:
            print("   No bets found!")
    print()
    
    # Summary
    print("=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    issues = []
    if not autonomous_engine.enabled:
        issues.append("❌ Autonomous engine not enabled")
    if not bankroll:
        issues.append("❌ No bankroll found")
    elif bankroll.get("balance", 0) <= 0:
        issues.append("⚠️ Bankroll is $0")
    if not predictions:
        issues.append("❌ No predictions available (need to run prediction generation)")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print()
        print("SOLUTIONS:")
        if "No predictions available" in str(issues):
            print("   1. Run: python3 scripts/generate_predictions_with_betting_metadata.py")
        if "not enabled" in str(issues):
            print("   2. Check server logs to see if autonomous betting started")
        if "No bankroll" in str(issues):
            print("   3. Create bankroll for demo_user")
    else:
        print("✅ No obvious issues found!")
        print("   Engine may be waiting for predictions or already placed bets today")


if __name__ == "__main__":
    asyncio.run(diagnose())



