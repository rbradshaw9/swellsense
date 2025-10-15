"""
NOAA GFS (Global Forecast System) / WaveWatch III Integration
Provides global wave and wind forecasts using NOAA's open data
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# NOAA NOMADS GFS/WaveWatch III endpoints
WAVEWATCH_BASE_URL = "https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl"
GFS_TIMEOUT = 8.0  # seconds
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
    Fetch wave and wind forecast from NOAA GFS/WaveWatch III
    
    Uses GRIB2 filtering to extract data for a small region around the coordinates.
    Provides global coverage with ~30km resolution.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, period, wind speed, or None on failure
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
        # Get current forecast cycle (00z, 06z, 12z, 18z)
        now = datetime.utcnow()
        cycle_hour = (now.hour // 6) * 6
        cycle_time = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)
        
        # If within 2 hours of cycle time, use previous cycle (data may not be ready)
        if (now - cycle_time).total_seconds() < 7200:
            cycle_time = cycle_time - timedelta(hours=6)
        
        # Format cycle time
        cycle_str = cycle_time.strftime("%Y%m%d")
        hour_str = cycle_time.strftime("%H")
        
        # Define region (1-degree box around point)
        leftlon = max(-180, lon - 1)
        rightlon = min(180, lon + 1)
        toplat = min(90, lat + 1)
        bottomlat = max(-90, lat - 1)
        
        # Normalize longitude to 0-360 for NOAA
        if leftlon < 0:
            leftlon += 360
        if rightlon < 0:
            rightlon += 360
        
        # Try multiple forecast hours (000, 003, 006)
        for forecast_hour in ["000", "003", "006"]:
            try:
                # Build GRIB2 filter URL
                params = {
                    "file": f"multi_1.glo_30m.t{hour_str}z.f{forecast_hour}.grib2",
                    "lev_surface": "on",
                    "var_HTSGW": "on",  # Significant wave height
                    "var_WIND": "on",   # Wind speed
                    "var_WVDIR": "on",  # Wave direction
                    "var_WVPER": "on",  # Wave period
                    "subregion": "",
                    "leftlon": leftlon,
                    "rightlon": rightlon,
                    "toplat": toplat,
                    "bottomlat": bottomlat,
                    "dir": f"/multi_1.{cycle_str}"
                }
                
                async with httpx.AsyncClient(timeout=GFS_TIMEOUT) as client:
                    response = await client.get(WAVEWATCH_BASE_URL, params=params)
                    
                    if response.status_code == 200:
                        # Successfully fetched GRIB2 data
                        # For now, we'll use a simplified approach since parsing GRIB2 
                        # requires additional libraries (pygrib/cfgrib)
                        # In production, you'd parse the GRIB2 file here
                        
                        # Mock response based on successful fetch
                        # TODO: Add actual GRIB2 parsing with pygrib or xarray
                        duration = (datetime.utcnow() - start_time).total_seconds()
                        logger.info(f"NOAA GFS API success in {duration:.2f}s (forecast hour: {forecast_hour})")
                        
                        # Return mock data structure for now
                        # In production, extract actual values from GRIB2
                        result = {
                            "source": "noaa_gfs",
                            "wave_height_m": None,  # Would be extracted from HTSGW
                            "wave_period_s": None,  # Would be extracted from WVPER
                            "wave_direction_deg": None,  # Would be extracted from WVDIR
                            "wind_speed_ms": None,  # Would be extracted from WIND
                            "wind_direction_deg": None,
                            "timestamp": (cycle_time + timedelta(hours=int(forecast_hour))).isoformat() + "Z",
                            "forecast_hour": forecast_hour,
                            "available": False,  # Set to True when GRIB2 parsing is implemented
                            "note": "GRIB2 parsing not yet implemented - requires pygrib or cfgrib library"
                        }
                        
                        # Cache the result
                        _gfs_cache[cache_key] = {
                            "data": result,
                            "cached_at": start_time
                        }
                        
                        return result
                        
            except httpx.TimeoutException:
                logger.warning(f"NOAA GFS timeout for forecast hour {forecast_hour}")
                continue
            except httpx.HTTPStatusError as e:
                logger.warning(f"NOAA GFS HTTP error {e.response.status_code} for hour {forecast_hour}")
                continue
            except Exception as e:
                logger.error(f"NOAA GFS error for hour {forecast_hour}: {str(e)}")
                continue
        
        # All forecast hours failed
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA GFS all forecast hours failed after {duration:.2f}s")
        return None
        
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA GFS error after {duration:.2f}s: {str(e)}")
        return None


async def health_check_noaa_gfs() -> Dict[str, Any]:
    """
    Health check for NOAA GFS service
    Tests availability of WaveWatch III data
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with a known location (mid-Pacific)
        result = await fetch_noaa_gfs(20.0, -160.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result:
            return {"ok": True, "latency_ms": int(duration)}
        else:
            return {"ok": False, "latency_ms": int(duration), "error": "No data available"}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}
