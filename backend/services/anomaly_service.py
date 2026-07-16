"""
Anomaly Detection Service

Detects anomalies in incident data including:
- Complaint spikes above normal patterns
- Regional concentrations of incidents
- Customer base anomalies (unusual impact)
- High impact regions

Uses statistical analysis to identify deviations from normal patterns.
"""

import logging
from typing import List, Dict, Any, Tuple
from statistics import mean, stdev
from backend.models.anomalies import (
    AnomalyFlag,
    IncidentAnomalies,
    AnomaliesResponse,
    AnomalyType,
    AnomalySeverity,
)

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Service for detecting anomalies in incident data."""
    
    # Thresholds for anomaly detection
    COMPLAINT_SPIKE_THRESHOLD = 1.5  # 1.5x above average
    REGIONAL_CONCENTRATION_THRESHOLD = 3  # 3+ incidents in same region
    CUSTOMER_BASE_THRESHOLD = 1.8  # 1.8x above average customers
    HIGH_TRAFFIC_THRESHOLD = 1.6  # 1.6x above average traffic
    
    def __init__(self):
        """Initialize anomaly detection service."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Baseline statistics (will be calculated from data)
        self.avg_complaints = 0.0
        self.avg_customers = 0.0
        self.avg_traffic = 0.0
        self.avg_escalation = 0.0
        
        # Regional statistics
        self.regional_incident_count = {}
        self.regional_customer_impact = {}
        self.regional_avg_traffic = {}
    
    def calculate_baselines(self, incidents: List[Dict[str, Any]]) -> None:
        """
        Calculate baseline statistics from incident data.
        
        Args:
            incidents: List of incident dictionaries with metrics
        """
        if not incidents:
            return
        
        # Calculate averages
        complaints = [i.get("complaint_count", 0) for i in incidents]
        customers = [i.get("affected_customers", 0) for i in incidents]
        traffic = [i.get("avg_traffic_gbps", 0) for i in incidents]
        escalations = [i.get("max_escalation", 1) for i in incidents]
        
        self.avg_complaints = mean(complaints) if complaints else 0
        self.avg_customers = mean(customers) if customers else 0
        self.avg_traffic = mean(traffic) if traffic else 0
        self.avg_escalation = mean(escalations) if escalations else 1
        
        # Calculate regional statistics
        self.regional_incident_count = {}
        self.regional_customer_impact = {}
        self.regional_avg_traffic = {}
        
        for incident in incidents:
            region = incident.get("region", "UNKNOWN")
            
            # Count incidents per region
            self.regional_incident_count[region] = (
                self.regional_incident_count.get(region, 0) + 1
            )
            
            # Sum customer impact per region
            customers = incident.get("affected_customers", 0)
            self.regional_customer_impact[region] = (
                self.regional_customer_impact.get(region, 0) + customers
            )
            
            # Average traffic per region
            traffic_list = self.regional_avg_traffic.get(region, [])
            traffic_list.append(incident.get("avg_traffic_gbps", 0))
            self.regional_avg_traffic[region] = traffic_list
        
        # Convert traffic lists to averages
        for region in self.regional_avg_traffic:
            traffic_values = self.regional_avg_traffic[region]
            self.regional_avg_traffic[region] = (
                mean(traffic_values) if traffic_values else 0
            )
        
        self.logger.info(
            f"Calculated baselines: "
            f"avg_complaints={self.avg_complaints:.1f}, "
            f"avg_customers={self.avg_customers:.0f}, "
            f"avg_traffic={self.avg_traffic:.1f} Gbps"
        )
    
    def detect_complaint_spike(
        self, incident: Dict[str, Any]
    ) -> List[AnomalyFlag]:
        """
        Detect if incident has unusually high complaint volume.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            List of AnomalyFlag objects (empty if no anomaly)
        """
        flags = []
        complaint_count = incident.get("complaint_count", 0)
        outage_id = incident.get("outage_id", "UNKNOWN")
        region = incident.get("region", "UNKNOWN")
        escalation = incident.get("max_escalation", 1)
        
        # Check if complaints exceed threshold
        if complaint_count > self.avg_complaints * self.COMPLAINT_SPIKE_THRESHOLD:
            deviation = ((complaint_count - self.avg_complaints) / 
                        (self.avg_complaints + 1)) * 100
            
            # Determine severity based on deviation and escalation
            if complaint_count > self.avg_complaints * 2.0 and escalation >= 4:
                severity = AnomalySeverity.HIGH
            elif complaint_count > self.avg_complaints * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            
            flag = AnomalyFlag(
                outage_id=outage_id,
                region=region,
                anomaly_type=AnomalyType.COMPLAINT_SPIKE,
                severity=severity,
                description=f"Complaint spike detected: {complaint_count} reports (baseline: {self.avg_complaints:.1f})",
                threshold_value=self.avg_complaints * self.COMPLAINT_SPIKE_THRESHOLD,
                actual_value=float(complaint_count),
                deviation_percent=deviation,
                recommendation="Prioritize this incident - customer impact is higher than normal",
            )
            flags.append(flag)
        
        return flags
    
    def detect_customer_base_anomaly(
        self, incident: Dict[str, Any]
    ) -> List[AnomalyFlag]:
        """
        Detect if incident affects unusually large customer base.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            List of AnomalyFlag objects (empty if no anomaly)
        """
        flags = []
        affected_customers = incident.get("affected_customers", 0)
        outage_id = incident.get("outage_id", "UNKNOWN")
        region = incident.get("region", "UNKNOWN")
        severity = incident.get("severity", "Minor")
        
        # Check if customer impact exceeds threshold
        if affected_customers > self.avg_customers * self.CUSTOMER_BASE_THRESHOLD:
            deviation = ((affected_customers - self.avg_customers) /
                        (self.avg_customers + 1)) * 100
            
            # Determine severity based on deviation and incident severity
            if affected_customers > self.avg_customers * 2.5 and severity in ["Critical", "Major"]:
                anomaly_severity = AnomalySeverity.HIGH
            elif affected_customers > self.avg_customers * 2.0:
                anomaly_severity = AnomalySeverity.MEDIUM
            else:
                anomaly_severity = AnomalySeverity.LOW
            
            flag = AnomalyFlag(
                outage_id=outage_id,
                region=region,
                anomaly_type=AnomalyType.CUSTOMER_BASE_ANOMALY,
                severity=anomaly_severity,
                description=f"Unusual customer base affected: {affected_customers:,} customers (baseline: {self.avg_customers:.0f})",
                threshold_value=self.avg_customers * self.CUSTOMER_BASE_THRESHOLD,
                actual_value=float(affected_customers),
                deviation_percent=deviation,
                recommendation="This incident impacts more customers than typical - escalate to management",
            )
            flags.append(flag)
        
        return flags
    
    def detect_regional_concentration(
        self, incident: Dict[str, Any], all_incidents: List[Dict[str, Any]]
    ) -> List[AnomalyFlag]:
        """
        Detect if region has concentration of incidents.
        
        Args:
            incident: Single incident dictionary
            all_incidents: All incidents for context
            
        Returns:
            List of AnomalyFlag objects (empty if no anomaly)
        """
        flags = []
        region = incident.get("region", "UNKNOWN")
        outage_id = incident.get("outage_id", "UNKNOWN")
        
        # Count incidents in this region
        region_count = sum(
            1 for i in all_incidents 
            if i.get("region", "UNKNOWN") == region
        )
        
        # Check if region has concentration
        if region_count >= self.REGIONAL_CONCENTRATION_THRESHOLD:
            avg_region_count = len(all_incidents) / max(len(self.regional_incident_count), 1)
            deviation = ((region_count - avg_region_count) / 
                        (avg_region_count + 1)) * 100
            
            # Determine severity
            if region_count >= 5:
                severity = AnomalySeverity.HIGH
            elif region_count >= 4:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            
            flag = AnomalyFlag(
                outage_id=outage_id,
                region=region,
                anomaly_type=AnomalyType.REGIONAL_CONCENTRATION,
                severity=severity,
                description=f"Regional concentration: {region_count} incidents in {region}",
                threshold_value=float(self.REGIONAL_CONCENTRATION_THRESHOLD),
                actual_value=float(region_count),
                deviation_percent=deviation,
                recommendation="Multiple incidents in same region - check for common root cause",
            )
            flags.append(flag)
        
        return flags
    
    def detect_high_impact_region(
        self, incident: Dict[str, Any]
    ) -> List[AnomalyFlag]:
        """
        Detect if incident occurs in high-impact region.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            List of AnomalyFlag objects (empty if no anomaly)
        """
        flags = []
        region = incident.get("region", "UNKNOWN")
        outage_id = incident.get("outage_id", "UNKNOWN")
        traffic = incident.get("avg_traffic_gbps", 0)
        severity = incident.get("severity", "Minor")
        
        # Get regional baseline
        regional_traffic_baseline = self.regional_avg_traffic.get(region, self.avg_traffic)
        
        # Check if traffic is unusually high for region
        if traffic > regional_traffic_baseline * self.HIGH_TRAFFIC_THRESHOLD:
            deviation = ((traffic - regional_traffic_baseline) /
                        (regional_traffic_baseline + 1)) * 100
            
            # Determine severity
            if traffic > regional_traffic_baseline * 2.0 and severity == "Critical":
                anomaly_severity = AnomalySeverity.HIGH
            elif traffic > regional_traffic_baseline * 1.8:
                anomaly_severity = AnomalySeverity.MEDIUM
            else:
                anomaly_severity = AnomalySeverity.LOW
            
            flag = AnomalyFlag(
                outage_id=outage_id,
                region=region,
                anomaly_type=AnomalyType.HIGH_IMPACT_REGION,
                severity=anomaly_severity,
                description=f"High-impact region: {traffic:.1f} Gbps (regional baseline: {regional_traffic_baseline:.1f} Gbps)",
                threshold_value=regional_traffic_baseline * self.HIGH_TRAFFIC_THRESHOLD,
                actual_value=float(traffic),
                deviation_percent=deviation,
                recommendation="This region is experiencing higher than normal traffic impact - monitor closely",
            )
            flags.append(flag)
        
        return flags
    
    def detect_incident_anomalies(
        self, incident: Dict[str, Any], all_incidents: List[Dict[str, Any]]
    ) -> IncidentAnomalies:
        """
        Detect all anomalies for a single incident.
        
        Args:
            incident: Incident dictionary
            all_incidents: All incidents for context
            
        Returns:
            IncidentAnomalies with all detected flags
        """
        flags = []
        
        # Run all anomaly detection methods
        flags.extend(self.detect_complaint_spike(incident))
        flags.extend(self.detect_customer_base_anomaly(incident))
        flags.extend(self.detect_regional_concentration(incident, all_incidents))
        flags.extend(self.detect_high_impact_region(incident))
        
        # Count severity levels
        high_severity = sum(1 for f in flags if f.severity == AnomalySeverity.HIGH)
        
        # Determine primary concern
        primary_concern = None
        if flags:
            # Sort by severity (HIGH > MEDIUM > LOW)
            severity_order = {AnomalySeverity.HIGH: 0, AnomalySeverity.MEDIUM: 1, AnomalySeverity.LOW: 2}
            sorted_flags = sorted(flags, key=lambda f: severity_order[f.severity])
            primary_concern = sorted_flags[0].description
        
        return IncidentAnomalies(
            outage_id=incident.get("outage_id", "UNKNOWN"),
            region=incident.get("region", "UNKNOWN"),
            incident_severity=incident.get("severity", "Unknown"),
            complaint_count=incident.get("complaint_count", 0),
            affected_customers=incident.get("affected_customers", 0),
            avg_traffic_gbps=incident.get("avg_traffic_gbps", 0),
            anomaly_flags=flags,
            has_anomalies=len(flags) > 0,
            total_flags=len(flags),
            high_severity_count=high_severity,
            primary_concern=primary_concern,
        )
    
    def detect_all_anomalies(
        self, incidents: List[Dict[str, Any]]
    ) -> AnomaliesResponse:
        """
        Detect anomalies for all incidents.
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            AnomaliesResponse with detected anomalies
        """
        # Calculate baselines
        self.calculate_baselines(incidents)
        
        # Detect anomalies for each incident
        incident_anomalies = []
        for incident in incidents:
            anomalies = self.detect_incident_anomalies(incident, incidents)
            incident_anomalies.append(anomalies)
        
        # Filter to only incidents with anomalies
        incidents_with_anomalies = [a for a in incident_anomalies if a.has_anomalies]
        
        # Count statistics
        total_anomalies = sum(a.total_flags for a in incident_anomalies)
        high_severity_count = sum(a.high_severity_count for a in incident_anomalies)
        
        self.logger.info(
            f"Detected anomalies: {len(incidents_with_anomalies)} incidents with "
            f"{total_anomalies} total anomalies ({high_severity_count} high severity)"
        )
        
        return AnomaliesResponse(
            status="success",
            total_incidents_analyzed=len(incidents),
            incidents_with_anomalies=len(incidents_with_anomalies),
            total_anomalies=total_anomalies,
            high_severity_anomalies=high_severity_count,
            incidents=incidents_with_anomalies,
        )
