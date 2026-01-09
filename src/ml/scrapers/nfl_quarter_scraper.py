import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFLScraper")

def scrape_nfl_quarters(start_year=2015, end_year=2025):
    # Lee Sharpe's NFL Games Data (Reliable Quarter/Overtime scores)
    url = "http://www.habitatring.com/games.csv"
    
    logger.info("Fetching NFL Games from nflverse...")
    try:
        df = pd.read_csv(url)
        # Filter years
        df = df[(df['season'] >= start_year) & (df['season'] <= end_year)]
        
        # Log columns to see what we have
        # logger.info(f"Columns: {df.columns.tolist()}")
        
        path = Path("data/raw_detailed")
        path.mkdir(parents=True, exist_ok=True)
        
        # Save raw dump
        output_path = path / "nfl_detailed.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} NFL games to {output_path}")
        
    except Exception as e:
        logger.error(f"Error fetching NFL data: {e}")

if __name__ == "__main__":
    scrape_nfl_quarters()
