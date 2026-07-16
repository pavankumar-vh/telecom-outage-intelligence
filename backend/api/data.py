"""Outage data routes"""
from fastapi import APIRouter, HTTPException
from backend.services.data_service import DataService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["data"])

# Initialize data service
data_service = DataService(data_dir="data")

@router.on_event("startup")
async def load_data():
    """Load and process data on startup"""
    logger.info("Loading data pipeline...")
    success, pipeline_status = data_service.process()
    if success:
        logger.info("Data pipeline loaded successfully")
        logger.info(f"Pipeline status: {pipeline_status}")
    else:
        logger.error(f"Data pipeline failed: {pipeline_status['errors']}")

@router.get("/processed-data")
async def get_processed_data():
    """Get processed and integrated outage data"""
    try:
        if data_service.processed_df is None:
            raise HTTPException(status_code=503, detail="Data not loaded. Please check server logs.")
        
        processed_data = data_service.get_processed_data()
        summary = data_service.get_summary()
        validation = data_service.validate_data()
        
        return {
            "status": "success",
            "total_records": len(processed_data),
            "data_quality": validation['data_quality'],
            "summary": summary,
            "data": processed_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving processed data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

@router.get("/data-quality")
async def get_data_quality():
    """Get data quality metrics"""
    try:
        validation = data_service.validate_data()
        return {
            "status": "success",
            "validation": validation
        }
    except Exception as e:
        logger.error(f"Error retrieving data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/data-summary")
async def get_data_summary():
    """Get summary statistics of processed data"""
    try:
        summary = data_service.get_summary()
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error retrieving summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
