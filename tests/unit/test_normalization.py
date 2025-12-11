
import pytest
from src.services.team_normalization import TeamNormalizationService

@pytest.fixture
def service():
    return TeamNormalizationService()

def test_normalize_name(service):
    # Basic cases
    assert service.normalize_name("Boston Celtics") == "boston celtics"
    assert service.normalize_name("  New York  Yankees  ") == "new york yankees"
    assert service.normalize_name("St. Louis Cardinals") == "st louis cardinals"
    assert service.normalize_name("A.C. Milan") == "ac milan"

def test_create_lookup_map(service):
    games = [
        {"id": 1, "home_team": "Boston Celtics", "away_team": "Lakers"},
        {"id": 2, "home_team": "New York Knicks", "away_team": "Heat"}
    ]
    
    lookup = service.create_lookup_map(games, 'home_team')
    
    assert "boston celtics" in lookup
    assert "new york knicks" in lookup
    assert lookup["boston celtics"]["id"] == 1

def test_find_match(service):
    games = [
        {"id": 1, "home_team": "Manchester United", "shortName": "Man Utd"},
        {"id": 2, "home_team": "Manchester City"}
    ]
    
    lookup = service.create_lookup_map(games, 'home_team')
    
    # Direct match
    match1 = service.find_match("Manchester United", lookup)
    assert match1 is not None
    assert match1["id"] == 1
    
    # Normalized match
    match2 = service.find_match("manchester united", lookup)
    assert match2 is not None
    assert match2["id"] == 1
    
    # Override match (assuming "man utd" -> "manchester united" is in overrides)
    match3 = service.find_match("Man Utd", lookup)
    assert match3 is not None
    assert match3["id"] == 1
    
    # No match
    match_none = service.find_match("Liverpool", lookup)
    assert match_none is None
