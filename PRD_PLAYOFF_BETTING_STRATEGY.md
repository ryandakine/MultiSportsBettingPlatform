# Product Requirements Document: Playoff Betting Strategy Enhancement

## Executive Summary

Develop and implement a data-driven playoff betting strategy that identifies which bet types have proven edge in college football playoff games, with a focus on finding value beyond standard moneyline and over/under bets that everyone else is betting.

---

## Background

### Problem Statement
- Moneyline and over/under bets are what everyone bets → efficient markets with less edge
- Need to find where the real edge exists in playoff games
- Theory isn't enough - need data-driven proof of edge
- Current system doesn't differentiate playoff games from regular season

### Business Value
- Higher win rates in playoff games by focusing on bet types with proven edge
- Better ROI by avoiding "public" bets with less value
- Competitive advantage through data-driven playoff strategy

---

## Goals & Objectives

### Primary Goals
1. **Identify bet types with proven edge** in playoff games through backtesting
2. **Implement playoff-specific betting logic** that prioritizes high-edge bet types
3. **Verify edge through historical data**, not assumptions

### Success Metrics
- Win rate improvement in playoff games (target: >55% for playoff-specific bets)
- ROI improvement (target: >15% ROI for playoff games)
- Reduction in "public" bet types (moneyline/over-under) during playoffs
- Increased focus on alternative bet types with proven edge

---

## Requirements

### Phase 1: Data Collection & Analysis ✅ COMPLETED
- [x] Create playoff game research script
- [x] Create playoff detection service
- [x] Recover existing backtesting data from external drive
- [x] Create backtesting framework for bet types

### Phase 2: Backtesting & Edge Verification (IN PROGRESS)

#### 2.1 Review Existing Backtesting Data
**Requirements:**
- Analyze existing backtesting scripts for playoff-specific logic
- Extract bet type performance data from historical backtests
- Identify which bet types were tested and their results
- Document findings from existing data

**Deliverables:**
- Analysis report of existing backtesting data
- Summary of bet type performance by round (semifinal, championship, etc.)
- List of bet types that showed edge in existing backtests

#### 2.2 Implement Comprehensive Bet Type Backtesting
**Requirements:**
- Test each bet type against historical playoff games:
  - Moneyline
  - Over/Under (Totals)
  - Spreads
  - First Half bets (if data available)
  - Prop bets (if data available)
  - Team totals (if data available)
- Use historical odds data for accurate backtesting
- Calculate win rate, ROI, and edge for each bet type
- Group results by playoff round (semifinal vs championship)

**Deliverables:**
- Backtesting results JSON files
- Performance reports per bet type
- Round-specific analysis (semifinal vs championship patterns)

#### 2.3 Edge Verification
**Requirements:**
- Only mark bet types as having "edge" if:
  - Positive ROI over sufficient sample size (min 20 games)
  - Win rate > 50% (or > implied probability + edge threshold)
  - Statistically significant results
- Document confidence levels for each finding
- Flag bet types without edge for exclusion

**Deliverables:**
- Edge verification report
- Confidence scores for each bet type
- Recommendations on which bet types to prioritize

### Phase 3: Integration (NEXT)

#### 3.1 Playoff Bet Type Prioritization
**Requirements:**
- Update playoff detector to flag bet types with proven edge
- Modify prediction generation to prioritize high-edge bet types for playoff games
- Skip or deprioritize bet types without edge during playoffs
- Log which bet types are being used and why

**Deliverables:**
- Updated playoff detector service
- Bet type prioritization logic
- Logging/monitoring for bet type selection

#### 3.2 Autonomous Betting Engine Updates
**Requirements:**
- Apply playoff-specific adjustments to single bets (moneyline, over/under)
- Require higher edge for "public" bet types (moneyline/over-under) in playoffs
- Prioritize alternative bet types with proven edge
- Adjust bet sizing based on bet type edge confidence

**Deliverables:**
- Updated autonomous betting engine
- Playoff-specific bet selection logic
- Bet sizing adjustments for playoff games

#### 3.3 Model Integration (if needed)
**Requirements:**
- Ensure lightgbm is properly installed and loadable
- Use trained models for predictions when available
- Fallback to odds-based calculations when models unavailable
- Log model usage for transparency

**Deliverables:**
- Verified lightgbm installation
- Model loading tests
- Model usage logging

### Phase 4: Testing & Validation

#### 4.1 Backtesting Validation
**Requirements:**
- Run backtests on historical playoff games
- Verify bet type performance matches expectations
- Compare playoff vs regular season performance
- Document any discrepancies or anomalies

#### 4.2 Paper Trading
**Requirements:**
- Run playoff betting strategy in paper trading mode
- Track performance by bet type
- Monitor edge detection accuracy
- Adjust thresholds based on real-world results

---

## Technical Specifications

### Data Requirements
- Historical playoff game results (2014-2024+)
- Historical odds data for playoff games (critical for accurate backtesting)
- Game metadata (round, teams, dates, scores)

### Dependencies
- `lightgbm` package (for NHL model - verify installation)
- Existing backtesting data from external drive
- Historical game data (ESPN API or stored data)

### File Structure
```
data/
  playoff_research/          # Research findings
  playoff_backtesting/       # Backtesting results
    existing_backtests/      # Recovered backtesting data
    results/                 # New backtesting results
    reports/                 # Analysis reports

scripts/
  research_ncaa_playoff_patterns.py
  backtest_playoff_bet_types.py

src/services/
  playoff_detector.py        # Playoff game detection
  autonomous_betting_engine.py  # Updated with playoff logic
```

---

## User Stories

### As a System Operator
- I want the system to automatically detect playoff games
- I want the system to prioritize bet types with proven edge in playoffs
- I want to see which bet types are being used and why
- I want to verify edge through backtesting, not assumptions

### As a Data Analyst
- I want to analyze which bet types have edge in playoff games
- I want to see performance by playoff round
- I want to verify findings through statistical analysis
- I want historical backtesting data to inform decisions

---

## Risks & Mitigations

### Risk: Insufficient Historical Data
**Mitigation:** Use existing backtesting data from external drive, supplement with ESPN API data

### Risk: Missing Historical Odds Data
**Mitigation:** Use available data sources, note limitations in reports, consider purchasing data if needed

### Risk: Small Sample Size for Some Bet Types
**Mitigation:** Only mark bet types as having edge with sufficient sample size (min 20 games), use confidence intervals

### Risk: Model Dependencies (lightgbm)
**Mitigation:** Verify installation, provide fallback logic if unavailable, document dependencies clearly

---

## Timeline & Priorities

### Immediate (Current Sprint)
1. ✅ Recover existing backtesting data
2. ✅ Create backtesting framework
3. 🔄 Review existing backtesting scripts
4. 🔄 Verify lightgbm installation

### Short Term (Next Sprint)
1. Analyze existing backtesting data
2. Implement comprehensive bet type backtesting
3. Verify edge through historical data
4. Document findings

### Medium Term (Future Sprint)
1. Integrate findings into betting engine
2. Update playoff detection and prioritization
3. Test in paper trading mode
4. Refine based on results

---

## Success Criteria

### Phase 2 Complete When:
- [ ] All bet types tested against historical playoff data
- [ ] Edge verified for at least 2 bet types with statistical significance
- [ ] Bet types without edge identified and documented
- [ ] Performance reports generated and reviewed

### Phase 3 Complete When:
- [ ] Playoff betting logic integrated into autonomous engine
- [ ] System prioritizes bet types with proven edge
- [ ] Logging shows bet type selection reasoning
- [ ] Lightgbm verified and working

### Overall Success:
- Playoff game win rate >55% (vs current baseline)
- ROI >15% for playoff games
- System automatically detects and handles playoff games differently
- All edge claims backed by historical data, not theory

---

## Notes

- Focus on **data-driven decisions** - no assumptions without proof
- **Moneyline and over/under are "public" bets** - expect less edge, require more edge to bet
- **Alternative bet types** may have more edge - need to find and verify through backtesting
- Existing backtesting data is valuable - analyze it thoroughly before building new tests
- Lightgbm needed for NHL model - verify it works but don't block on it for playoff work

---

## Appendix

### Related Documents
- `PLAYOFF_RESEARCH_PLAN.md` - Research approach for playoff patterns
- `PLAYOFF_BACKTESTING_PLAN.md` - Detailed backtesting plan
- `MODEL_RECOVERY_STATUS.md` - Model integration status

### Key Files
- `scripts/research_ncaa_playoff_patterns.py` - Research script
- `scripts/backtest_playoff_bet_types.py` - Backtesting framework
- `src/services/playoff_detector.py` - Playoff detection service
- `src/services/autonomous_betting_engine.py` - Betting engine (to be updated)


