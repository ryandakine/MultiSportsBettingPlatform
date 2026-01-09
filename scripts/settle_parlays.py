#!/usr/bin/env python3
"""
Settle Parlay Bets
==================
Settle parlay bets by checking all legs and determining if the parlay won/lost.
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

async def settle_leg(leg, all_games):
    """Settle a single parlay leg."""
    sport = leg.get('sport', '').lower()
    bet_type = leg.get('bet_type', '').lower()
    game_id = leg.get('game_id')
    home_team = leg.get('home_team')
    away_team = leg.get('away_team')
    team = leg.get('team')
    line = leg.get('line')
    
    # Find matching game
    matched_game = None
    
    # Try game ID
    if game_id and game_id.isdigit():
        for game in all_games:
            if str(game.get('id', '')) == str(game_id):
                matched_game = game
                break
    
    # Try team matching
    if not matched_game:
        search_teams = []
        if home_team and away_team:
            search_teams = [home_team, away_team]
        elif team and team.lower() not in ['over', 'under', 'o', 'u']:
            search_teams = [team]
        
        for search_team in search_teams:
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
        return None  # Game not found
    
    # Check if final
    status = matched_game.get('status', '').lower()
    has_scores = matched_game.get('home_score', 0) > 0 or matched_game.get('away_score', 0) > 0
    if 'final' not in status and 'finished' not in status and not has_scores:
        return "pending"  # Not finished yet
    
    # Determine outcome
    home_score = matched_game.get('home_score', 0)
    away_score = matched_game.get('away_score', 0)
    
    if bet_type == 'moneyline':
        if team:
            team_norm = normalization_service.normalize_name(team)
            home_norm = normalization_service.normalize_name(matched_game.get('home_team', ''))
            away_norm = normalization_service.normalize_name(matched_game.get('away_team', ''))
            
            is_home = team_norm in home_norm
            is_away = team_norm in away_norm
            
            if (is_home and home_score > away_score) or (is_away and away_score > home_score):
                return "won"
            return "lost"
    
    elif bet_type == 'spread':
        if team and line is not None:
            bet_team_norm = normalization_service.normalize_name(team)
            home_norm = normalization_service.normalize_name(matched_game.get('home_team', ''))
            away_norm = normalization_service.normalize_name(matched_game.get('away_team', ''))
            
            is_home = bet_team_norm in home_norm
            is_away = bet_team_norm in away_norm
            
            if not is_home and not is_away:
                return None
            
            home_margin = home_score - away_score
            
            if is_home:
                if home_margin > line:
                    return "won"
                elif home_margin == line:
                    return "pushed"
                return "lost"
            else:
                away_margin = away_score - home_score
                if line < 0:
                    if away_margin > abs(line):
                        return "won"
                    elif away_margin == abs(line):
                        return "pushed"
                    return "lost"
                else:
                    if away_margin > line:
                        return "won"
                    elif away_margin == line:
                        return "pushed"
                    return "lost"
    
    elif bet_type in ['over_under', 'total']:
        if line is not None:
            total = home_score + away_score
            team_lower = (team or '').lower()
            
            if 'under' in team_lower or team_lower == 'u':
                is_over = False
            elif 'over' in team_lower or team_lower == 'o':
                is_over = True
            else:
                is_over = True  # Default
            
            if total > line:
                return "won" if is_over else "lost"
            elif total < line:
                return "won" if not is_over else "lost"
            elif total == line:
                return "pushed"
    
    return None

async def settle_all_parlays():
    """Settle all pending parlay bets."""
    async with AsyncSessionLocal() as db:
        # Get all pending parlay bets
        result = await db.execute(text("""
            SELECT id, amount, odds, placed_at
            FROM bets
            WHERE status = 'pending' AND bet_type = 'parlay'
        """))
        parlay_bets = [dict(row._mapping) for row in result.fetchall()]
        
        logger.info(f"🎯 Found {len(parlay_bets)} pending parlay bets")
        
        if not parlay_bets:
            logger.info("✅ No parlay bets to settle")
            return
        
        sport_code_map = {
            "football": ["ncaaf", "nfl"],
            "basketball": ["ncaab", "nba", "ncaaw", "wnba"],
            "baseball": ["mlb"],
            "hockey": ["nhl"],
        }
        
        settled = 0
        won = 0
        lost = 0
        
        for parlay_bet in parlay_bets:
            try:
                # Get all legs for this parlay
                result = await db.execute(text("""
                    SELECT id, sport, game_id, home_team, away_team, team, game_date, 
                           bet_type, line, odds, result
                    FROM parlay_legs
                    WHERE parlay_bet_id = :parlay_id
                """), {"parlay_id": parlay_bet['id']})
                legs = [dict(row._mapping) for row in result.fetchall()]
                
                logger.info(f"📊 Processing parlay {parlay_bet['id'][:8]}... with {len(legs)} legs")
                
                # Collect all dates and sports for this parlay
                all_dates = set()
                all_sports = set()
                for leg in legs:
                    if leg.get('game_date'):
                        if isinstance(leg['game_date'], str):
                            try:
                                d = datetime.fromisoformat(leg['game_date'].replace('Z', '+00:00')).date()
                                all_dates.add(d)
                            except:
                                pass
                        else:
                            d = leg['game_date'].date() if hasattr(leg['game_date'], 'date') else leg['game_date']
                            all_dates.add(d)
                    all_sports.add(leg.get('sport', '').lower())
                
                # Fetch all games for all dates/sports
                all_games = []
                for search_date in all_dates:
                    for sport in all_sports:
                        sport_codes = sport_code_map.get(sport, [sport])
                        for sport_code in sport_codes:
                            try:
                                endpoint = aggressive_game_finder.ENDPOINTS.get(sport_code)
                                if endpoint:
                                    url = f"{aggressive_game_finder.BASE_URL}{endpoint}"
                                    date_str = search_date.strftime('%Y%m%d')
                                    
                                    import httpx
                                    async with httpx.AsyncClient(timeout=15.0) as client:
                                        response = await client.get(url, params={'dates': date_str})
                                        if response.status_code == 200:
                                            data = response.json()
                                            games = aggressive_game_finder._parse_games(data)
                                            all_games.extend(games)
                            except:
                                continue
                
                logger.info(f"✅ Loaded {len(all_games)} games for parlay legs")
                
                # Settle each leg
                leg_results = []
                all_final = True
                
                for leg in legs:
                    leg_result = await settle_leg(leg, all_games)
                    leg_results.append(leg_result)
                    
                    if leg_result == "pending" or leg_result is None:
                        all_final = False
                
                # Determine parlay outcome
                if not all_final:
                    logger.info(f"⏳ Parlay {parlay_bet['id'][:8]}... has pending legs")
                    continue
                
                # Check for any losses (parlay loses if any leg loses)
                if "lost" in leg_results:
                    outcome = "lost"
                # Check for any pushes (push means leg doesn't count, but parlay continues)
                elif "pushed" in leg_results:
                    # If all legs pushed, parlay is a push
                    if all(r == "pushed" for r in leg_results):
                        outcome = "pushed"
                    # If some pushed but rest won, recalculate odds without pushed legs
                    elif all(r in ["won", "pushed"] for r in leg_results):
                        # For now, treat as won (pushed legs don't count)
                        outcome = "won"
                    else:
                        outcome = "lost"
                # All legs won
                elif all(r == "won" for r in leg_results):
                    outcome = "won"
                else:
                    logger.warning(f"⚠️ Unexpected leg results: {leg_results}")
                    continue
                
                # Update parlay bet
                if outcome == "won":
                    amount = parlay_bet['amount']
                    odds = parlay_bet['odds']
                    if odds > 0:
                        payout = round(amount * (1 + odds / 100), 2)
                    else:
                        payout = round(amount * (1 + 100 / abs(odds)), 2)
                    roi = round(((payout - amount) / amount) * 100, 2)
                    
                    await db.execute(text("""
                        UPDATE bets SET status='won', settled_at=:now, payout=:payout, roi=:roi
                        WHERE id=:id
                    """), {"now": datetime.now(), "payout": payout, "roi": roi, "id": parlay_bet['id']})
                    won += 1
                    logger.info(f"✅ PARLAY WON: {parlay_bet['id'][:8]}... | {len(legs)} legs")
                
                elif outcome == "pushed":
                    await db.execute(text("""
                        UPDATE bets SET status='pushed', settled_at=:now, payout=:amount, roi=0
                        WHERE id=:id
                    """), {"now": datetime.now(), "amount": parlay_bet['amount'], "id": parlay_bet['id']})
                    logger.info(f"🔄 PARLAY PUSHED: {parlay_bet['id'][:8]}...")
                
                else:
                    await db.execute(text("""
                        UPDATE bets SET status='lost', settled_at=:now, payout=0, roi=-100
                        WHERE id=:id
                    """), {"now": datetime.now(), "id": parlay_bet['id']})
                    lost += 1
                    logger.info(f"❌ PARLAY LOST: {parlay_bet['id'][:8]}... | {len(legs)} legs")
                
                await db.commit()
                settled += 1
                
            except Exception as e:
                logger.error(f"❌ Error settling parlay {parlay_bet.get('id', 'unknown')[:8]}...: {e}")
                continue
        
        logger.info(f"\n📊 PARLAY SETTLEMENT COMPLETE:")
        logger.info(f"   ✅ Settled: {settled} parlays")
        logger.info(f"   🏆 Won: {won}")
        logger.info(f"   ❌ Lost: {lost}")

if __name__ == "__main__":
    asyncio.run(settle_all_parlays())


