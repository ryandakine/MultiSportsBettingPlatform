"""
Bet Settlement Service
======================
Automatically settle bets by checking game results from sports APIs.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus, BetType
from src.services.bet_tracker import bet_tracker
from src.services.real_sports_service import real_sports_service
from src.services.historical_game_scraper import historical_game_scraper
from src.services.team_normalization import normalization_service

logger = logging.getLogger(__name__)


class BetSettlementService:
    """
    Service to automatically settle bets based on game results.
    
    Features:
    - Fetches game results from ESPN API
    - Matches bets to games by game_id or team names
    - Determines win/loss based on bet type and game outcome
    - Updates bet status and calculates payouts
    """
    
    # Sport code mapping (database -> ESPN API)
    SPORT_MAPPING = {
        "football": "nfl",
        "basketball": "ncaab",  # Default to college, but should check context
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
    
    async def settle_pending_bets(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Settle all pending bets from the last N days.
        
        Args:
            days_back: Number of days to look back for pending bets
            
        Returns:
            Dict with settlement statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        async with AsyncSessionLocal() as session:
            # Get all pending bets from last N days using raw SQL to avoid enum issues
            from sqlalchemy import text
            query = text("""
                SELECT id FROM bets
                WHERE status = 'pending'
                AND placed_at >= :cutoff_date
                ORDER BY placed_at DESC
            """)
            result = await session.execute(query, {"cutoff_date": cutoff_date})
            bet_ids = [row[0] for row in result.fetchall()]
            
            # Load Bet objects by ID (now that enum values are fixed)
            pending_bets = []
            for bet_id in bet_ids:
                try:
                    bet_result = await session.execute(select(Bet).where(Bet.id == bet_id))
                    bet = bet_result.scalar_one_or_none()
                    if bet:
                        pending_bets.append(bet)
                except Exception as e:
                    logger.warning(f"Could not load bet {bet_id}: {e}")
                    continue
            
            if not pending_bets:
                logger.info("✅ No pending bets to settle")
                return {
                    "success": True,
                    "bets_checked": 0,
                    "bets_settled": 0,
                    "bets_won": 0,
                    "bets_lost": 0,
                    "bets_pushed": 0,
                    "bets_skipped": 0
                }
            
            logger.info(f"🔍 Found {len(pending_bets)} pending bets to check")
            
            # Group bets by sport and date for efficient API calls
            bets_by_sport_date = {}
            for bet in pending_bets:
                sport_key = self.SPORT_MAPPING.get(bet.sport.lower(), bet.sport.lower())
                # Use game_date if available, otherwise use placed_at date
                bet_date = bet.game_date.date() if bet.game_date else bet.placed_at.date()
                key = (sport_key, bet_date)
                if key not in bets_by_sport_date:
                    bets_by_sport_date[key] = []
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
            
            # Process each sport/date group
            for (sport, bet_date), bets in bets_by_sport_date.items():
                logger.info(f"📊 Processing {len(bets)} bets for {sport} on {bet_date}")
                
                try:
                    # Fetch games for this sport/date
                    games = await self._fetch_games_for_date(sport, bet_date)
                    
                    if not games:
                        logger.warning(f"⚠️ No games found for {sport} on {bet_date}")
                        stats["bets_skipped"] += len(bets)
                        continue
                    
                    # Settle each bet
                    for bet in bets:
                        try:
                            settled = await self._settle_bet(bet, games)
                            if settled:
                                stats["bets_settled"] += 1
                                if bet.status == BetStatus.WON:
                                    stats["bets_won"] += 1
                                elif bet.status == BetStatus.LOST:
                                    stats["bets_lost"] += 1
                                elif bet.status == BetStatus.PUSHED:
                                    stats["bets_pushed"] += 1
                            else:
                                stats["bets_skipped"] += 1
                        except Exception as e:
                            logger.error(f"❌ Error settling bet {bet.id}: {e}")
                            stats["errors"].append(f"Bet {bet.id}: {str(e)}")
                            stats["bets_skipped"] += 1
                            
                except Exception as e:
                    logger.error(f"❌ Error processing {sport} on {bet_date}: {e}")
                    stats["errors"].append(f"{sport} {bet_date}: {str(e)}")
                    stats["bets_skipped"] += len(bets)
            
            logger.info(f"✅ Settlement complete: {stats['bets_settled']} settled, {stats['bets_won']} won, {stats['bets_lost']} lost")
            
            return {
                "success": True,
                **stats
            }
    
    async def _fetch_games_for_date(self, sport: str, date: datetime.date) -> List[Dict[str, Any]]:
        """Fetch games for a specific sport and date."""
        try:
            # Check if this is a historical date (more than 2 days old)
            days_old = (datetime.now().date() - date).days
            
            if days_old > 2:
                # Use historical scraper for older dates
                logger.info(f"📜 Using historical scraper for {sport} on {date} ({days_old} days old)")
                games = await historical_game_scraper.get_historical_games(sport, date)
            else:
                # Use regular API for recent dates
                games = await real_sports_service.get_live_games(sport, date=date)
            
            # Filter for games on the target date (in case API returns nearby dates)
            target_date_str = date.strftime('%Y-%m-%d')
            filtered_games = []
            
            for game in games:
                # Check game_date if available, otherwise use date field
                game_date = None
                if 'game_date' in game:
                    game_date = game['game_date']
                    if isinstance(game_date, str):
                        try:
                            game_date = datetime.fromisoformat(game_date.replace('Z', '+00:00')).date()
                        except:
                            pass
                
                if not game_date:
                    game_date_str = game.get('date', '')
                    try:
                        if 'T' in game_date_str:
                            game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00')).date()
                        elif game_date_str.startswith(target_date_str):
                            game_date = date
                    except Exception:
                        pass
                
                if game_date == date or (not game_date and target_date_str in game.get('date', '')):
                    filtered_games.append(game)
            
            return filtered_games
            
        except Exception as e:
            logger.error(f"❌ Error fetching games for {sport} on {date}: {e}")
            return []
    
    async def _settle_bet(self, bet: Bet, games: List[Dict[str, Any]]) -> bool:
        """
        Settle a single bet by matching it to a game result.
        
        Returns:
            True if bet was settled, False if game not found or still in progress
        """
        # Try to find matching game
        game = self._find_matching_game(bet, games)
        
        if not game:
            logger.debug(f"⚠️ Game not found for bet {bet.id} (game_id: {bet.game_id})")
            return False
        
        # Check if game is completed
        game_status = game.get('status', '').lower()
        if 'final' not in game_status and 'finished' not in game_status:
            logger.debug(f"⏳ Game {bet.game_id} not yet finished (status: {game_status})")
            return False
        
        # Determine bet outcome
        outcome = self._determine_bet_outcome(bet, game)
        
        if outcome is None:
            logger.warning(f"⚠️ Could not determine outcome for bet {bet.id}")
            return False
        
        # Update bet status
        if outcome == "won":
            await bet_tracker.update_bet_status(bet.id, BetStatus.WON)
            logger.info(f"✅ Bet {bet.id} WON")
        elif outcome == "lost":
            await bet_tracker.update_bet_status(bet.id, BetStatus.LOST)
            logger.info(f"❌ Bet {bet.id} LOST")
        elif outcome == "pushed":
            await bet_tracker.update_bet_status(bet.id, BetStatus.PUSHED)
            logger.info(f"🔄 Bet {bet.id} PUSHED")
        
        return True
    
    def _find_matching_game(self, bet: Bet, games: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the game that matches this bet."""
        # First try to match by game_id
        if bet.game_id:
            for game in games:
                if str(game.get('id', '')) == str(bet.game_id):
                    return game
        
        # If no game_id match, try to match by team names
        if bet.home_team and bet.away_team:
            for game in games:
                home_match = normalization_service.normalize_name(bet.home_team) in normalization_service.normalize_name(game.get('home_team', ''))
                away_match = normalization_service.normalize_name(bet.away_team) in normalization_service.normalize_name(game.get('away_team', ''))
                
                if home_match and away_match:
                    return game
        
        # Last resort: match by team name (if only team is set)
        if bet.team:
            bet_team_normalized = normalization_service.normalize_name(bet.team)
            for game in games:
                home_team = normalization_service.normalize_name(game.get('home_team', ''))
                away_team = normalization_service.normalize_name(game.get('away_team', ''))
                
                if bet_team_normalized in home_team or bet_team_normalized in away_team:
                    return game
        
        return None
    
    def _determine_bet_outcome(self, bet: Bet, game: Dict[str, Any]) -> Optional[str]:
        """
        Determine if bet won, lost, or pushed based on game result.
        
        Returns:
            "won", "lost", "pushed", or None if cannot determine
        """
        home_score = game.get('home_score', 0)
        away_score = game.get('away_score', 0)
        
        home_team = game.get('home_team', '')
        away_team = game.get('away_team', '')
        
        bet_team = bet.team or ''
        bet_type = bet.bet_type.value if bet.bet_type else ''
        line = bet.line
        
        # Determine which team the bet is on
        is_home_bet = normalization_service.normalize_name(bet_team) in normalization_service.normalize_name(home_team)
        is_away_bet = normalization_service.normalize_name(bet_team) in normalization_service.normalize_name(away_team)
        
        if not is_home_bet and not is_away_bet:
            logger.warning(f"⚠️ Could not match bet team {bet_team} to game teams")
            return None
        
        # Moneyline bet
        if bet_type in ['moneyline', 'MONEYLINE']:
            if is_home_bet and home_score > away_score:
                return "won"
            elif is_away_bet and away_score > home_score:
                return "won"
            else:
                return "lost"
        
        # Spread bet
        elif bet_type in ['spread', 'SPREAD']:
            if line is None:
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
                # Away team needs to lose by less than spread (or win)
                away_margin = away_score - home_score
                if away_margin > abs(line) or (away_margin == abs(line) and line < 0):
                    return "won"
                elif away_margin == abs(line):
                    return "pushed"
                else:
                    return "lost"
        
        # Over/Under bet
        elif bet_type in ['over_under', 'OVER_UNDER', 'total', 'TOTAL']:
            if line is None:
                return None
            
            total_score = home_score + away_score
            
            # Check if bet is for over or under
            # If team name suggests "over" or "under", or if line context helps
            # For now, assume team field contains indication or we need to infer from context
            # This is a simplification - real implementation would need better context
            
            # Check if the "team" field actually indicates over/under
            bet_team_lower = bet_team.lower()
            if 'over' in bet_team_lower or 'o ' in bet_team_lower:
                is_over = True
            elif 'under' in bet_team_lower or 'u ' in bet_team_lower:
                is_over = False
            else:
                # Default: if no indication, we can't determine
                # In real implementation, this would be stored separately
                logger.warning(f"⚠️ Cannot determine over/under direction for bet {bet.id}")
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


# Global instance
bet_settlement_service = BetSettlementService()

