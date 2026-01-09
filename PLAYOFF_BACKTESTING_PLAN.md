# Playoff Bet Type Backtesting Plan

## Goal
Use backtesting to **prove** which bet types actually have edge in playoff games, not just theorize about it.

## The Problem
- Moneyline and over/under bets are what everyone bets → less edge (efficient markets)
- Need to find where the real edge exists in playoff games
- Theory isn't enough - need data-driven proof

## Backtesting Approach

### 1. Data Collection (Research Phase)
**Script**: `scripts/research_ncaa_playoff_patterns.py`

Collects:
- Historical playoff games (2014-2024+)
- Game results (scores, winners)
- Game metadata (round, teams, dates)
- Saves to: `data/playoff_research/playoff_games_*.json`

### 2. Backtesting (Analysis Phase)
**Script**: `scripts/backtest_playoff_bet_types.py`

Tests each bet type against historical data:
- **Moneyline**: Win/loss, ROI, win rate
- **Over/Under**: Win/loss, ROI, win rate
- **Spread**: Win/loss, ROI, win rate
- **Future**: First half, props, team totals (when data available)

### 3. What We Need for Real Backtesting

#### A. Historical Odds Data
- Get historical odds for each playoff game
- Sources:
  - The Odds API (if they provide historical data)
  - Sportsbook APIs (historical lines)
  - Web scraping (historical lines from sportsbook sites)
  - Paid data providers

#### B. Bet Outcome Calculation
For each bet type, calculate:
- **Moneyline**: Did our pick win? Calculate profit/loss
- **Over/Under**: Did over/under hit? Calculate profit/loss
- **Spread**: Did spread cover? Calculate profit/loss

#### C. Edge Calculation
- For each game, determine if we would have bet (based on edge/confidence)
- Calculate actual outcome vs expected outcome
- Track ROI, win rate, profit/loss

### 4. Expected Outputs

#### Performance Metrics Per Bet Type:
- Total bets placed
- Win rate (%)
- ROI (%)
- Total profit/loss
- Average edge
- **Has edge?** (yes/no based on positive ROI)

#### Findings:
- Which bet types have edge in playoffs?
- Which bet types should we avoid?
- Round-specific performance (semifinal vs championship)
- Recommended betting strategy

### 5. Integration

Once backtesting finds which bet types have edge:

1. **Update Playoff Detector**:
   - Prioritize bet types with proven edge
   - Adjust confidence/edge thresholds based on findings

2. **Update Autonomous Betting Engine**:
   - For playoff games, focus on bet types with edge
   - Skip or penalize bet types without edge

3. **Update Prediction Generation**:
   - Generate predictions for bet types with edge
   - Don't waste resources on bet types without edge

## Current Status

✅ **Framework Created**:
- `scripts/backtest_playoff_bet_types.py` - Backtesting engine structure
- Can test multiple bet types
- Analyzes results and generates reports

⚠️ **Needs Data**:
- Historical playoff games (collect via research script)
- Historical odds data (need to find/collect this)
- Implementation of bet outcome calculation

## Next Steps

1. **Run Research Script**: Collect playoff game data
   ```bash
   python3 scripts/research_ncaa_playoff_patterns.py
   ```

2. **Find Historical Odds Data**:
   - Research sources for historical odds
   - The Odds API, sportsbook APIs, data providers
   - May need to scrape or purchase data

3. **Implement Bet Outcome Calculation**:
   - Logic to determine win/loss for each bet type
   - Profit/loss calculation based on odds

4. **Run Backtesting**:
   ```bash
   python3 scripts/backtest_playoff_bet_types.py
   ```

5. **Integrate Findings**:
   - Update playoff detection/adjustment logic
   - Focus on bet types with proven edge

## Key Principle

> **No assumptions, only data-driven decisions.**
> 
> We don't guess which bet types have edge - we backtest and prove it.


