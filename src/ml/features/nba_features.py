import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NBAFeatures")

class NBAFeatureEngineer:
    """
    Processes raw NBA game data into ML-ready feature vectors.
    """
    
    RAW_DIR = Path("data/raw/nba")
    PROCESSED_DIR = Path("data/processed/nba")
    
    def __init__(self):
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """Load and merge all raw game CSVs."""
        files = list(self.RAW_DIR.glob("nba_games_*.csv"))
        if not files:
            logger.warning("No raw data found!")
            return pd.DataFrame()
            
        dfs = []
        for f in files:
            try:
                df = pd.read_csv(f)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {f}: {e}")
                
        if not dfs:
            return pd.DataFrame()
            
        full_df = pd.concat(dfs, ignore_index=True)
        
        # Basic cleanup
        # Date cleaning
        # Handle 'Start (ET)' if needed
        # Ensure scores are numeric
        full_df['pd_date'] = pd.to_datetime(full_df['Date'], errors='coerce')
        full_df['HomePoints'] = pd.to_numeric(full_df['HomePoints'], errors='coerce')
        full_df['AwayPoints'] = pd.to_numeric(full_df['AwayPoints'], errors='coerce')
        
        # Drop rows with bad data (header rows, 'Playoffs', etc.)
        full_df = full_df.dropna(subset=['pd_date', 'HomePoints', 'AwayPoints'])
        
        full_df = full_df.sort_values('pd_date')
        
        return full_df

    def create_features(self):
        df = self.load_data()
        if df.empty:
            return
            
        logger.info(f"Processing {len(df)} games from {df['pd_date'].min()} to {df['pd_date'].max()}")
        
        # Transform to Team-Game level
        # Use pd_date for sorting to ensure chronological order
        
        # Home perspective
        home_df = df[['pd_date', 'Date', 'HomeTeam', 'HomePoints', 'AwayTeam', 'AwayPoints']].copy()
        home_df['Team'] = home_df['HomeTeam']
        home_df['Opponent'] = home_df['AwayTeam']
        home_df['PointsFor'] = home_df['HomePoints']
        home_df['PointsAgainst'] = home_df['AwayPoints']
        home_df['IsHome'] = 1
        home_df['Won'] = (home_df['HomePoints'] > home_df['AwayPoints']).astype(int)
        
        # Away perspective
        away_df = df[['pd_date', 'Date', 'HomeTeam', 'HomePoints', 'AwayTeam', 'AwayPoints']].copy()
        away_df['Team'] = away_df['AwayTeam']
        away_df['Opponent'] = away_df['HomeTeam']
        away_df['PointsFor'] = away_df['AwayPoints']
        away_df['PointsAgainst'] = away_df['HomePoints']
        away_df['IsHome'] = 0
        away_df['Won'] = (away_df['AwayPoints'] > home_df['HomePoints']).astype(int)
        
        # Combine and Sort by Team then Date (Chronological)
        team_logs = pd.concat([home_df, away_df]).sort_values(['Team', 'pd_date'])
        
        # Rolling Features
        rolling_stats = team_logs.groupby('Team').apply(self._calculate_rolling_metrics, include_groups=False)
        rolling_stats = rolling_stats.reset_index(drop=False) # Keep Team
        # Reset index restores 'Team' from groupby, but 'level_1' might be original index.
        # Check index preservation. Usually apply returns index aligned.
        
        # We need to recover the corresponding Game Identifier (Date + Team) to merge back.
        # Since we sorted team_logs, the rolling_stats *should* align if index was preserved.
        # But separate apply is safer if we just join on keys.
        
        # Better approach: Calculate on team_logs directly.
        
        # Re-implement without apply to avoid index issues:
        # Sort is already done.
        team_logs['Last5_PF'] = team_logs.groupby('Team')['PointsFor'].transform(lambda x: x.shift(1).rolling(5).mean())
        team_logs['Last5_PA'] = team_logs.groupby('Team')['PointsAgainst'].transform(lambda x: x.shift(1).rolling(5).mean())
        team_logs['Last5_WinPct'] = team_logs.groupby('Team')['Won'].transform(lambda x: x.shift(1).rolling(5).mean())
        team_logs['RestDays'] = team_logs.groupby('Team')['pd_date'].diff().dt.days.fillna(3)
        
        # Now merge back to get Game level features
        # Create unique join key per team-date
        # Use string version of pd_date to ensure format match, or just use pd_date
        
        final_df = self._merge_game_features(df, team_logs)
        
        output_path = self.PROCESSED_DIR / "nba_training_data.csv"
        final_df.to_csv(output_path, index=False)
        logger.info(f"✅ Saved processed features to {output_path} with shape {final_df.shape}")
        return final_df

    def _calculate_rolling_metrics(self, group):
        # Deprecated
        pass

    def _merge_game_features(self, original_games, team_stats):
        """Join Home and Away stats back to the game schedule."""
        
        # Using pd_date is safer if both have it. original_games has it from load_data.
        
        # Join Home Stats (Team=HomeTeam, Date=Date)
        original_games = pd.merge(
            original_games,
            team_stats[['pd_date', 'Team', 'Last5_PF', 'Last5_PA', 'Last5_WinPct', 'RestDays']],
            left_on=['pd_date', 'HomeTeam'],
            right_on=['pd_date', 'Team'],
            suffixes=('', '_Home')
        )
        
        # Join Away Stats
        original_games = pd.merge(
            original_games,
            team_stats[['pd_date', 'Team', 'Last5_PF', 'Last5_PA', 'Last5_WinPct', 'RestDays']],
            left_on=['pd_date', 'AwayTeam'],
            right_on=['pd_date', 'Team'],
            suffixes=('_HomeStats', '_AwayStats')
        )
        
        # Target Variables
        original_games['Target_HomeWin'] = (original_games['HomePoints'] > original_games['AwayPoints']).astype(int)
        original_games['Target_TotalPoints'] = original_games['HomePoints'] + original_games['AwayPoints']
        original_games['Target_PointSpread'] = original_games['HomePoints'] - original_games['AwayPoints']
        
        logger.info(f"Before dropna: {len(original_games)}")
        
        # Drop irrelevant columns causing NaN drops
        cols_to_drop = ['Notes', 'Unnamed: 6', 'Unnamed: 7', 'Attend.', 'LOG', 'Arena', 'Start (ET)']
        original_games = original_games.drop(columns=[c for c in cols_to_drop if c in original_games.columns], errors='ignore')

        logger.info(f"NaN counts after column drop:\n{original_games.isna().sum()}")
        
        # Drop rows with NaN (should only be early season games now)
        original_games = original_games.dropna()
        
        return original_games

if __name__ == "__main__":
    engineer = NBAFeatureEngineer()
    engineer.create_features()
