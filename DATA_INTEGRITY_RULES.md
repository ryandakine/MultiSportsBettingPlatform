# Data Integrity Rules - Project Wide

## CRITICAL RULE: NO SYNTHETIC DATA

**This rule applies to ALL code, scripts, services, and AI interactions in this project.**

## Core Principle

> **When data is missing or unavailable, FAIL GRACEFULLY AND ALERT IMMEDIATELY rather than inventing values.**
> 
> It is BETTER to skip a bet, prediction, or operation than to use synthetic/mocked data.
> 
> **Missing data = System failure** that requires immediate attention. We don't just fail gracefully - we alert, track, and monitor data quality issues.

## Rules

### 1. Betting Data Validation

- **NEVER** use default values for missing odds, lines, or probabilities
- **NEVER** invent game IDs, team names, or dates
- **NEVER** substitute placeholder values like -110 odds when real odds are unavailable
- **ALWAYS** validate data from real API sources (ESPN, The Odds API) before use
- **ALWAYS** include API verification flags in metadata

### 2. Over/Under Bet Requirements

- Line MUST be positive (totals are always positive, e.g., 45.5, 220.5)
- Line MUST NOT be negative (negative lines like -7.5 are SPREAD bets, not totals)
- Team field MUST be "Over" or "Under" (NOT a team name like "Chiefs" or "Lakers")
- Reject any over/under bet that violates these rules

### 3. Spread Bet Requirements

- Line MUST be present (can be positive or negative)
- Team MUST match either home_team or away_team from the game
- Reject bets where team doesn't match game teams

### 4. Moneyline Bet Requirements

- Team MUST match either home_team or away_team from the game
- Odds MUST come from verified API source
- Reject bets with default odds (-110) unless verified from API

### 5. Data Source Tracking

All prediction/betting data must include:
- `api_verified`: Boolean flag indicating data came from API
- `odds_source`: Source of odds data (e.g., "the_odds_api", "espn")
- `metadata_json`: Should contain source verification

### 6. Validation Before Bet Placement

**ALWAYS** validate data using `DataValidationService` before:
- Placing any bet
- Creating any prediction
- Storing any betting data

### 7. Error Handling & Alerting

When validation fails:
- **DO**: Log at CRITICAL level with full context
- **DO**: Record a data quality incident via `DataQualityMonitor`
- **DO**: Alert immediately (missing data = system failure)
- **DO**: Skip the bet/prediction gracefully (but alert!)
- **DO**: Track the incident in `data_quality_incidents` table
- **DO**: Return False/None rather than proceeding
- **DON'T**: Substitute default values
- **DON'T**: Use fallback/mock data
- **DON'T**: Continue with invalid data "just to make it work"
- **DON'T**: Silently skip - always alert and track

### 8. Data Quality Monitoring

The `DataQualityMonitor` service (`src/services/data_quality_monitor.py`) automatically:
- Records all missing data incidents with severity and context
- Logs at CRITICAL level when data blocks operations
- Stores incidents in `data_quality_incidents` database table
- Provides statistics for monitoring dashboards
- Supports custom alert handlers (email, SMS, monitoring systems)

## Implementation

- Use `src/services/data_validation.py` for all validation
- Call `await data_validator.validate_prediction_for_betting()` before placing bets (automatically records incidents)
- Call `await data_validator.validate_bet_data()` as final check before storing (automatically records incidents)
- Use `data_validator.require_api_verification()` to check data sources
- All validation failures automatically record incidents via `DataQualityMonitor`
- Check `data_quality_incidents` table to monitor data quality issues

## Examples

### ❌ BAD - Inventing Data
```python
# DON'T DO THIS
if not odds:
    odds = -110  # Default odds - THIS IS WRONG!
    
if not line:
    line = 0.0  # Default line - THIS IS WRONG!
```

### ✅ GOOD - Failing Gracefully
```python
# DO THIS INSTEAD
if not odds:
    logger.warning("Missing odds - skipping bet")
    return False

is_valid, error = await data_validator.validate_prediction_for_betting(prediction)
if not is_valid:
    logger.warning(f"Validation failed: {error}")
    return False
```

## Enforcement

This rule is enforced in:
- `.cursorrules` - Project-wide AI context
- `src/services/data_validation.py` - Validation service
- `src/services/autonomous_betting_engine.py` - Bet placement logic
- All prediction generation scripts

## Why This Matters

Using synthetic data:
- Creates false confidence in predictions
- Leads to unprofitable bets
- Makes performance metrics meaningless
- Violates the core principle of data-driven betting

Real data or nothing.

