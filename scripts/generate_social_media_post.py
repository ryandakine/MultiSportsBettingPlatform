#!/usr/bin/env python3
"""
Generate Social Media Posts
============================
Generate formatted posts for Twitter/Discord from today's picks and parlays.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime
from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetType
from src.services.parlay_tracker import parlay_tracker
from src.services.social_media_formatter import social_media_formatter
from sqlalchemy import select, and_


async def generate_social_media_posts():
    """Generate social media posts from today's picks."""
    user_id = "demo_user"
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print("=" * 80)
    print("📱 GENERATING SOCIAL MEDIA POSTS")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as session:
        # Get today's single bet (daily pick)
        result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type != BetType.PARLAY
                )
            ).order_by(Bet.placed_at.desc())
        )
        daily_picks = result.scalars().all()
        
        # Get today's parlays
        parlay_result = await session.execute(
            select(Bet).where(
                and_(
                    Bet.user_id == user_id,
                    Bet.placed_at >= today_start,
                    Bet.bet_type == BetType.PARLAY
                )
            ).order_by(Bet.placed_at.desc())
        )
        parlays = parlay_result.scalars().all()
        
        if not daily_picks:
            print("❌ No daily picks found for today")
            return
        
        if not parlays:
            print("❌ No parlays found for today")
            return
        
        # Get first daily pick (or best one)
        best_pick = daily_picks[0]
        daily_pick_dict = {
            "team": best_pick.team,
            "sport": best_pick.sport,
            "odds": best_pick.odds,
            "bet_type": best_pick.bet_type.value,
            "line": best_pick.line,
            "game_date": best_pick.game_date
        }
        
        # Find 3-leg and 6-leg parlays
        three_leg_parlay = None
        six_leg_parlay = None
        
        for parlay_bet in parlays:
            legs = await parlay_tracker.get_parlay_legs(parlay_bet.id)
            num_legs = len(legs)
            
            if num_legs == 3 and not three_leg_parlay:
                three_leg_parlay = {
                    "legs": legs,
                    "combined_odds": parlay_bet.odds,
                    "amount": parlay_bet.amount
                }
            elif num_legs == 6 and not six_leg_parlay:
                six_leg_parlay = {
                    "legs": legs,
                    "combined_odds": parlay_bet.odds,
                    "amount": parlay_bet.amount
                }
            
            if three_leg_parlay and six_leg_parlay:
                break
        
        if not three_leg_parlay:
            print("⚠️ No 3-leg parlay found for today")
            return
        
        if not six_leg_parlay:
            print("⚠️ No 6-leg parlay found for today")
            return
        
        # Generate posts
        print("📝 Generating formatted posts...\n")
        
        # Twitter format
        twitter_posts = social_media_formatter.format_daily_post(
            daily_pick_dict,
            three_leg_parlay,
            six_leg_parlay,
            platform="twitter"
        )
        
        print("🐦 TWITTER POSTS:")
        print("-" * 80)
        for i, (key, post) in enumerate(twitter_posts.items(), 1):
            print(f"\nTweet {i}:")
            print(post)
            print(f"\nCharacter count: {len(post)}")
        print("\n" + "=" * 80)
        
        # Discord format
        discord_post = social_media_formatter.format_daily_post(
            daily_pick_dict,
            three_leg_parlay,
            six_leg_parlay,
            platform="discord"
        )
        
        print("\n💬 DISCORD POST:")
        print("-" * 80)
        print(discord_post.get("discord", ""))
        print("\n" + "=" * 80)
        
        # Save to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"social_media_post_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("SOCIAL MEDIA POSTS\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("TWITTER POSTS:\n")
            f.write("-" * 80 + "\n")
            for i, (key, post) in enumerate(twitter_posts.items(), 1):
                f.write(f"\nTweet {i}:\n")
                f.write(post + "\n")
                f.write(f"\nCharacter count: {len(post)}\n\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
            f.write("DISCORD POST:\n")
            f.write("-" * 80 + "\n")
            f.write(discord_post.get("discord", "") + "\n")
        
        print(f"\n✅ Posts saved to: {filename}")


if __name__ == "__main__":
    asyncio.run(generate_social_media_posts())

