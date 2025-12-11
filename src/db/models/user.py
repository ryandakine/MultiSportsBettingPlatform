"""
User Database Model
==================
SQLAlchemy model representing a user.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from src.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(JSON, default=lambda: {"count": 0, "last_attempt": None})
    locked_until = Column(DateTime, nullable=True)
    
    preferences = Column(JSON, default=dict)
