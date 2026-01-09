#!/usr/bin/env python3
"""
Settle EVERYTHING - Comprehensive Settlement
============================================
Handle spread bets, parlays, and all edge cases. Be better than everyone else.
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

async def fetch_all_games_for_date_range(sport_codes, start_date, days_range=5):
    """Fetch all games in a date range."""
    all_games = {}
    for offset in range(-days_range, days_range + 1):
        check_date = start_date + timedelta(days=offset)
        for sport_code in sport_codes:
            try:
                endpoint = aggressive_game_finder.ENDPOINTS.get(sport_code)
                if not endpoint:
                    continue
                url = f"{aggressive_game_finder.BASE_URL}{endpoint}"
                date_str = check_date.strftime('%Y%m%d')
                
                import httpx
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(url, params={'dates': date_str})
                    if response.status_code == 200:
                        data = response.json()
                        games = aggressive_game_finder._parse_games(data)
                        for game in games:
                            game_id = str(game.get('id', ''))
                            if game_id not in all_games:
                                all_games[game_id] = game
                                all_games[game_id]['_sport'] = sport_code
                                all_games[game_id]['_date'] = check_date
            except Exception as e:
                logger.debug(f"Error fetching {sport_code} on {check_date}: {e}")
                continue
    return list(all_games.values())

def calculate_spread_outcome(bet_team, home_team, away_team, home_score, away_score, line):
    """Calculate spread bet outcome."""
    if line is None:
        return None
    
    bet_team_norm = normalization_service.normalize_name(bet_team)
    home_norm = normalization_service.normalize_name(home_team)
    away_norm = normalization_service.normalize_name(away_team)
    
    is_home_bet = bet_team_norm in home_norm
    is_away_bet = bet_team_norm in away_norm
    
    if not is_home_bet and not is_away_bet:
        return None
    
    home_margin = home_score - away_score
    
    if is_home_bet:
        # Home team needs to win by more than the spread
        if home_margin > line:
            return "won"
        elif home_margin == line:
            return "pushed"
        else:
            return "lost"
    else:  # away bet
        # Away team spread: line is typically negative (e.g., -3.5 means they're favored by 3.5)
        # If line is negative, away team needs to lose by less than |line| or win
        away_margin = away_score - home_score
        if line < 0:
            # Away team favored
            if away_margin > abs(line) or (away_margin == abs(line) and away_margin > 0):
                return "won"
            elif away_margin == abs(line):
                return "pushed"
            else:
                return "lost"
        else:
            # Away team underdog
            if away_margin > line:
                return "won"
            elif away_margin == line:
                return "pushed"
            else:
                return "lost"

async def settle_comprehensive():
    """Settle ALL remaining bets with comprehensive logic."""
    async with AsyncSessionLocal() as db:
        # Get ALL pending bets
        result = await db.execute(text("""
            SELECT id, sport, game_id, home_team, away_team, team, game_date, placed_at, 
                   bet_type, line, amount, odds
            FROM bets
            WHERE status = 'pending'
            ORDER BY placed_at
        """))
        bets = [dict(row._mapping) for row in result.fetchall()]
        
        logger.info(f"🎯 Comprehensive settlement for {len(bets)} remaining bets")
        
        sport_code_map = {
            "football": ["ncaaf", "nfl"],
            "basketball": ["ncaab", "nba", "ncaaw", "wnba"],
            "baseball": ["mlb"],
            "hockey": ["nhl"],
        }
        
        settled = 0
        won = 0
        lost = 0
        pushed = 0
        
        # Process bets in batches by date to optimize API calls
        bets_by_date = {}
        for bet in bets:
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
                if isinstance(bet['placed_at'], str):
                    try:
                        search_date = datetime.fromisoformat(bet['placed_at'].replace('Z', '+00:00')).date()
                    except:
                        pass
                else:
                    search_date = bet['placed_at'].date() if hasattr(bet['placed_at'], 'date') else bet['placed_at']
            
            if search_date:
                if search_date not in bets_by_date:
                    bets_by_date[search_date] = []
                bets_by_date[search_date].append(bet)
        
        # Process each date batch
        for search_date, date_bets in bets_by_date.items():
            logger.info(f"📅 Processing {len(date_bets)} bets for {search_date}")
            
            # Get all sports involved
            sports_involved = set(bet.get('sport', '').lower() for bet in date_bets)
            all_sport_codes = []
            for sport in sports_involved:
                all_sport_codes.extend(sport_code_map.get(sport, [sport]))
            
            # Fetch all games for this date range (more aggressively)
            all_games = await fetch_all_games_for_date_range(all_sport_codes, search_date, days_range=3)
            logger.info(f"✅ Loaded {len(all_games)} games for date range around {search_date}")
            
            # Process each bet
            for bet in date_bets:
                try:
                    sport = bet.get('sport', '').lower()
                    bet_type = bet.get('bet_type', '').lower()
                    game_id = bet.get('game_id')
                    
                    # Find matching game
                    matched_game = None
                    
                    # Try game ID first
                    if game_id and game_id.isdigit():
                        for game in all_games:
                            if str(game.get('id', '')) == str(game_id):
                                matched_game = game
                                break
                    
                    # Try team matching
                    if not matched_game:
                        team = bet.get('team') or ''
                        home_team = bet.get('home_team')
                        away_team = bet.get('away_team')
                        
                        # For over/under, try home/away teams
                        if bet_type in ['over_under', 'total']:
                            search_teams = [h for h in [home_team, away_team] if h]
                        else:
                            search_teams = [t for t in [team, home_team, away_team] if t and t.lower() not in ['over', 'under', 'o', 'u']]
                        
                        for search_team in search_teams:
                            if not search_team:
                                continue
                            for game in all_games:
                                team_norm = normalization_service.normalize_name(search_team)
                                home_norm = normalization_service.normalize_name(game.get('home_team', ''))
                                away_norm = normalization_service.normalize_name(game.get('away_team', ''))
                                
                                if team_norm in home_norm or team_norm in away_norm:
                                    matched_game = game
                                    break
                            if matched_game:
                                break
                    
                    if not matched_game:
                        logger.debug(f"⚠️ No game match for {bet['id'][:8]}...")
                        continue
                    
                    # Check if final
                    status = matched_game.get('status', '').lower()
                    has_scores = matched_game.get('home_score', 0) > 0 or matched_game.get('away_score', 0) > 0
                    if 'final' not in status and 'finished' not in status and not has_scores:
                        logger.debug(f"⏳ Game not final: {status}")
                        continue
                    
                    # Determine outcome based on bet type
                    home_score = matched_game.get('home_score', 0)
                    away_score = matched_game.get('away_score', 0)
                    line = bet.get('line')
                    team = bet.get('team') or ''
                    
                    outcome = None
                    
                    if bet_type == 'moneyline':
                        if team:
                            team_norm = normalization_service.normalize_name(team)
                            home_norm = normalization_service.normalize_name(matched_game.get('home_team', ''))
                            away_norm = normalization_service.normalize_name(matched_game.get('away_team', ''))
                            
                            is_home = team_norm in home_norm
                            is_away = team_norm in away_norm
                            
                            if (is_home and home_score > away_score) or (is_away and away_score > home_score):
                                outcome = "won"
                            else:
                                outcome = "lost"
                    
                    elif bet_type == 'spread':
                        if team and line is not None:
                            outcome = calculate_spread_outcome(
                                team,
                                matched_game.get('home_team', ''),
                                matched_game.get('away_team', ''),
                                home_score,
                                away_score,
                                line
                            )
                    
                    elif bet_type in ['over_under', 'total']:
                        if line is not None:
                            total = home_score + away_score
                            team_lower = team.lower() if team else ''
                            
                            # Determine over/under direction
                            if 'under' in team_lower or team_lower == 'u':
                                is_over = False
                            elif 'over' in team_lower or team_lower == 'o':
                                is_over = True
                            else:
                                # Default to over if unclear (conservative)
                                is_over = True
                            
                            if total > line:
                                outcome = "won" if is_over else "lost"
                            elif total < line:
                                outcome = "won" if not is_over else "lost"
                            elif total == line:
                                outcome = "pushed"
                    
                    if not outcome:
                        logger.debug(f"⚠️ Could not determine outcome for {bet['id'][:8]}...")
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
                        logger.info(f"✅ WON: {bet['id'][:8]}... | {team} | {bet_type}")
                    
                    elif outcome == "pushed":
                        await db.execute(text("""
                            UPDATE bets SET status='pushed', settled_at=:now, payout=:amount, roi=0
                            WHERE id=:id
                        """), {"now": datetime.now(), "amount": bet['amount'], "id": bet['id']})
                        pushed += 1
                        logger.info(f"🔄 PUSHED: {bet['id'][:8]}... | {team} | {bet_type}")
                    
                    else:
                        await db.execute(text("""
                            UPDATE bets SET status='lost', settled_at=:now, payout=0, roi=-100
                            WHERE id=:id
                        """), {"now": datetime.now(), "id": bet['id']})
                        lost += 1
                        logger.info(f"❌ LOST: {bet['id'][:8]}... | {team} | {bet_type}")
                    
                    await db.commit()
                    settled += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {bet.get('id', 'unknown')[:8]}...: {e}")
                    continue
        
        logger.info(f"\n📊 COMPREHENSIVE SETTLEMENT COMPLETE:")
        logger.info(f"   ✅ Settled: {settled} bets")
        logger.info(f"   🏆 Won: {won}")
        logger.info(f"   ❌ Lost: {lost}")
        logger.info(f"   🔄 Pushed: {pushed}")

if __name__ == "__main__":
    asyncio.run(settle_comprehensive())


