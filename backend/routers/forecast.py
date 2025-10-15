"""
Forecast API endpoints for SwellSense
Serves surf condition data from the database
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import (
    get_db, 
    SurfCondition, 
    BuoyStation,
    MarineCondition,
    WeatherData,
    TideData,
    OceanCurrent
)

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/forecast")
async def get_forecast(
    limit: int = 24,
    buoy_id: Optional[str] = None,
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
            "buoy_id": buoy_id,
            "time_range_hours": hours,
            "data_points": len(conditions),
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating forecast stats: {str(e)}"
        )


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km using Haversine formula"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


@router.get("/forecast/global")
async def get_global_forecast(
    lat: float,
    lon: float,
    hours: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """
    Get merged forecast from all available data sources for any location worldwide
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        hours: Number of hours to forecast (default 12)
        db: Database session
    
    Returns:
        Unified forecast with data from NOAA, StormGlass, Met.no, OpenWeather, WorldTides
        
    Example:
        /api/forecast/global?lat=33.63&lon=-118.00&hours=24
    """
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        # Time window
        now = datetime.utcnow()
        future = now + timedelta(hours=hours)
        
        # Find nearest buoy station for location name
        buoy_stmt = select(BuoyStation)
        buoy_result = await db.execute(buoy_stmt)
        buoy_stations = buoy_result.scalars().all()
        
        nearest_buoy = None
        min_distance = float('inf')
        
        for station in buoy_stations:
            dist = calculate_distance(lat, lon, station.latitude, station.longitude)
            if dist < min_distance:
                min_distance = dist
                nearest_buoy = station
        
        location_name = f"{nearest_buoy.region}" if nearest_buoy else f"{lat}, {lon}"
        
        # Search radius in degrees (~50km)
        radius = 0.5
        
        # Query marine conditions (StormGlass, Met.no, NOAA)
        marine_stmt = select(MarineCondition).where(
            and_(
                MarineCondition.timestamp >= now,
                MarineCondition.timestamp <= future,
                MarineCondition.latitude.between(lat - radius, lat + radius),
                MarineCondition.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(MarineCondition.timestamp)
        
        marine_result = await db.execute(marine_stmt)
        marine_data = marine_result.scalars().all()
        
        # Query weather data (OpenWeatherMap)
        weather_stmt = select(WeatherData).where(
            and_(
                WeatherData.timestamp >= now,
                WeatherData.timestamp <= future,
                WeatherData.latitude.between(lat - radius, lat + radius),
                WeatherData.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(WeatherData.timestamp)
        
        weather_result = await db.execute(weather_stmt)
        weather_data = weather_result.scalars().all()
        
        # Query tide data (WorldTides)
        tide_stmt = select(TideData).where(
            and_(
                TideData.timestamp >= now,
                TideData.timestamp <= future,
                TideData.latitude.between(lat - radius, lat + radius),
                TideData.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(TideData.timestamp)
        
        tide_result = await db.execute(tide_stmt)
        tide_data = tide_result.scalars().all()
        
        # Aggregate latest conditions
        latest_marine = marine_data[0] if marine_data else None
        latest_weather = weather_data[0] if weather_data else None
        latest_tide = tide_data[0] if tide_data else None
        
        # Calculate averages from marine data
        wave_heights = [m.wave_height for m in marine_data if m.wave_height]
        swell_periods = [m.swell_period for m in marine_data if m.swell_period]
        wave_directions = [m.wave_direction for m in marine_data if m.wave_direction]
        water_temps = [m.water_temperature for m in marine_data if m.water_temperature]
        current_speeds = [m.current_speed for m in marine_data if m.current_speed]
        
        # Calculate averages from weather data
        wind_speeds = [w.wind_speed for w in weather_data if w.wind_speed]
        wind_directions = [w.wind_direction for w in weather_data if w.wind_direction]
        temperatures = [w.temperature for w in weather_data if w.temperature]
        
        # Get tide heights
        tide_heights = [t.tide_height_meters for t in tide_data if t.tide_height_meters]
        
        # Determine sources used
        sources_used = []
        if marine_data:
            sources = set(m.source for m in marine_data)
            sources_used.extend(list(sources))
        if weather_data:
            sources_used.append('openweather')
        if tide_data:
            sources_used.append('worldtides')
        
        # Build response
        response = {
            "location": location_name,
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": now.isoformat() + "Z",
            "forecast_hours": hours,
            "data_points": {
                "marine": len(marine_data),
                "weather": len(weather_data),
                "tide": len(tide_data)
            },
            "current_conditions": {
                "wave_height_m": round(wave_heights[0], 2) if wave_heights else None,
                "swell_period_s": round(swell_periods[0], 1) if swell_periods else None,
                "swell_direction_deg": round(wave_directions[0], 0) if wave_directions else None,
                "wind_speed_ms": round(wind_speeds[0], 1) if wind_speeds else None,
                "wind_direction_deg": round(wind_directions[0], 0) if wind_directions else None,
                "water_temp_c": round(water_temps[0], 1) if water_temps else None,
                "air_temp_c": round(temperatures[0], 1) if temperatures else None,
                "tide_m": round(tide_heights[0], 2) if tide_heights else None,
                "current_speed_ms": round(current_speeds[0], 2) if current_speeds else None,
            },
            "forecast_averages": {
                "wave_height_m": round(sum(wave_heights) / len(wave_heights), 2) if wave_heights else None,
                "swell_period_s": round(sum(swell_periods) / len(swell_periods), 1) if swell_periods else None,
                "wind_speed_ms": round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None,
                "water_temp_c": round(sum(water_temps) / len(water_temps), 1) if water_temps else None,
            },
            "sources_used": list(set(sources_used)),
            "nearest_buoy": {
                "id": nearest_buoy.station_id if nearest_buoy else None,
                "distance_km": round(min_distance, 1) if nearest_buoy else None
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating global forecast: {str(e)}"
        )


@router.get("/forecast/latest")
async def get_latest_forecast(
    buoy_id: Optional[str] = None,
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
    buoy_id: Optional[str] = None,
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
