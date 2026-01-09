import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class FeatureService:
    """
    Provides real-time features for live game predictions by looking up
    the latest historical stats for teams.
    """
    
    def __init__(self):
        self.nba_data_path = Path("data/processed/nba/nba_training_data.csv")
        self.tennis_data_paths = {
            'atp': Path("data/processed/tennis/atp_training_data.csv"),
            'wta': Path("data/processed/tennis/wta_training_data.csv")
        }
        self.nba_stats = {}
        self.tennis_stats = {}
        
    async def initialize(self):
        self._load_nba_stats()
        self._load_tennis_stats()

    def _load_nba_stats(self):
        if not self.nba_data_path.exists():
            return

        try:
            df = pd.read_csv(self.nba_data_path)
            # We want the LATEST stats for every team.
            # The Training Data has "Team_HomeStats" and "Last5_PF_HomeStats" etc.
            # We can extract a "Team State" dataframe.
            
            # Extract Home stats
            h = df[['pd_date', 'Team_HomeStats', 'Last5_PF_HomeStats', 'Last5_PA_HomeStats', 'Last5_WinPct_HomeStats']].copy()
            h.columns = ['Date', 'Team', 'Last5_PF', 'Last5_PA', 'Last5_WinPct']
            
            # Extract Away stats
            a = df[['pd_date', 'Team_AwayStats', 'Last5_PF_AwayStats', 'Last5_PA_AwayStats', 'Last5_WinPct_AwayStats']].copy()
            a.columns = ['Date', 'Team', 'Last5_PF', 'Last5_PA', 'Last5_WinPct']
            
            # Combine
            full = pd.concat([h, a]).sort_values('Date')
            
            # Drop entries where stats are NaN (start of season)
            full = full.dropna()
            
            # Keep last row per Team
            latest = full.groupby('Team').last().reset_index()
            
            # Convert to dict for fast lookup
            self.nba_stats = latest.set_index('Team').to_dict('index')
            logger.info(f"✅ Loaded latest NBA stats for {len(self.nba_stats)} teams")
            
        except Exception as e:
            logger.error(f"Error loading NBA stats: {e}")

    def _load_tennis_stats(self):
        """Load latest stats for Tennis players."""
        try:
            frames = []
            for tour in ['atp', 'wta']:
                path = self.tennis_data_paths[tour]
                if path.exists():
                    df = pd.read_csv(path)
                    # Helper to extract player stats from match rows
                    # Row: Player1, Player2, Rank1, Pts1...
                    p1 = df[['Date', 'Player1', 'Rank1', 'Pts1']].rename(columns={'Player1': 'Player', 'Rank1': 'Rank', 'Pts1': 'Pts'})
                    p2 = df[['Date', 'Player2', 'Rank2', 'Pts2']].rename(columns={'Player2': 'Player', 'Rank2': 'Rank', 'Pts2': 'Pts'})
                    combined = pd.concat([p1, p2])
                    
                    # Sort by Date and keep last
                    # Date format in csv usually YYYY-MM-DD from scraper
                    combined['Date'] = pd.to_datetime(combined['Date'], errors='coerce')
                    combined = combined.sort_values('Date').dropna(subset=['Date'])
                    
                    latest = combined.groupby('Player').last().reset_index()
                    
                    # Store in dict
                    # Using a combined dict for simplicity, or separate by tour?
                    # Player names usually distinct enough, or we check tour key.
                    stats_dict = latest.set_index('Player')[['Rank', 'Pts', 'Date']].to_dict('index')
                    self.tennis_stats.update(stats_dict)
            
            logger.info(f"✅ Loaded latest Tennis stats for {len(self.tennis_stats)} players")
            
        except Exception as e:
            logger.error(f"Error loading Tennis stats: {e}")

    def get_nba_features(self, home_team: str, away_team: str, game_date: datetime = None):
        """Construct feature vector for a matchup."""
        home_stats = self._find_team_stats(home_team)
        away_stats = self._find_team_stats(away_team)
        
        if not home_stats or not away_stats:
            return None
            
        # Calculate Rest Days
        # If game_date is None, assume today
        if not game_date:
            game_date = datetime.now()
        
        def calc_rest(last_date_str):
            try:
                last_date = pd.to_datetime(last_date_str)
                # Ensure we handle timezones or naive vs aware? 
                # Scraper uses naive usually. datetime.now() is naive local.
                # Let's strip time.
                delta = (game_date - last_date).days
                return max(1, min(delta, 10)) # Clip 1-10
            except:
                return 2 # Fallback
                
        rest_home = calc_rest(home_stats['Date'])
        rest_away = calc_rest(away_stats['Date'])
            
        features = pd.DataFrame([{
            'Last5_PF_HomeStats': home_stats['Last5_PF'],
            'Last5_PA_HomeStats': home_stats['Last5_PA'],
            'Last5_WinPct_HomeStats': home_stats['Last5_WinPct'],
            'RestDays_HomeStats': rest_home,
            
            'Last5_PF_AwayStats': away_stats['Last5_PF'],
            'Last5_PA_AwayStats': away_stats['Last5_PA'],
            'Last5_WinPct_AwayStats': away_stats['Last5_WinPct'],
            'RestDays_AwayStats': rest_away,
        }])
        
        return features

    def get_tennis_features(self, player1: str, player2: str, odds1: float, odds2: float):
        """Construct feature vector for Tennis match."""
        # Tennis logic expects: RankDiff, PtsDiff, Odds1, Odds2, Rank1, Rank2
        # (Based on tennis_features.py implementation)
        
        p1_stats = self.tennis_stats.get(player1)
        p2_stats = self.tennis_stats.get(player2)
        
        if not p1_stats or not p2_stats:
            # Try fuzzy match?
            # For now return None
            return None
            
        rank1 = p1_stats.get('Rank', 100)
        rank2 = p2_stats.get('Rank', 100)
        pts1 = p1_stats.get('Pts', 0)
        pts2 = p2_stats.get('Pts', 0)
        
        # Features must match training columns EXACTLY
        # In tennis_features.py:
        # features=['RankDiff', 'PtsDiff', 'Odds1', 'Odds2', 'Rank1', 'Rank2']
        
        # We need to handle 'Odds' scaling if the model expects normalized.
        # But XGBoost handles raw fine usually.
        
        # Features must match training columns EXACTLY
        # In tennis_features.py:
        # features=['RankDiff', 'PtsDiff', 'Odds1', 'Odds2', 'Rank1', 'Rank2', 'Surface_...']
        
        # We assume Hard court for now as default to prevent schema mismatch
        # Valid cols likely: Surface_Clay, Surface_Grass, Surface_Hard
        # (Depending on what get_dummies produced).
        # We'll just add common ones. XGBoost ignores extras usually, but needs missing ones.
        
        features = pd.DataFrame([{
            'RankDiff': rank2 - rank1,
            'PtsDiff': pts1 - pts2,
            'Odds1': odds1,
            'Odds2': odds2,
            'Rank1': rank1,
            'Rank2': rank2,
            'Surface_Clay': 0,
            'Surface_Grass': 0,
            'Surface_Hard': 1
        }])
        
        return features

    def _find_team_stats(self, team_name):
        """Find stats with basic fuzzy matching."""
        if team_name in self.nba_stats:
            return self.nba_stats[team_name]
            
        # Try simple partial
        for key in self.nba_stats:
            if team_name in key or key in team_name:
                return self.nba_stats[key]
                
        return None

feature_service = FeatureService()
