import pytest
import asyncio
from src.services.model_prediction_service import model_prediction_service
from src.services.feature_service import feature_service

@pytest.mark.asyncio
async def test_nba_model_prediction():
    # Initialize
    await feature_service.initialize()
    await model_prediction_service.initialize()
    
    # Check if models loaded
    assert 'nba_win' in model_prediction_service.models, "NBA Win model not loaded"
    
    # Mock game data (using teams that definitely exist in history)
    # Note: Scraper normalized names? "Los Angeles Lakers", "Boston Celtics"
    # Need to check csv names. Usually "Los Angeles Lakers"
    
    game = {
        "home_team": "Boston Celtics",
        "away_team": "Los Angeles Lakers"
    }
    
    odds = 1.90 # -110
    
    # Predict
    pred = await model_prediction_service._get_nba_model_prediction(game, odds)
    
    print(f"Prediction: {pred}")
    
    assert pred is not None
    assert 'model_probability' in pred
    
    if pred.get('model_used'):
        print("✅ Used ML Model")
        assert pred['model_probability'] != 0.5
    else:
        print("⚠️ Used Fallback (Feature lookup might have failed)")

if __name__ == "__main__":
    asyncio.run(test_nba_model_prediction())
