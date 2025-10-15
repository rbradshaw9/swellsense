"""
Status and Health Check API endpoints for SwellSense
Provides system status and database connectivity checks
"""
from fastapi import APIRouter, Depends, Response
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
