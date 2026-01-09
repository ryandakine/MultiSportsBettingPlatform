import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TennisFeatures")

class TennisFeatureEngineer:
    """
    Processes raw Tennis data (ATP/WTA) into ML features.
    """
    RAW_DIR = Path("data/raw/tennis")
    PROCESSED_DIR = Path("data/processed/tennis")
    
    def __init__(self):
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
    def process_data(self):
        for tour in ['atp', 'wta']:
            files = list(self.RAW_DIR.glob(f"{tour}_*.csv"))
            if not files:
                continue
                
            dfs = [pd.read_csv(f) for f in files]
            full_df = pd.concat(dfs, ignore_index=True)
            
            # Feature Engineering
            processed_df = self._create_features(full_df)
            
            output = self.PROCESSED_DIR / f"{tour}_training_data.csv"
            processed_df.to_csv(output, index=False)
            logger.info(f"✅ Saved {tour.upper()} training data: {len(processed_df)} records")

    def _create_features(self, df):
        # Expected cols: Winner, Loser, WRank, LRank, Wpts, Lpts, Surface, Odds(B365W, B365L)
        
        # We need to create symmetric training data:
        # Row 1: PlayerA=Winner, PlayerB=Loser, Target=1
        # Row 2: PlayerA=Loser, PlayerB=Winner, Target=0 (flipped)
        # But to avoid data leakage and double counting, we randomly flip.
        
        data = []
        
        for _, row in df.iterrows():
            # Basic cleanup
            try:
                if pd.isna(row['Winner']) or pd.isna(row['Loser']):
                    continue
                    
                # Skip retired (Totals valid only for completed)
                comment = str(row.get('Comment', 'Completed'))
                if 'Ret' in comment or 'Walkover' in comment:
                    continue

                # Calculate Total Games
                total_games = 0
                for i in range(1, 6):
                    w_set = row.get(f'W{i}', 0)
                    l_set = row.get(f'L{i}', 0)
                    if pd.notna(w_set): total_games += w_set
                    if pd.notna(l_set): total_games += l_set
                
                # Flip coin
                if np.random.random() > 0.5:
                    p1 = row['Winner']
                    p2 = row['Loser']
                    p1_rank = row.get('WRank', 1000)
                    p2_rank = row.get('LRank', 1000)
                    p1_pts = row.get('WPts', 0)
                    p2_pts = row.get('LPts', 0)
                    p1_odds = row.get('B365W', row.get('PSW', 0))
                    p2_odds = row.get('B365L', row.get('PSL', 0))
                    target = 1
                else:
                    p1 = row['Loser']
                    p2 = row['Winner']
                    p1_rank = row.get('LRank', 1000)
                    p2_rank = row.get('WRank', 1000)
                    p1_pts = row.get('LPts', 0)
                    p2_pts = row.get('WPts', 0)
                    p1_odds = row.get('B365L', row.get('PSL', 0))
                    p2_odds = row.get('B365W', row.get('PSW', 0))
                    target = 0
                
                # Handle NaNs in ranks
                p1_rank = 1000 if pd.isna(p1_rank) else p1_rank
                p2_rank = 1000 if pd.isna(p2_rank) else p2_rank
                
                # Features
                feat = {
                    'Date': row.get('Date'),
                    'Player1': p1,
                    'Player2': p2,
                    'RankDiff': float(p2_rank) - float(p1_rank), # Positive if P1 is better (lower rank)
                    'Rank1': float(p1_rank),
                    'Rank2': float(p2_rank),
                    'PtsDiff': float(p1_pts) - float(p2_pts) if pd.notna(p1_pts) and pd.notna(p2_pts) else 0,
                    'Surface': row.get('Surface', 'Hard'), # Need One-Hot encoding later
                    'Odds1': float(p1_odds) if pd.notna(p1_odds) else 0.0,
                    'Odds2': float(p2_odds) if pd.notna(p2_odds) else 0.0,
                    'Odds2': float(p2_odds) if pd.notna(p2_odds) else 0.0,
                    'Target_Win': target,
                    'Target_TotalGames': total_games
                }
                data.append(feat)
                
            except Exception as e:
                continue
                
        return pd.DataFrame(data)

if __name__ == "__main__":
    engineer = TennisFeatureEngineer()
    engineer.process_data()
