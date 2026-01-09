import pandas as pd
import xgboost as xgb
import joblib
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelTrainer")

class ModelTrainer:
    """Trains ML models for NBA and Tennis."""
    
    PROCESSED_DIR = Path("data/processed")
    MODELS_DIR = Path("models/trained")
    
    def __init__(self):
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
    def train_nba(self):
        data_path = self.PROCESSED_DIR / "nba" / "nba_training_data.csv"
        if not data_path.exists():
            logger.warning("NBA training data not found.")
            return

        df = pd.read_csv(data_path)
        
        # Features & Target
        # Drop columns that leak future info (Scores, etc.)
        drop_cols = ['HomePoints', 'AwayPoints', 'Target_HomeWin', 'Target_TotalPoints', 
                     'Target_PointSpread', 'Date', 'HomeTeam', 'AwayTeam', 'DateStr']
        
        X = df.drop(columns=[c for c in drop_cols if c in df.columns])
        
        # We need to handle strings if any (Team names usually dropped or encoded)
        # In merged features, we have 'Team', 'Team_Home', etc. - better drop non-numeric
        X = X.select_dtypes(include=['number'])
        
        y_win = df['Target_HomeWin']
        y_spread = df['Target_PointSpread']
        
        # Train Classifier (Win/Loss)
        logger.info(f"Training NBA Win Model on {len(df)} games...")
        clf = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, eval_metric='logloss')
        clf.fit(X, y_win)
        
        # Save
        joblib.dump(clf, self.MODELS_DIR / "nba_win_model.pkl")
        logger.info("✅ Saved NBA Win Model")
        
        # Train Regressor (Spread)
        logger.info("Training NBA Spread Model...")
        reg = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
        reg.fit(X, y_spread)
        joblib.dump(reg, self.MODELS_DIR / "nba_spread_model.pkl")
        logger.info("✅ Saved NBA Spread Model")

    def train_tennis(self):
        for tour in ['atp', 'wta']:
            data_path = self.PROCESSED_DIR / "tennis" / f"{tour}_training_data.csv"
            if not data_path.exists():
                continue
                
            df = pd.read_csv(data_path)
            
            # Features
            drop_cols = ['Player1', 'Player2', 'Target_Win', 'Surface', 'Date'] # Need OneHot for Surface if used
            
            # Simple OneHot for Surface
            if 'Surface' in df.columns:
                df = pd.get_dummies(df, columns=['Surface'], drop_first=True)
            
            X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
            y = df['Target_Win']
            
            # Train
            logger.info(f"Training {tour.upper()} Model on {len(df)} matches...")
            clf = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05)
            clf.fit(X, y)
            
            joblib.dump(clf, self.MODELS_DIR / f"tennis_{tour}_model.pkl")
            logger.info(f"✅ Saved {tour.upper()} Model")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_nba()
    trainer.train_tennis()
