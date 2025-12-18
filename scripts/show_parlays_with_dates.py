#!/usr/bin/env python3
"""
Show Parlays with Dates
=======================
Display parlay bets with game dates for each leg.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime
from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetType
from src.db.models.parlay import ParlayLeg
from sqlalchemy import select, and_
from dateutil import parser


async def show_parlays_with_dates():
    """Show parlays with game dates."""
    user_id = "demo_user"
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    async with AsyncSessionLocal() as session:
        # Get today's parlays
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type == BetType.PARLAY
                )
            )
            .order_by(Bet.placed_at.desc())
        )
        parlays = result.scalars().all()
        
        print("=" * 80)
        print("📊 TODAY'S PARLAYS WITH GAME DATES")
        print("=" * 80)
        print()
        
        if not parlays:
            print("No parlays found for today")
            return
        
        for i, parlay in enumerate(parlays, 1):
            print(f"Parlay #{i}")
            print(f"ID: {parlay.id}")
            print(f"Amount: ${parlay.amount:.2f}")
            print(f"Combined Odds: +{parlay.odds:.2f}" if parlay.odds > 0 else f"Combined Odds: {parlay.odds:.2f}")
            print(f"Status: {parlay.status.value}")
            print()
            print("Legs:")
            
            # Get legs for this parlay
            legs_result = await session.execute(
                select(ParlayLeg).where(ParlayLeg.parlay_bet_id == parlay.id)
                .order_by(ParlayLeg.created_at)
            )
            legs = legs_result.scalars().all()
            
            for j, leg in enumerate(legs, 1):
                # Try to get game date from the bet's game_date or from prediction metadata
                game_date_str = "TBD"
                if parlay.game_date:
                    try:
                        if isinstance(parlay.game_date, str):
                            dt = parser.parse(parlay.game_date)
                        else:
                            dt = parlay.game_date
                        game_date_str = dt.strftime("%Y-%m-%d %I:%M %p %Z")
                    except:
                        game_date_str = str(parlay.game_date)
                
                print(f"  {j}. {leg.sport.upper()} | {leg.team or 'TBD'}")
                print(f"     Bet: {leg.bet_type} @ {leg.odds:.0f}")
                if leg.line is not None:
                    print(f"     Line: {leg.line:+.1f}")
                print(f"     Game: {leg.home_team or 'TBD'} vs {leg.away_team or 'TBD'}")
                print(f"     Date: {game_date_str}")
                print()
            
            print("-" * 80)
            print()


async def main():
    """Main entry point."""
    try:
        await show_parlays_with_dates()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

