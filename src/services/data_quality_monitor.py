"""
Data Quality Monitor & Alerting Service
========================================
Tracks missing data incidents and sends alerts when critical data is unavailable.
Missing data = system failure that needs immediate attention.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class DataQualitySeverity(str, Enum):
    """Severity levels for missing data incidents."""
    CRITICAL = "critical"  # System cannot function
    HIGH = "high"  # Significant functionality impaired
    MEDIUM = "medium"  # Some functionality affected
    LOW = "low"  # Minor impact


@dataclass
class MissingDataIncident:
    """Record of a missing data incident."""
    incident_id: str
    timestamp: datetime
    severity: DataQualitySeverity
    data_type: str  # e.g., "odds", "game_data", "team_names"
    data_source: str  # e.g., "espn_api", "the_odds_api"
    missing_fields: List[str]  # What specific fields are missing
    context: Dict[str, Any]  # Additional context (prediction_id, game_id, etc.)
    impact: str  # What operation failed (bet_placement, prediction_generation, etc.)
    error_message: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class DataQualityMonitor:
    """
    Monitor and alert on data quality issues.
    
    When critical data is missing, this service:
    1. Logs the incident at CRITICAL level
    2. Stores the incident for tracking
    3. Sends alerts to monitoring systems
    4. Tracks patterns to identify systemic issues
    """
    
    def __init__(self):
        self.incidents: List[MissingDataIncident] = []
        self.alert_handlers: List[callable] = []
        
    async def record_missing_data(
        self,
        data_type: str,
        data_source: str,
        missing_fields: List[str],
        impact: str,
        context: Dict[str, Any] = None,
        severity: DataQualitySeverity = DataQualitySeverity.CRITICAL,
        error_message: Optional[str] = None
    ) -> str:
        """
        Record a missing data incident and trigger alerts.
        
        Args:
            data_type: Type of data missing (e.g., "odds", "game_data")
            data_source: Source that should have provided data (e.g., "espn_api")
            missing_fields: List of specific fields that are missing
            impact: What operation failed due to missing data
            context: Additional context (prediction_id, game_id, user_id, etc.)
            severity: How critical this missing data is
            error_message: Optional error message
            
        Returns:
            incident_id for tracking
        """
        from uuid import uuid4
        
        incident_id = str(uuid4())
        context = context or {}
        
        incident = MissingDataIncident(
            incident_id=incident_id,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            data_type=data_type,
            data_source=data_source,
            missing_fields=missing_fields,
            context=context,
            impact=impact,
            error_message=error_message
        )
        
        self.incidents.append(incident)
        
        # Log at appropriate level
        log_message = (
            f"🚨 MISSING DATA INCIDENT [{severity.value.upper()}] | "
            f"Type: {data_type} | Source: {data_source} | "
            f"Missing: {', '.join(missing_fields)} | Impact: {impact}"
        )
        
        if severity == DataQualitySeverity.CRITICAL:
            logger.critical(log_message)
            if context:
                logger.critical(f"   Context: {context}")
        elif severity == DataQualitySeverity.HIGH:
            logger.error(log_message)
        else:
            logger.warning(log_message)
        
        # Send alerts
        await self._send_alert(incident)
        
        # Store in database (async, non-blocking)
        asyncio.create_task(self._store_incident(incident))
        
        return incident_id
    
    async def _send_alert(self, incident: MissingDataIncident):
        """Send alert about missing data incident."""
        try:
            # Log alert details
            alert_message = (
                f"🚨 DATA QUALITY ALERT:\n"
                f"   Severity: {incident.severity.value}\n"
                f"   Data Type: {incident.data_type}\n"
                f"   Source: {incident.data_source}\n"
                f"   Missing Fields: {', '.join(incident.missing_fields)}\n"
                f"   Impact: {incident.impact}\n"
                f"   Time: {incident.timestamp.isoformat()}\n"
            )
            
            if incident.context:
                alert_message += f"   Context: {incident.context}\n"
            
            if incident.error_message:
                alert_message += f"   Error: {incident.error_message}\n"
            
            logger.critical(alert_message)
            
            # TODO: Send to monitoring system (Prometheus, Datadog, PagerDuty, etc.)
            # TODO: Send email/SMS alerts for CRITICAL incidents
            # TODO: Post to Slack/Discord channel
            
            # Call registered alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(incident)
                except Exception as e:
                    logger.error(f"❌ Alert handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
    
    async def _store_incident(self, incident: MissingDataIncident):
        """Store incident in database for tracking and analysis."""
        try:
            import json
            from src.db.database import AsyncSessionLocal
            from sqlalchemy import text
            
            async with AsyncSessionLocal() as session:
                await session.execute(text("""
                    INSERT INTO data_quality_incidents 
                    (incident_id, timestamp, severity, data_type, data_source, missing_fields, 
                     context, impact, error_message, resolved)
                    VALUES (:incident_id, :timestamp, :severity, :data_type, :data_source, 
                            :missing_fields, :context, :impact, :error_message, :resolved)
                """), {
                    "incident_id": incident.incident_id,
                    "timestamp": incident.timestamp,
                    "severity": incident.severity.value,
                    "data_type": incident.data_type,
                    "data_source": incident.data_source,
                    "missing_fields": json.dumps(incident.missing_fields),  # Store as JSON string
                    "context": json.dumps(incident.context),  # Store as JSON string
                    "impact": incident.impact,
                    "error_message": incident.error_message,
                    "resolved": incident.resolved
                })
                await session.commit()
                logger.debug(f"✅ Stored incident {incident.incident_id}")
                
        except Exception as e:
            # Don't fail if we can't store - at least we logged it
            logger.warning(f"⚠️ Could not store incident in database: {e}")
    
    def register_alert_handler(self, handler: callable):
        """Register a custom alert handler function."""
        self.alert_handlers.append(handler)
    
    async def get_recent_incidents(
        self, 
        hours: int = 24,
        severity: Optional[DataQualitySeverity] = None
    ) -> List[MissingDataIncident]:
        """Get recent incidents for monitoring dashboard."""
        cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        filtered = [
            inc for inc in self.incidents 
            if inc.timestamp.timestamp() >= cutoff
        ]
        
        if severity:
            filtered = [inc for inc in filtered if inc.severity == severity]
        
        return sorted(filtered, key=lambda x: x.timestamp, reverse=True)
    
    async def get_incident_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics about data quality incidents."""
        recent = await self.get_recent_incidents(hours)
        
        stats = {
            "total_incidents": len(recent),
            "by_severity": {},
            "by_data_type": {},
            "by_source": {},
            "by_impact": {}
        }
        
        for incident in recent:
            # Count by severity
            stats["by_severity"][incident.severity.value] = \
                stats["by_severity"].get(incident.severity.value, 0) + 1
            
            # Count by data type
            stats["by_data_type"][incident.data_type] = \
                stats["by_data_type"].get(incident.data_type, 0) + 1
            
            # Count by source
            stats["by_source"][incident.data_source] = \
                stats["by_source"].get(incident.data_source, 0) + 1
            
            # Count by impact
            stats["by_impact"][incident.impact] = \
                stats["by_impact"].get(incident.impact, 0) + 1
        
        return stats


# Global instance
data_quality_monitor = DataQualityMonitor()

