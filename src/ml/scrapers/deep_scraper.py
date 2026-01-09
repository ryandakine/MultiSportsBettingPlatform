import pandas as pd
import requests
import time
import logging
from pathlib import Path
from nba_api.stats.endpoints import leaguegamelog, scoreboardv2
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepScraper")

class DeepScraper:
    def __init__(self):
        self.data_dir = Path("data/raw_detailed")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_nba_api(self, start_year=2015, end_year=2025):
        logger.info(f"Starting NBA API Deep Scrape ({start_year}-{end_year})")
        
        path = self.data_dir / "nba_detailed.csv"
        processed_dates = set()
        if path.exists():
            try:
                # NBA API returns GAME_DATE_EST usually (or GAME_DATE). Check schema.
                # If file is empty or corrupt, we ignore.
                df_exist = pd.read_csv(path)
                # Check for likely date columns
                if 'GAME_DATE_EST' in df_exist.columns:
                    processed_dates = set(pd.to_datetime(df_exist['GAME_DATE_EST']).dt.strftime('%m/%d/%Y'))
                    logger.info(f"Resuming: Found {len(processed_dates)} processed dates.")
            except Exception as e:
                logger.warning(f"Could not read existing file to resume: {e}")

        for year in range(start_year, end_year + 1):
            season_str = f"{year-1}-{str(year)[-2:]}"
            logger.info(f"Checking {season_str}...")
            
            try:
                log = leaguegamelog.LeagueGameLog(season=season_str, player_or_team_abbreviation='T').get_data_frames()[0]
                dates = log['GAME_DATE'].unique()
                
                # Filter dates
                dates_to_proc = [d for d in dates if pd.to_datetime(d).strftime('%m/%d/%Y') not in processed_dates]
                
                if not dates_to_proc:
                    logger.info(f"Season {season_str} already complete.")
                    continue
                    
                logger.info(f"Processing {len(dates_to_proc)} new dates in {season_str}...")
                
                batch = []
                for idx, dt in enumerate(dates_to_proc):
                    try:
                        dt_str = pd.to_datetime(dt).strftime("%m/%d/%Y")
                        # Skip if done (double check)
                        if dt_str in processed_dates: continue
                        
                        board = scoreboardv2.ScoreboardV2(game_date=dt_str, timeout=30).get_data_frames()
                        if len(board) > 1:
                            linesObject = board[1]
                            batch.append(linesObject)
                        
                        # Save batch every 10 dates
                        if len(batch) >= 10:
                            df_batch = pd.concat(batch, ignore_index=True)
                            df_batch.to_csv(path, mode='a', header=(not path.exists()), index=False)
                            processed_dates.update(set(pd.to_datetime(df_batch['GAME_DATE_EST']).dt.strftime('%m/%d/%Y')))
                            batch = []
                            logger.info(f"Saved batch. Progress: {idx}/{len(dates_to_proc)}")

                        time.sleep(0.6)
                    except Exception as e:
                        logger.error(f"Error {dt}: {e}")
                
                # Save residuals
                if batch:
                    df_batch = pd.concat(batch, ignore_index=True)
                    df_batch.to_csv(path, mode='a', header=(not path.exists()), index=False)
                    batch = []

            except Exception as e:
                logger.error(f"Error fetching season {season_str}: {e}")

    def scrape_nhl_api(self, start_year=2015, end_year=2025):
        # NHL API usage (Placeholders for next task)
        pass

if __name__ == "__main__":
    scraper = DeepScraper()
    # Run only NBA for now (Task 2)
    scraper.scrape_nba_api(2015, 2025)
