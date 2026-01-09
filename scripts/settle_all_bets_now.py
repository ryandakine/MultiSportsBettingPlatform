#!/usr/bin/env python3
"""
Settle ALL Pending Bets Right Now
==================================
Direct, fast settlement of all pending bets.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.db.database import AsyncSessionLocal
from src.services.historical_game_scraper import historical_game_scraper
from src.services.real_sports_service import real_sports_service
from src.services.team_normalization import normalization_service
from src.services.aggressive_game_finder import aggressive_game_finder
from sqlalchemy import text
from datetime import datetime, timedelta, date
from typing import Optional
import logging

SPORT_MAPPING = {
    "football": ["ncaaf", "nfl"],  # Try college first
    "basketball": ["ncaab", "nba"],
    "baseball": ["mlb"],
    "hockey": ["nhl"],
}

def determine_outcome(bet, game):
    """Determine bet outcome."""
    home_score = game.get('home_score', 0)
    away_score = game.get('away_score', 0)
    bet_type = bet.get('bet_type', '').lower()
    line = bet.get('line')
    bet_team = (bet.get('team') or '').lower()
    
    # Moneyline
    if bet_type == 'moneyline':
        home_team = game.get('home_team', '')
        away_team = game.get('away_team', '')
        bet_team_norm = normalization_service.normalize_name(bet.get('team', ''))
        home_norm = normalization_service.normalize_name(home_team)
        away_norm = normalization_service.normalize_name(away_team)
        
        is_home = bet_team_norm in home_norm
        is_away = bet_team_norm in away_norm
        
        if (is_home and home_score > away_score) or (is_away and away_score > home_score):
            return "won"
        return "lost"
    
    # Spread
    elif bet_type == 'spread':
        if line is None:
            return None
        # Simplified - would need proper team detection
        return None
    
    # Over/Under
    elif bet_type in ['over_under', 'total']:
        if line is None:
            return None
        total = home_score + away_score
        is_over = 'over' in bet_team or 'o ' in bet_team
        
        if total == line:
            return "pushed"
        elif (is_over and total > line) or (not is_over and total < line):
            return "won"
        return "lost"
    
    return None

async def find_game(bet, games, bet_date, sport):
    """Find matching game - try multiple strategies."""
    game_id = bet.get('game_id')
    home_team = bet.get('home_team')
    away_team = bet.get('away_team')
    bet_team = bet.get('team')
    
    # Strategy 1: Try game ID in provided games list
    if game_id and game_id.isdigit():
        for game in games:
            if str(game.get('id', '')) == str(game_id):
                return game
    
    # Strategy 2: Try team names in provided games list
    if home_team and away_team:
        home_norm = normalization_service.normalize_name(home_team)
        away_norm = normalization_service.normalize_name(away_team)
        for game in games:
            game_home = normalization_service.normalize_name(game.get('home_team', ''))
            game_away = normalization_service.normalize_name(game.get('away_team', ''))
            if (home_norm in game_home and away_norm in game_away) or (home_norm in game_away and away_norm in game_home):
                return game
    
    # Strategy 3: Aggressive search by team names + date
    if bet_team or home_team or away_team:
        search_team1 = bet_team or home_team or away_team
        search_team2 = away_team if home_team and away_team and search_team1 == home_team else None
        
        found_game = await aggressive_game_finder.find_game_by_teams_and_date(
            search_team1, search_team2, bet_date, sport
        )
        if found_game:
            return found_game
    
    return None

async def settle_all():
    """Settle all pending bets."""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    async with AsyncSessionLocal() as db:
        # Get all pending bets with dates
        result = await db.execute(text("""
            SELECT id, sport, game_id, home_team, away_team, team, game_date, bet_type, line, amount, odds
            FROM bets
            WHERE status = 'pending' AND game_date IS NOT NULL
            ORDER BY game_date
        """))
        bets = [dict(row._mapping) for row in result.fetchall()]
        
        logger.info(f"🎯 Found {len(bets)} pending bets with dates")
        
        settled = 0
        won = 0
        lost = 0
        
        # Group by date and sport
        by_date_sport = {}
        for bet in bets:
            if isinstance(bet['game_date'], str):
                try:
                    d = datetime.fromisoformat(bet['game_date'].replace('Z', '+00:00')).date()
                except:
                    continue
            else:
                d = bet['game_date'].date() if hasattr(bet['game_date'], 'date') else bet['game_date']
            
            sport = bet['sport'].lower()
            key = (d, sport)
            if key not in by_date_sport:
                by_date_sport[key] = []
            by_date_sport[key].append(bet)
        
        # Process each date/sport combo
        for (bet_date, sport), date_bets in by_date_sport.items():
            logger.info(f"📅 Processing {len(date_bets)} bets for {sport} on {bet_date}")
            
            # Try sport codes
            sport_codes = SPORT_MAPPING.get(sport, [sport])
            games = []
            
            for sport_code in sport_codes:
                days_old = (date.today() - bet_date).days
                try:
                    if days_old > 2:
                        games = await historical_game_scraper.get_historical_games(sport_code, bet_date)
                    else:
                        games = await real_sports_service.get_live_games(sport_code, date=bet_date)
                    
                    if games:
                        logger.info(f"✅ Found {len(games)} games using {sport_code}")
                        break
                except Exception as e:
                    logger.debug(f"Error fetching {sport_code}: {e}")
                    continue
            
            if not games:
                logger.warning(f"⚠️ No games found for {sport} on {bet_date}")
                continue
            
            # Settle each bet
            for bet in date_bets:
                # Parse bet date
                if isinstance(bet['game_date'], str):
                    try:
                        bet_date = datetime.fromisoformat(bet['game_date'].replace('Z', '+00:00')).date()
                    except:
                        bet_date = date.today()
                else:
                    bet_date = bet['game_date'].date() if hasattr(bet['game_date'], 'date') else bet['game_date']
                
                # Try finding game in fetched games first
                game = await find_game(bet, games, bet_date, sport)
                if not game:
                    continue
                
                # Check if final
                status = game.get('status', '').lower()
                has_scores = game.get('home_score', 0) > 0 or game.get('away_score', 0) > 0
                if 'final' not in status and 'finished' not in status and not has_scores:
                    continue
                
                # Determine outcome
                outcome = determine_outcome(bet, game)
                if not outcome:
                    continue
                
                # Update bet
                if outcome == "won":
                    amount = bet['amount']
                    odds = bet['odds']
                    if odds > 0:
                        payout = round(amount * (1 + odds / 100), 2)
                    else:
                        payout = round(amount * (1 + 100 / abs(odds)), 2)
                    roi = round(((payout - amount) / amount) * 100, 2)
                    
                    await db.execute(text("""
                        UPDATE bets SET status='won', settled_at=:now, payout=:payout, roi=:roi
                        WHERE id=:id
                    """), {"now": datetime.now(), "payout": payout, "roi": roi, "id": bet['id']})
                    won += 1
                else:
                    await db.execute(text("""
                        UPDATE bets SET status=:status, settled_at=:now, payout=0, roi=-100
                        WHERE id=:id
                    """), {"status": outcome, "now": datetime.now(), "id": bet['id']})
                    lost += 1
                
                await db.commit()
                settled += 1
                logger.info(f"✅ Settled bet {bet['id'][:8]}... - {outcome.upper()}")
        
        logger.info(f"\n📊 FINAL: Settled {settled} bets ({won} won, {lost} lost)")

if __name__ == "__main__":
    asyncio.run(settle_all())

