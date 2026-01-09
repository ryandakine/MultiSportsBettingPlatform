# Data Quality Monitoring & Alerting

## Overview

The Data Quality Monitor tracks and alerts on missing data incidents. **Missing data = system failure** - it's not just a warning, it's a critical issue that prevents the system from functioning properly.

## How It Works

### Automatic Incident Recording

When data validation fails (via `DataValidator`), incidents are automatically recorded:

```python
from src.services.data_validation import data_validator

# This automatically records incidents when validation fails
is_valid, error = await data_validator.validate_prediction_for_betting(prediction)
```

### What Gets Tracked

Each incident includes:
- **incident_id**: Unique identifier
- **timestamp**: When the incident occurred
- **severity**: critical, high, medium, low
- **data_type**: Type of missing data (e.g., "odds", "game_data", "bet_data")
- **data_source**: Source that should have provided data (e.g., "espn_api", "the_odds_api")
- **missing_fields**: List of specific fields that are missing
- **context**: Additional context (prediction_id, game_id, bet_type, etc.)
- **impact**: What operation failed (bet_placement_failed, prediction_validation_failed, etc.)
- **error_message**: Detailed error message
- **resolved**: Whether the incident has been resolved

### Severity Levels

- **CRITICAL**: System cannot function (e.g., missing odds for bet placement)
- **HIGH**: Significant functionality impaired
- **MEDIUM**: Some functionality affected
- **LOW**: Minor impact

## Database Schema

Incidents are stored in the `data_quality_incidents` table:

```sql
CREATE TABLE data_quality_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,
    timestamp DATETIME NOT NULL,
    severity TEXT NOT NULL,
    data_type TEXT NOT NULL,
    data_source TEXT NOT NULL,
    missing_fields TEXT,  -- JSON array
    context TEXT,  -- JSON object
    impact TEXT NOT NULL,
    error_message TEXT,
    resolved BOOLEAN NOT NULL DEFAULT 0,
    resolved_at DATETIME
);
```

## Querying Incidents

### Get Recent Incidents

```python
from src.services.data_quality_monitor import data_quality_monitor

# Get incidents from last 24 hours
incidents = await data_quality_monitor.get_recent_incidents(hours=24)

# Get only CRITICAL incidents
critical = await data_quality_monitor.get_recent_incidents(
    hours=24, 
    severity=DataQualitySeverity.CRITICAL
)
```

### Get Statistics

```python
# Get incident statistics
stats = await data_quality_monitor.get_incident_stats(hours=24)

# Returns:
# {
#     "total_incidents": 42,
#     "by_severity": {"critical": 35, "high": 5, "medium": 2},
#     "by_data_type": {"odds": 20, "game_data": 15, "bet_data": 7},
#     "by_source": {"espn_api": 30, "the_odds_api": 12},
#     "by_impact": {"bet_placement_failed": 25, "prediction_validation_failed": 17}
# }
```

## Custom Alert Handlers

You can register custom alert handlers for notifications:

```python
async def send_email_alert(incident: MissingDataIncident):
    # Send email notification
    pass

async def send_slack_alert(incident: MissingDataIncident):
    # Send Slack message
    pass

# Register handlers
data_quality_monitor.register_alert_handler(send_email_alert)
data_quality_monitor.register_alert_handler(send_slack_alert)
```

## Monitoring Dashboard

To build a monitoring dashboard:

1. Query recent incidents by severity
2. Track incidents by data type and source
3. Monitor trends over time
4. Alert when incident rate spikes
5. Track resolution status

## Integration Points

### Prediction Generation

When generating predictions, missing game data or odds automatically triggers incidents:

```python
# In prediction generation scripts
prediction = {
    "game_id": None,  # MISSING - triggers CRITICAL incident
    "odds": None,     # MISSING - triggers CRITICAL incident
    # ...
}

is_valid, error = await data_validator.validate_prediction_for_betting(prediction)
# Incident automatically recorded if validation fails
```

### Bet Placement

When placing bets, missing or invalid data triggers incidents:

```python
# In autonomous_betting_engine.py
is_valid, error = await data_validator.validate_prediction_for_betting(prediction)
if not is_valid:
    # Incident already recorded by validator
    return False
```

## Best Practices

1. **Don't ignore incidents** - Every incident indicates a real problem
2. **Monitor patterns** - Look for systemic issues (e.g., ESPN API consistently failing)
3. **Set up alerts** - Get notified when CRITICAL incidents occur
4. **Track resolution** - Mark incidents as resolved when fixed
5. **Analyze trends** - Use statistics to identify data quality improvements needed

## Future Enhancements

- [ ] Email/SMS alert integration
- [ ] PagerDuty integration for CRITICAL incidents
- [ ] Slack/Discord webhook notifications
- [ ] Automated incident resolution tracking
- [ ] Data quality dashboards
- [ ] Alert throttling to prevent spam
- [ ] Incident correlation to identify root causes


