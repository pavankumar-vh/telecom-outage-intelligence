"""Incident scoring and ranking routes"""
import logging
from fastapi import APIRouter
from backend.services.data_service import DataService
from backend.services.scoring_service import ScoringService

router = APIRouter(prefix="/api", tags=["incidents"])

# Global service instances
data_service: DataService = None
scoring_service: ScoringService = None

logger = logging.getLogger(__name__)


@router.on_event("startup")
def startup_incident_services():
    """Initialize incident services on API startup"""
    global data_service, scoring_service
    
    if data_service is None:
        data_service = DataService()
        data_service.process()
        logger.info("DataService initialized for incidents")
    
    if scoring_service is None:
        scoring_service = ScoringService()
        logger.info("ScoringService initialized for incidents")


@router.get("/ranked-incidents")
async def get_ranked_incidents():
    """
    Get all incidents ranked by impact score.
    
    Returns incidents sorted by overall impact score (highest to lowest),
    with detailed scoring breakdown and explanations.
    
    Response includes:
    - overall_score: 0-100 impact score
    - severity_score: Severity component (40% weight)
    - complaint_score: Complaint volume component (35% weight)
    - usage_score: Traffic/user impact component (25% weight)
    - explanation: Human-readable impact analysis
    - rank: Priority ranking (1 = highest impact)
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
                "total_incidents": 0,
                "incidents": [],
            }
        
        # Score and rank incidents
        response = scoring_service.get_ranked_incidents(processed_data)
        
        logger.info(f"Ranked {response.total_incidents} incidents by impact score")
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Error ranking incidents: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to rank incidents: {str(e)}",
            "incidents": [],
        }


@router.get("/ranked-incidents/{region}")
async def get_ranked_incidents_by_region(region: str):
    """
    Get incidents ranked by impact score for a specific region.
    
    Args:
        region: Region code (e.g., US-EAST-01, EMEA-WEST, ASIA-PAC)
    
    Returns incidents for the specified region sorted by impact score.
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
        
        # Filter by region
        region_data = [
            incident for incident in processed_data 
            if incident.get("region", "").upper() == region.upper()
        ]
        
        if not region_data:
            return {
                "status": "success",
                "total_incidents": 0,
                "region": region,
                "incidents": [],
            }
        
        # Score and rank incidents for this region
        response = scoring_service.get_ranked_incidents(region_data)
        
        logger.info(f"Ranked {response.total_incidents} incidents in {region}")
        return {
            **response.to_dict(),
            "region": region,
        }
    
    except Exception as e:
        logger.error(f"Error ranking incidents for region {region}: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to rank incidents: {str(e)}",
            "incidents": [],
        }
