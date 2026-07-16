"""
Impact Scoring Service

Implements the scoring algorithm that combines severity, complaint volume, and usage impact
into a single explainable impact score for each incident.

Scoring Formula:
Impact Score = (0.40 × Severity Score) + (0.35 × Complaint Score) + (0.25 × Usage Score)

All component scores are normalized to 0-100 scale before weighting.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.models.scoring import (
    IncidentScore,
    SeverityScore,
    ComplaintScore,
    UsageScore,
    RankedIncidentsResponse,
)

logger = logging.getLogger(__name__)


class ScoringService:
    """Service for calculating incident impact scores."""
    
    # Severity levels and their base impact values
    SEVERITY_MAPPING = {
        "Critical": 1.0,
        "Major": 0.75,
        "Warning": 0.5,
        "Minor": 0.25,
    }
    
    # Escalation level weights
    ESCALATION_WEIGHTS = {
        1: 0.25,
        2: 0.5,
        3: 0.75,
        4: 1.0,
        5: 1.0,
    }
    
    def __init__(self):
        """Initialize scoring service with normalization parameters."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Normalization parameters (learned from typical incident data)
        self.max_complaints = 100  # Assume max 100 complaints per incident
        self.max_escalation = 5    # Escalation levels 1-5
        self.max_traffic_gbps = 1000  # Normalize to max 1000 Gbps
        self.max_active_users = 100000  # Normalize to max 100K users
        self.max_utilization = 100  # Already in percentage (0-100)
    
    def calculate_severity_score(self, severity: str) -> SeverityScore:
        """
        Calculate severity component score.
        
        Args:
            severity: Incident severity level (Critical, Major, Warning, Minor)
            
        Returns:
            SeverityScore with normalized value and contribution
        """
        normalized_value = self.SEVERITY_MAPPING.get(severity, 0.0)
        contribution = normalized_value * 0.40  # Weight: 40%
        
        return SeverityScore(
            level=severity,
            normalized_value=normalized_value,
            contribution=contribution * 100,  # Convert to 0-100 scale
        )
    
    def calculate_complaint_score(
        self, complaint_count: int, max_escalation: int
    ) -> ComplaintScore:
        """
        Calculate complaint component score.
        
        Combines complaint volume and escalation level:
        - Complaint volume (60%): Normalized by max complaints
        - Escalation level (40%): Weighted by escalation importance
        
        Args:
            complaint_count: Number of complaints for incident
            max_escalation: Maximum escalation level (1-5)
            
        Returns:
            ComplaintScore with normalized value and contribution
        """
        # Complaint volume component (60%)
        complaint_normalized = min(complaint_count / self.max_complaints, 1.0)
        complaint_component = complaint_normalized * 0.60
        
        # Escalation level component (40%)
        escalation_weight = self.ESCALATION_WEIGHTS.get(max_escalation, 0.0)
        escalation_component = escalation_weight * 0.40
        
        # Combined normalized value
        normalized_value = complaint_component + escalation_component
        contribution = normalized_value * 0.35  # Weight: 35%
        
        return ComplaintScore(
            complaint_count=complaint_count,
            max_escalation=max_escalation,
            normalized_value=normalized_value,
            contribution=contribution * 100,  # Convert to 0-100 scale
        )
    
    def calculate_usage_score(
        self,
        avg_traffic_gbps: float,
        peak_active_users: int,
        peak_utilization_percent: float,
    ) -> UsageScore:
        """
        Calculate usage impact component score.
        
        Combines three factors:
        - Traffic impact (40%): Peak traffic in Gbps
        - User disruption (40%): Active users at time of outage
        - System stress (20%): Peak utilization percentage
        
        Args:
            avg_traffic_gbps: Average traffic during outage
            peak_active_users: Peak concurrent active users
            peak_utilization_percent: Peak utilization percentage
            
        Returns:
            UsageScore with normalized value and contribution
        """
        # Traffic impact (40%)
        traffic_normalized = min(avg_traffic_gbps / self.max_traffic_gbps, 1.0)
        traffic_component = traffic_normalized * 0.40
        
        # User disruption (40%)
        users_normalized = min(peak_active_users / self.max_active_users, 1.0)
        users_component = users_normalized * 0.40
        
        # System stress (20%)
        stress_normalized = min(peak_utilization_percent / self.max_utilization, 1.0)
        stress_component = stress_normalized * 0.20
        
        # Combined normalized value
        normalized_value = traffic_component + users_component + stress_component
        contribution = normalized_value * 0.25  # Weight: 25%
        
        return UsageScore(
            avg_traffic_gbps=avg_traffic_gbps,
            peak_active_users=peak_active_users,
            peak_utilization_percent=peak_utilization_percent,
            normalized_value=normalized_value,
            contribution=contribution * 100,  # Convert to 0-100 scale
        )
    
    def generate_explanation(
        self,
        severity: str,
        severity_score: SeverityScore,
        complaint_score: ComplaintScore,
        usage_score: UsageScore,
        overall_score: float,
    ) -> str:
        """
        Generate human-readable explanation for impact score.
        
        Args:
            severity: Incident severity
            severity_score: Severity component
            complaint_score: Complaint component
            usage_score: Usage component
            overall_score: Overall impact score
            
        Returns:
            Formatted explanation string
        """
        # Determine score level
        if overall_score >= 80:
            level = "CRITICAL"
        elif overall_score >= 60:
            level = "HIGH"
        elif overall_score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        # Find dominant factor
        factors = [
            ("severity", severity_score.contribution),
            ("complaints", complaint_score.contribution),
            ("usage impact", usage_score.contribution),
        ]
        dominant_factor = max(factors, key=lambda x: x[1])[0]
        
        # Build explanation
        parts = [
            f"[{level}] Impact Score: {overall_score:.1f}/100",
            f"Severity: {severity} incident",
            f"Complaints: {complaint_score.complaint_count} reports (escalation level {complaint_score.max_escalation})",
            f"Usage Impact: {usage_score.peak_active_users:,} users, {usage_score.avg_traffic_gbps:.1f} Gbps",
            f"Primary driver: {dominant_factor.upper()}",
        ]
        
        return " | ".join(parts)
    
    def score_incident(self, incident_data: Dict[str, Any]) -> IncidentScore:
        """
        Calculate complete impact score for a single incident.
        
        Args:
            incident_data: Dictionary with incident details from processed data
                Required keys: outage_id, region, timestamp, severity, component,
                              status, duration_minutes, complaint_count, 
                              affected_customers, max_escalation, avg_traffic_gbps,
                              peak_active_users, peak_utilization
                              
        Returns:
            IncidentScore with all components and explanation
        """
        try:
            # Extract data
            outage_id = incident_data.get("outage_id", "UNKNOWN")
            region = incident_data.get("region", "UNKNOWN")
            timestamp = incident_data.get("timestamp", "")
            severity = incident_data.get("severity", "Minor")
            duration = incident_data.get("duration_minutes", 0)
            
            complaint_count = max(0, incident_data.get("complaint_count", 0))
            max_escalation = max(1, incident_data.get("max_escalation", 1))
            avg_traffic_gbps = max(0, incident_data.get("avg_traffic_gbps", 0))
            peak_active_users = max(0, incident_data.get("peak_active_users", 0))
            peak_utilization = max(0, incident_data.get("peak_utilization", 0))
            
            # Calculate component scores
            severity_score = self.calculate_severity_score(severity)
            complaint_score = self.calculate_complaint_score(
                complaint_count, max_escalation
            )
            usage_score = self.calculate_usage_score(
                avg_traffic_gbps, peak_active_users, peak_utilization
            )
            
            # Calculate overall score
            overall_score = (
                severity_score.contribution
                + complaint_score.contribution
                + usage_score.contribution
            )
            overall_score = min(100.0, max(0.0, overall_score))  # Clamp to 0-100
            
            # Generate explanation
            explanation = self.generate_explanation(
                severity, severity_score, complaint_score, usage_score, overall_score
            )
            
            return IncidentScore(
                outage_id=outage_id,
                region=region,
                timestamp=timestamp,
                severity=severity,
                duration_minutes=duration,
                overall_score=overall_score,
                severity_score=severity_score,
                complaint_score=complaint_score,
                usage_score=usage_score,
                explanation=explanation,
            )
        
        except Exception as e:
            self.logger.error(f"Error scoring incident {incident_data.get('outage_id')}: {str(e)}")
            raise
    
    def score_all_incidents(
        self, processed_data: List[Dict[str, Any]]
    ) -> List[IncidentScore]:
        """
        Score all incidents and return sorted by impact (descending).
        
        Args:
            processed_data: List of processed incident dictionaries
            
        Returns:
            List of IncidentScore objects sorted by overall_score (highest first)
        """
        scores = []
        
        for incident in processed_data:
            try:
                score = self.score_incident(incident)
                scores.append(score)
            except Exception as e:
                self.logger.warning(
                    f"Failed to score incident {incident.get('outage_id')}: {str(e)}"
                )
                continue
        
        # Sort by overall score (descending)
        scores.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Add rank numbers
        for rank, score in enumerate(scores, 1):
            score.rank = rank
        
        self.logger.info(f"Scored {len(scores)} incidents")
        return scores
    
    def get_ranked_incidents(
        self, processed_data: List[Dict[str, Any]]
    ) -> RankedIncidentsResponse:
        """
        Get ranked incidents for API response.
        
        Args:
            processed_data: List of processed incident dictionaries
            
        Returns:
            RankedIncidentsResponse with scored and ranked incidents
        """
        scored_incidents = self.score_all_incidents(processed_data)
        
        return RankedIncidentsResponse(
            status="success",
            total_incidents=len(scored_incidents),
            incidents=scored_incidents,
        )
