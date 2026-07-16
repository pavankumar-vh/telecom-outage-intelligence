"""Incident scoring and ranking routes"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["incidents"])

@router.get("/ranked-incidents")
async def get_ranked_incidents():
    """Get ranked incidents by impact score - Phase 3"""
    return {
        "status": "pending",
        "message": "Impact scoring implementation coming in Phase 3",
        "incidents": []
    }
