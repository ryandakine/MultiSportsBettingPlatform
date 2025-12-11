"""
Database Configuration
======================
Configures SQLAlchemy engine and session factory.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to SQLite for easy local development, but support Postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./multisports_betting.db"
)

# SQLite implementation needs a specific check for ensure_related_objects
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
