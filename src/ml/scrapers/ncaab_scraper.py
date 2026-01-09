import pandas as pd
import requests
import logging
from pathlib import Path
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NCAABScraper")

def scrape_current_season():
    # Scrape 2025-2026 Season Games (Sample recent)
    # Target: Get Halves (1H, 2H)
    # Source: sports-reference boxscores
    
    # In a real deep run, we iterate all days.
    # For now, we scrape the last 7 days to get 'recent' data for immediate use.
    
    today = datetime.date(2026, 1, 7)
    dates = [today - datetime.timedelta(days=x) for x in range(1, 8)]
    
    all_games = []
    
    for dt in dates:
        url = f"https://www.sports-reference.com/cbb/boxscores/index.cgi?month={dt.month}&day={dt.day}&year={dt.year}"
        logger.info(f"Fetching {dt}...")
        try:
            dfs = pd.read_html(url)
            # The page might contain multiple tables.
            # Usually searching for tables with 'Final'
            pass
        except Exception as e:
            logger.error(f"Failed {dt}: {e}")
            
    # Placeholder: Saving what we find
    # pd.DataFrame(all_games).to_csv("data/raw_detailed/ncaab_recent.csv")
    logger.info("NCAAB Scrape Complete (Demo)")

if __name__ == "__main__":
    scrape_current_season()
