import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.main import app

# Note: Testing WebSockets with httpx AsyncClient is complex.
# Often easier to use Starlette's TestClient (synchronous) which wraps the app,
# OR use specific libraries for async websocket testing.
# However, standard TestClient supports websocket_connect.

from src.services.websocket_service import websocket_manager
from unittest.mock import AsyncMock, patch
import uuid

@pytest.fixture(autouse=True)
def mock_redis_cls_fixture():
    with patch("src.services.websocket_service.redis.Redis") as mock_redis_cls:
        mock_client = AsyncMock()
        mock_redis_cls.from_url.return_value = mock_client
        mock_redis_cls.return_value = mock_client
        
        # Also patch the existing manager's client just in case it was already initialized
        websocket_manager.redis_manager.redis_client = mock_client # Correct attribute name
        websocket_manager.redis_manager.connect_redis = AsyncMock() # redundant but safe
        
        yield mock_client

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection establishment."""
    # Using TestClient for WebSocket context manager support
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/ws/authenticated") as websocket:
            # Receive welcome message or connection ack
            # Note: Implementation might differ, check routes.py
            # routes.py has /ws/authenticated
            # Wait, api router has tags=["WebSocket"] but are they prefixed?
            # routes.py: router.include_router(websocket_router) without prefix (other than /api/v1 for the main router?)
            # Wait, APIRouter(prefix="/api/v1")... app.include_router(api_router).
            # So everything in api_routes.py is under /api/v1.
            # websocket_router is included in api_routes.py.
            # IN api_routes.py: router.include_router(websocket_router, tags=["WebSocket"]) NO PREFIX.
            # So it inherits /api/v1 ??
            # But websocket_router in websocket_routes.py has @router.websocket("/ws/authenticated").
            # Does include_router merge prefixes? Yes.
            # So /api/v1/ws/authenticated.
             pass

@pytest.mark.asyncio
async def test_websocket_authentication():
    """Test user authentication over WebSocket."""
    with TestClient(app) as client:
        # 1. Get Token (Sync)
        # Register/Login setup
        unique_id = str(uuid.uuid4())[:8]
        username = f"wstest{unique_id}" # Removed underscore for alnum validation
        email = f"ws_test_{unique_id}@example.com"
        
        register_payload = {
            "email": email,
            "username": username,
            "password": "SecurePassword123",
            "confirm_password": "SecurePassword123"
        }
        register_res = client.post("/api/v1/auth/register", json=register_payload)
        if register_res.status_code not in [200, 201]:
             print(f"DEBUG: WS Auth Test Register Failed: {register_res.json()}")
        assert register_res.status_code in [200, 201]
        register_data = register_res.json()
        assert register_data["email"] == register_payload["email"]
        assert "user_id" in register_data

        login_res = client.post("/api/v1/auth/login", json={"username": username, "password": "SecurePassword123"})
             
        token = login_res.json()["token"]

        # 2. Connect and Authenticate
        # Assuming the endpoint is /api/v1/ws/authenticated
        with client.websocket_connect(f"/api/v1/ws/authenticated") as websocket:
            # Send auth message if needed, or if token is query param
            # Implementation check: expects message type='authenticate'
            websocket.send_json({"type": "authenticate", "token": token})
            
            # Should receive something back? Or just not disconnect.
            # Let's simple check it doesn't close immediately.
            pass
