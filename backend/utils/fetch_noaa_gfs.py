"""
NOAA GFS (Global Forecast System) / WaveWatch III Integration
Provides global wave and wind forecasts via GribStream API

Uses GribStream's JSON API for clean, reliable access to GFS data
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# GribStream API Configuration
GRIBSTREAM_BASE_URL = "https://api.gribstream.com/v1/gfs"
GFS_TIMEOUT = 10.0  # seconds
CACHE_TTL = 3600  # 1 hour in seconds

# Simple in-memory cache
_gfs_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for grid cell (rounded to 0.5 degrees)"""
    lat_rounded = round(lat * 2) / 2
    lon_rounded = round(lon * 2) / 2
    return f"{lat_rounded},{lon_rounded}"


async def fetch_noaa_gfs(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch wave and wind forecast from NOAA GFS via GribStream API
    
    GribStream provides clean JSON access to GFS/WaveWatch III data
    without the complexity of GRIB2 parsing.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, period, direction, wind, or error message
    """
    start_time = datetime.utcnow()
    cache_key = _get_cache_key(lat, lon)
    
    # Check cache
    if cache_key in _gfs_cache:
        cached = _gfs_cache[cache_key]
        cache_age = (start_time - cached["cached_at"]).total_seconds()
        if cache_age < CACHE_TTL:
            logger.info(f"NOAA GFS cache hit (age: {cache_age:.0f}s)")
            return cached["data"]
    
    try:
        # Build GribStream API URL
        params = {
            "lat": lat,
            "lon": lon,
            "params": "waves,wind"  # Request wave and wind data
        }
        
        async with httpx.AsyncClient(timeout=GFS_TIMEOUT) as client:
            response = await client.get(GRIBSTREAM_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract wave data from GribStream response
            # GribStream returns current forecast with fields like:
            # wave_height, wave_period, wave_direction, wind_speed, wind_direction, time
            
            wave_height = data.get("wave_height")
            wave_period = data.get("wave_period") 
            wave_direction = data.get("wave_direction")
            wind_speed = data.get("wind_speed")
            wind_direction = data.get("wind_direction")
            timestamp = data.get("time", datetime.utcnow().isoformat() + "Z")
            
            logger.info(f"NOAA GFS (GribStream) success in {duration:.2f}s (wave: {wave_height}m)")
            
            result = {
                "source": "noaa_gfs",
                "wave_height_m": round(float(wave_height), 2) if wave_height is not None else None,
                "wave_period_s": round(float(wave_period), 1) if wave_period is not None else None,
                "wave_direction_deg": round(float(wave_direction), 1) if wave_direction is not None else None,
                "wind_speed_ms": round(float(wind_speed), 2) if wind_speed is not None else None,
                "wind_direction_deg": round(float(wind_direction), 1) if wind_direction is not None else None,
                "timestamp": timestamp,
                "available": True
            }
            
            # Cache the result
            _gfs_cache[cache_key] = {
                "data": result,
                "cached_at": start_time
            }
            
            return result
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"NOAA GFS (GribStream) timeout after {duration:.2f}s")
        return {
            "source": "noaa_gfs",
            "error": "GribStream API timeout",
            "available": False,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA GFS (GribStream) HTTP {e.response.status_code} after {duration:.2f}s")
        return {
            "source": "noaa_gfs",
            "error": f"GribStream API returned {e.response.status_code}",
            "available": False,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA GFS (GribStream) error after {duration:.2f}s: {str(e)}")
        return {
            "source": "noaa_gfs",
            "error": str(e),
            "available": False,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    


# Alias for WaveWatch III compatibility
async def fetch_ww3(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Alias for fetch_noaa_gfs - WaveWatch III data fetcher via GribStream"""
    return await fetch_noaa_gfs(lat, lon)


# Health check alias
async def health_check_ww3() -> Dict[str, Any]:
    """Alias for health_check_noaa_gfs"""
    return await health_check_noaa_gfs()


async def health_check_noaa_gfs() -> Dict[str, Any]:
    """
    Health check for NOAA GFS service via GribStream
    Tests availability of GribStream API
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with a known location (mid-Pacific)
        result = await fetch_noaa_gfs(20.0, -160.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and result.get("available"):
            return {
                "ok": True,
                "latency_ms": int(duration),
                "note": "Live data from GribStream API"
            }
        else:
            return {
                "ok": False,
                "latency_ms": int(duration),
                "note": "GribStream API unavailable or returned errors"
            }
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "ok": False,
            "latency_ms": int(duration),
            "error": str(e)[:100]
        }
