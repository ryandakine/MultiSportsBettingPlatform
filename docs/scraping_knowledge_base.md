# Scraping Knowledge Base & Best Practices

This document records the most effective data sources, API endpoints, and strategies discovered during the development of the Multi-Sports Betting Platform. Use this as a reference for future scraper maintenance or new feature development.

## 🏆 Verified Data Sources

### NCAA (Men's & Women's Basketball)
*   **Status**: ✅ **GOLD STANDARD**
*   **Source**: ESPN Internal API (Unofficial but Public)
*   **Why**: 
    *   **JSON Format**: Blazing fast parsing compared to HTML.
    *   **Detailed**: Contains **Linescores** (Period/Half scores) directly in the scoreboard response, eliminating the need for "N+1" requests (fetching a detail page for every game).
    *   **Reliable**: No aggressive WAF (Access Denied) or Captchas like `stats.ncaa.org`.
    *   **History**: Deep historical coverage (10+ years).
*   **Endpoints**:
    *   **Men's**: `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={YYYYMMDD}&limit=500`
    *   **Women's**: `http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard?dates={YYYYMMDD}&limit=500`
*   **Notes**: 
    *   Women's Basketball switched from Halves to Quarters in 2015-16. The API returns `linescores` array. For older games, it has 2 items (Halves). For newer, 4 items (Quarters). Code must adapt dynamically.

### NBA
*   **Status**: ✅ Reliable
*   **Source**: `nba_api` (Python Package) wrapper for `stats.nba.com`
*   **Endpoint**: `ScoreboardV2`
*   **Why**: Official data, extremely detailed.
*   **Caveats**: Strict Rate Limiting. Use `time.sleep(0.6)` minimum between calls. Supports resuming is critical.

### NHL
*   **Status**: ✅ Reliable
*   **Source**: NHL/SAP Web API
*   **Endpoint**: `https://api-web.nhle.com/v1/score/{YYYY-MM-DD}`
*   **Why**: Official JSON API. Contains period-by-period scoring in the `goals` list (requires counting goals per period) or sometimes summary.
*   **Caveats**: The `goals` list parsing is more robust than looking for a linescore object which might be missing for older games.

### NFL
*   **Status**: ✅ BEST
*   **Source**: `nflverse` (Parquet Files)
*   **Method**: Direct Download of PBP (Play-by-Play) files.
*   **Why**: 
    *   Scraping NFL.com is slow and difficult.
    *   `nflverse` provides pre-compiled, cleaned Parquet files of every play for 20+ years.
    *   Can extract Quarter scores by summing points in PBP data.
*   **Tools**: `pandas` + `pyarrow`.

## 🚫 Deprecated / Problematic Sources

*   **stats.ncaa.org**: 
    *   **Issue**: Aggressive WAF (Akamai/Edgesuite). strict 403 blocks for Python requests. Slow HTML parsing. 
    *   **Verdict**: Avoid unless absolutely necessary.
*   **Sports-Reference (HTML)**:
    *   **Issue**: Good for validation, but strict rate limits (20 req/min). Too slow for bulk historical scraping (takes days for 10 years).
    *   **Verdict**: Good for "Last 10 Games" or specific manual lookups, bad for Deep History.

## 🛠️ Best Practices

1.  **JSON over HTML**: Always look for a hidden JSON API (Network tab in DevTools -> XHR/Fetch) before writing a BeautifulSoup/HTML scraper.
2.  **Resume Logic**: Historical scrapers must check for existing files/IDs and **resume** processing. Do not restart from scratch.
3.  **Incremental Saving**: Save data to CSV every N records or every Day. Do not hold 10 years of data in RAM.
4.  **Logging**: Log "Zero Games Found" events to distinguish between "Broken Scraper" and "Empty Day".
5.  **User Feedback**: For long-running tasks, provide a dashboard or visual indicator (Desktop Shortcut) so the user knows the system is alive.
