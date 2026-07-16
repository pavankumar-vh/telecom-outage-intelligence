"""
Anomaly Detection Models and Data Structures

Defines the structure for detecting and reporting anomalies in incident data.
Includes complaint spikes, regional anomalies, and customer base anomalies.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""
    COMPLAINT_SPIKE = "complaint_spike"
    REGIONAL_CONCENTRATION = "regional_concentration"
    CUSTOMER_BASE_ANOMALY = "customer_base_anomaly"
    HIGH_IMPACT_REGION = "high_impact_region"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AnomalyFlag:
    """A single anomaly flag for an incident."""
    outage_id: str
    region: str
    anomaly_type: str  # AnomalyType value
    severity: str  # AnomalySeverity value
    
    description: str  # Human-readable description
    threshold_value: float  # Threshold that was breached
    actual_value: float  # Actual observed value
    deviation_percent: float  # % deviation from normal
    
    recommendation: Optional[str] = None  # Optional action recommendation
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IncidentAnomalies:
    """All anomalies detected for a specific incident."""
    outage_id: str
    region: str
    incident_severity: str
    complaint_count: int
    affected_customers: int
    avg_traffic_gbps: float
    
    anomaly_flags: List[AnomalyFlag]
    has_anomalies: bool
    total_flags: int
    high_severity_count: int
    
    primary_concern: Optional[str] = None  # Most important anomaly
    
    def to_dict(self) -> Dict:
        return {
            "outage_id": self.outage_id,
            "region": self.region,
            "incident_severity": self.incident_severity,
            "complaint_count": self.complaint_count,
            "affected_customers": self.affected_customers,
            "avg_traffic_gbps": self.avg_traffic_gbps,
            "has_anomalies": self.has_anomalies,
            "total_flags": self.total_flags,
            "high_severity_count": self.high_severity_count,
            "primary_concern": self.primary_concern,
            "anomaly_flags": [flag.to_dict() for flag in self.anomaly_flags],
        }


@dataclass
class AnomaliesResponse:
    """API response with detected anomalies."""
    status: str
    total_incidents_analyzed: int
    incidents_with_anomalies: int
    total_anomalies: int
    high_severity_anomalies: int
    
    incidents: List[IncidentAnomalies]
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "total_incidents_analyzed": self.total_incidents_analyzed,
            "incidents_with_anomalies": self.incidents_with_anomalies,
            "total_anomalies": self.total_anomalies,
            "high_severity_anomalies": self.high_severity_anomalies,
            "incidents": [incident.to_dict() for incident in self.incidents],
        }
