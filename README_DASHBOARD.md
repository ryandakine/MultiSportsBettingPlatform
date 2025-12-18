# System Health Dashboard

## Overview

A simple HTML dashboard to monitor your betting system's health and status.

## Usage

### Option 1: Open directly in browser

Simply open `system_health_dashboard.html` in your web browser:

```bash
# On Linux/Mac
open system_health_dashboard.html
# or
xdg-open system_health_dashboard.html

# On Windows
start system_health_dashboard.html
```

### Option 2: Serve via Python (recommended)

```bash
# Python 3
python3 -m http.server 8080

# Then open: http://localhost:8080/system_health_dashboard.html
```

### Option 3: Access via FastAPI static files

Add the dashboard to your FastAPI static file serving (if configured).

## Features

- ✅ **System Health Status** - Overall system health indicator
- ✅ **Betting Engine Status** - Whether autonomous betting is running
- ✅ **Financial Overview** - Current balance, available balance, net profit, ROI
- ✅ **Performance Metrics** - Win rate, total bets, wins, losses
- ✅ **Active Bets** - Number of pending bets
- ✅ **Settings** - Current betting configuration
- ✅ **Auto-refresh** - Updates every 30 seconds automatically

## Configuration

The dashboard connects to:
- **Health endpoint**: `http://localhost:8000/health`
- **Betting status**: `http://localhost:8000/api/v1/betting/status/public`

If your server runs on a different port, edit the `API_BASE` constant in the HTML file:

```javascript
const API_BASE = 'http://localhost:YOUR_PORT/api/v1';
```

## Status Indicators

- 🟢 **Healthy & Running** - System is up and betting is active
- 🟡 **Healthy (Betting Stopped)** - System is up but betting is not running
- 🔴 **System Error** - Health check failed
- ⏸️ **Stopped** - System is not running

## Notes

- The dashboard uses public endpoints that don't require authentication
- Performance and ROI data currently shows mock values (0) - these endpoints require auth
- To show real performance data, either:
  1. Create public endpoints with limited data
  2. Add authentication to the dashboard
  3. Use the existing `/betting/status/public` endpoint and add more public endpoints as needed

