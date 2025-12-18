"""
Bet Tracker Service
===================
Track all bets in real-time and calculate performance metrics.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.bet import Bet, Bankroll, DailyPerformance, BetStatus, BetType
from src.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class BetTracker:
    """
    Track bets and calculate real-time ROI.
    
    Features:
    - Record all bets placed
    - Update bet status automatically
    - Calculate ROI metrics
    - Track daily/weekly/monthly performance
    """
    
    async def place_bet(
        self,
        user_id: str,
        bet_data: Dict[str, Any],
        is_autonomous: bool = False
    ) -> str:
        """
        Record a new bet in the database.
        
        Args:
            user_id: User ID
            bet_data: Bet details dict
            is_autonomous: Whether bet was placed autonomously
        
        Returns:
            Bet ID
        """
        async with AsyncSessionLocal() as session:
            bet_id = str(uuid.uuid4())
            
            # Parse game_date if provided as string or datetime
            game_date = bet_data.get("game_date")
            if game_date and isinstance(game_date, str):
                try:
                    from dateutil import parser
                    game_date = parser.parse(game_date)
                except Exception:
                    game_date = None
            
            bet = Bet(
                id=bet_id,
                user_id=user_id,
                is_autonomous=is_autonomous,
                sportsbook=bet_data.get("sportsbook", "draftkings"),
                sport=bet_data["sport"],
                game_id=bet_data["game_id"],
                game_date=game_date,
                home_team=bet_data.get("home_team"),
                away_team=bet_data.get("away_team"),
                bet_type=bet_data["bet_type"],
                team=bet_data.get("team"),
                line=bet_data.get("line"),
                amount=bet_data["amount"],
                odds=bet_data["odds"],
                predicted_probability=bet_data.get("predicted_probability"),
                predicted_edge=bet_data.get("predicted_edge"),
                model_confidence=bet_data.get("model_confidence"),
                status=BetStatus.PENDING
            )
            
            session.add(bet)
            
            # Update bankroll
            await self._update_bankroll_on_bet(session, user_id, bet_data["amount"])
            
            await session.commit()
            
            logger.info(f"✅ Bet placed: {bet_id} | {bet_data['sport']} | ${bet_data['amount']}")
            
            return bet_id
    
    async def update_bet_status(
        self,
        bet_id: str,
        status: BetStatus,
        payout: Optional[float] = None
    ) -> bool:
        """
        Update bet status and calculate ROI.
        
        Args:
            bet_id: Bet ID
            status: New status (won, lost, pushed)
            payout: Actual payout if won
        
        Returns:
            Success boolean
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Bet).where(Bet.id == bet_id)
            )
            bet = result.scalar_one_or_none()
            
            if not bet:
                logger.error(f"Bet {bet_id} not found")
                return False
            
            bet.status = status
            bet.settled_at = datetime.utcnow()
            
            # Calculate payout and ROI
            if status == BetStatus.WON and payout:
                bet.payout = payout
                bet.roi = ((payout - bet.amount) / bet.amount) * 100
            elif status == BetStatus.WON:
                # Calculate from odds
                payout = self._calculate_payout(bet.amount, bet.odds)
                bet.payout = payout
                bet.roi = ((payout - bet.amount) / bet.amount) * 100
            elif status == BetStatus.LOST:
                bet.payout = 0
                bet.roi = -100.0
            elif status == BetStatus.PUSHED:
                bet.payout = bet.amount
                bet.roi = 0.0
            
            # Update bankroll
            await self._update_bankroll_on_settlement(
                session, bet.user_id, bet.amount, bet.payout, status
            )
            
            await session.commit()
            
            logger.info(f"📊 Bet {bet_id} settled: {status.value} | ROI: {bet.roi}%")
            
            return True
    
    async def get_active_bets(self, user_id: str) -> List[Dict]:
        """Get all active (pending) bets."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Bet).where(
                    and_(
                        Bet.user_id == user_id,
                        Bet.status == BetStatus.PENDING
                    )
                ).order_by(Bet.placed_at.desc())
            )
            bets = result.scalars().all()
            
            return [self._bet_to_dict(bet) for bet in bets]
    
    async def get_bet_history(
        self,
        user_id: str,
        limit: int = 50,
        sport: Optional[str] = None
    ) -> List[Dict]:
        """Get bet history."""
        async with AsyncSessionLocal() as session:
            query = select(Bet).where(Bet.user_id == user_id)
            
            if sport:
                query = query.where(Bet.sport == sport)
            
            query = query.order_by(Bet.placed_at.desc()).limit(limit)
            
            result = await session.execute(query)
            bets = result.scalars().all()
            
            return [self._bet_to_dict(bet) for bet in bets]
    
    async def calculate_roi(self, user_id: str, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate ROI and performance metrics.
        
        Args:
            user_id: User ID
            days: Optional days to look back (None = all time)
        
        Returns:
            ROI metrics dict
        """
        async with AsyncSessionLocal() as session:
            query = select(Bet).where(Bet.user_id == user_id)
            
            if days:
                since = datetime.utcnow() - timedelta(days=days)
                query = query.where(Bet.placed_at >= since)
            
            result = await session.execute(query)
            bets = result.scalars().all()
            
            if not bets:
                return {
                    "total_bets": 0,
                    "total_wagered": 0.0,
                    "total_won": 0.0,
                    "net_profit": 0.0,
                    "roi_percentage": 0.0,
                    "win_rate": 0.0
                }
            
            total_wagered = sum(bet.amount for bet in bets)
            settled_bets = [b for b in bets if b.status != BetStatus.PENDING]
            
            wins = [b for b in settled_bets if b.status == BetStatus.WON]
            losses = [b for b in settled_bets if b.status == BetStatus.LOST]
            
            total_won = sum(bet.payout for bet in wins if bet.payout)
            total_lost = sum(bet.amount for bet in losses)
            
            net_profit = total_won - total_wagered
            roi_percentage = (net_profit / total_wagered * 100) if total_wagered > 0 else 0.0
            win_rate = (len(wins) / len(settled_bets) * 100) if settled_bets else 0.0
            
            return {
                "total_bets": len(bets),
                "settled_bets": len(settled_bets),
                "total_wagered": round(total_wagered, 2),
                "total_won": round(total_won, 2),
                "total_lost": round(total_lost, 2),
                "net_profit": round(net_profit, 2),
                "roi_percentage": round(roi_percentage, 2),
                "win_rate": round(win_rate, 2),
                "wins": len(wins),
                "losses": len(losses),
                "pushes": len([b for b in settled_bets if b.status == BetStatus.PUSHED])
            }
    
    async def get_bankroll(self, user_id: str) -> Optional[Dict]:
        """Get current bankroll status."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Bankroll).where(Bankroll.user_id == user_id)
            )
            bankroll = result.scalar_one_or_none()
            
            if not bankroll:
                return None
            
            return {
                "current_balance": bankroll.current_balance,
                "initial_deposit": bankroll.initial_deposit,
                "total_wagered": bankroll.total_wagered,
                "total_won": bankroll.total_won,
                "total_lost": bankroll.total_lost,
                "roi_percentage": bankroll.roi_percentage,
                "win_rate": bankroll.win_rate,
                "active_bets_count": bankroll.active_bets_count,
                "active_bets_amount": bankroll.active_bets_amount,
                "available_balance": bankroll.available_balance
            }
    
    def _calculate_payout(self, amount: float, american_odds: float) -> float:
        """Calculate payout from American odds."""
        if american_odds > 0:
            return amount + (amount * (american_odds / 100))
        else:
            return amount + (amount * (100 / abs(american_odds)))
    
    async def _update_bankroll_on_bet(
        self,
        session: AsyncSession,
        user_id: str,
        amount: float
    ):
        """Update bankroll when bet is placed."""
        result = await session.execute(
            select(Bankroll).where(Bankroll.user_id == user_id)
        )
        bankroll = result.scalar_one_or_none()
        
        if bankroll:
            bankroll.active_bets_count += 1
            bankroll.active_bets_amount += amount
            bankroll.available_balance -= amount
            bankroll.total_wagered += amount
            bankroll.last_bet_at = datetime.utcnow()
    
    async def _update_bankroll_on_settlement(
        self,
        session: AsyncSession,
        user_id: str,
        amount: float,
        payout: float,
        status: BetStatus
    ):
        """Update bankroll when bet settles."""
        result = await session.execute(
            select(Bankroll).where(Bankroll.user_id == user_id)
        )
        bankroll = result.scalar_one_or_none()
        
        if bankroll:
            bankroll.active_bets_count -= 1
            bankroll.active_bets_amount -= amount
            
            if status == BetStatus.WON:
                bankroll.current_balance += payout
                bankroll.available_balance += payout
                bankroll.total_won += payout
            elif status == BetStatus.LOST:
                bankroll.total_lost += amount
            elif status == BetStatus.PUSHED:
                bankroll.available_balance += amount
            
            # Recalculate ROI
            net = bankroll.total_won - (bankroll.total_wagered - bankroll.active_bets_amount)
            bankroll.roi_percentage = (net / bankroll.initial_deposit * 100) if bankroll.initial_deposit > 0 else 0
    
    def _bet_to_dict(self, bet: Bet) -> Dict:
        """Convert Bet model to dict."""
        return {
            "id": bet.id,
            "sport": bet.sport,
            "game_id": bet.game_id,
            "bet_type": bet.bet_type.value if bet.bet_type else None,
            "team": bet.team,
            "amount": bet.amount,
            "odds": bet.odds,
            "status": bet.status.value if bet.status else None,
            "payout": bet.payout,
            "roi": bet.roi,
            "placed_at": bet.placed_at.isoformat() if bet.placed_at else None,
            "settled_at": bet.settled_at.isoformat() if bet.settled_at else None,
            "is_autonomous": bet.is_autonomous
        }


# Global bet tracker instance
bet_tracker = BetTracker()
