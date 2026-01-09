#!/usr/bin/env python3
"""
Settle Bets Using Direct SQL
=============================
Bypass ORM enum issues by using raw SQL for settlement.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.db.database import AsyncSessionLocal, engine
from src.services.real_sports_service import real_sports_service
from src.services.historical_game_scraper import historical_game_scraper
from src.services.team_normalization import normalization_service
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Sport mapping - try to detect college vs pro based on team names
SPORT_MAPPING = {
    "football": "nfl",  # Default to NFL, but may need to try NCAAF
    "basketball": "ncaab",  # Default to college, but may need to try NBA
    "baseball": "mlb",
    "hockey": "nhl",
    "nfl": "nfl",
    "ncaaf": "ncaaf",
    "ncaab": "ncaab",
    "ncaaw": "ncaaw",
    "wnba": "wnba",
    "mlb": "mlb",
    "nhl": "nhl"
}

COLLEGE_KEYWORDS = ["bulls", "monarchs", "bobcats", "ravens", "hens", "ragin", "cajuns", "unlv", "rebels", "celtics", "heat", "lakers", "warriors", "suns", "bruins", "maple leafs"]

def detect_sport_from_teams(bet_row: dict, default_sport: str) -> list:
    """Try to detect if this is college or pro based on team names. Returns list of sport codes to try."""
    teams = []
    if bet_row.get('home_team'):
        teams.append(bet_row['home_team'].lower())
    if bet_row.get('away_team'):
        teams.append(bet_row['away_team'].lower())
    if bet_row.get('team'):
        teams.append(bet_row['team'].lower())
    
    team_text = ' '.join(teams).lower()
    
    # Check for college keywords
    has_college_keywords = any(kw in team_text for kw in COLLEGE_KEYWORDS)
    
    if default_sport == "nfl":
        # If we detect college keywords, try NCAAF first, then NFL
        if has_college_keywords:
            return ["ncaaf", "nfl"]
        else:
            return ["nfl", "ncaaf"]  # Try NFL first, but fallback to NCAAF
    
    return [default_sport]


def determine_outcome(bet_row: dict, game: dict) -> Optional[str]:
    """Determine bet outcome: 'won', 'lost', 'pushed', or None."""
    home_score = game.get('home_score', 0)
    away_score = game.get('away_score', 0)
    
    home_team = game.get('home_team', '')
    away_team = game.get('away_team', '')
    
    bet_team = bet_row.get('team', '') or ''
    bet_type = bet_row.get('bet_type', '').lower()
    line = bet_row.get('line')
    
    # Determine which team the bet is on
    is_home_bet = normalization_service.normalize_name(bet_team) in normalization_service.normalize_name(home_team)
    is_away_bet = normalization_service.normalize_name(bet_team) in normalization_service.normalize_name(away_team)
    
    if not is_home_bet and not is_away_bet:
        logger.debug(f"⚠️ Could not match bet team {bet_team} to game teams")
        return None
    
    # Moneyline bet
    if bet_type == 'moneyline':
        if is_home_bet and home_score > away_score:
            return "won"
        elif is_away_bet and away_score > home_score:
            return "won"
        else:
            return "lost"
    
    # Spread bet
    elif bet_type == 'spread':
        if line is None:
            return None
        
        home_margin = home_score - away_score
        
        if is_home_bet:
            if home_margin > line:
                return "won"
            elif home_margin == line:
                return "pushed"
            else:
                return "lost"
        else:  # away bet
            away_margin = away_score - home_score
            if away_margin > abs(line) or (away_margin == abs(line) and line < 0):
                return "won"
            elif away_margin == abs(line):
                return "pushed"
            else:
                return "lost"
    
    # Over/Under bet
    elif bet_type in ['over_under', 'total']:
        if line is None:
            return None
        
        total_score = home_score + away_score
        
        # Check if bet is for over or under
        bet_team_lower = bet_team.lower()
        if 'over' in bet_team_lower or 'o ' in bet_team_lower:
            is_over = True
        elif 'under' in bet_team_lower or 'u ' in bet_team_lower:
            is_over = False
        else:
            logger.warning(f"⚠️ Cannot determine over/under direction for bet {bet_row.get('id')}")
            return None
        
        if is_over and total_score > line:
            return "won"
        elif not is_over and total_score < line:
            return "won"
        elif total_score == line:
            return "pushed"
        else:
            return "lost"
    
    return None


def find_matching_game(bet_row: dict, games: list) -> Optional[dict]:
    """Find the game that matches this bet."""
    game_id = bet_row.get('game_id')
    home_team = bet_row.get('home_team')
    away_team = bet_row.get('away_team')
    bet_team = bet_row.get('team', '')
    
    # First try to match by game_id (most reliable)
    if game_id:
        for game in games:
            if str(game.get('id', '')) == str(game_id):
                return game
    
    # If no game_id match, try to match by team names (both teams must match)
    if home_team and away_team:
        home_norm = normalization_service.normalize_name(home_team)
        away_norm = normalization_service.normalize_name(away_team)
        
        for game in games:
            game_home_norm = normalization_service.normalize_name(game.get('home_team', ''))
            game_away_norm = normalization_service.normalize_name(game.get('away_team', ''))
            
            # Check both directions (home/away can be swapped in some data)
            match1 = home_norm in game_home_norm and away_norm in game_away_norm
            match2 = home_norm in game_away_norm and away_norm in game_home_norm
            
            if match1 or match2:
                return game
    
    # Last resort: match by single team name (less reliable)
    if bet_team:
        bet_team_normalized = normalization_service.normalize_name(bet_team)
        for game in games:
            game_home = normalization_service.normalize_name(game.get('home_team', ''))
            game_away = normalization_service.normalize_name(game.get('away_team', ''))
            
            if bet_team_normalized in game_home or bet_team_normalized in game_away:
                return game
    
    return None


async def settle_all_pending_direct():
    """Settle all pending bets using direct SQL."""
    logger.info("🎯 Starting direct SQL settlement of all pending bets...")
    
    async with AsyncSessionLocal() as db:
        # Get all pending bets using raw SQL
        result = await db.execute(text("""
            SELECT id, sport, game_id, game_date, home_team, away_team, team, bet_type, line, amount, odds
            FROM bets
            WHERE status = 'pending'
            ORDER BY game_date, placed_at
        """))
        pending_bets = [dict(row._mapping) for row in result.fetchall()]
        
        logger.info(f"📊 Found {len(pending_bets)} pending bets")
        
        if not pending_bets:
            logger.info("✅ No pending bets to settle")
            return
        
        # Group bets by sport and date
        bets_by_sport_date = {}
        for bet in pending_bets:
            default_sport_key = SPORT_MAPPING.get(bet['sport'].lower(), bet['sport'].lower())
            # Detect if college or pro - will try multiple sport codes if needed
            sport_keys_to_try = detect_sport_from_teams(bet, default_sport_key)
            primary_sport_key = sport_keys_to_try[0]  # Use first one for grouping
            
            # Use game_date if available, otherwise use placed_at date
            if bet['game_date']:
                if isinstance(bet['game_date'], str):
                    try:
                        bet_date = datetime.fromisoformat(bet['game_date'].replace('Z', '+00:00')).date()
                    except:
                        bet_date = datetime.now().date()
                else:
                    bet_date = bet['game_date'].date() if hasattr(bet['game_date'], 'date') else bet['game_date']
            else:
                # Fallback to today if no date
                bet_date = datetime.now().date()
                
                # Store bets by their primary date (we'll check +/- 1 day when fetching games)
                # Store sport keys to try with each bet
                key = (primary_sport_key, bet_date)
                if key not in bets_by_sport_date:
                    bets_by_sport_date[key] = []
                bet['_sport_keys_to_try'] = sport_keys_to_try  # Store for later
                bets_by_sport_date[key].append(bet)
        
        stats = {
            "bets_checked": len(pending_bets),
            "bets_settled": 0,
            "bets_won": 0,
            "bets_lost": 0,
            "bets_pushed": 0,
            "bets_skipped": 0,
            "errors": []
        }
        
        # Process each sport/date group (dedupe bets first)
        processed_bet_ids = set()
        for (sport, bet_date), bets in bets_by_sport_date.items():
            # Filter out already processed bets
            bets = [b for b in bets if b['id'] not in processed_bet_ids]
            logger.info(f"📊 Processing {len(bets)} bets for {sport} on {bet_date}")
            
            try:
                # Check if this is a historical date (more than 2 days old)
                days_old = (datetime.now().date() - bet_date).days
                
                # Try each sport code until we find games (for bets that might be college or pro)
                games = []
                sport_keys_to_try = bets[0].get('_sport_keys_to_try', [sport]) if bets else [sport]
                
                for try_sport in sport_keys_to_try:
                    if days_old > 2:
                        logger.info(f"📜 Trying historical scraper for {try_sport} on {bet_date}")
                        games = await historical_game_scraper.get_historical_games(try_sport, bet_date)
                    else:
                        logger.info(f"🔍 Trying API for {try_sport} on {bet_date}")
                        games = await real_sports_service.get_live_games(try_sport, date=bet_date)
                    
                    if games:
                        logger.info(f"✅ Found {len(games)} games using {try_sport}")
                        sport = try_sport  # Update sport for this batch
                        break
                
                if not games:
                    logger.warning(f"⚠️ No games found for {sport} on {bet_date}")
                    stats["bets_skipped"] += len(bets)
                    continue
                
                # Settle each bet
                for bet in bets:
                    if bet['id'] in processed_bet_ids:
                        continue
                    
                    processed_bet_ids.add(bet['id'])
                    
                    try:
                        # Try to find matching game
                        game = find_matching_game(bet, games)
                        
                        if not game:
                            # Try fetching games for date +/- 1 day (for late games)
                            for day_offset in [-1, 1]:
                                try:
                                    alt_date = bet_date + timedelta(days=day_offset)
                                    alt_games = await historical_game_scraper.get_historical_games(sport, alt_date) if days_old > 2 else await real_sports_service.get_live_games(sport, date=alt_date)
                                    game = find_matching_game(bet, alt_games)
                                    if game:
                                        logger.info(f"✅ Found game on {alt_date} (offset {day_offset} days)")
                                        break
                                except:
                                    pass
                            
                            if not game:
                                logger.debug(f"⚠️ Game not found for bet {bet['id'][:8]}... (game_id: {bet.get('game_id')}, teams: {bet.get('home_team')} vs {bet.get('away_team')}, date: {bet_date})")
                                stats["bets_skipped"] += 1
                                continue
                        
                        # Check if game is completed
                        game_status = game.get('status', '').lower()
                        # For historical games, assume they're final if they have scores
                        has_scores = game.get('home_score', 0) > 0 or game.get('away_score', 0) > 0
                        is_final = 'final' in game_status or 'finished' in game_status or has_scores
                        
                        if not is_final:
                            logger.debug(f"⏳ Game {bet['game_id']} not yet finished (status: {game_status})")
                            stats["bets_skipped"] += 1
                            continue
                        
                        # Determine outcome
                        outcome = determine_outcome(bet, game)
                        
                        if outcome is None:
                            logger.warning(f"⚠️ Could not determine outcome for bet {bet['id']}")
                            stats["bets_skipped"] += 1
                            continue
                        
                        # Calculate payout
                        payout = None
                        if outcome == "won":
                            # Calculate payout from odds
                            amount = bet['amount']
                            odds = bet['odds']
                            if odds > 0:
                                payout = amount * (1 + odds / 100)
                            else:
                                payout = amount * (1 + 100 / abs(odds))
                            
                            # Round to 2 decimal places
                            payout = round(payout, 2)
                        
                        # Update bet status using raw SQL
                        status_map = {"won": "won", "lost": "lost", "pushed": "pushed"}
                        new_status = status_map[outcome]
                        
                        update_sql = text("""
                            UPDATE bets
                            SET status = :status,
                                settled_at = :settled_at
                            WHERE id = :bet_id
                        """)
                        
                        if payout is not None:
                            update_sql = text("""
                                UPDATE bets
                                SET status = :status,
                                    settled_at = :settled_at,
                                    payout = :payout,
                                    roi = :roi
                                WHERE id = :bet_id
                            """)
                            roi = ((payout - bet['amount']) / bet['amount']) * 100
                            await db.execute(update_sql, {
                                "status": new_status,
                                "settled_at": datetime.utcnow(),
                                "payout": payout,
                                "roi": roi,
                                "bet_id": bet['id']
                            })
                        else:
                            await db.execute(update_sql, {
                                "status": new_status,
                                "settled_at": datetime.utcnow(),
                                "bet_id": bet['id']
                            })
                        
                        await db.commit()
                        
                        stats["bets_settled"] += 1
                        if outcome == "won":
                            stats["bets_won"] += 1
                            logger.info(f"✅ Bet {bet['id']} WON")
                        elif outcome == "lost":
                            stats["bets_lost"] += 1
                            logger.info(f"❌ Bet {bet['id']} LOST")
                        elif outcome == "pushed":
                            stats["bets_pushed"] += 1
                            logger.info(f"🔄 Bet {bet['id']} PUSHED")
                            
                    except Exception as e:
                        logger.error(f"❌ Error settling bet {bet.get('id', 'unknown')}: {e}")
                        stats["errors"].append(f"Bet {bet.get('id', 'unknown')}: {str(e)}")
                        stats["bets_skipped"] += 1
                        await db.rollback()
                        
            except Exception as e:
                logger.error(f"❌ Error processing {sport} on {bet_date}: {e}")
                stats["errors"].append(f"{sport} {bet_date}: {str(e)}")
                stats["bets_skipped"] += len(bets)
        
        logger.info("=" * 60)
        logger.info("📊 SETTLEMENT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Bets checked: {stats['bets_checked']}")
        logger.info(f"✅ Bets settled: {stats['bets_settled']}")
        logger.info(f"✅ Bets won: {stats['bets_won']}")
        logger.info(f"❌ Bets lost: {stats['bets_lost']}")
        logger.info(f"🔄 Bets pushed: {stats['bets_pushed']}")
        logger.info(f"⏭️  Bets skipped: {stats['bets_skipped']}")
        
        if stats['errors']:
            logger.warning(f"⚠️  Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:10]:
                logger.warning(f"   - {error}")
        
        # Check final status
        result = await db.execute(text("SELECT status, COUNT(*) FROM bets GROUP BY status"))
        logger.info("\n📊 Final bet status distribution:")
        for row in result.fetchall():
            logger.info(f"   {row[0]}: {row[1]}")


if __name__ == "__main__":
    asyncio.run(settle_all_pending_direct())
