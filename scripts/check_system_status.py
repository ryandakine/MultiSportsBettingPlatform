#!/usr/bin/env python3
"""
Check System Status
===================
Quick status check for the betting platform.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction
from src.db.models.bet import Bet
from sqlalchemy import select, func
from datetime import datetime, timedelta


async def check_status():
    """Check system status."""
    print("🔍 Checking MultiSports Betting Platform Status...")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        # Check predictions
        result = await db.execute(select(func.count(Prediction.id)))
        total_predictions = result.scalar()
        
        result2 = await db.execute(
            select(func.count(Prediction.id)).where(
                Prediction.timestamp >= datetime.now() - timedelta(days=1)
            )
        )
        recent_predictions = result2.scalar()
        
        # Check bets
        result3 = await db.execute(select(func.count(Bet.id)))
        total_bets = result3.scalar()
        
        result4 = await db.execute(
            select(func.count(Bet.id)).where(
                Bet.placed_at >= datetime.now() - timedelta(days=1)
            )
        )
        recent_bets = result4.scalar()
        
        print(f"\n📊 Database Status:")
        print(f"   Total Predictions: {total_predictions}")
        print(f"   Predictions (last 24h): {recent_predictions}")
        print(f"   Total Bets: {total_bets}")
        print(f"   Bets (last 24h): {recent_bets}")
        
        # Check recent predictions
        if recent_predictions > 0:
            result5 = await db.execute(
                select(Prediction)
                .where(Prediction.timestamp >= datetime.now() - timedelta(days=1))
                .order_by(Prediction.timestamp.desc())
                .limit(5)
            )
            recent_preds = result5.scalars().all()
            print(f"\n📝 Recent Predictions (last 5):")
            for pred in recent_preds:
                print(f"   - {pred.sport} | {pred.prediction_text[:60]}... | {pred.timestamp}")
        
        # Check recent bets
        if recent_bets > 0:
            result6 = await db.execute(
                select(Bet)
                .where(Bet.placed_at >= datetime.now() - timedelta(days=1))
                .order_by(Bet.placed_at.desc())
                .limit(5)
            )
            recent_bets_list = result6.scalars().all()
            print(f"\n💰 Recent Bets (last 5):")
            for bet in recent_bets_list:
                status_emoji = "✅" if bet.status == "won" else "❌" if bet.status == "lost" else "⏳"
                print(f"   {status_emoji} ${bet.amount:.2f} | {bet.sport} | {bet.status} | {bet.placed_at}")
        
        print("\n" + "=" * 60)
        
        if recent_predictions == 0:
            print("⚠️  WARNING: No predictions in the last 24 hours!")
            print("   → Prediction generation may not be running")
            print("   → Check: scripts/generate_predictions_with_betting_metadata.py")
        
        if recent_bets == 0:
            print("⚠️  WARNING: No bets placed in the last 24 hours!")
            print("   → Autonomous betting engine may not be running")
            print("   → Check: src/services/autonomous_betting_engine.py")


if __name__ == "__main__":
    asyncio.run(check_status())



