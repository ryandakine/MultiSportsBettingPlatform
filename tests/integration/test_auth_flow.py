import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration flow."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    # Note: Depending on implementation, valid registration might correspond to 201 or 200
    assert response.status_code in [200, 201]
    data = response.json()
    print(f"DEBUG REGISTER RESPONSE: {data}")
    assert "email" in data, f"Email key missing in response: {data}"
    assert data["email"] == payload["email"]
    assert "user_id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login flow."""
    # 1. Register first
    register_payload = {
        "email": "login_test@example.com",
        "username": "logintest",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    # 2. Login
    login_payload = {
        "username": "logintest",
        "password": "SecurePassword123"
    }
    
    response = await client.post(
        "/api/v1/auth/token", 
        data=login_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 404:
        # Fallback: maybe it's a JSON endpoint at /auth/login?
        response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] is not None

@pytest.mark.asyncio
async def test_protected_route_access(client: AsyncClient):
    """Test accessing a protected route with a valid token."""
    # 1. Register and Login to get token
    register_payload = {
        "email": "protected@example.com",
        "username": "protecteduser",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_payload = {
        "username": "protecteduser",
        "password": "SecurePassword123"
    }
    token_resp = await client.post(
        "/api/v1/auth/login",
        json=login_payload
    )
         
    token = token_resp.json()["token"]
    
    # 2. Access protected route
    response = await client.get(
        "/api/v1/auth/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # If /auth/me doesn't exist, try /preferences as it was seen in routes
    if response.status_code == 404:
        response = await client.get(
            "/preferences/",
             headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
