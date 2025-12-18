# Automatic Daily Betting Setup ✅

## Configuration Complete!

The system is now configured to **run automatically every day** without any manual intervention.

## How It Works

### 1. Auto-Start on Server Launch
When you start the FastAPI server (`python3 run.py`), the autonomous betting engine will automatically start if enabled.

### 2. Daily Execution Logic
- **Checks once per day** for new predictions
- Places daily picks (straight bets) first
- Then builds parlays (2-leg, 3-leg, 6-leg)
- **Waits until midnight** before checking again
- Prevents duplicate betting on the same day

### 3. Environment Configuration

Create a `.env` file (or set environment variables):

```bash
# Enable/disable automatic betting
AUTO_BETTING_ENABLED=true

# User ID for autonomous betting
AUTO_BETTING_USER_ID=demo_user

# Paper trading mode (true = safe, false = LIVE betting)
AUTO_BETTING_PAPER_TRADING=true
```

### 4. Default Behavior
- ✅ **Enabled by default** (if `AUTO_BETTING_ENABLED` not set)
- ✅ **Paper trading by default** (safe mode)
- ✅ **User**: `demo_user` (unless `AUTO_BETTING_USER_ID` is set)

## Daily Cycle

1. **Server starts** → Autonomous betting engine starts automatically
2. **Checks for predictions** → Fetches recent predictions from database
3. **Places daily picks** → Best individual bets (straight bets)
4. **Builds parlays** → 2-leg, 3-leg, and 6-leg parlays
5. **Waits until tomorrow** → Sleeps until midnight, then repeats

## Monitoring

### Check Status
```bash
# View today's bets
python3 scripts/view_parlays.py --days 1

# Check betting status via API
curl http://localhost:8000/api/v1/betting/status
```

### Logs
The system logs all activities:
- When bets are placed
- When parlays are built
- When waiting until next day
- Any errors or issues

## Disabling Auto-Betting

If you want to disable automatic betting:

1. **Set environment variable:**
   ```bash
   export AUTO_BETTING_ENABLED=false
   ```

2. **Or in `.env` file:**
   ```
   AUTO_BETTING_ENABLED=false
   ```

3. **Or start manually via API:**
   ```bash
   POST /api/v1/betting/start
   ```

## Safety Features

✅ **Paper Trading Default** - Starts in safe mode
✅ **Daily Limits** - Won't bet if daily loss limit hit
✅ **No Duplicates** - Checks if bets already placed today
✅ **Bankroll Protection** - Verifies bankroll exists before betting

## Next Steps

1. **Start the server:**
   ```bash
   python3 run.py
   ```

2. **That's it!** The system will now:
   - Start automatically when server starts
   - Place bets every day
   - Wait between cycles
   - Log everything

3. **Monitor via:**
   - Server logs
   - API endpoints
   - Database queries
   - View scripts

## Summary

🎯 **Set it and forget it!**

The system will now:
- ✅ Start automatically with the server
- ✅ Run once per day
- ✅ Place daily picks and parlays
- ✅ Wait until next day
- ✅ Repeat automatically

No manual intervention needed! 🚀

