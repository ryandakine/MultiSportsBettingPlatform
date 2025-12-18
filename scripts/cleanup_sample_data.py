#!/usr/bin/env python3
"""
Cleanup Sample Data Script
===========================
Remove all sample/test predictions from the database.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from sqlalchemy import select, or_, and_
from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction
from datetime import datetime, timedelta


async def cleanup_sample_predictions():
    """Remove sample/test predictions from database."""
    
    async with AsyncSessionLocal() as session:
        # Identify sample predictions - these are the ones from seed_betting_predictions.py
        # They have specific game_ids like "game_nfl_001", "game_nba_001", etc.
        sample_game_ids = [
            "game_nfl_001", "game_nfl_002", "game_nfl_003",
            "game_nba_001", "game_nba_002", "game_nba_003",
            "game_nhl_001", "game_nhl_002",
            "game_mlb_001", "game_mlb_002"
        ]
        
        # Also look for predictions with sample team names from seed script
        sample_teams = [
            "Kansas City Chiefs", "Buffalo Bills", "Philadelphia Eagles", "Dallas Cowboys",
            "Cincinnati Bengals", "Pittsburgh Steelers",
            "Los Angeles Lakers", "Golden State Warriors", "Boston Celtics", "Miami Heat",
            "Phoenix Suns", "Warriors",
            "Boston Bruins", "Toronto Maple Leafs", "Colorado Avalanche", "Edmonton Oilers",
            "New York Yankees", "Boston Red Sox", "Los Angeles Dodgers", "San Francisco Giants"
        ]
        
        # Find predictions to delete
        result = await session.execute(
            select(Prediction)
        )
        all_predictions = result.scalars().all()
        
        predictions_to_delete = []
        for pred in all_predictions:
            metadata = pred.metadata_json or {}
            game_id = metadata.get("game_id", "")
            home_team = metadata.get("home_team", "")
            away_team = metadata.get("away_team", "")
            team = metadata.get("team", "")
            
            # Check if this is a sample prediction
            is_sample = False
            
            # Check game_id
            if any(sample_id in game_id for sample_id in sample_game_ids):
                is_sample = True
            
            # Check team names
            if any(sample_team in home_team or sample_team in away_team or sample_team in team 
                   for sample_team in sample_teams if sample_team):
                # Double check - make sure it's not a real game
                # Real games wouldn't have these exact combinations
                if "Kansas City Chiefs" in home_team and "Buffalo Bills" in away_team:
                    is_sample = True
                elif "Los Angeles Lakers" in home_team and "Golden State Warriors" in away_team:
                    is_sample = True
                elif "Boston Celtics" in home_team and "Miami Heat" in away_team:
                    is_sample = True
                elif "Boston Bruins" in home_team and "Toronto Maple Leafs" in away_team:
                    is_sample = True
                elif "New York Yankees" in home_team and "Boston Red Sox" in away_team:
                    is_sample = True
            
            if is_sample:
                predictions_to_delete.append(pred)
        
        if not predictions_to_delete:
            print("✅ No sample predictions found in database")
            return
        
        print(f"🗑️  Found {len(predictions_to_delete)} sample prediction(s) to delete:")
        for pred in predictions_to_delete:
            metadata = pred.metadata_json or {}
            print(f"   - {pred.sport}: {metadata.get('home_team', 'N/A')} vs {metadata.get('away_team', 'N/A')}")
            print(f"     ID: {pred.id}")
            print(f"     Created: {pred.timestamp}")
        
        # Delete them
        for pred in predictions_to_delete:
            await session.delete(pred)
        
        await session.commit()
        print()
        print(f"✅ Deleted {len(predictions_to_delete)} sample prediction(s)")


async def main():
    """Main entry point."""
    try:
        await cleanup_sample_predictions()
        print()
        print("🎯 Sample data cleanup complete!")
    except Exception as e:
        print(f"❌ Error cleaning up sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

