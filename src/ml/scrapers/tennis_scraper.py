import pandas as pd
import requests
import io
import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TennisScraper")

class TennisScraper:
    """
    Scrapes historical ATP/WTA match data from Tennis-Data.co.uk.
    Includes Odds, Ranking, Match Stats.
    """
    
    BASE_URL = "http://www.tennis-data.co.uk"
    DATA_DIR = Path("data/raw/tennis")
    
    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
    def fetch_data(self, start_year=2023, end_year=2025):
        """
        Download CSVs for specified years.
        Example URL: http://www.tennis-data.co.uk/2023/2023.xlsx (or .csv)
        Usually follows format: /{year}/{year}.xlsx (ATP) and /{year}/wta{year}.csv (WTA? Need to verify)
        
        Tennis-Data.co.uk URL patterns have varied.
        Common pattern: 
        ATP: http://www.tennis-data.co.uk/{year}/{year}.xlsx
        WTA: http://www.tennis-data.co.uk/{year}/w{year}.xlsx
        """
        
        for year in range(start_year, end_year + 1):
            # ATP
            self._download_file(year, "atp")
            time.sleep(2)
            
            # WTA
            self._download_file(year, "wta")
            time.sleep(2)

    def _download_file(self, year, tour):
        """Download single season file."""
        # Setup file names
        if tour == "atp":
            url = f"{self.BASE_URL}/{year}/{year}.xlsx"
            filename = f"atp_{year}.xlsx"
        else:
            url = f"{self.BASE_URL}/{year}/w{year}.xlsx"
            filename = f"wta_{year}.xlsx"
            
        logger.info(f"Downloading {tour.upper()} {year} from {url}...")
        
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                save_path = self.DATA_DIR / filename
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ Saved {filename}")
                
                # Verify we can read it (transform to CSV for easier use later)
                try:
                    df = pd.read_excel(save_path)
                    csv_path = self.DATA_DIR / filename.replace('.xlsx', '.csv')
                    df.to_csv(csv_path, index=False)
                    logger.info(f"   Converted to CSV: {len(df)} matches")
                except Exception as e:
                    logger.warning(f"   Could not convert to CSV (might be empty or format changed): {e}")

            elif response.status_code == 404:
                logger.warning(f"⚠️ File not found for {year} (Season might not be complete)")
            else:
                logger.error(f"❌ Failed to download {year}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error downloading {year}: {e}")

if __name__ == "__main__":
    scraper = TennisScraper()
    # Scrape 2015-2025
    scraper.fetch_data(start_year=2015, end_year=2025)
