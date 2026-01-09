import pandas as pd
import requests
import logging
from pathlib import Path
import time
from datetime import timedelta, date
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NCAA_ESPN")

class NCAAESPNScraper:
    def __init__(self, sport_code='MBB'):
        # MBB or WBB
        self.sport_code = sport_code
        if sport_code == 'MBB':
            self.sport_slug = 'mens-college-basketball'
            self.fname = "ncaa_mbb_detailed.csv"
        else:
            self.sport_slug = 'womens-college-basketball'
            self.fname = "ncaa_wbb_detailed.csv"
            
        self.data_dir = Path("data/raw_detailed")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_history(self, start_year=2015, end_year=2025):
        logger.info(f"Starting ESPN API Scrape for {self.sport_code} ({start_year}-{end_year})")
        
        path = self.data_dir / self.fname
        processed_dates = set()
        
        # Initialize
        if not path.exists():
            with open(path, 'w') as f:
                # Dynamic columns? 
                # WBB has Q1-Q4. MBB has H1-H2.
                # I'll include P1-P4 to cover both.
                f.write("Date,GameID,Visitor,Home,VisScore,HomeScore,VisP1,VisP2,VisP3,VisP4,HomeP1,HomeP2,HomeP3,HomeP4\n")
        else:
            try:
                processed_dates = set(pd.read_csv(path, usecols=['Date'])['Date'].unique())
                logger.info(f"Resuming {self.sport_code}: {len(processed_dates)} dates done.")
            except: pass

        for year in range(start_year, end_year + 1):
            # Season: Nov 1 to Apr 8
            start_date = date(year-1, 11, 1)
            end_date = date(year, 4, 8)
            current_date = start_date
            
            while current_date <= end_date:
                dt_str = current_date.strftime("%Y-%m-%d") # Format for CSV
                api_dt = current_date.strftime("%Y%m%d") # Format for ESPN
                
                # Check resume
                # Note: CSV format might be different than loop? 
                # If CSV has YYYY-MM-DD, we match.
                if dt_str in processed_dates:
                    current_date += timedelta(days=1)
                    continue
                
                url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/{self.sport_slug}/scoreboard?dates={api_dt}&limit=500"
                
                try:
                    resp = self.session.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        events = data.get('events', [])
                        
                        day_recs = []
                        for evt in events:
                            try:
                                status = evt['status']['type']['state']
                                if status != 'post': continue # Only final
                                
                                comps = evt['competitions'][0]['competitors']
                                # Usually 0 is Home, 1 is Away? Or check 'homeAway' field.
                                home = next((c for c in comps if c['homeAway']=='home'), None)
                                away = next((c for c in comps if c['homeAway']=='away'), None)
                                
                                if not home or not away: continue
                                
                                # Linescores
                                h_lines = home.get('linescores', [])
                                a_lines = away.get('linescores', [])
                                
                                # Extract P1-P4
                                def get_p(lines, p):
                                    # Period is 1-based index in lines (usually)
                                    # But sometimes lines object has 'period': p
                                    val = next((x['value'] for x in lines if x.get('period') == p), 0)
                                    return val
                                
                                rec = {
                                    'Date': dt_str,
                                    'GameID': evt['id'],
                                    'Visitor': away['team']['abbreviation'],
                                    'Home': home['team']['abbreviation'],
                                    'VisScore': away['score'],
                                    'HomeScore': home['score'],
                                    'VisP1': get_p(a_lines, 1),
                                    'VisP2': get_p(a_lines, 2),
                                    'VisP3': get_p(a_lines, 3), # Halves will stick to P1/P2/P3/P4? 
                                    'VisP4': get_p(a_lines, 4), # MBB just has P1, P2. WBB has P1-P4.
                                    'HomeP1': get_p(h_lines, 1),
                                    'HomeP2': get_p(h_lines, 2),
                                    'HomeP3': get_p(h_lines, 3),
                                    'HomeP4': get_p(h_lines, 4)
                                }
                                day_recs.append(rec)
                            except: pass
                            
                        # Save Batch (Day)
                        if day_recs:
                            df_b = pd.DataFrame(day_recs)
                            # Handle column order to match header
                            cols = ["Date","GameID","Visitor","Home","VisScore","HomeScore","VisP1","VisP2","VisP3","VisP4","HomeP1","HomeP2","HomeP3","HomeP4"]
                            # Fill missing cols if any (already in dict)
                            df_b = df_b[cols]
                            df_b.to_csv(path, mode='a', header=(not path.exists() and path.stat().st_size == 0), index=False)
                            # logger.info(f"Saved {len(day_recs)} games for {dt_str}")
                
                    processed_dates.add(dt_str)
                    
                except Exception as e:
                    logger.error(f"Error {dt_str}: {e}")
                
                # Rate limit (ESPN is generous, but mild sleep)
                time.sleep(0.2)
                current_date += timedelta(days=1)

if __name__ == "__main__":
    import sys
    import threading
    
    # Run both if no args, or specific
    codes = ['MBB', 'WBB']
    
    # Arg support
    if len(sys.argv) > 1:
        codes = [sys.argv[1]]
        
    threads = []
    for c in codes:
        s = NCAAESPNScraper(c)
        t = threading.Thread(target=s.scrape_history, args=(2015, 2025))
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
