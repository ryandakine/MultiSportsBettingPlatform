import pandas as pd
from pathlib import Path
import datetime
import os

def check_status():
    raw_dir = Path("data/raw_detailed")
    files = {
        'NBA': 'nba_detailed.csv',
        'NHL': 'nhl_detailed.csv',
        'NFL': 'nfl_detailed.csv',
        'NCAAM': 'ncaa_mbb_detailed.csv',
        'NCAAW': 'ncaa_wbb_detailed.csv'
    }
    
    print(f"--- SCRAPER STATUS ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    # Check Logs for activity
    log_dir = raw_dir
    # nba_scrape.log, nhl_scrape.log
    
    for sport, fname in files.items():
        p = raw_dir / fname
        if p.exists():
            try:
                # Quick line count using wc -l? 
                # Or pandas with usecols
                # Check file size first
                size_mb = p.stat().st_size / (1024*1024)
                
                if size_mb > 500:
                    print(f"{sport}: File size {size_mb:.1f}MB (Too big to scan quick)")
                    continue
                    
                df = pd.read_csv(p, usecols=[0]) # Read first col
                count = len(df)
                
                # Estimate totals (10 years)
                # NBA: 1230 * 10 = 12300
                # NHL: 1312 * 10 = 13120
                # NFL: 272 * 10 = 2720
                estimates = {'NBA': 12300, 'NHL': 13120, 'NFL': 2720, 'NCAAM': 50000, 'NCAAW': 50000}
                est = estimates.get(sport, 10000)
                
                pct = min(100.0, (count / est) * 100)
                print(f"{sport}: {count} records | ~{pct:.1f}% Complete | File: {size_mb:.1f}MB")
                
            except Exception as e:
                print(f"{sport}: File exists but error reading: {e}")
        else:
            # Check if log active
            log_file = raw_dir / f"{sport.lower()}_scrape.log"
            if log_file.exists():
                print(f"{sport}: Running (Log exists, Data file not yet flushed)")
            else:
                print(f"{sport}: Not Started / No Data")

if __name__ == "__main__":
    check_status()
