import pandas as pd
import requests
import logging
from pathlib import Path
import time
from datetime import timedelta, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NHLScraper")

class NHLPeriodScraper:
    def __init__(self):
        self.data_dir = Path("data/raw_detailed")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()

    def scrape_history(self, start_date="2015-10-01", end_date="2025-06-30"):
        dates = pd.date_range(start_date, end_date)
        logger.info(f"Scraping NHL Period Data from {start_date} to {end_date}")
        
        path = self.data_dir / "nhl_detailed.csv"
        processed_dates = set()
        
        # Resume Logic
        if path.exists():
            try:
                # Read just Date col to avoid full load
                df_ex = pd.read_csv(path, usecols=['Date'])
                processed_dates = set(df_ex['Date'].unique())
                logger.info(f"Resuming: {len(processed_dates)} dates already done.")
            except: pass
        
        batch = []
        
        # Filter: Skip Summer (July-Sept usually empty, but June has playoffs)
        valid_dates = [d for d in dates if d.month in [10,11,12,1,2,3,4,5,6]]
        
        for i, dt in enumerate(valid_dates):
            d_str = dt.strftime("%Y-%m-%d")
            
            # Skip if processed
            if d_str in processed_dates: continue
            
            url = f"https://api-web.nhle.com/v1/score/{d_str}"
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    games = data.get('games', [])
                    
                    for g in games:
                        if g.get('gameState') not in ['FINAL', 'OFF', 'OT']: continue
                        
                        # Parse Goals list to get Period Scores
                        goals = g.get('goals', [])
                        
                        # Helper for period count
                        def count_goals(team_abbr, pd_num):
                            return sum(1 for x in goals if x['period'] == pd_num and x.get('teamAbbrev') == team_abbr)

                        h_abbr = g['homeTeam']['abbrev']
                        a_abbr = g['awayTeam']['abbrev']

                        rec_home = {
                            'GameID': g['id'],
                            'Date': d_str,
                            'Team': h_abbr,
                            'Opponent': a_abbr,
                            'IsHome': 1,
                            'Final': g['homeTeam'].get('score', 0),
                            'P1': count_goals(h_abbr, 1),
                            'P2': count_goals(h_abbr, 2),
                            'P3': count_goals(h_abbr, 3)
                        }
                        rec_away = {
                            'GameID': g['id'],
                            'Date': d_str,
                            'Team': a_abbr,
                            'Opponent': h_abbr,
                            'IsHome': 0,
                            'Final': g['awayTeam'].get('score', 0),
                            'P1': count_goals(a_abbr, 1),
                            'P2': count_goals(a_abbr, 2),
                            'P3': count_goals(a_abbr, 3)
                        }
                        
                        batch.append(rec_home)
                        batch.append(rec_away)
                        
                # Batch Save (Every 20 dates or ~100 games)
                if len(batch) >= 100:
                    df_b = pd.DataFrame(batch)
                    df_b.to_csv(path, mode='a', header=(not path.exists()), index=False)
                    processed_dates.update(set(df_b['Date']))
                    batch = []
                    logger.info(f"Saved batch. Progress: {i}/{len(valid_dates)}")

            except Exception as e:
                # logger.error(f"Error {d_str}: {e}")
                pass
            
            # Rate limit
            time.sleep(0.1)
            
        # Final Flush
        if batch:
            df_b = pd.DataFrame(batch)
            df_b.to_csv(path, mode='a', header=(not path.exists()), index=False)
        logger.info("Done.")

if __name__ == "__main__":
    scraper = NHLPeriodScraper()
    scraper.scrape_history()
