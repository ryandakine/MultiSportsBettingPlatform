import pytest
import asyncio
import os
import sys
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.db.database import Base, get_db
from src.config import settings

# Use an in-memory SQLite database for testing to avoid messing with real data
# check_same_thread=False is needed for SQLite with asyncio which runs on different threads
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"



@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}, 
        pool_pre_ping=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        await session.begin()
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with the database session overridden."""
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("THE_ODDS_API_KEY", "test_key")
    monkeypatch.setenv("ESPN_API_KEY", "test_key")
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
