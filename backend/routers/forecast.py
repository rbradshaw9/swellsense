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
import asyncio
import logging

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

from utils.api_clients import (
    fetch_stormglass,
    fetch_openweather,
    fetch_worldtides,
    fetch_metno,
    health_check_stormglass,
    health_check_openweather,
    health_check_worldtides,
    health_check_metno
)

# Global forecast models
from utils.fetch_noaa_erddap import fetch_noaa_erddap, health_check_noaa_erddap  # Stable THREDDS endpoint
from utils.fetch_noaa_gfs import fetch_noaa_gfs, health_check_noaa_gfs  # WaveWatch III via GribStream API
from utils.fetch_era5 import fetch_era5, health_check_era5
from utils.fetch_openmeteo import fetch_openmeteo, health_check_openmeteo  # Free, reliable backup
from utils.fetch_copernicus import fetch_copernicus, health_check_copernicus  # Ocean currents + temp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["forecast"])

# Health check cache (5 minute TTL)
_health_cache = {"timestamp": None, "data": None}
_health_cache_ttl = 300  # 5 minutes in seconds


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
    Get resilient multi-source forecast from all available data sources worldwide
    
    Fetches data in parallel from StormGlass, OpenWeather, WorldTides, and Met.no APIs.
    Returns unified forecast even if some sources fail (graceful degradation).
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        hours: Number of hours to forecast (default 12)
        db: Database session
    
    Returns:
        Unified forecast with data from all available sources, partial flag if any failed
        
    Example:
        /api/forecast/global?lat=33.63&lon=-118.00&hours=24
    """
    request_start = datetime.utcnow()
    
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        logger.info(f"Global forecast request for lat={lat}, lon={lon}")
        
        # Fetch all sources in parallel with return_exceptions=True for fault tolerance
        # Regional APIs + Global models + Free backups = 9 total sources
        results = await asyncio.gather(
            fetch_stormglass(lat, lon),
            fetch_openweather(lat, lon),
            fetch_worldtides(lat, lon),
            fetch_metno(lat, lon),
            fetch_noaa_erddap(lat, lon),
            fetch_noaa_gfs(lat, lon),
            fetch_era5(lat, lon),
            fetch_openmeteo(lat, lon),
            fetch_copernicus(lat, lon),
            return_exceptions=True
        )
        
        # Unpack results (None if failed or exception occurred)
        stormglass_data = results[0] if not isinstance(results[0], Exception) else None
        openweather_data = results[1] if not isinstance(results[1], Exception) else None
        worldtides_data = results[2] if not isinstance(results[2], Exception) else None
        metno_data = results[3] if not isinstance(results[3], Exception) else None
        noaa_erddap_data = results[4] if not isinstance(results[4], Exception) else None
        noaa_gfs_data = results[5] if not isinstance(results[5], Exception) else None
        era5_data = results[6] if not isinstance(results[6], Exception) else None
        openmeteo_data = results[7] if not isinstance(results[7], Exception) else None
        copernicus_data = results[8] if not isinstance(results[8], Exception) else None
        
        # Track which sources succeeded
        sources_available = []
        sources_failed = []
        
        if stormglass_data:
            sources_available.append("stormglass")
        else:
            sources_failed.append("stormglass")
            
        if openweather_data:
            sources_available.append("openweather")
        else:
            sources_failed.append("openweather")
            
        if worldtides_data:
            sources_available.append("worldtides")
        else:
            sources_failed.append("worldtides")
            
        if metno_data:
            sources_available.append("metno")
        else:
            sources_failed.append("metno")
        
        if noaa_erddap_data and noaa_erddap_data.get("available") is not False:
            sources_available.append("noaa_erddap")
        else:
            sources_failed.append("noaa_erddap")
        
        if noaa_gfs_data and noaa_gfs_data.get("available") is not False:
            sources_available.append("noaa_gfs")
        else:
            sources_failed.append("noaa_gfs")
        
        if era5_data and era5_data.get("available") is not False:
            sources_available.append("era5")
        else:
            sources_failed.append("era5")
        
        if openmeteo_data and openmeteo_data.get("available") is not False:
            sources_available.append("openmeteo")
        else:
            sources_failed.append("openmeteo")
        
        if copernicus_data and copernicus_data.get("available") is not False:
            sources_available.append("copernicus_marine")
        else:
            sources_failed.append("copernicus_marine")
        
        # Calculate averages from available data
        wave_heights = []
        wind_speeds = []
        temperatures = []
        
        if stormglass_data and stormglass_data.get("wave_height_m"):
            wave_heights.append(stormglass_data["wave_height_m"])
        if metno_data and metno_data.get("wave_height_m"):
            wave_heights.append(metno_data["wave_height_m"])
        if noaa_erddap_data and noaa_erddap_data.get("wave_height_m"):
            wave_heights.append(noaa_erddap_data["wave_height_m"])
        if noaa_gfs_data and noaa_gfs_data.get("wave_height_m"):
            wave_heights.append(noaa_gfs_data["wave_height_m"])
        if era5_data and era5_data.get("wave_height_m"):
            wave_heights.append(era5_data["wave_height_m"])
        if openmeteo_data and openmeteo_data.get("wave_height_m"):
            wave_heights.append(openmeteo_data["wave_height_m"])
            
        if stormglass_data and stormglass_data.get("wind_speed_ms"):
            wind_speeds.append(stormglass_data["wind_speed_ms"])
        if openweather_data and openweather_data.get("wind_speed_ms"):
            wind_speeds.append(openweather_data["wind_speed_ms"])
        if noaa_erddap_data and noaa_erddap_data.get("wind_speed_ms"):
            wind_speeds.append(noaa_erddap_data["wind_speed_ms"])
        if noaa_gfs_data and noaa_gfs_data.get("wind_speed_ms"):
            wind_speeds.append(noaa_gfs_data["wind_speed_ms"])
        if era5_data and era5_data.get("wind_speed_ms"):
            wind_speeds.append(era5_data["wind_speed_ms"])
            
        if openweather_data and openweather_data.get("temperature_c"):
            temperatures.append(openweather_data["temperature_c"])
        
        # Build human-readable conditions summary
        conditions_text = "Forecast unavailable"
        if wave_heights and wind_speeds:
            avg_wave = sum(wave_heights) / len(wave_heights)
            avg_wind = sum(wind_speeds) / len(wind_speeds)
            
            # Convert to feet for surf description
            wave_ft = avg_wave * 3.28084
            wind_kts = avg_wind * 1.94384
            
            # Classify wave size
            if wave_ft < 2:
                size = "Small"
            elif wave_ft < 4:
                size = "2-3ft"
            elif wave_ft < 6:
                size = "4-5ft"
            elif wave_ft < 8:
                size = "6-7ft"
            else:
                size = f"{int(wave_ft)}ft+"
            
            # Classify wind
            if wind_kts < 5:
                wind_desc = "calm"
            elif wind_kts < 10:
                wind_desc = "light wind"
            elif wind_kts < 15:
                wind_desc = "moderate wind"
            else:
                wind_desc = "strong wind"
            
            conditions_text = f"{size} waves, {wind_desc}"
        
        # Calculate total response time
        duration = (datetime.utcnow() - request_start).total_seconds()
        logger.info(f"Global forecast completed in {duration:.2f}s with {len(sources_available)}/9 sources")
        
        # Build unified response
        response = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {
                "lat": lat,
                "lon": lon
            },
            "sources": {
                "stormglass": stormglass_data,
                "openweather": openweather_data,
                "worldtides": worldtides_data,
                "metno": metno_data,
                "noaa_erddap": noaa_erddap_data,
                "noaa_gfs": noaa_gfs_data,
                "era5": era5_data,
                "openmeteo": openmeteo_data,
                "copernicus_marine": copernicus_data
            },
            "summary": {
                "wave_height_m": round(sum(wave_heights) / len(wave_heights), 2) if wave_heights else None,
                "wind_speed_ms": round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None,
                "temperature_c": round(sum(temperatures) / len(temperatures), 1) if temperatures else None,
                "tide_height_m": worldtides_data.get("current_tide_m") if worldtides_data else None,
                "conditions": conditions_text
            },
            "partial": len(sources_failed) > 0,
            "sources_available": sources_available,
            "sources_failed": sources_failed if sources_failed else None,
            "response_time_s": round(duration, 2)
        }
        
        # Always return 200 even if partial (graceful degradation)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.utcnow() - request_start).total_seconds()
        logger.error(f"Global forecast error after {duration:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating global forecast: {str(e)}"
        )


@router.get("/forecast/debug")
async def get_forecast_debug(
    lat: float,
    lon: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Debug endpoint showing raw data from each source + aggregated result with variance
    
    Returns detailed breakdown of:
    - Raw values from each source (wave height, wind speed, etc.)
    - Aggregated values (simple mean)
    - Variance and standard deviation across sources
    - Data quality metrics (agreement between sources)
    
    Use this endpoint to:
    - Verify individual source accuracy
    - Identify outlier sources
    - Debug aggregation logic
    - Compare source performance by region
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        db: Database session
    
    Returns:
        Detailed debug information with raw + aggregated data
        
    Example:
        /api/forecast/debug?lat=18.33&lon=-67.25  (Rincon, Puerto Rico)
    """
    request_start = datetime.utcnow()
    
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        logger.info(f"Debug forecast request for lat={lat}, lon={lon}")
        
        # Fetch all sources in parallel
        results = await asyncio.gather(
            fetch_stormglass(lat, lon),
            fetch_openweather(lat, lon),
            fetch_worldtides(lat, lon),
            fetch_metno(lat, lon),
            fetch_noaa_erddap(lat, lon),
            fetch_noaa_gfs(lat, lon),
            fetch_era5(lat, lon),
            fetch_openmeteo(lat, lon),
            fetch_copernicus(lat, lon),
            return_exceptions=True
        )
        
        # Unpack results with error handling (handle None, Exception, and dict)
        def normalize_result(result, source_name):
            if result is None:
                return {"error": f"{source_name} returned None", "available": False}
            elif isinstance(result, Exception):
                return {"error": str(result)[:200], "available": False}
            elif isinstance(result, dict):
                return result
            else:
                return {"error": f"Unexpected type: {type(result)}", "available": False}
        
        source_data = {
            "stormglass": normalize_result(results[0], "stormglass"),
            "openweather": normalize_result(results[1], "openweather"),
            "worldtides": normalize_result(results[2], "worldtides"),
            "metno": normalize_result(results[3], "metno"),
            "noaa_erddap": normalize_result(results[4], "noaa_erddap"),
            "noaa_gfs": normalize_result(results[5], "noaa_gfs"),
            "era5": normalize_result(results[6], "era5"),
            "openmeteo": normalize_result(results[7], "openmeteo"),
            "copernicus_marine": normalize_result(results[8], "copernicus_marine")
        }
        
        # Extract wave heights from all sources
        wave_heights = []
        wave_heights_by_source = {}
        for source_name, data in source_data.items():
            if data and data.get("available") is not False and data.get("wave_height_m") is not None:
                wave_heights.append(data["wave_height_m"])
                wave_heights_by_source[source_name] = data["wave_height_m"]
        
        # Extract wind speeds from all sources
        wind_speeds = []
        wind_speeds_by_source = {}
        for source_name, data in source_data.items():
            if data and data.get("available") is not False and data.get("wind_speed_ms") is not None:
                wind_speeds.append(data["wind_speed_ms"])
                wind_speeds_by_source[source_name] = data["wind_speed_ms"]
        
        # Extract wave periods
        wave_periods = []
        wave_periods_by_source = {}
        for source_name, data in source_data.items():
            if data and data.get("available") is not False and data.get("wave_period_s") is not None:
                wave_periods.append(data["wave_period_s"])
                wave_periods_by_source[source_name] = data["wave_period_s"]
        
        # Calculate statistics for wave height
        def calculate_stats(values: List[float], name: str) -> Dict[str, Any]:
            if not values:
                return {"available": False}
            
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values) if len(values) > 1 else 0
            std_dev = math.sqrt(variance)
            coefficient_of_variation = (std_dev / mean * 100) if mean > 0 else 0
            
            return {
                "available": True,
                "count": len(values),
                "mean": round(mean, 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "std_dev": round(std_dev, 2),
                "variance": round(variance, 3),
                "coefficient_of_variation_pct": round(coefficient_of_variation, 1),
                "agreement_level": (
                    "excellent" if coefficient_of_variation < 10 else
                    "good" if coefficient_of_variation < 20 else
                    "moderate" if coefficient_of_variation < 30 else
                    "poor"
                )
            }
        
        wave_height_stats = calculate_stats(wave_heights, "wave_height_m")
        wind_speed_stats = calculate_stats(wind_speeds, "wind_speed_ms")
        wave_period_stats = calculate_stats(wave_periods, "wave_period_s")
        
        # Identify outliers (values more than 1.5 std deviations from mean)
        def find_outliers(values_by_source: Dict[str, float], mean: float, std_dev: float) -> List[str]:
            if std_dev == 0:
                return []
            outliers = []
            for source, value in values_by_source.items():
                z_score = abs(value - mean) / std_dev
                if z_score > 1.5:
                    outliers.append(f"{source} ({value:.2f}m, z-score: {z_score:.1f})")
            return outliers
        
        wave_height_outliers = []
        if wave_height_stats.get("available"):
            wave_height_outliers = find_outliers(
                wave_heights_by_source,
                wave_height_stats["mean"],
                wave_height_stats["std_dev"]
            )
        
        wind_speed_outliers = []
        if wind_speed_stats.get("available"):
            wind_speed_outliers = find_outliers(
                wind_speeds_by_source,
                wind_speed_stats["mean"],
                wind_speed_stats["std_dev"]
            )
        
        # Track sources status
        sources_available = [k for k, v in source_data.items() if v.get("available") is not False]
        sources_failed = [k for k, v in source_data.items() if v.get("available") is False]
        
        # Calculate response time
        duration = (datetime.utcnow() - request_start).total_seconds()
        
        # Build debug response
        debug_response = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {
                "lat": lat,
                "lon": lon
            },
            "raw_data_by_source": source_data,
            "aggregated_values": {
                "wave_height_m": wave_height_stats.get("mean") if wave_height_stats.get("available") else None,
                "wind_speed_ms": wind_speed_stats.get("mean") if wind_speed_stats.get("available") else None,
                "wave_period_s": wave_period_stats.get("mean") if wave_period_stats.get("available") else None
            },
            "statistics": {
                "wave_height": wave_height_stats,
                "wind_speed": wind_speed_stats,
                "wave_period": wave_period_stats
            },
            "data_quality": {
                "wave_height_outliers": wave_height_outliers if wave_height_outliers else None,
                "wind_speed_outliers": wind_speed_outliers if wind_speed_outliers else None,
                "overall_agreement": (
                    "excellent" if all(
                        stat.get("agreement_level") in ["excellent", "good"]
                        for stat in [wave_height_stats, wind_speed_stats]
                        if stat.get("available")
                    ) else "needs_review"
                )
            },
            "sources_status": {
                "available": sources_available,
                "failed": sources_failed if sources_failed else None,
                "availability_pct": round(len(sources_available) / 9 * 100, 1)
            },
            "response_time_s": round(duration, 2),
            "note": "This debug endpoint shows raw data from each source. Use for troubleshooting accuracy issues."
        }
        
        logger.info(f"Debug forecast completed in {duration:.2f}s - {len(sources_available)}/9 sources available")
        
        return debug_response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.utcnow() - request_start).total_seconds()
        logger.error(f"Debug forecast error after {duration:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating debug forecast: {str(e)}"
        )


@router.get("/forecast/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check for external APIs and database connectivity
    
    Returns service status, latency metrics, and database connection health.
    Results are cached for 5 minutes to avoid rate limiting.
    
    Returns:
        200 OK if all services healthy
        207 Multi-Status if some services degraded
        
    Example:
        /api/forecast/health
    """
    global _health_cache
    
    request_start = datetime.utcnow()
    
    # Check cache validity
    if _health_cache["timestamp"]:
        cache_age = (request_start - _health_cache["timestamp"]).total_seconds()
        if cache_age < _health_cache_ttl:
            logger.info(f"Returning cached health check (age: {cache_age:.0f}s)")
            return _health_cache["data"]
    
    try:
        logger.info("Running health checks on all services")
        
        # Test database connection
        db_ok = False
        try:
            await db.execute(select(1))
            db_ok = True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
        
        # Test all external APIs in parallel
        api_results = await asyncio.gather(
            health_check_stormglass(),
            health_check_openweather(),
            health_check_worldtides(),
            health_check_metno(),
            health_check_noaa_erddap(),
            health_check_noaa_gfs(),
            health_check_era5(),
            health_check_openmeteo(),
            health_check_copernicus(),
            return_exceptions=True
        )
        
        # Unpack results (handle exceptions)
        stormglass_health = api_results[0] if not isinstance(api_results[0], Exception) else {"ok": False, "error": str(api_results[0])[:100]}
        openweather_health = api_results[1] if not isinstance(api_results[1], Exception) else {"ok": False, "error": str(api_results[1])[:100]}
        worldtides_health = api_results[2] if not isinstance(api_results[2], Exception) else {"ok": False, "error": str(api_results[2])[:100]}
        metno_health = api_results[3] if not isinstance(api_results[3], Exception) else {"ok": False, "error": str(api_results[3])[:100]}
        noaa_erddap_health = api_results[4] if not isinstance(api_results[4], Exception) else {"ok": False, "error": str(api_results[4])[:100]}
        noaa_gfs_health = api_results[5] if not isinstance(api_results[5], Exception) else {"ok": False, "error": str(api_results[5])[:100]}
        era5_health = api_results[6] if not isinstance(api_results[6], Exception) else {"ok": False, "error": str(api_results[6])[:100]}
        openmeteo_health = api_results[7] if not isinstance(api_results[7], Exception) else {"ok": False, "error": str(api_results[7])[:100]}
        copernicus_health = api_results[8] if not isinstance(api_results[8], Exception) else {"ok": False, "error": str(api_results[8])[:100]}
        
        # Determine overall status
        all_services = [
            stormglass_health.get("ok", False),
            openweather_health.get("ok", False),
            worldtides_health.get("ok", False),
            metno_health.get("ok", False),
            noaa_erddap_health.get("ok", False),
            noaa_gfs_health.get("ok", False),
            era5_health.get("ok", False),
            openmeteo_health.get("ok", False),
            copernicus_health.get("ok", False),
            db_ok
        ]
        
        failed_services = []
        if not stormglass_health.get("ok"):
            failed_services.append("stormglass")
        if not openweather_health.get("ok"):
            failed_services.append("openweather")
        if not worldtides_health.get("ok"):
            failed_services.append("worldtides")
        if not metno_health.get("ok"):
            failed_services.append("metno")
        if not noaa_erddap_health.get("ok"):
            failed_services.append("noaa_erddap")
        if not noaa_gfs_health.get("ok"):
            failed_services.append("noaa_gfs")
        if not era5_health.get("ok"):
            failed_services.append("era5")
        if not openmeteo_health.get("ok"):
            failed_services.append("openmeteo")
        if not copernicus_health.get("ok"):
            failed_services.append("copernicus_marine")
        if not db_ok:
            failed_services.append("database")
        
        overall_status = "ok" if all(all_services) else "degraded"
        
        duration = (datetime.utcnow() - request_start).total_seconds()
        
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {
                "stormglass": stormglass_health,
                "openweather": openweather_health,
                "worldtides": worldtides_health,
                "metno": metno_health,
                "noaa_erddap": noaa_erddap_health,
                "noaa_gfs": noaa_gfs_health,
                "era5": era5_health,
                "openmeteo": openmeteo_health,
                "copernicus_marine": copernicus_health
            },
            "database": {
                "connected": db_ok
            },
            "failed_services": failed_services if failed_services else None,
            "version": "v0.6",
            "check_duration_s": round(duration, 2)
        }
        
        # Update cache
        _health_cache = {
            "timestamp": request_start,
            "data": response
        }
        
        logger.info(f"Health check complete: {overall_status} ({len(failed_services)} failures)")
        
        # Return 207 Multi-Status if degraded, 200 if ok
        status_code = 207 if overall_status == "degraded" else 200
        
        return response
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing health check: {str(e)}"
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
