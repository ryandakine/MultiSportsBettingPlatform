
import pytest
from src.services.real_sports_service import RealSportsService

def test_real_sports_service_initialization():
    """Test that RealSportsService initializes correctly."""
    service = RealSportsService()
    assert service.BASE_URL == "https://site.api.espn.com/apis/site/v2/sports"
    assert "wnba" in service.ENDPOINTS
    assert "nba" not in service.ENDPOINTS
    assert service.ODDS_API_URL == "https://api.the-odds-api.com/v4/sports"

@pytest.mark.asyncio
async def test_endpoint_mapping():
    """Test that endpoint mapping logic works."""
    service = RealSportsService()
    assert service.ENDPOINTS["nfl"] == "/football/nfl/scoreboard"
    assert service.ENDPOINTS["ncaab"] == "/basketball/mens-college-basketball/scoreboard"
