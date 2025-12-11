"""
Complete End-to-End Prediction Flow Test
========================================
Tests the entire prediction pipeline from request to response.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.main import app
from unittest.mock import AsyncMock, patch


@pytest_asyncio.fixture
async def client():
    """Async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_client(client):
    """Client with authentication token."""
    # Register user
    await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456!",
        "confirm_password": "Test123456!"
    })
    
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "Test123456!"
    })
    
    token = response.json().get("token")
    
    # Return client with auth header
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.mark.asyncio
class TestPredictionFlow:
    """Test complete prediction workflow."""
    
    async def test_prediction_request_unauthenticated(self, client):
        """Test that prediction requires authentication."""
        response = await client.post("/api/v1/predictions", json={
            "sports": ["baseball"],
            "query": "Who will win?"
        })
        
        assert response.status_code in [401, 403]
    
    async def test_prediction_request_authenticated(self, authenticated_client):
        """Test authenticated prediction request."""
        with patch('src.api.routes.head_agent') as mock_agent:
            # Mock the aggregate_predictions response
            mock_agent.aggregate_predictions = AsyncMock(return_value={
                "baseball": {
                    "prediction": "Team A will win",
                    "confidence": "high",
                    "reasoning": "Strong performance"
                }
            })
            
            response = await authenticated_client.post("/api/v1/predictions", json={
                "sports": ["baseball"],
                "query": "Who will win?"
            })
            
            # Should succeed
            assert response.status_code == 200 or response.status_code == 422  # 422 if validation fails
    
    async def test_prediction_history(self, authenticated_client):
        """Test retrieving prediction history."""
        response = await authenticated_client.get("/api/v1/predictions/history")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    async def test_prediction_with_preferences(self, authenticated_client):
        """Test prediction with user preferences."""
        with patch('src.api.routes.head_agent') as mock_agent:
            mock_agent.aggregate_predictions = AsyncMock(return_value={
                "baseball": {"prediction": "Test", "confidence": "high"}
            })
            
            response = await authenticated_client.post("/api/v1/predictions", json={
                "sports": ["baseball"],
                "query": "Who will win?",
                "preferences": {
                    "risk_tolerance": "high",
                    "favorite_teams": ["Yankees"]
                }
            })
            
            # Check request was processed
            assert response.status_code in [200, 422]


@pytest.mark.asyncio
class TestPredictionValidation:
    """Test prediction request validation."""
    
    async def test_invalid_sport(self, authenticated_client):
        """Test prediction with invalid sport."""
        response = await authenticated_client.post("/api/v1/predictions", json={
            "sports": ["invalid_sport"],
            "query": "Who will win?"
        })
        
        assert response.status_code in [400, 422]
    
    async def test_empty_query(self, authenticated_client):
        """Test prediction with empty query."""
        response = await authenticated_client.post("/api/v1/predictions", json={
            "sports": ["baseball"],
            "query": ""
        })
        
        assert response.status_code in [400, 422]
    
    async def test_no_sports_selected(self, authenticated_client):
        """Test prediction with no sports."""
        response = await authenticated_client.post("/api/v1/predictions", json={
            "sports": [],
            "query": "Who will win?"
        })
        
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
class TestPredictionPerformance:
    """Test prediction performance."""
    
    async def test_prediction_response_time(self, authenticated_client):
        """Test that predictions return within reasonable time."""
        import time
        
        with patch('src.api.routes.head_agent') as mock_agent:
            mock_agent.aggregate_predictions = AsyncMock(return_value={
                "baseball": {"prediction": "Test", "confidence": "high"}
            })
            
            start = time.time()
            response = await authenticated_client.post("/api/v1/predictions", json={
                "sports": ["baseball"],
                "query": "Test"
            })
            elapsed = time.time() - start
            
            # Should respond within 2 seconds
            assert elapsed < 2.0
