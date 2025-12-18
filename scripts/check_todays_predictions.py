#!/usr/bin/env python3
"""
Check Today's Predictions Script
=================================
Check what predictions the system has for today's games.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction


async def check_todays_predictions():
    """Check predictions for today's games."""
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Sports to check
    sports_to_check = {
        "college_football": ["ncaaf", "college-football", "college_football", "football"],
        "hockey": ["nhl", "hockey"],
        "college_basketball_mens": ["ncaab", "college-basketball", "college_basketball", "basketball"],
        "college_basketball_womens": ["ncaaw", "womens-college-basketball", "womens_basketball", "wncaab"]
    }
    
    async with AsyncSessionLocal() as session:
        print("=" * 80)
        print("📊 TODAY'S PREDICTIONS CHECK")
        print("=" * 80)
        print(f"Date: {today_start.strftime('%Y-%m-%d')}")
        print()
        
        # Check recent predictions (last 24 hours)
        result = await session.execute(
            select(Prediction)
            .where(Prediction.timestamp >= today_start - timedelta(hours=24))
            .order_by(Prediction.timestamp.desc())
        )
        all_predictions = result.scalars().all()
        
        if not all_predictions:
            print("⚠️ No predictions found in the last 24 hours")
            print()
            print("💡 To generate predictions:")
            print("   1. Make sure your head agent is running")
            print("   2. Use the prediction API: POST /api/v1/predict")
            print("   3. Or check if autonomous betting has generated any")
            return
        
        print(f"Found {len(all_predictions)} predictions in the last 24 hours")
        print()
        
        # Group by sport
        predictions_by_sport = {}
        for pred in all_predictions:
            sport = pred.sport.lower()
            if sport not in predictions_by_sport:
                predictions_by_sport[sport] = []
            predictions_by_sport[sport].append(pred)
        
        # Check each requested sport
        for sport_name, sport_variants in sports_to_check.items():
            print(f"{'='*80}")
            display_name = sport_name.replace('_', ' ').title()
            if 'womens' in sport_name.lower():
                display_name = "🏀 Women's College Basketball"
            elif 'mens' in sport_name.lower():
                display_name = "🏀 Men's College Basketball"
            elif 'college' in sport_name.lower() and 'basketball' not in sport_name.lower():
                display_name = "🏈 College Football"
            elif 'hockey' in sport_name.lower():
                display_name = "🏒 Hockey"
            print(f"{display_name}")
            print(f"{'='*80}")
            
            found = False
            for variant in sport_variants:
                if variant in predictions_by_sport:
                    found = True
                    preds = predictions_by_sport[variant]
                    print(f"✅ Found {len(preds)} prediction(s) for {variant}:")
                    print()
                    
                    for i, pred in enumerate(preds, 1):
                        metadata = pred.metadata_json or {}
                        game_date = metadata.get("game_date") or pred.timestamp
                        
                        print(f"  {i}. {pred.prediction_text}")
                        print(f"     Sport: {pred.sport}")
                        print(f"     Confidence: {pred.confidence}")
                        if metadata.get("home_team") and metadata.get("away_team"):
                            print(f"     Game: {metadata.get('away_team')} @ {metadata.get('home_team')}")
                        if metadata.get("team"):
                            print(f"     Pick: {metadata.get('team')}")
                        if metadata.get("bet_type"):
                            print(f"     Bet Type: {metadata.get('bet_type')}")
                        if metadata.get("odds"):
                            print(f"     Odds: {metadata.get('odds')}")
                        if metadata.get("probability"):
                            print(f"     Probability: {metadata.get('probability', 0) * 100:.1f}%")
                        if metadata.get("edge"):
                            print(f"     Edge: {metadata.get('edge', 0) * 100:.1f}%")
                        print(f"     Created: {pred.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                        if pred.reasoning:
                            print(f"     Reasoning: {pred.reasoning[:100]}...")
                        print()
                    break
            
            if not found:
                print(f"❌ No predictions found for {sport_name}")
                print(f"   Checked variants: {', '.join(sport_variants)}")
                print()
        
        # Show all sports found
        print(f"{'='*80}")
        print("📋 ALL SPORTS WITH PREDICTIONS")
        print(f"{'='*80}")
        if predictions_by_sport:
            for sport, preds in predictions_by_sport.items():
                print(f"  {sport}: {len(preds)} prediction(s)")
        else:
            print("  No predictions found")
        print()


async def check_real_games_today():
    """Check what real games are happening today."""
    try:
        from src.services.real_sports_service import RealSportsService
        
        print()
        print("=" * 80)
        print("🎮 CHECKING REAL GAMES TODAY")
        print("=" * 80)
        print()
        
        real_sports = RealSportsService()
        
        # Check each sport
        sports_to_check = {
            "ncaaf": "College Football",
            "nhl": "NHL Hockey",
            "ncaab": "Men's College Basketball",
            "ncaaw": "Women's College Basketball"
        }
        
        for sport_code, sport_name in sports_to_check.items():
            print(f"Checking {sport_name} ({sport_code})...")
            try:
                games = await real_sports.get_live_games(sport_code)
                if games:
                    print(f"  ✅ Found {len(games)} game(s) today:")
                    for game in games[:5]:  # Show first 5
                        home = game.get("home_team", "TBD")
                        away = game.get("away_team", "TBD")
                        status = game.get("status", "scheduled")
                        print(f"     {away} @ {home} - {status}")
                else:
                    print(f"  ⚠️ No games found for {sport_name} today")
            except Exception as e:
                print(f"  ❌ Error checking {sport_name}: {e}")
            print()
            
    except Exception as e:
        print(f"⚠️ Could not check real games: {e}")
        print("   (This is okay - real games API may not be configured)")


async def main():
    """Main entry point."""
    await check_todays_predictions()
    await check_real_games_today()


if __name__ == "__main__":
    asyncio.run(main())

