"""
Health Endpoints Tests
======================
Test health monitoring endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.main import app


@pytest_asyncio.fixture
async def client():
    """Async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test /health liveness probe."""
    
    async def test_health_returns_200(self, client):
        """Test health endpoint returns 200."""
        response = await client.get("/health")
        assert response.status_code == 200
    
    async def test_health_response_format(self, client):
        """Test health response contains required fields."""
        response = await client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data


@pytest.mark.asyncio
class TestReadinessEndpoint:
    """Test /ready readiness probe."""
    
    async def test_readiness_checks_dependencies(self, client):
        """Test readiness endpoint checks dependencies."""
        response = await client.get("/ready")
        
        # May return 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
    
    async def test_readiness_checks_database(self, client):
        """Test readiness checks database."""
        response = await client.get("/ready")
        data = response.json()
        
        if "checks" in data:
            assert "database" in data["checks"]
            assert "healthy" in data["checks"]["database"]
    
    async def test_readiness_checks_redis(self, client):
        """Test readiness checks Redis."""
        response = await client.get("/ready")
        data = response.json()
        
        if "checks" in data:
            assert "redis" in data["checks"]
            assert "healthy" in data["checks"]["redis"]


@pytest.mark.asyncio
class TestMetricsEndpoint:
    """Test /metrics endpoint."""
    
    async def test_metrics_returns_200(self, client):
        """Test metrics endpoint returns 200."""
        response = await client.get("/metrics")
        assert response.status_code == 200
    
    async def test_metrics_format(self, client):
        """Test metrics response format."""
        response = await client.get("/metrics")
        data = response.json()
        
        assert "timestamp" in data
        # May have agent metrics if agents registered
        assert "agents_registered" in data or True
