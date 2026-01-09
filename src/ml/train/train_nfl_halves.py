import pandas as pd
import xgboost as xgb
import logging
from pathlib import Path
from sklearn.metrics import mean_absolute_error
import numpy as np
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFLTrainer")

def train_nfl_halves():
    path = Path("data/raw_detailed/nfl_detailed.csv")
    if not path.exists():
        logger.error("No NFL data found")
        return

    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} NFL games")
    
    # Create Team-Level DataFrame for Features
    home_df = df[['GameID', 'Season', 'HomeTeam', 'AwayTeam', 'Home1H', 'Away1H']].copy()
    home_df.columns = ['GameID', 'Season', 'Team', 'Opponent', 'PointsFor', 'PointsAgainst']
    home_df['IsHome'] = 1
    
    away_df = df[['GameID', 'Season', 'AwayTeam', 'HomeTeam', 'Away1H', 'Home1H']].copy()
    away_df.columns = ['GameID', 'Season', 'Team', 'Opponent', 'PointsFor', 'PointsAgainst']
    away_df['IsHome'] = 0
    
    combined = pd.concat([home_df, away_df]).sort_values(['Team', 'Season', 'GameID'])
    
    # Rolling Features
    combined['Avg1H_For'] = combined.groupby('Team')['PointsFor'].transform(lambda x: x.shift(1).rolling(3).mean())
    combined['Avg1H_Against'] = combined.groupby('Team')['PointsAgainst'].transform(lambda x: x.shift(1).rolling(3).mean())
    
    # Join back to Game
    # Merge Home Stats
    df = df.merge(combined[combined['IsHome']==1][['GameID', 'Avg1H_For', 'Avg1H_Against']], on='GameID', suffixes=('', '_Home'))
    # Merge Away Stats
    df = df.merge(combined[combined['IsHome']==0][['GameID', 'Avg1H_For', 'Avg1H_Against']], on='GameID', suffixes=('_Home', '_Away'))
    
    df = df.dropna()
    
    # Target: 1st Half Total
    y_total = df['Home1H'] + df['Away1H']
    X = df[['Avg1H_For_Home', 'Avg1H_Against_Home', 'Avg1H_For_Away', 'Avg1H_Against_Away']]
    
    # Train Total Model
    model_total = xgb.XGBRegressor(n_estimators=100, max_depth=3)
    model_total.fit(X, y_total)
    
    preds = model_total.predict(X)
    mae = mean_absolute_error(y_total, preds)
    logger.info(f"NFL 1st Half Total MAE: {mae:.2f}")
    
    # Save
    models_dir = Path("models/trained")
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_total, models_dir / "nfl_1h_total_model.pkl")
    
    # Train Spread Model (margin)
    y_spread = df['Home1H'] - df['Away1H'] # Home Margin
    model_spread = xgb.XGBRegressor(n_estimators=100, max_depth=3)
    model_spread.fit(X, y_spread)
    
    preds_s = model_spread.predict(X)
    mae_s = mean_absolute_error(y_spread, preds_s)
    logger.info(f"NFL 1st Half Spread MAE: {mae_s:.2f}")
    joblib.dump(model_spread, models_dir / "nfl_1h_spread_model.pkl")

if __name__ == "__main__":
    train_nfl_halves()
