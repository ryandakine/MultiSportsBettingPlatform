import pandas as pd
import numpy as np
import xgboost as xgb
import logging
from pathlib import Path
from sklearn.metrics import accuracy_score, log_loss, mean_absolute_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BacktestEngine")

class BacktestEngine:
    def __init__(self):
        self.processed_dir = Path("data/processed")
        self.results_dir = Path("reports/backtest")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self, sport):
        """Load and prep data for backtesting."""
        if sport == 'nba':
            path = self.processed_dir / "nba" / "nba_training_data.csv"
            if not path.exists(): return None
            df = pd.read_csv(path)
            # Ensure sorting
            if 'pd_date' in df.columns:
                 df['Date'] = pd.to_datetime(df['pd_date'])
            elif 'Date_HomeStats' in df.columns:
                 df['Date'] = pd.to_datetime(df['Date_HomeStats'])
            elif 'Date' in df.columns:
                 df['Date'] = pd.to_datetime(df['Date'])
            return df.sort_values('Date')
        
        elif sport == 'tennis':
            dfs = []
            for tour in ['atp', 'wta']:
                p = self.processed_dir / "tennis" / f"{tour}_training_data.csv"
                if p.exists():
                    d = pd.read_csv(p)
                    d['Tour'] = tour
                    dfs.append(d)
            if not dfs: return None
            df = pd.concat(dfs)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
                return df.sort_values('Date')
            return None

    def run_walk_forward(self, sport, start_year=2016):
        """Run Walk-Forward Validation (Train on past, Test on next year)."""
        df = self.load_data(sport)
        if df is None:
            logger.error(f"No data found for {sport}. Scraper might still be running.")
            return
            
        logger.info(f"Starting {sport.upper()} Backtest (Total Records: {len(df)})")
        years = sorted(df['Date'].dt.year.unique())
        test_years = [y for y in years if y >= start_year]
        
        metrics = []
        
        for year in test_years:
            # Expanding Window Training
            train_df = df[df['Date'].dt.year < year]
            test_df = df[df['Date'].dt.year == year]
            
            if len(train_df) < 500 or len(test_df) == 0:
                logger.warning(f"Skipping {year}: Insufficient training data ({len(train_df)})")
                continue
                
            logger.info(f"  Testing Season {year} (Train: {len(train_df)}, Test: {len(test_df)})")
            
            # Train
            model = self._train_model(train_df, sport)
            
            # Predict & Evaluate
            acc, loss, roi = self._evaluate(model, test_df, sport)
            logger.info(f"  ➡️ Result {year}: Accuracy={acc:.1%}, ROI={roi:.1%}")
            
            metrics.append({
                'Year': year,
                'Accuracy': acc,
                'ROI': roi,
                'TrainSamples': len(train_df)
            })
            
        # Summary
        if metrics:
            res_df = pd.DataFrame(metrics)
            print("\n=== Backtest Summary ===")
            print(res_df)
            res_df.to_csv(self.results_dir / f"{sport}_backtest_results.csv", index=False)
            logger.info(f"Results saved to {self.results_dir}")

    def _train_model(self, df, sport):
        drop_cols = ['Date', 'Target_HomeWin', 'Target_Win', 'HomeTeam', 'AwayTeam', 
                     'Player1', 'Player2', 'Tour', 'Odds1', 'Odds2', 
                     'Target_PointSpread', 'Target_TotalPoints', 'DateStr',
                     'HomePoints', 'AwayPoints']
                     
        X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore').select_dtypes(include=np.number)
        
        if sport == 'nba':
            y = df['Target_HomeWin']
        else:
            y = df['Target_Win']
            
        # Using typical params - can be grid-searched later
        model = xgb.XGBClassifier(
            n_estimators=100, 
            max_depth=3, 
            learning_rate=0.05, 
            eval_metric='logloss',
            n_jobs=-1
        )
        model.fit(X, y)
        return model

    def _evaluate(self, model, df, sport):
        drop_cols = ['Date', 'Target_HomeWin', 'Target_Win', 'HomeTeam', 'AwayTeam', 
                     'Player1', 'Player2', 'Tour', 'Odds1', 'Odds2', 
                     'Target_PointSpread', 'Target_TotalPoints', 'DateStr',
                     'HomePoints', 'AwayPoints']
                     
        X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore').select_dtypes(include=np.number)
        
        if sport == 'nba':
             y = df['Target_HomeWin']
        else:
             y = df['Target_Win']
             
        preds = model.predict(X)
        acc = accuracy_score(y, preds)
        loss = log_loss(y, model.predict_proba(X))
        
        roi = 0.0
        # ROI Calculation for Tennis (if odds available)
        if sport == 'tennis' and 'Odds1' in df.columns:
            # Flat betting simulation on Model Predictions
            # If Pred=1 (P1 Win), Bet 1u on Odds1.
            # If Result=1, Win (Odds1-1). Else Lose -1.
            
            pnl = []
            for i, (pred, actual) in enumerate(zip(preds, y)):
                if pred == 1: # Bet P1
                    odds = df.iloc[i].get('Odds1', 0)
                    if actual == 1: pnl.append(odds - 1)
                    else: pnl.append(-1)
                else: # Bet P2 (Target=0)
                    odds = df.iloc[i].get('Odds2', 0)
                    if actual == 0: pnl.append(odds - 1)
                    else: pnl.append(-1)
            
            if pnl:
                roi = sum(pnl) / len(pnl) # ROI per bet
        
        return acc, loss, roi

    def run_totals_backtest(self, sport, start_year=2016):
        df = self.load_data(sport)
        if df is None: return
        
        logger.info(f"Backtesting {sport.upper()} TOTALS...")
        years = sorted(df['Date'].dt.year.unique())
        test_years = [y for y in years if y >= start_year]
        
        metrics = []
        for year in test_years:
            train_df = df[df['Date'].dt.year < year]
            test_df = df[df['Date'].dt.year == year]
            
            if len(train_df) < 500: continue
            
            # Train Regressor
            drop = ['Date', 'HomePoints', 'AwayPoints', 'Target_HomeWin', 'Target_Win', 'Target_PointSpread', 'Target_TotalPoints', 'Target_TotalGames', 'HomeTeam', 'AwayTeam', 'Player1', 'Player2', 'Tour', 'Odds1', 'Odds2', 'DateStr', 'Notes', 'pd_date']
            X_train = train_df.drop(columns=[c for c in drop if c in train_df.columns], errors='ignore').select_dtypes(include=np.number)
            
            if sport == 'nba':
                y_train = train_df['Target_TotalPoints']
                y_test = test_df['Target_TotalPoints']
            else:
                if 'Target_TotalGames' not in train_df.columns: continue
                y_train = train_df['Target_TotalGames']
                y_test = test_df['Target_TotalGames']
            
            # Filter valid
            X_train = X_train[y_train > 0]
            y_train = y_train[y_train > 0]
            
            model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
            model.fit(X_train, y_train)
            
            # Predict
            X_test = test_df.drop(columns=[c for c in drop if c in test_df.columns], errors='ignore').select_dtypes(include=np.number)
            preds = model.predict(X_test)
            
            mae = mean_absolute_error(y_test, preds)
            logger.info(f"  Year {year}: MAE={mae:.2f}")
            metrics.append({'Year': year, 'MAE': mae})
            
        pd.DataFrame(metrics).to_csv(self.results_dir / f"{sport}_totals_backtest.csv", index=False)

if __name__ == "__main__":
    bt = BacktestEngine()
    # Run Tennis first (faster)
    bt.run_walk_forward('tennis')
    bt.run_walk_forward('nba')
    
    # Run Totals
    bt.run_totals_backtest('nba')
    bt.run_totals_backtest('tennis')
