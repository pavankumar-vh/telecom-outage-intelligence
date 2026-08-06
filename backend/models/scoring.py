"""
Scoring Models and Data Structures

Defines the structure for incident scoring, impact calculations, and explanations.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class SeverityScore:
    """Score contribution from incident severity level."""
    level: str  # Critical, Major, Warning, Minor
    weight: float = 0.40
    normalized_value: float = 0.0  # 0.0-1.0
    contribution: float = 0.0  # weighted contribution
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ComplaintScore:
    """Score contribution from complaint volume and escalation."""
    complaint_count: int
    max_escalation: int
    affected_customers: int = 0
    weight: float = 0.35
    normalized_value: float = 0.0  # 0.0-1.0
    contribution: float = 0.0  # weighted contribution
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UsageScore:
    """Score contribution from traffic impact and user disruption."""
    avg_traffic_gbps: float
    peak_active_users: int
    peak_utilization_percent: float
    weight: float = 0.25
    normalized_value: float = 0.0  # 0.0-1.0
    contribution: float = 0.0  # weighted contribution
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IncidentScore:
    """Complete impact score for an incident."""
    outage_id: str
    region: str
    timestamp: str
    severity: str
    duration_minutes: int
    affected_customers: int
    
    overall_score: float  # 0-100
    
    severity_score: SeverityScore
    complaint_score: ComplaintScore
    usage_score: UsageScore
    
    explanation: str
    rank: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            "outage_id": self.outage_id,
            "region": self.region,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "duration_minutes": self.duration_minutes,
            "affected_customers": self.affected_customers,
            "overall_score": round(self.overall_score, 2),
            "rank": self.rank,
            "severity_score": self.severity_score.to_dict(),
            "complaint_score": self.complaint_score.to_dict(),
            "usage_score": self.usage_score.to_dict(),
            "explanation": self.explanation,
        }


@dataclass
class RankedIncidentsResponse:
    """API response with ranked incidents."""
    status: str
    total_incidents: int
    incidents: List[IncidentScore]
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "total_incidents": self.total_incidents,
            "incidents": [incident.to_dict() for incident in self.incidents],
        }
