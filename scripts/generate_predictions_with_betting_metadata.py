#!/usr/bin/env python3
"""
Generate Predictions with Betting Metadata
==========================================
Creates predictions with full betting metadata for the daily picks system.
This fetches real games and generates predictions with odds, probability, and edge.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import uuid
from datetime import datetime, timedelta
from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction
from src.services.real_sports_service import real_sports_service
from src.services.model_prediction_service import model_prediction_service


async def generate_predictions_with_betting_metadata():
    """Generate predictions with betting metadata from real games."""
    print("=" * 80)
    print("🎯 GENERATING PREDICTIONS WITH BETTING METADATA")
    print("=" * 80)
    print()
    
    # Initialize model prediction service (loads trained models if available)
    print("🤖 Initializing model prediction service...")
    await model_prediction_service.initialize()
    model_status = model_prediction_service.get_model_status()
    if model_status['model_loaded']:
        print(f"   ✅ Using trained models: {', '.join(model_status['models_loaded'])}")
    else:
        print(f"   ⚠️  No trained models found - using fallback calculations")
    print()
    
    user_id = "demo_user"
    
    # Get today's games
    print("1️⃣ Fetching today's games...")
    
    sports_to_check = ["ncaaf", "nhl", "ncaab", "ncaaw"]  # College football, NHL, college basketball, women's college basketball
    
    all_games = []
    sports_to_fetch = ["ncaaf", "nhl", "ncaab", "ncaaw"]
    
    # Get today and tomorrow's dates
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_date = today_start.date()
    tomorrow_date = today_date + timedelta(days=1)
    
    # Since it's early morning (before 10 AM UTC), check both today AND tomorrow
    # Games scheduled for "tomorrow" in UTC might be happening later today in local time
    # Also, if it's late evening (after 10 PM), include early tomorrow games
    check_tomorrow = now.hour < 10 or now.hour >= 22
    
    print(f"   Current time (UTC): {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Filtering games for: {today_date}")
    if check_tomorrow:
        print(f"   Also checking tomorrow: {tomorrow_date} (early morning or late evening)")
    
    for sport_key in sports_to_fetch:
        try:
            print(f"   Fetching {sport_key} games...")
            games = await real_sports_service.get_live_games(sport_key)
            if games:
                print(f"   ✅ Found {len(games)} total {sport_key} games from API")
                
                # Filter to today's games (and tomorrow if checking)
                eligible_games = []
                
                for game in games:
                    game_date_str = game.get("date")
                    if game_date_str:
                        try:
                            from dateutil import parser
                            game_date = parser.parse(game_date_str)
                            game_date_only = game_date.date()
                            
                            # Include games from today
                            if game_date_only == today_date:
                                game["sport_key"] = sport_key
                                eligible_games.append(game)
                            # Include games from tomorrow if we're checking tomorrow
                            elif check_tomorrow and game_date_only == tomorrow_date:
                                game["sport_key"] = sport_key
                                eligible_games.append(game)
                        except Exception as e:
                            # If we can't parse the date, skip this game
                            continue
                
                date_label = "today" if not check_tomorrow else "today/tomorrow"
                print(f"   ✅ {len(eligible_games)} {sport_key} games scheduled for {date_label}")
                all_games.extend(eligible_games)
            else:
                print(f"   ⚠️ No {sport_key} games found")
        except Exception as e:
            print(f"   ❌ Error fetching {sport_key} games: {e}")
    
    print(f"\n   Total games scheduled for today: {len(all_games)}")
    print()
    
    if not all_games:
        print("❌ No games found for today")
        return
    
    # Generate predictions for each game - distribute evenly across sports
    print("2️⃣ Generating predictions with betting metadata...")
    
    # Group games by sport_key to distribute evenly
    games_by_sport = {}
    for game in all_games:
        sport_key = game.get("sport_key", "unknown")
        if sport_key not in games_by_sport:
            games_by_sport[sport_key] = []
        games_by_sport[sport_key].append(game)
    
    # Take up to 5-6 games from each sport (or all if less)
    games_per_sport = 5
    selected_games = []
    for sport_key, games in games_by_sport.items():
        selected_games.extend(games[:games_per_sport])
    
    print(f"   Selected {len(selected_games)} games across {len(games_by_sport)} sports")
    for sport_key, games in games_by_sport.items():
        selected_count = min(games_per_sport, len(games))
        print(f"   {sport_key}: {selected_count} games")
    print()
    
    predictions_created = 0
    
    async with AsyncSessionLocal() as session:
        for game in selected_games:
            try:
                # Extract game info - home_team and away_team are strings in the response
                home_team = game.get("home_team", "Home Team")
                away_team = game.get("away_team", "Away Team")
                game_id = game.get("id", f"game_{uuid.uuid4()}")
                
                # Determine sport name - preserve specific sport types
                sport_key = game.get("sport_key", "basketball")
                sport_map = {
                    "ncaaf": "football",
                    "nfl": "football",
                    "nhl": "hockey",
                    "ncaab": "basketball",
                    "ncaaw": "women_basketball",  # Keep women's basketball separate
                    "nba": "basketball",
                    "wnba": "women_basketball",
                    "mlb": "baseball"
                }
                sport = sport_map.get(sport_key, "basketball")
                
                # Extract odds from real_odds if available
                real_odds = game.get("real_odds", {})
                markets = real_odds.get("markets", [])
                
                # Try to get moneyline odds, fallback to spread, then default
                odds = -110  # Default odds
                bet_type = "moneyline"
                line = None
                team = home_team  # Default to home team
                
                # Look for moneyline (h2h) first
                for market in markets:
                    if market.get("key") == "h2h":
                        outcomes = market.get("outcomes", [])
                        if outcomes:
                            # Use home team odds
                            home_outcome = next((o for o in outcomes if o.get("name") == home_team), None)
                            if home_outcome:
                                odds = home_outcome.get("price", -110)
                                bet_type = "moneyline"
                                team = home_team
                                break
                    
                    elif market.get("key") == "spreads" and bet_type == "moneyline":
                        # Fallback to spread if no moneyline
                        outcomes = market.get("outcomes", [])
                        if outcomes:
                            home_outcome = next((o for o in outcomes if o.get("name") == home_team), None)
                            if home_outcome:
                                odds = home_outcome.get("price", -110)
                                line = home_outcome.get("point", 0)
                                bet_type = "spread"
                                team = home_team
                                break
                
                # Generate prediction text
                if bet_type == "moneyline":
                    prediction_text = f"{home_team} to win (Moneyline)"
                else:
                    prediction_text = f"{home_team} {line:+.1f} (Spread)"
                
                # Get model prediction (uses trained models if available, fallback otherwise)
                game_data = {
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "date": game.get("date", datetime.utcnow().isoformat()),
                    "sport": sport
                }
                
                model_result = await model_prediction_service.get_model_prediction(
                    sport=sport_key,
                    game_data=game_data,
                    odds=odds
                )
                
                model_probability = model_result['model_probability']
                model_confidence = model_result['confidence']
                edge = model_result['edge']
                model_reasoning = model_result['reasoning']
                model_used = model_result.get('model_used', False)
                
                # Calculate implied probability from odds
                if odds > 0:
                    implied_probability = 100 / (odds + 100)
                else:
                    implied_probability = abs(odds) / (abs(odds) + 100)
                
                # Use model probability (from trained model or fallback)
                probability = implied_probability  # Base probability from odds
                
                # Set confidence level based on edge and model confidence
                if model_used:
                    # When using trained model, use model's confidence
                    if model_confidence > 0.70:
                        confidence = "high"
                    elif model_confidence > 0.60:
                        confidence = "medium"
                    else:
                        confidence = "low"
                else:
                    # Fallback: use edge-based confidence
                    if edge > 0.10:
                        confidence = "high"
                    elif edge > 0.05:
                        confidence = "medium"
                    else:
                        confidence = "low"
                
                # Create prediction with betting metadata
                prediction = Prediction(
                    id=f"pred_{sport}_{uuid.uuid4()}",
                    user_id=user_id,
                    sport=sport,
                    prediction_text=prediction_text,
                    confidence=confidence,
                    reasoning=f"{model_reasoning} | {home_team} vs {away_team}",
                    timestamp=datetime.utcnow(),
                    metadata_json={
                        "game_id": game_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "team": home_team,
                        "bet_type": "moneyline",
                        "line": None,
                        "odds": odds,
                        "probability": probability,
                        "model_probability": model_probability,  # What model thinks
                        "edge": edge,
                        "model_used": model_used,  # Whether trained model was used
                        "model_confidence": model_confidence,  # Model's confidence level
                        "game_date": game.get("date", datetime.utcnow().isoformat()),
                        "game_date_display": game.get("date", ""),  # For display purposes
                        "sport_key": sport_key
                    }
                )
                
                session.add(prediction)
                predictions_created += 1
                
            except Exception as e:
                print(f"   ⚠️ Error processing game: {e}")
                continue
        
        await session.commit()
    
    print(f"✅ Created {predictions_created} predictions with betting metadata")
    print()
    print("=" * 80)
    print("📊 PREDICTIONS CREATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run: python3 scripts/check_daily_picks.py")
    print("2. The autonomous betting engine should now be able to place daily picks")
    print()


async def main():
    """Main entry point."""
    try:
        await generate_predictions_with_betting_metadata()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

