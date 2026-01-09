"""
License Application Model
=========================
Stores license applications from marketing site.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from src.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class LicenseApplication(Base):
    """License application from marketing site."""
    
    __tablename__ = "license_applications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Applicant info
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    
    # Application details
    experience = Column(Text, nullable=True)  # Betting experience
    interest = Column(Text, nullable=True)  # Why interested
    
    # Status
    status = Column(String, default="pending", nullable=False, index=True)  # pending, approved, rejected
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Payment info (after approval)
    payment_status = Column(String, default="not_started", nullable=False)  # not_started, pending, completed
    payment_id = Column(String, nullable=True)
    monero_address = Column(String, nullable=True)
    payment_amount = Column(String, nullable=True)  # Amount in XMR
    
    # License info (after payment)
    license_key = Column(String, nullable=True, unique=True, index=True)
    license_activated = Column(Boolean, default=False)
    license_activation_date = Column(DateTime, nullable=True)
    
    # Legal
    monero_acknowledged = Column(Boolean, default=False)
    nda_signed = Column(Boolean, default=False)
    nda_signed_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)




