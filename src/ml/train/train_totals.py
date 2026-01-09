import pandas as pd
import xgboost as xgb
import joblib
import logging
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TotalsTrainer")

class TotalsTrainer:
    def __init__(self):
        self.processed_dir = Path("data/processed")
        self.models_dir = Path("models/trained")
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def train_nba_totals(self):
        path = self.processed_dir / "nba" / "nba_training_data.csv"
        if not path.exists(): return
        df = pd.read_csv(path)
        
        # Features
        # Drop Leaks (Score components)
        drop_cols = ['Date', 'HomePoints', 'AwayPoints', 'Target_HomeWin', 'Target_Win', 
                     'Target_PointSpread', 'Target_TotalPoints', 'HomeTeam', 'AwayTeam', 
                     'DateStr', 'Notes', 'pd_date']
                     
        X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore').select_dtypes(include=['number'])
        y = df['Target_TotalPoints']
        
        logger.info(f"Training NBA Totals Model on {len(df)} games...")
        
        reg = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
        reg.fit(X, y)
        
        joblib.dump(reg, self.models_dir / "nba_totals_model.pkl")
        logger.info("✅ Saved NBA Totals Model")
        
        # Quick Validation
        preds = reg.predict(X)
        mae = mean_absolute_error(y, preds)
        logger.info(f"NBA MAE: {mae:.2f}")

    def train_tennis_totals(self):
        dfs = []
        for tour in ['atp', 'wta']:
            p = self.processed_dir / "tennis" / f"{tour}_training_data.csv"
            if p.exists(): dfs.append(pd.read_csv(p))
            
        if not dfs: return
        df = pd.concat(dfs)
        
        # Use Date drop
        drop_cols = ['Player1', 'Player2', 'Target_Win', 'Surface', 'Date', 'Target_TotalGames', 'Tour', 'Odds1', 'Odds2']
        if 'Surface' in df.columns:
            df = pd.get_dummies(df, columns=['Surface'], drop_first=True)
            
        X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore').select_dtypes(include=['number'])
        
        if 'Target_TotalGames' not in df.columns:
            logger.warning("Target_TotalGames not found in Tennis data. Need to re-run features.")
            return

        y = df['Target_TotalGames']
        
        # Drop rows where TotalGames is missing or 0
        mask = (y > 0)
        X = X[mask]
        y = y[mask]
        
        logger.info(f"Training Tennis Totals Model on {len(X)} matches...")
        reg = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
        reg.fit(X, y)
        
        joblib.dump(reg, self.models_dir / "tennis_totals_model.pkl")
        logger.info("✅ Saved Tennis Totals Model")
        
        preds = reg.predict(X)
        mae = mean_absolute_error(y, preds)
        logger.info(f"Tennis MAE: {mae:.2f}")

if __name__ == "__main__":
    t = TotalsTrainer()
    t.train_nba_totals()
    t.train_tennis_totals()
