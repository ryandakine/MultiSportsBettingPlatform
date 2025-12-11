"""
Load Tests for Authentication
=============================
Tests concurrent authentication requests to validate async performance improvements.
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from src.main import app


@pytest_asyncio.fixture
async def client():
    """Provide async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
@pytest.mark.benchmark
class TestConcurrentAuth:
    """Test concurrent authentication performance."""
    
    async def test_concurrent_registrations(self, client):
        """Test 50 concurrent user registrations."""
        async def register_user(i):
            response = await client.post("/api/v1/auth/register", json={
                "username": f"testuser{i}",
                "email": f"test{i}@example.com",
                "password": "Test123456!",
                "confirm_password": "Test123456!"
            })
            return response.status_code
        
        # Create 50 concurrent registrations
        tasks = [register_user(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        successes = sum(1 for r in results if r == 200)
        
        # Should have high success rate (>90%)
        assert successes > 45, f"Only {successes}/50 registrations succeeded"
    
    async def test_concurrent_logins(self, client):
        """Test 100 concurrent login requests."""
        # First create a test user
        await client.post("/api/v1/auth/register", json={
            "username": "loadtest",
            "email": "loadtest@example.com",
            "password": "Test123456!",
            "confirm_password": "Test123456!"
        })
        
        async def login_user():
            response = await client.post("/api/v1/auth/login", json={
                "username": "loadtest",
                "password": "Test123456!"
            })
            return response.status_code, response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
        
        # Create 100 concurrent logins
        tasks = [login_user() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        successes = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)
        
        # Should handle all requests
        assert successes > 95, f"Only {successes}/100 logins succeeded"
    
    async def test_login_performance_under_load(self, client):
        """Test that login performance stays good under concurrent load."""
        # Create test user
        await client.post("/api/v1/auth/register", json={
            "username": "perftest",
            "email": "perftest@example.com",
            "password": "Test123456!",
            "confirm_password": "Test123456!"
        })
        
        import time
        
        async def timed_login():
            start = time.time()
            response = await client.post("/api/v1/auth/login", json={
                "username": "perftest",
                "password": "Test123456!"
            })
            elapsed = time.time() - start
            return response.status_code, elapsed
        
        # 50 concurrent requests
        tasks = [timed_login() for _ in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate average response time
        response_times = [r[1] for r in results if isinstance(r, tuple) and r[0] == 200]
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            
            # Should average < 200ms per request
            assert avg_time < 0.2, f"Average response time {avg_time:.3f}s too slow"


@pytest.mark.asyncio
@pytest.mark.benchmark
class TestConcurrentTokenValidation:
    """Test concurrent token validation."""
    
    async def test_concurrent_token_validations(self, client):
        """Test 100 concurrent token validation requests."""
        # Register and login to get token
        await client.post("/api/v1/auth/register", json={
            "username": "tokentest",
            "email": "tokentest@example.com",
            "password": "Test123456!",
            "confirm_password": "Test123456!"
        })
        
        login_response = await client.post("/api/v1/auth/login", json={
            "username": "tokentest",
            "password": "Test123456!"
        })
        
        token = login_response.json().get("token")
        
        async def validate_token():
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code
        
        # 100 concurrent validations
        tasks = [validate_token() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successes = sum(1 for r in results if r == 200)
        
        # All should succeed
        assert successes == 100, f"Only {successes}/100 validations succeeded"
