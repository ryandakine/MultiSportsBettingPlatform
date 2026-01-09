import pandas as pd
import time
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import requests
from io import StringIO

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NBAScraper")

class NBAScraper:
    """
    Scrapes historical NBA data for ML training.
    Sources: Basketball-Reference.com
    Features: Game Results (Target), Advanced Stats (Features)
    """
    
    BASE_URL = "https://www.basketball-reference.com/leagues"
    DATA_DIR = Path("data/raw/nba")
    DB_PATH = Path("data/nba.db")
    
    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_season_games(self, year: int):
        """
        Fetch game results for a specific season (e.g., 2024 for 2023-24).
        Column format: Date, Start (ET), Visitor/Neutral, PTS, Home/Neutral, PTS.1, ...
        """
        url = f"{self.BASE_URL}/NBA_{year}_games.html"
        logger.info(f"Fetching games from {url}")
        
        try:
            # Months are usually split by tabs, we might need to iterate months if main page is just a menu
            # But usually 'games.html' has a filter or full list.
            # Actually, standard structure is /leagues/NBA_{year}_games-{month}.html
            # But let's try reading the aggregate page first.
            
            # Basketball-Reference splits structure. We will iterate common months.
            months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
            all_games = []
            
            for month in months:
                month_url = f"{self.BASE_URL}/NBA_{year}_games-{month}.html"
                logger.info(f"  Fetching {month}...")
                
                try:
                    response = self.session.get(month_url)
                    if response.status_code == 404:
                         logger.debug(f"  No games in {month}")
                         continue
                         
                    if response.status_code != 200:
                        logger.warning(f"  Failed to fetch {month}: {response.status_code}")
                        continue
                        
                    tables = pd.read_html(StringIO(response.text))
                    if tables:
                        df = tables[0]
                        # Filter out headers repeated in rows
                        df = df[df['Date'] != 'Date']
                        df['Season'] = year
                        all_games.append(df)
                        
                    time.sleep(3) # Rate limit respect (20 req/min)
                    
                except Exception as e:
                    logger.warning(f"  Error fetching {month}: {e}")
                    
            if not all_games:
                return None
                
            full_df = pd.concat(all_games, ignore_index=True)
            
            # Clean Column Names
            # Columns usually: Date, Start (ET), Visitor/Neutral, PTS, Home/Neutral, PTS.1, ...
            full_df.rename(columns={
                'Visitor/Neutral': 'AwayTeam',
                'PTS': 'AwayPoints',
                'Home/Neutral': 'HomeTeam',
                'PTS.1': 'HomePoints'
            }, inplace=True)
            
            # Save raw
            full_df.to_csv(self.DATA_DIR / f"nba_games_{year}.csv", index=False)
            logger.info(f"✅ Saved {len(full_df)} games for {year}")
            
            return full_df
            
        except Exception as e:
            logger.error(f"Failed to fetch games for {year}: {e}")
            return None

    def fetch_advanced_stats(self, year: int):
        """
        Fetch advanced team stats (Pace, ORtg, DRtg).
        """
        url = f"{self.BASE_URL}/NBA_{year}_ratings.html"
        logger.info(f"Fetching stats from {url}")
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                tables = pd.read_html(StringIO(response.text))
                if tables:
                    df = tables[0]
                    # Cleanup: Remove multi-level header if present
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.droplevel(0)
                        
                    df['Season'] = year
                    df.to_csv(self.DATA_DIR / f"nba_stats_{year}.csv", index=False)
                    logger.info(f"✅ Saved advanced stats for {year}")
                    return df
            else:
                logger.error(f"Failed to fetch stats: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching stats for {year}: {e}")
            return None

    def run_backfill(self, start_year=2022, end_year=2025):
        """Scrape data for multiple seasons."""
        logger.info(f"Starting backfill from {start_year} to {end_year}")
        
        for year in range(start_year, end_year + 1):
            self.fetch_season_games(year)
            self.fetch_advanced_stats(year)
            time.sleep(5) # Pause between seasons

if __name__ == "__main__":
    scraper = NBAScraper()
    # Scrape last 10 completed seasons + current
    scraper.run_backfill(start_year=2015, end_year=2025)
