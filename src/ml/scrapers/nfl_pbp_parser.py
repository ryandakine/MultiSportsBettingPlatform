import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFLParser")

def parse_nfl_pbp(start=2015, end=2025):
    all_games = []
    
    for year in range(start, end + 1):
        url = f"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.parquet"
        logger.info(f"Processing NFL {year} PBP Data...")
        try:
            # Load specific columns to save memory
            df = pd.read_parquet(url, columns=['game_id', 'home_team', 'away_team', 'qtr', 'total_home_score', 'total_away_score'])
            
            # Group by Game
            grouped = df.groupby('game_id')
            
            for gid, group in grouped:
                rec = {
                    'GameID': gid, 
                    'Season': year, 
                    'HomeTeam': group['home_team'].iloc[0], 
                    'AwayTeam': group['away_team'].iloc[0]
                }
                
                h_cum = {0:0}
                a_cum = {0:0}
                
                for q in [1, 2, 3, 4]:
                    # Filter for quarter
                    q_plays = group[group['qtr'] == q]
                    
                    if not q_plays.empty:
                        # Max score in that quarter is the cumulative score at end of quarter
                        h_score = q_plays['total_home_score'].max()
                        a_score = q_plays['total_away_score'].max()
                    else:
                        # If no plays in Q4 (e.g. game ended? or OT only?), carry over
                        # Usually Q4 exists.
                        h_score = h_cum[q-1]
                        a_score = a_cum[q-1]
                    
                    h_cum[q] = h_score
                    a_cum[q] = a_score
                    
                    # Store Period Score (Current Cumulative - Previous Cumulative)
                    rec[f'HomeQ{q}'] = float(h_score) - float(h_cum[q-1])
                    rec[f'AwayQ{q}'] = float(a_score) - float(a_cum[q-1])
                
                # 1st Half Totals
                rec['Home1H'] = rec['HomeQ1'] + rec['HomeQ2']
                rec['Away1H'] = rec['AwayQ1'] + rec['AwayQ2']
                
                all_games.append(rec)
                
        except Exception as e:
            logger.error(f"Failed to process {year}: {e}")
            
    # Save
    path = Path("data/raw_detailed/nfl_detailed.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_games).to_csv(path, index=False)
    logger.info(f"Saved {len(all_games)} NFL games with quarter splits.")

if __name__ == "__main__":
    parse_nfl_pbp()
