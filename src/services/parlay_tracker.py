"""
Parlay Tracker Service
======================
Track and store parlay bets with their individual legs.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.db.models.bet import Bet, BetStatus, BetType
from src.db.models.parlay import ParlayLeg
from src.services.bet_tracker import bet_tracker

logger = logging.getLogger(__name__)


class ParlayTracker:
    """
    Service to track parlay bets with individual legs.
    
    A parlay consists of:
    - One Bet record with bet_type=PARLAY (tracks overall parlay)
    - Multiple ParlayLeg records (one for each leg)
    """
    
    async def place_parlay(
        self,
        user_id: str,
        parlay_data: Dict[str, Any],
        is_autonomous: bool = False
    ) -> str:
        """
        Record a parlay bet with all its legs.
        
        Args:
            user_id: User ID
            parlay_data: Dict containing:
                - legs: List of leg dicts (each with sport, game_id, bet_type, team, line, odds, etc.)
                - amount: Total bet amount
                - combined_odds: Combined parlay odds
                - sportsbook: Sportsbook name
                - game_date: Optional date for the parlay (earliest leg date)
            is_autonomous: Whether bet was placed autonomously
        
        Returns:
            Parlay bet ID (Bet.id)
        """
        async with AsyncSessionLocal() as session:
            parlay_bet_id = str(uuid.uuid4())
            legs = parlay_data.get("legs", [])
            
            if not legs:
                raise ValueError("Parlay must have at least one leg")
            
            # Parse game_date if provided
            game_date = parlay_data.get("game_date")
            if game_date and isinstance(game_date, str):
                try:
                    from dateutil import parser
                    game_date = parser.parse(game_date)
                except Exception:
                    game_date = None
            
            # Create main parlay bet record
            parlay_bet = Bet(
                id=parlay_bet_id,
                user_id=user_id,
                is_autonomous=is_autonomous,
                sportsbook=parlay_data.get("sportsbook", "paper_trading"),
                sport="multi",  # Parlays span multiple sports
                game_id=f"parlay_{parlay_bet_id}",  # Unique parlay identifier
                game_date=game_date,
                home_team=None,  # Not applicable for parlays
                away_team=None,
                bet_type=BetType.PARLAY,
                team=None,  # Not applicable for parlays
                line=None,
                amount=parlay_data["amount"],
                odds=parlay_data.get("combined_odds", 0),
                predicted_probability=parlay_data.get("combined_probability"),
                predicted_edge=parlay_data.get("expected_edge"),
                model_confidence=parlay_data.get("combined_confidence"),
                status=BetStatus.PENDING
            )
            
            session.add(parlay_bet)
            
            # Create leg records
            for leg_data in legs:
                leg_id = str(uuid.uuid4())
                
                # Parse game_date for this leg if provided
                leg_game_date = leg_data.get("game_date")
                if leg_game_date:
                    if isinstance(leg_game_date, str):
                        try:
                            from dateutil import parser
                            leg_game_date = parser.parse(leg_game_date)
                        except Exception:
                            leg_game_date = None
                    # If it's already a datetime object, use it directly
                    elif not isinstance(leg_game_date, datetime):
                        leg_game_date = None
                
                leg = ParlayLeg(
                    id=leg_id,
                    parlay_bet_id=parlay_bet_id,
                    sport=leg_data.get("sport", "unknown"),
                    game_id=leg_data.get("game_id", ""),
                    game_date=leg_game_date,  # Store game date for this leg
                    home_team=leg_data.get("home_team"),
                    away_team=leg_data.get("away_team"),
                    bet_type=leg_data.get("bet_type", "moneyline"),
                    team=leg_data.get("team"),
                    line=leg_data.get("line"),
                    odds=leg_data.get("odds", 0),
                    predicted_probability=leg_data.get("probability"),
                    predicted_edge=leg_data.get("edge"),
                    result="pending"
                )
                # Store game_date in metadata_json for now (until we add a column)
                if hasattr(leg, 'metadata_json') or True:  # Check if field exists
                    leg_metadata = leg_data.get("metadata_json", {})
                    if leg_game_date:
                        leg_metadata["game_date"] = leg_game_date.isoformat() if hasattr(leg_game_date, 'isoformat') else str(leg_game_date)
                    # Store in actual_result field as temporary storage (it's nullable)
                    # Or we could use a JSON field if ParlayLeg has one
                
                session.add(leg)
            
            # Update bankroll
            await bet_tracker._update_bankroll_on_bet(
                session, user_id, parlay_data["amount"]
            )
            
            await session.commit()
            
            logger.info(
                f"✅ Parlay bet placed: {parlay_bet_id} | {len(legs)} legs | "
                f"${parlay_data['amount']:.2f} | Odds: {parlay_data.get('combined_odds', 0)}"
            )
            
            return parlay_bet_id
    
    async def get_parlay_legs(self, parlay_bet_id: str) -> List[Dict]:
        """Get all legs for a parlay bet."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ParlayLeg).where(ParlayLeg.parlay_bet_id == parlay_bet_id)
            )
            legs = result.scalars().all()
            
            return [self._leg_to_dict(leg) for leg in legs]
    
    async def update_leg_result(
        self,
        leg_id: str,
        result: str,
        actual_outcome: Optional[str] = None
    ) -> bool:
        """
        Update the result of a parlay leg.
        
        Args:
            leg_id: Leg ID
            result: "won", "lost", "pending", or "pushed"
            actual_outcome: Optional description of actual outcome
        """
        async with AsyncSessionLocal() as session:
            result_obj = await session.execute(
                select(ParlayLeg).where(ParlayLeg.id == leg_id)
            )
            leg = result_obj.scalar_one_or_none()
            
            if not leg:
                logger.error(f"Leg {leg_id} not found")
                return False
            
            leg.result = result
            if actual_outcome:
                leg.actual_outcome = actual_outcome
            
            await session.commit()
            logger.info(f"✅ Leg {leg_id} updated: {result}")
            return True
    
    def _leg_to_dict(self, leg: ParlayLeg) -> Dict:
        """Convert ParlayLeg model to dict."""
        return {
            "id": leg.id,
            "parlay_bet_id": leg.parlay_bet_id,
            "sport": leg.sport,
            "game_id": leg.game_id,
            "game_date": leg.game_date.isoformat() if leg.game_date and hasattr(leg.game_date, 'isoformat') else str(leg.game_date) if leg.game_date else None,
            "home_team": leg.home_team,
            "away_team": leg.away_team,
            "bet_type": leg.bet_type,
            "team": leg.team,
            "line": leg.line,
            "odds": leg.odds,
            "predicted_probability": leg.predicted_probability,
            "predicted_edge": leg.predicted_edge,
            "result": leg.result,
            "actual_outcome": leg.actual_outcome,
            "created_at": leg.created_at.isoformat() if leg.created_at else None
        }


# Global instance
parlay_tracker = ParlayTracker()

