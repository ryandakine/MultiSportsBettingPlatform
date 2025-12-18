# System Startup Checklist

## ✅ Completed
- [x] Parlay logging system (ParlayTracker service)
- [x] Daily parlay generation (2-leg, 3-leg, 6-leg)
- [x] Betting order optimized (daily picks first, then parlays)
- [x] Bet settlement service
- [x] Scheduled tasks for automated settlement
- [x] Game date and team info tracking for bets

## 🔍 To Verify/Complete

### 1. Database Migrations
- [ ] Check if `parlay_legs` table migration exists
- [ ] Run migrations if needed: `alembic upgrade head`
- [ ] Verify tables exist: `bets`, `parlay_legs`, `bankroll`

### 2. Prediction Source
- [ ] Verify `_get_predictions()` method is implemented in `autonomous_betting_engine.py`
- [ ] Ensure predictions come from head_agent or appropriate source
- [ ] Test that predictions have required fields: `sport`, `game_id`, `team`, `odds`, `probability`, `confidence`, `edge`, `game_date`, `home_team`, `away_team`

### 3. Bankroll Setup
- [ ] Initialize bankroll for user (if not exists)
- [ ] Script: `scripts/init_paper_trading.py` should work
- [ ] Verify bankroll has sufficient balance

### 4. Autonomous Betting Engine
- [ ] Test starting engine via API: `POST /api/v1/betting/start`
- [ ] Verify engine fetches predictions correctly
- [ ] Check that daily picks are placed first
- [ ] Verify parlays are built after daily picks
- [ ] Monitor logs for any errors

### 5. Scheduled Tasks
- [ ] Verify bet settlement runs hourly (already configured)
- [ ] Test manual settlement: `POST /api/v1/betting/settle`

### 6. Testing & Verification
- [ ] Test parlay generation script: `python3 scripts/generate_daily_parlays.py`
- [ ] View parlays: `python3 scripts/view_parlays.py --days 7`
- [ ] Check bet status: `GET /api/v1/betting/history`
- [ ] Verify parlays have legs stored correctly

## 🚀 Quick Start Commands

```bash
# 1. Run database migrations
cd /home/ryan/MultiSportsBettingPlatform
python3 -m alembic upgrade head

# 2. Initialize paper trading bankroll (if needed)
python3 scripts/init_paper_trading.py --user-id demo_user

# 3. Start the FastAPI server
python3 run.py
# OR
uvicorn src.main:app --reload --port 8000

# 4. Start autonomous betting (via API or ensure it auto-starts)
curl -X POST http://localhost:8000/api/v1/betting/start \
  -H "Content-Type: application/json" \
  -d '{"paper_trading": true, "enable_parlays": true}'

# 5. Check status
curl http://localhost:8000/api/v1/betting/status

# 6. View today's parlays
python3 scripts/view_parlays.py --days 1

# 7. Manually settle bets (if needed)
curl -X POST http://localhost:8000/api/v1/betting/settle?days_back=7
```

## 📝 Next Steps Priority

1. **Verify database migrations** - Most critical
2. **Check prediction source** - Engine needs predictions to work
3. **Test end-to-end flow** - Daily picks → Parlays
4. **Monitor logs** - Watch for any issues
5. **Verify settlement** - Ensure bets are settling correctly

