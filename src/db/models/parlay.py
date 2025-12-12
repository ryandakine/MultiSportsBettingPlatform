"""
Parlay Bet Models
=================
Extended support for multi-leg parlay bets.
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.models import Base


class ParlayLeg(Base):
    """Individual leg of a parlay bet."""
    
    __tablename__ = "parlay_legs"
    
    id = Column(String, primary_key=True)
    parlay_bet_id = Column(String, ForeignKey("bets.id"), nullable=False, index=True)
    
    # Game details
    sport = Column(String, nullable=False)
    game_id = Column(String, nullable=False)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    
    # Leg details
    bet_type = Column(String, nullable=False)  # moneyline, spread, total
    team = Column(String, nullable=True)
    line = Column(Float, nullable=True)
    odds = Column(Float, nullable=False)  # Individual leg odds
    
    # Prediction
    predicted_probability = Column(Float, nullable=True)
    predicted_edge = Column(Float, nullable=True)
    
    # Outcome
    result = Column(String, nullable=True)  # won, lost, pending, pushed
    actual_outcome = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())


class ParlayCard(Base):
    """Parlay betting card with recommendations."""
    
    __tablename__ = "parlay_cards"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Card details
    name = Column(String, nullable=True)  # "Today's Best Plays", etc.
    num_legs = Column(Integer, nullable=False)
    
    # Risk profile
    risk_level = Column(String, nullable=False)  # conservative, moderate, aggressive
    min_odds = Column(Float, nullable=False)  # Combined odds
    max_odds = Column(Float, nullable=False)
    
    # AI recommendations
    recommended_amount = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    combined_probability = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="active")  # active, completed, expired
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    legs_json = Column(JSON, nullable=True)  # Store leg details for quick access
    metadata_json = Column(JSON, nullable=True)
