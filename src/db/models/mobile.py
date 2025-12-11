"""
Mobile Database Models
=====================
SQLAlchemy models for mobile-specific features, replacing the legacy mobile_api.db.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class MobileDevice(Base):
    """
    Represents a user's mobile device.
    Replaces legacy 'mobile_users' table.
    """
    __tablename__ = "mobile_devices"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    device_token = Column(String, nullable=False, unique=True, index=True)
    platform = Column(String, nullable=False)  # android, ios, etc.
    app_version = Column(String, nullable=False)
    os_version = Column(String, nullable=False)
    device_model = Column(String, nullable=False)
    
    push_enabled = Column(Boolean, default=True, nullable=False)
    notification_preferences = Column(JSON, default=dict)
    
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", backref="devices")

class Notification(Base):
    """
    History of push notifications sent to devices.
    Replaces legacy 'push_notifications' table.
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    type = Column(String, nullable=False) # prediction_update, bet_result, etc.
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    data = Column(JSON, default=dict)
    
    priority = Column(String, default="normal")
    ttl = Column(Integer, default=3600)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered = Column(Boolean, default=False)

class OfflineAction(Base):
    """
    Queue for actions performed while offline.
    Replaces legacy 'offline_actions' table.
    """
    __tablename__ = "offline_actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    action_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    synced = Column(Boolean, default=False, index=True)
    retry_count = Column(Integer, default=0)
    processed_at = Column(DateTime, nullable=True)
