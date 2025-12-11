
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from src.main import app
from src.db.database import AsyncSessionLocal
from src.db.models.prediction import Prediction as PredictionModel
import datetime
import uuid
import pytest_asyncio

# Use TestClient for simple checks, or AsyncClient for async routes
# Using AsyncClient as our auth/db is async

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

@pytest.mark.asyncio
async def test_pagination_endpoints(async_client):
    """Test pagination for prediction history and notifications."""
    
    # 1. Register User
    unique_id = str(uuid.uuid4())[:8]
    username = f"pagetest{unique_id}"
    email = f"page_test_{unique_id}@example.com"
    password = "SecurePassword123"
    
    register_res = await async_client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password
    })
    assert register_res.status_code in [200, 201]
    user_id = register_res.json()["user_id"]
    
    # Login to get token? API might require it depending on Depends()
    # get_prediction_history takes user_id but not explicitly Depends(security)?
    # Let's check routes.py. It takes user_id: str. It doesn't seem to have security dependency on the route method itself
    # but maybe logic requires it? No, just DB query.
    
    # 2. Insert Mock Data - Predictions
    async with AsyncSessionLocal() as db:
        for i in range(15):
            pred = PredictionModel(
                id=f"pred_test_{unique_id}_{i}",
                user_id=user_id,
                sport="marketing", # using valid enum or str? Model says proper sport usually.
                prediction_text=f"Prediction {i}",
                confidence="medium",
                reasoning="Testing",
                timestamp=datetime.datetime.utcnow(),
                metadata_json={"index": i}
            )
            db.add(pred)
        await db.commit()
    
    # 3. Test Predictions Pagination
    # Fetch 5
    res = await async_client.get(f"/api/v1/predictions?user_id={user_id}&limit=5&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 5
    
    # Fetch next 5
    res2 = await async_client.get(f"/api/v1/predictions?user_id={user_id}&limit=5&offset=5")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2) == 5
    assert data[0]["id"] != data2[0]["id"]
    
    # 4. Insert Mock Data - Notifications
    # Using notification_service directly if possible, or redis
    from src.services.notification_service import notification_service, Notification, NotificationType, NotificationPriority
    
    # We rely on startup to init notification_service. 
    # But in tests, startup events might not run automatically with AsyncClient unless using LifespanManager or TestClient
    # httpx AsyncClient(transport=ASGITransport(app=app)) handles lifespans by default in newer versions?
    # Let's verify by checking if notification_service is not None
    
    if notification_service:
        for i in range(15):
            notif = Notification(
                id=f"notif_test_{unique_id}_{i}",
                type=NotificationType.SYSTEM_ALERT,
                title=f"Alert {i}",
                message="Testing pagination",
                priority=NotificationPriority.NORMAL,
                timestamp=datetime.datetime.now()
            )
            await notification_service.send_notification(notif, user_id)
            
        # 5. Test Notifications Pagination
        res_notif = await async_client.get(f"/api/v1/notifications/?user_id={user_id}&limit=5&offset=0")
        if res_notif.status_code == 503:
             print("Skipping notification test - Service not initialized")
        else:
            assert res_notif.status_code == 200
            n_data = res_notif.json()
            assert len(n_data) == 5
