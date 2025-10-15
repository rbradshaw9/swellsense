"""
Forecast API endpoints for SwellSense
Serves surf condition data from the database
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime, timedelta

from ..database import get_db, SurfCondition

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/forecast")
async def get_forecast(
    limit: int = 24,
    buoy_id: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent surf conditions from the database
    
    Args:
        limit: Number of records to return (default 24)
        buoy_id: Optional filter by specific buoy station ID
        db: Database session
    
    Returns:
        List of surf condition records with wave height, period, wind speed, etc.
    """
    try:
        # Build query
        query = select(SurfCondition).order_by(desc(SurfCondition.timestamp))
        
        # Filter by buoy_id if provided
        if buoy_id:
            query = query.where(SurfCondition.buoy_id == buoy_id)
        
        # Limit results
        query = query.limit(limit)
        
        # Execute query
        result = await db.execute(query)
        conditions = result.scalars().all()
        
        # Convert to dict
        return {
            "status": "success",
            "count": len(conditions),
            "data": [condition.to_dict() for condition in conditions]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching forecast data: {str(e)}"
        )


@router.get("/forecast/latest")
async def get_latest_forecast(
    buoy_id: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent surf condition reading
    
    Args:
        buoy_id: Optional filter by specific buoy station ID
        db: Database session
    
    Returns:
        Single most recent surf condition record
    """
    try:
        # Build query
        query = select(SurfCondition).order_by(desc(SurfCondition.timestamp))
        
        # Filter by buoy_id if provided
        if buoy_id:
            query = query.where(SurfCondition.buoy_id == buoy_id)
        
        # Get first result
        result = await db.execute(query.limit(1))
        condition = result.scalar_one_or_none()
        
        if not condition:
            return {
                "status": "success",
                "message": "No forecast data available yet",
                "data": None
            }
        
        return {
            "status": "success",
            "data": condition.to_dict()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching latest forecast: {str(e)}"
        )


@router.get("/forecast/stats")
async def get_forecast_stats(
    hours: int = 24,
    buoy_id: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistical summary of surf conditions over a time period
    
    Args:
        hours: Number of hours to analyze (default 24)
        buoy_id: Optional filter by specific buoy station ID
        db: Database session
    
    Returns:
        Statistics including average, min, max wave height and wind speed
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = select(SurfCondition).where(
            SurfCondition.timestamp >= time_threshold
        ).order_by(desc(SurfCondition.timestamp))
        
        # Filter by buoy_id if provided
        if buoy_id:
            query = query.where(SurfCondition.buoy_id == buoy_id)
        
        # Execute query
        result = await db.execute(query)
        conditions = result.scalars().all()
        
        if not conditions:
            return {
                "status": "success",
                "message": f"No data available for the last {hours} hours",
                "data": None
            }
        
        # Calculate statistics
        wave_heights = [c.wave_height for c in conditions if c.wave_height is not None]
        wind_speeds = [c.wind_speed for c in conditions if c.wind_speed is not None]
        wave_periods = [c.wave_period for c in conditions if c.wave_period is not None]
        
        stats = {
            "period_hours": hours,
            "record_count": len(conditions),
            "wave_height": {
                "avg": round(sum(wave_heights) / len(wave_heights), 2) if wave_heights else None,
                "min": round(min(wave_heights), 2) if wave_heights else None,
                "max": round(max(wave_heights), 2) if wave_heights else None,
                "unit": "meters"
            },
            "wind_speed": {
                "avg": round(sum(wind_speeds) / len(wind_speeds), 2) if wind_speeds else None,
                "min": round(min(wind_speeds), 2) if wind_speeds else None,
                "max": round(max(wind_speeds), 2) if wind_speeds else None,
                "unit": "m/s"
            },
            "wave_period": {
                "avg": round(sum(wave_periods) / len(wave_periods), 2) if wave_periods else None,
                "unit": "seconds"
            }
        }
        
        return {
            "status": "success",
            "data": stats
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating forecast statistics: {str(e)}"
        )
