"""Outage data routes"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["data"])

@router.get("/processed-data")
async def get_processed_data():
    """Get processed outage data - Phase 2"""
    return {"status": "pending", "message": "Data pipeline implementation coming in Phase 2"}
