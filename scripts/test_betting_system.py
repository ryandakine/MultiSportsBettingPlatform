#!/usr/bin/env python3
"""
Test Betting System Script
==========================
Test the autonomous betting system end-to-end.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import httpx
import time
from src.services.autonomous_betting_engine import autonomous_engine
from src.services.bet_tracker import bet_tracker


async def test_system():
    """Test the betting system."""
    print("=" * 80)
    print("🧪 TESTING AUTONOMOUS BETTING SYSTEM")
    print("=" * 80)
    print()
    
    user_id = "demo_user"
    
    # 1. Check bankroll
    print("1️⃣ Checking bankroll...")
    bankroll = await bet_tracker.get_bankroll(user_id)
    if bankroll:
        print(f"   ✅ Bankroll found: ${bankroll.get('available_balance', 0):,.2f}")
    else:
        print("   ❌ No bankroll found - please run init_paper_trading.py first")
        return
    
    print()
    
    # 2. Test prediction fetching
    print("2️⃣ Testing prediction fetching...")
    predictions = await autonomous_engine._get_predictions(user_id)
    if predictions:
        print(f"   ✅ Found {len(predictions)} predictions")
        print(f"   Sample prediction: {predictions[0].get('sport', 'unknown')} - {predictions[0].get('team', 'TBD')}")
    else:
        print("   ⚠️ No predictions found - run seed_betting_predictions.py to create test data")
        return
    
    print()
    
    # 3. Test processing predictions (one cycle)
    print("3️⃣ Testing prediction processing (single cycle)...")
    try:
        bets_placed = await autonomous_engine._process_predictions(user_id, predictions, bankroll)
        print(f"   ✅ Processed predictions, placed {bets_placed} bets")
    except Exception as e:
        print(f"   ❌ Error processing predictions: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # 4. Check results
    print("4️⃣ Checking results...")
    from src.services.parlay_tracker import parlay_tracker
    from src.db.database import AsyncSessionLocal
    from src.db.models.bet import Bet, BetType
    from sqlalchemy import select, and_
    from datetime import datetime, timedelta
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    async with AsyncSessionLocal() as session:
        # Get today's bets
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start
                )
            ).order_by(Bet.placed_at.desc())
        )
        bets = result.scalars().all()
        
        # Get parlays
        parlay_bets = [b for b in bets if b.bet_type == BetType.PARLAY]
        straight_bets = [b for b in bets if b.bet_type != BetType.PARLAY]
        
        print(f"   ✅ Total bets today: {len(bets)}")
        print(f"      - Straight bets: {len(straight_bets)}")
        print(f"      - Parlays: {len(parlay_bets)}")
        
        # Show parlay details
        if parlay_bets:
            print()
            print("   📊 Parlays placed:")
            for parlay in parlay_bets[:5]:  # Show first 5
                legs = await parlay_tracker.get_parlay_legs(parlay.id)
                print(f"      - {len(legs)}-leg parlay: ${parlay.amount:.2f} @ {parlay.odds}")
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


async def test_via_api():
    """Test via API (requires server to be running)."""
    print()
    print("=" * 80)
    print("🌐 TESTING VIA API (requires server running)")
    print("=" * 80)
    print()
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Check health
            print("1️⃣ Checking server health...")
            try:
                response = await client.get(f"{base_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print("   ✅ Server is running")
                else:
                    print(f"   ⚠️ Server responded with {response.status_code}")
                    return
            except Exception as e:
                print(f"   ❌ Server not accessible: {e}")
                print("   💡 Start server with: python3 run.py")
                return
            
            print()
            
            # Check betting status
            print("2️⃣ Checking betting status...")
            # Note: This would require authentication, so we'll skip for now
            print("   ⚠️ API testing requires authentication setup")
            print("   💡 You can test manually via:")
            print(f"      POST {base_url}/api/v1/betting/start")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    """Main entry point."""
    await test_system()
    await test_via_api()


if __name__ == "__main__":
    asyncio.run(main())

