#!/usr/bin/env python3
"""
Settle Remaining Bets Aggressively
===================================
Use ANY available data to find games - team names, placed_at dates, etc.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.db.database import AsyncSessionLocal
from src.services.aggressive_game_finder import aggressive_game_finder
from src.services.team_normalization import normalization_service
from sqlalchemy import text
from datetime import datetime, date, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SPORT_CODES = {
    "football": ["ncaaf", "nfl"],
    "basketball": ["ncaab", "nba", "ncaaw", "wnba"],
    "baseball": ["mlb"],
    "hockey": ["nhl"],
}

def determine_outcome_simple(bet, game):
    """Simple outcome determination."""
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
    
    # Spread - simplified, would need proper team detection
    elif bet_type == 'spread':
        # For now, skip spread bets without proper team context
        return None
    
    return None

async def settle_remaining():
    """Settle all remaining pending bets using any available data."""
    async with AsyncSessionLocal() as db:
        # Get ALL pending bets
        result = await db.execute(text("""
            SELECT id, sport, game_id, home_team, away_team, team, game_date, placed_at, bet_type, line, amount, odds
            FROM bets
            WHERE status = 'pending'
            ORDER BY placed_at
        """))
        bets = [dict(row._mapping) for row in result.fetchall()]
        
        logger.info(f"🎯 Processing {len(bets)} remaining pending bets")
        
        settled = 0
        won = 0
        lost = 0
        skipped = 0
        
        for bet in bets:
            try:
                # Determine search date - use game_date if available, otherwise placed_at
                search_date = None
                if bet.get('game_date'):
                    if isinstance(bet['game_date'], str):
                        try:
                            search_date = datetime.fromisoformat(bet['game_date'].replace('Z', '+00:00')).date()
                        except:
                            pass
                    else:
                        search_date = bet['game_date'].date() if hasattr(bet['game_date'], 'date') else bet['game_date']
                
                if not search_date and bet.get('placed_at'):
                    # Use placed_at as fallback
                    if isinstance(bet['placed_at'], str):
                        try:
                            search_date = datetime.fromisoformat(bet['placed_at'].replace('Z', '+00:00')).date()
                        except:
                            pass
                    else:
                        search_date = bet['placed_at'].date() if hasattr(bet['placed_at'], 'date') else bet['placed_at']
                
                if not search_date:
                    logger.debug(f"⚠️ No date for bet {bet['id'][:8]}...")
                    skipped += 1
                    continue
                
                # Get team to search for - handle over/under cases
                search_team = bet.get('team') or bet.get('home_team') or bet.get('away_team')
                bet_type = bet.get('bet_type', '').lower()
                
                # For over/under, the "team" field might be "Over" or "Under" 
                # Try to extract actual team name if possible, or use home/away teams
                if bet_type in ['over_under', 'total']:
                    team_lower = (search_team or '').lower()
                    if team_lower in ['over', 'under', 'o', 'u']:
                        # Use home/away teams instead
                        search_team = bet.get('home_team') or bet.get('away_team')
                
                if not search_team:
                    logger.debug(f"⚠️ No team for bet {bet['id'][:8]}...")
                    skipped += 1
                    continue
                
                # Try to find game - search more broadly
                sport = bet.get('sport', '').lower()
                
                # First try with the search team
                game = await aggressive_game_finder.find_game_by_teams_and_date(
                    search_team,
                    None,
                    search_date,
                    sport
                )
                
                # If we have home/away teams, try those too
                if not game and bet.get('home_team') and bet.get('away_team'):
                    game = await aggressive_game_finder.find_game_by_teams_and_date(
                        bet.get('home_team'),
                        bet.get('away_team'),
                        search_date,
                        sport
                    )
                
                if not game:
                    # Try a few days around the placed_at date
                    for day_offset in [-1, 1, -2, 2]:
                        try:
                            alt_date = search_date + timedelta(days=day_offset)
                            game = await aggressive_game_finder.find_game_by_teams_and_date(
                                search_team, None, alt_date, sport
                            )
                            if game:
                                logger.info(f"✅ Found game on {alt_date} (offset {day_offset} days)")
                                break
                        except:
                            continue
                
                if not game:
                    logger.debug(f"⚠️ Game not found for {search_team} on {search_date}")
                    skipped += 1
                    continue
                
                # Check if final
                status = game.get('status', '').lower()
                has_scores = game.get('home_score', 0) > 0 or game.get('away_score', 0) > 0
                if 'final' not in status and 'finished' not in status and not has_scores:
                    logger.debug(f"⏳ Game not final: {status}")
                    skipped += 1
                    continue
                
                # Determine outcome
                outcome = determine_outcome_simple(bet, game)
                if not outcome:
                    logger.debug(f"⚠️ Could not determine outcome for bet {bet['id'][:8]}...")
                    skipped += 1
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
                    logger.info(f"✅ WON: {bet['id'][:8]}... | {search_team} on {search_date}")
                else:
                    await db.execute(text("""
                        UPDATE bets SET status=:status, settled_at=:now, payout=0, roi=-100
                        WHERE id=:id
                    """), {"status": outcome, "now": datetime.now(), "id": bet['id']})
                    lost += 1
                    logger.info(f"❌ {outcome.upper()}: {bet['id'][:8]}... | {search_team} on {search_date}")
                
                await db.commit()
                settled += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing bet {bet.get('id', 'unknown')[:8]}...: {e}")
                skipped += 1
                continue
        
        logger.info(f"\n📊 FINAL RESULTS:")
        logger.info(f"   ✅ Settled: {settled} ({won} won, {lost} lost)")
        logger.info(f"   ⏭️  Skipped: {skipped}")

if __name__ == "__main__":
    asyncio.run(settle_remaining())

