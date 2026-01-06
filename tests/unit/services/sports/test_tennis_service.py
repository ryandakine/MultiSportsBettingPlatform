import pytest
import respx
from httpx import Response
from src.services.sports.tennis import TennisService

@pytest.mark.asyncio
async def test_fetch_atp_odds():
    service = TennisService("tennis_atp")
    
    mock_response = [
        {
            "id": "match1", 
            "sport_key": "tennis_atp",
            "home_team": "Novak Djokovic",
            "away_team": "Carlos Alcaraz",
            "bookmakers": []
        }
    ]
    
    with respx.mock(base_url="https://api.the-odds-api.com") as respx_mock:
        respx_mock.get("/v4/sports/tennis_atp/odds").mock(
            return_value=Response(200, json=mock_response)
        )
        
        odds = await service.fetch_odds()
        assert len(odds) == 1
        assert odds[0]["home_team"] == "Novak Djokovic"

@pytest.mark.asyncio
async def test_fetch_wta_odds():
    service = TennisService("tennis_wta")
    
    mock_response = [{"id": "match2", "sport_key": "tennis_wta"}]
    
    with respx.mock(base_url="https://api.the-odds-api.com") as respx_mock:
        respx_mock.get("/v4/sports/tennis_wta/odds").mock(
            return_value=Response(200, json=mock_response)
        )
        
        odds = await service.fetch_odds()
        assert len(odds) == 1
