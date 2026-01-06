import pytest
import respx
from httpx import Response
from src.services.sports.nba import NBAService

@pytest.mark.asyncio
async def test_fetch_nba_odds():
    service = NBAService()
    
    # Mock data
    mock_response = [
        {
            "id": "game1",
            "sport_key": "basketball_nba",
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "bookmakers": []
        }
    ]
    
    with respx.mock(base_url="https://api.the-odds-api.com") as respx_mock:
        respx_mock.get("/v4/sports/basketball_nba/odds").mock(
            return_value=Response(200, json=mock_response)
        )
        
        odds = await service.fetch_odds()
        assert len(odds) == 1
        assert odds[0]["home_team"] == "Los Angeles Lakers"

def test_process_game_data():
    service = NBAService()
    raw_data = [{"id": "1", "home_team": "Celtics"}]
    processed = service.process_game_data(raw_data)
    assert len(processed) == 1
    assert processed[0]["home_team"] == "Celtics"
