"""Anomaly detection routes"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["anomalies"])

@router.get("/anomalies")
async def get_anomalies():
    """Get detected anomalies - Phase 4"""
    return {
        "status": "pending",
        "message": "Anomaly detection implementation coming in Phase 4",
        "anomalies": []
    }
