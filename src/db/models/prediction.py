"""
Prediction Database Model
========================
SQLAlchemy model representing a betting prediction.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean
from src.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True, nullable=True) # Optional link to user who requested it
    
    sport = Column(String, index=True, nullable=False)
    prediction_text = Column(String, nullable=False)
    confidence = Column(String, nullable=False) # Stored as string enum (low/medium/high) or float
    reasoning = Column(String, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = Column(JSON, default=dict) # avoiding 'metadata' reserved keyword conflict
    
    outcome = Column(Boolean, nullable=True) # True=Win, False=Loss, None=Pending
    outcome_reported_at = Column(DateTime, nullable=True)
