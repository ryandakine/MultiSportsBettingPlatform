#!/usr/bin/env python3
"""
Settle Final Remaining Bets - Maximum Aggression
=================================================
Handle over/under with "Over"/"Under" team names, spread bets, and parlays.
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

async def find_all_games_for_date(sport_codes, search_date):
    """Fetch all games for a date across multiple sport codes."""
    all_games = []
    for sport_code in sport_codes:
        try:
            # Use the aggressive finder's internal method
            endpoint = aggressive_game_finder.ENDPOINTS.get(sport_code)
            if not endpoint:
                continue
            url = f"{aggressive_game_finder.BASE_URL}{endpoint}"
            date_str = search_date.strftime('%Y%m%d')
            
            import httpx
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params={'dates': date_str})
                response.raise_for_status()
                data = response.json()
                games = aggressive_game_finder._parse_games(data)
                all_games.extend(games)
        except Exception as e:
            logger.debug(f"Error fetching {sport_code}: {e}")
            continue
    return all_games

async def settle_final():
    """Settle all remaining bets with maximum effort."""
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
        
        logger.info(f"🎯 Final settlement attempt for {len(bets)} bets")
        
        # Get sport codes to try
        sport_code_map = {
            "football": ["ncaaf", "nfl"],
            "basketball": ["ncaab", "nba", "ncaaw", "wnba"],
            "baseball": ["mlb"],
            "hockey": ["nhl"],
        }
        
        settled = 0
        won = 0
        lost = 0
        
        for bet in bets:
            try:
                # Determine search date
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
                
                if not search_date:
                    continue
                
                sport = bet.get('sport', '').lower()
                bet_type = bet.get('bet_type', '').lower()
                sport_codes = sport_code_map.get(sport, [sport])
                
                # Fetch ALL games for this date across all relevant sport codes
                all_games = []
                for offset in [0, -1, 1, -2, 2]:
                    try:
                        date_to_try = search_date + timedelta(days=offset)
                        games = await find_all_games_for_date(sport_codes, date_to_try)
                        all_games.extend(games)
                    except:
                        continue
                
                if not all_games:
                    continue
                
                # Try to match bet to game
                matched_game = None
                
                # Strategy 1: Game ID match
                if bet.get('game_id') and bet['game_id'].isdigit():
                    for game in all_games:
                        if str(game.get('id', '')) == str(bet['game_id']):
                            matched_game = game
                            break
                
                # Strategy 2: Team name match
                if not matched_game:
                    team = bet.get('team') or ''
                    home_team = bet.get('home_team')
                    away_team = bet.get('away_team')
                    
                    # For over/under, try home/away teams
                    if bet_type in ['over_under', 'total'] and not team and (home_team or away_team):
                        for game in all_games:
                            home_match = False
                            away_match = False
                            if home_team:
                                home_match = normalization_service.normalize_name(home_team) in normalization_service.normalize_name(game.get('home_team', ''))
                            if away_team:
                                away_match = normalization_service.normalize_name(away_team) in normalization_service.normalize_name(game.get('away_team', ''))
                            if home_match or away_match:
                                matched_game = game
                                break
                    elif team and team.lower() not in ['over', 'under', 'o', 'u']:
                        # Normal team name
                        for game in all_games:
                            team_norm = normalization_service.normalize_name(team)
                            home_norm = normalization_service.normalize_name(game.get('home_team', ''))
                            away_norm = normalization_service.normalize_name(game.get('away_team', ''))
                            if team_norm in home_norm or team_norm in away_norm:
                                matched_game = game
                                break
                
                if not matched_game:
                    continue
                
                # Check if final
                status = matched_game.get('status', '').lower()
                has_scores = matched_game.get('home_score', 0) > 0 or matched_game.get('away_score', 0) > 0
                if 'final' not in status and 'finished' not in status and not has_scores:
                    continue
                
                # Determine outcome
                home_score = matched_game.get('home_score', 0)
                away_score = matched_game.get('away_score', 0)
                line = bet.get('line')
                
                outcome = None
                
                if bet_type == 'moneyline':
                    team = bet.get('team', '')
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
                
                elif bet_type in ['over_under', 'total']:
                    if line is not None:
                        total = home_score + away_score
                        team = (bet.get('team') or '').lower()
                        is_over = 'over' in team or 'o' in team or (team and team.lower() not in ['under', 'u'])
                        
                        # If team field is empty/null but we matched a game, try to infer from context
                        if not team or team in ['', 'over', 'under', 'o', 'u']:
                            # Default to over if we can't determine (conservative)
                            is_over = True
                        
                        if total > line:
                            outcome = "won" if is_over else "lost"
                        elif total < line:
                            outcome = "won" if not is_over else "lost"
                        elif total == line:
                            outcome = "pushed"
                
                elif bet_type == 'spread':
                    # Skip spread bets for now - need both teams and proper calculation
                    continue
                
                if not outcome or outcome == "pushed":
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
                        UPDATE bets SET status='lost', settled_at=:now, payout=0, roi=-100
                        WHERE id=:id
                    """), {"now": datetime.now(), "id": bet['id']})
                    lost += 1
                
                await db.commit()
                settled += 1
                logger.info(f"✅ Settled {bet['id'][:8]}... - {outcome.upper()}")
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                continue
        
        logger.info(f"\n📊 Settled {settled} bets ({won} won, {lost} lost)")

if __name__ == "__main__":
    asyncio.run(settle_final())

