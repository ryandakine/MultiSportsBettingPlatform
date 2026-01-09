#!/bin/bash
# Multi-Sport Scraper Manager (Resume Logic)

# Ensure we are in project dir
cd /home/ryan/MultiSportsBettingPlatform

echo "Checking Scraper Status..."

# Create log dir if missing
mkdir -p data/raw_detailed

# NBA
if pgrep -f "deep_scraper.py" > /dev/null; then
    echo "✅ NBA Scraper is running."
else
    echo "🚀 Starting NBA Scraper (Resumable)..."
    nohup python3 src/ml/scrapers/deep_scraper.py >> data/raw_detailed/nba_scrape.log 2>&1 &
fi

# NHL
if pgrep -f "nhl_period_scraper.py" > /dev/null; then
    echo "✅ NHL Scraper is running."
else
    echo "🚀 Starting NHL Scraper..."
    nohup python3 src/ml/scrapers/nhl_period_scraper.py >> data/raw_detailed/nhl_scrape.log 2>&1 &
fi

# NCAA
if pgrep -f "ncaa_deep_scraper.py" > /dev/null; then
    echo "✅ NCAA Scraper is running."
else
    echo "🚀 Starting NCAA Scrapers (MBB & WBB)..."
    nohup python3 src/ml/scrapers/ncaa_deep_scraper.py MBB >> data/raw_detailed/ncaa_mbb.log 2>&1 &
    nohup python3 src/ml/scrapers/ncaa_deep_scraper.py WBB >> data/raw_detailed/ncaa_wbb.log 2>&1 &
fi

echo "All scrapers are active. Check progress with: python3 check_scraper_status.py"
