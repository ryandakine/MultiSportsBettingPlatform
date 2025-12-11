"""
Database Configuration
======================
Configures SQLAlchemy engine and session factory.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

# Get DB URL from settings
DATABASE_URL = settings.database_url

# SQLite implementation needs a specific check for ensure_related_objects
connect_args = {}
pool_settings = {}

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support connection pooling the same way
else:
    # Production PostgreSQL pooling settings
    pool_settings = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "20")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 3600,   # Recycle connections after 1 hour
    }

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    connect_args=connect_args,
    future=True,
    **pool_settings
)

# Async Session Factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
