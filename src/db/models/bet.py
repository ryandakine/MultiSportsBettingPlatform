"""
Bet Database Models
===================
Track all bets placed, outcomes, and performance.
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from src.db.database import Base
import enum


class BetStatus(str, enum.Enum):
    """Bet status enum."""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSHED = "pushed"
    CANCELLED = "cancelled"


class BetType(str, enum.Enum):
    """Bet type enum."""
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    OVER_UNDER = "over_under"
    TOTAL = "total"  # Alias for over_under (legacy compatibility)
    PARLAY = "parlay"
    PROP = "prop"


class Bet(Base):
    """Individual bet model with full tracking."""
    
    __tablename__ = "bets"
    
    # Identity
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    is_autonomous = Column(Boolean, default=False)  # Auto vs manual
    
    # Sportsbook
    sportsbook = Column(String, nullable=False)  # draftkings, fanduel, etc.
    sportsbook_bet_id = Column(String, nullable=True)  # External bet ID
    
    # Game details
    sport = Column(String, nullable=False)
    game_id = Column(String, nullable=False)
    game_date = Column(DateTime, nullable=True)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    
    # Bet details
    bet_type = Column(SQLEnum(BetType), nullable=False)
    team = Column(String, nullable=True)  # Team bet on
    line = Column(Float, nullable=True)  # Spread or total line
    amount = Column(Float, nullable=False)  # Bet amount ($)
    odds = Column(Float, nullable=False)  # American odds (-110, +150)
    
    # AI prediction data
    predicted_probability = Column(Float, nullable=True)  # Model's predicted prob
    predicted_edge = Column(Float, nullable=True)  # Expected edge %
    model_confidence = Column(Float, nullable=True)  # Model confidence 0-1
    model_version = Column(String, nullable=True)  # Which model used
    
    # Outcome
    status = Column(SQLEnum(BetStatus), default=BetStatus.PENDING, index=True)
    actual_result = Column(String, nullable=True)  # Actual game result
    payout = Column(Float, nullable=True)  # Actual payout received
    roi = Column(Float, nullable=True)  # Return on this bet
    
    # Timestamps
    placed_at = Column(DateTime, server_default=func.now(), index=True)
    settled_at = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(String, nullable=True)


class Bankroll(Base):
    """Track bankroll and overall performance."""
    
    __tablename__ = "bankrolls"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    sportsbook = Column(String, nullable=False)
    
    # Balances
    current_balance = Column(Float, nullable=False)
    initial_deposit = Column(Float, nullable=False)
    
    # Lifetime stats
    total_wagered = Column(Float, default=0.0)
    total_won = Column(Float, default=0.0)
    total_lost = Column(Float, default=0.0)
    total_bets = Column(Integer, default=0)
    
    # Performance
    roi_percentage = Column(Float, default=0.0)  # Overall ROI
    win_rate = Column(Float, default=0.0)  # Win %
    average_edge = Column(Float, default=0.0)  # Avg predicted edge
    sharpe_ratio = Column(Float, nullable=True)  # Risk-adjusted returns
    max_drawdown = Column(Float, default=0.0)  # Worst drawdown %
    
    # Current state
    active_bets_count = Column(Integer, default=0)
    active_bets_amount = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)  # For new bets
    
    # Risk management
    max_bet_amount = Column(Float, default=0.0)  # Max single bet
    daily_loss_limit = Column(Float, default=0.0)  # Stop if hit
    daily_losses_today = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_bet_at = Column(DateTime, nullable=True)


class DailyPerformance(Base):
    """Track daily performance metrics."""
    
    __tablename__ = "daily_performance"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Daily stats
    bets_placed = Column(Integer, default=0)
    bets_won = Column(Integer, default=0)
    bets_lost = Column(Integer, default=0)
    amount_wagered = Column(Float, default=0.0)
    amount_won = Column(Float, default=0.0)
    amount_lost = Column(Float, default=0.0)
    daily_roi = Column(Float, default=0.0)
    
    # Ending balance
    ending_balance = Column(Float, default=0.0)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)
