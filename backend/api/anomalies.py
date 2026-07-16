"""Anomaly detection routes"""
import logging
from fastapi import APIRouter
from backend.services.data_service import DataService
from backend.services.anomaly_service import AnomalyDetectionService

router = APIRouter(prefix="/api", tags=["anomalies"])

# Global service instances
data_service: DataService = None
anomaly_service: AnomalyDetectionService = None

logger = logging.getLogger(__name__)


@router.on_event("startup")
def startup_anomaly_services():
    """Initialize anomaly detection services on API startup"""
    global data_service, anomaly_service
    
    if data_service is None:
        data_service = DataService()
        data_service.process()
        logger.info("DataService initialized for anomalies")
    
    if anomaly_service is None:
        anomaly_service = AnomalyDetectionService()
        logger.info("AnomalyDetectionService initialized")


@router.get("/anomalies")
async def get_anomalies():
    """
    Get detected anomalies in incident data.
    
    Detects:
    - Complaint spikes (complaints exceeding 1.5x baseline)
    - Regional concentrations (3+ incidents in same region)
    - Customer base anomalies (affected customers 1.8x+ baseline)
    - High impact regions (traffic 1.6x+ regional baseline)
    
    Returns incidents with anomalies sorted by severity (HIGH > MEDIUM > LOW).
    """
    try:
        if data_service is None or not data_service.validated:
            return {
                "status": "error",
                "message": "Data service not initialized",
                "incidents": [],
            }
        
        # Get processed incident data
        processed_data = data_service.get_processed_data()
        
        if not processed_data:
            return {
                "status": "success",
                "total_incidents_analyzed": 0,
                "incidents_with_anomalies": 0,
                "total_anomalies": 0,
                "high_severity_anomalies": 0,
                "incidents": [],
            }
        
        # Detect anomalies
        response = anomaly_service.detect_all_anomalies(processed_data)
        
        logger.info(
            f"Detected anomalies: {response.incidents_with_anomalies} incidents with "
            f"{response.total_anomalies} total anomalies"
        )
        
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to detect anomalies: {str(e)}",
            "incidents": [],
        }


@router.get("/anomalies/{severity}")
async def get_anomalies_by_severity(severity: str):
    """
    Get anomalies filtered by severity level.
    
    Args:
        severity: Severity filter (high, medium, low)
    
    Returns incidents with anomalies matching the specified severity.
    """
    try:
        if data_service is None or not data_service.validated:
            return {
                "status": "error",
                "message": "Data service not initialized",
                "incidents": [],
            }
        
        severity_lower = severity.lower()
        if severity_lower not in ["high", "medium", "low"]:
            return {
                "status": "error",
                "message": f"Invalid severity: {severity}. Must be high, medium, or low",
                "incidents": [],
            }
        
        # Get processed incident data
        processed_data = data_service.get_processed_data()
        
        if not processed_data:
            return {
                "status": "success",
                "severity": severity_lower,
                "total_incidents_analyzed": 0,
                "incidents_with_anomalies": 0,
                "total_anomalies": 0,
                "incidents": [],
            }
        
        # Detect anomalies
        response = anomaly_service.detect_all_anomalies(processed_data)
        
        # Filter by severity
        filtered_incidents = []
        total_anomalies = 0
        
        for incident in response.incidents:
            # Filter flags by severity
            filtered_flags = [
                f for f in incident.anomaly_flags
                if f.severity.value == severity_lower
            ]
            
            if filtered_flags:
                # Create new incident with filtered flags
                filtered_incident = incident.__class__(
                    outage_id=incident.outage_id,
                    region=incident.region,
                    incident_severity=incident.incident_severity,
                    complaint_count=incident.complaint_count,
                    affected_customers=incident.affected_customers,
                    avg_traffic_gbps=incident.avg_traffic_gbps,
                    anomaly_flags=filtered_flags,
                    has_anomalies=len(filtered_flags) > 0,
                    total_flags=len(filtered_flags),
                    high_severity_count=1 if severity_lower == "high" else 0,
                    primary_concern=filtered_flags[0].description,
                )
                filtered_incidents.append(filtered_incident)
                total_anomalies += len(filtered_flags)
        
        logger.info(
            f"Filtered anomalies by {severity_lower}: "
            f"{len(filtered_incidents)} incidents with {total_anomalies} anomalies"
        )
        
        return {
            "status": "success",
            "severity": severity_lower,
            "total_incidents_analyzed": response.total_incidents_analyzed,
            "incidents_with_anomalies": len(filtered_incidents),
            "total_anomalies": total_anomalies,
            "incidents": [i.to_dict() for i in filtered_incidents],
        }
    
    except Exception as e:
        logger.error(f"Error filtering anomalies by severity: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to filter anomalies: {str(e)}",
            "incidents": [],
        }


@router.get("/anomalies/region/{region}")
async def get_anomalies_by_region(region: str):
    """
    Get anomalies for a specific region.
    
    Args:
        region: Region code (e.g., US-EAST-01, EMEA-WEST)
    
    Returns incidents with anomalies in the specified region.
    """
    try:
        if data_service is None or not data_service.validated:
            return {
                "status": "error",
                "message": "Data service not initialized",
                "incidents": [],
            }
        
        # Get processed incident data
        processed_data = data_service.get_processed_data()
        
        if not processed_data:
            return {
                "status": "success",
                "region": region,
                "total_incidents_analyzed": 0,
                "incidents_with_anomalies": 0,
                "total_anomalies": 0,
                "incidents": [],
            }
        
        # Detect anomalies
        response = anomaly_service.detect_all_anomalies(processed_data)
        
        # Filter by region
        filtered_incidents = [
            i for i in response.incidents
            if i.region.upper() == region.upper()
        ]
        
        total_anomalies = sum(i.total_flags for i in filtered_incidents)
        
        logger.info(
            f"Found {len(filtered_incidents)} incidents with anomalies in {region}"
        )
        
        return {
            "status": "success",
            "region": region,
            "total_incidents_analyzed": response.total_incidents_analyzed,
            "incidents_with_anomalies": len(filtered_incidents),
            "total_anomalies": total_anomalies,
            "incidents": [i.to_dict() for i in filtered_incidents],
        }
    
    except Exception as e:
        logger.error(f"Error filtering anomalies by region: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to filter anomalies: {str(e)}",
            "incidents": [],
        }
