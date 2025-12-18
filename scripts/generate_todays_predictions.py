#!/usr/bin/env python3
"""
Generate Today's Predictions Script
====================================
Generate predictions for today's real games using the head agent.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime
from src.services.real_sports_service import RealSportsService
from src.api.routes import head_agent, initialize_sub_agents
from src.agents.head_agent import UserQuery, SportType


async def generate_predictions_for_todays_games():
    """Generate predictions for today's real games."""
    
    print("=" * 80)
    print("🎯 GENERATING PREDICTIONS FOR TODAY'S GAMES")
    print("=" * 80)
    print()
    
    # Initialize sub-agents if needed
    try:
        await initialize_sub_agents()
        print("✅ Sub-agents initialized")
    except Exception as e:
        print(f"⚠️ Sub-agent initialization: {e}")
    
    real_sports = RealSportsService()
    
    # Sports to check
    sports_config = {
        "ncaaf": {
            "name": "College Football",
            "sport_type": SportType.FOOTBALL,
            "query": "What are the best betting opportunities for today's college football games?"
        },
        "nhl": {
            "name": "NHL Hockey",
            "sport_type": SportType.HOCKEY,
            "query": "What are the best betting opportunities for today's NHL games?"
        },
        "ncaab": {
            "name": "College Basketball",
            "sport_type": SportType.BASKETBALL,
            "query": "What are the best betting opportunities for today's college basketball games?"
        }
    }
    
    all_predictions = {}
    
    for sport_code, config in sports_config.items():
        print()
        print(f"{'='*80}")
        print(f"🏈 {config['name']} ({sport_code.upper()})")
        print(f"{'='*80}")
        
        # Get today's games
        try:
            games = await real_sports.get_live_games(sport_code)
            
            if not games:
                print(f"  ⚠️ No games found for {config['name']} today")
                continue
            
            print(f"  ✅ Found {len(games)} game(s) today")
            print()
            
            # Generate predictions for each game
            game_predictions = []
            for game in games[:10]:  # Limit to first 10 games
                home_team = game.get("home_team", "TBD")
                away_team = game.get("away_team", "TBD")
                game_id = game.get("game_id", f"{sport_code}_{home_team}_{away_team}")
                status = game.get("status", "scheduled")
                
                if status not in ["scheduled", "preview"]:
                    print(f"  ⏭️ Skipping {away_team} @ {home_team} (status: {status})")
                    continue
                
                print(f"  🎯 Generating prediction for: {away_team} @ {home_team}")
                
                try:
                    # Create user query
                    user_query = UserQuery(
                        user_id="system",
                        sports=[config['sport_type']],
                        query_text=f"{config['query']} Specifically: {away_team} @ {home_team}",
                        preferences={"autonomous": True},
                        timestamp=datetime.now()
                    )
                    
                    # Get prediction from head agent
                    result = await head_agent.aggregate_predictions(user_query)
                    
                    if "error" in result:
                        print(f"     ❌ Error: {result['error']}")
                        continue
                    
                    # Extract prediction
                    if config['sport_type'].value in result.get("predictions", {}):
                        pred_data = result["predictions"][config['sport_type'].value]
                        
                        if "error" not in pred_data:
                            print(f"     ✅ Prediction generated")
                            print(f"        Recommendation: {pred_data.get('prediction', 'N/A')}")
                            print(f"        Confidence: {pred_data.get('confidence', 'N/A')}")
                            
                            game_predictions.append({
                                "game": f"{away_team} @ {home_team}",
                                "game_id": game_id,
                                "home_team": home_team,
                                "away_team": away_team,
                                "prediction": pred_data,
                                "odds": game.get("odds", {}),
                                "status": status
                            })
                        else:
                            print(f"     ⚠️ Prediction error: {pred_data.get('error')}")
                    else:
                        print(f"     ⚠️ No prediction returned for this sport")
                    
                except Exception as e:
                    print(f"     ❌ Error generating prediction: {e}")
                    import traceback
                    traceback.print_exc()
            
            all_predictions[sport_code] = {
                "name": config['name'],
                "games": game_predictions,
                "total_games": len(games),
                "predictions_generated": len(game_predictions)
            }
            
            print()
            print(f"  📊 Summary: Generated {len(game_predictions)} predictions from {len(games)} games")
            
        except Exception as e:
            print(f"  ❌ Error processing {config['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print()
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    for sport_code, data in all_predictions.items():
        print(f"{data['name']}:")
        print(f"  Total games today: {data['total_games']}")
        print(f"  Predictions generated: {data['predictions_generated']}")
        if data['games']:
            print(f"  Games with predictions:")
            for game_pred in data['games']:
                print(f"    - {game_pred['game']}")
        print()


async def main():
    """Main entry point."""
    try:
        await generate_predictions_for_todays_games()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

