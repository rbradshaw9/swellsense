"""
Status and Health Check API endpoints for SwellSense
Provides system status and database connectivity checks
"""
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["status"])

VERSION = "v0.3"


@router.get("/status")
async def get_status(
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint with database connectivity test
    
    Returns:
        JSON with status, database connection state, and version
        HTTP 200 if healthy, 500 if database connection fails
    """
    status_data = {
        "status": "ok",
        "database": "unknown",
        "version": VERSION
    }
    
    # Test database connection
    try:
        # Execute simple query to verify connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        status_data["database"] = "connected"
        logger.info("Health check: Database connection successful")
        response.status_code = 200
        
    except Exception as e:
        status_data["status"] = "error"
        status_data["database"] = "error"
        status_data["error"] = str(e)
        logger.error(f"Health check: Database connection failed - {str(e)}")
        response.status_code = 500
    
    return status_data


@router.get("/health")
async def health_check():
    """
    Simple health check without database dependency
    Useful for container orchestration health probes
    
    Returns:
        JSON with basic status
    """
    return {
        "status": "ok",
        "version": VERSION
    }


@router.post("/ingest/trigger")
async def trigger_ingestion():
    """
    Manually trigger NOAA buoy data ingestion
    Useful for testing or immediate data updates
    
    Returns:
        JSON with ingestion results
    """
    try:
        from services.ingestion_service import ingestion_service
        
        logger.info("🔧 Manual ingestion triggered via API")
        count = await ingestion_service.ingest_all_buoys()
        
        return {
            "status": "success",
            "message": f"Ingestion completed successfully",
            "records_inserted": count,
            "buoys_processed": len(ingestion_service.buoy_stations)
        }
    
    except Exception as e:
        logger.error(f"❌ Manual ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get("/ingest/status")
async def ingestion_status():
    """
    Check the status of the background ingestion service
    
    Returns:
        JSON with service status and configuration
    """
    try:
        from services.ingestion_service import ingestion_service, INGESTION_INTERVAL
        
        return {
            "status": "running" if ingestion_service.is_running else "stopped",
            "buoy_stations": ingestion_service.buoy_stations,
            "interval_hours": INGESTION_INTERVAL / 3600,
            "version": VERSION
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ingestion status: {str(e)}"
        )
