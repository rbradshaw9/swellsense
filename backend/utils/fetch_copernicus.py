"""
Copernicus Marine Environment Monitoring Service (CMEMS) Integration
Provides high-quality ocean current and sea temperature data
Requires free CMEMS account credentials
"""
import httpx
import logging
import io
import os
from typing import Optional, Dict, Any
from datetime import datetime
import math

logger = logging.getLogger(__name__)

# CMEMS Configuration
CMEMS_BASE_URL = "https://nrt.cmems-du.eu/thredds/ncss/global-analysis-forecast-phy-001-024-hourly"
CMEMS_TIMEOUT = 15.0  # seconds
CACHE_TTL = 3600  # 1 hour

# Get credentials from environment (check both Railway and standard naming)
CMEMS_USERNAME = os.getenv("CMEMS_USERNAME") or os.getenv("CMEMS_USER")
CMEMS_PASSWORD = os.getenv("CMEMS_PASSWORD") or os.getenv("CMEMS_PASS")

# Simple in-memory cache
_cmems_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key (rounded to 0.25 degrees)"""
    lat_rounded = round(lat * 4) / 4
    lon_rounded = round(lon * 4) / 4
    return f"{lat_rounded},{lon_rounded}"


async def fetch_copernicus(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch ocean data from Copernicus Marine Service
    
    CMEMS provides high-resolution global ocean analysis and forecasts
    including currents, sea temperature, and salinity.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with ocean current speed/direction, sea temperature
    """
    start_time = datetime.utcnow()
    cache_key = _get_cache_key(lat, lon)
    
    # Check cache
    if cache_key in _cmems_cache:
        cached = _cmems_cache[cache_key]
        cache_age = (start_time - cached["cached_at"]).total_seconds()
        if cache_age < CACHE_TTL:
            logger.info(f"Copernicus Marine cache hit (age: {cache_age:.0f}s)")
            return cached["data"]
    
    # Check if credentials are configured
    if not CMEMS_USERNAME or not CMEMS_PASSWORD:
        logger.info("Copernicus Marine credentials not configured")
        return {
            "source": "copernicus_marine",
            "current_speed_ms": None,
            "current_direction_deg": None,
            "sea_temp_c": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "available": False,
            "note": "CMEMS credentials not configured - set CMEMS_USERNAME and CMEMS_PASSWORD"
        }
    
    try:
        # Define bounding box
        north = min(90, lat + 0.5)
        south = max(-90, lat - 0.5)
        east = min(180, lon + 0.5)
        west = max(-180, lon - 0.5)
        
        # Build query URL
        # Note: Actual CMEMS THREDDS endpoints may vary - this is a template
        url = (
            f"{CMEMS_BASE_URL}?"
            f"var=uo&var=vo&var=thetao"
            f"&north={north}&south={south}&east={east}&west={west}"
            "&time=latest&accept=netcdf"
        )
        
        auth = (CMEMS_USERNAME, CMEMS_PASSWORD)
        
        async with httpx.AsyncClient(timeout=CMEMS_TIMEOUT, auth=auth) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse NetCDF response
            try:
                import xarray as xr
                
                ds = xr.open_dataset(io.BytesIO(response.content))
                
                # Extract ocean currents (U and V components)
                if "uo" in ds.variables and "vo" in ds.variables:
                    u = float(ds["uo"].mean().values)
                    v = float(ds["vo"].mean().values)
                    
                    # Calculate current speed and direction
                    current_speed = math.sqrt(u**2 + v**2)
                    current_direction = (math.degrees(math.atan2(v, u)) + 90) % 360
                else:
                    u = v = None
                    current_speed = None
                    current_direction = None
                
                # Extract sea temperature
                if "thetao" in ds.variables:
                    sea_temp = float(ds["thetao"].mean().values)
                else:
                    sea_temp = None
                
                # Get timestamp
                if "time" in ds.variables:
                    time_val = ds["time"].values
                    if hasattr(time_val, 'astype'):
                        timestamp = str(time_val.astype('datetime64[s]'))
                    else:
                        timestamp = datetime.utcnow().isoformat() + "Z"
                else:
                    timestamp = datetime.utcnow().isoformat() + "Z"
                
                ds.close()
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Copernicus Marine API success in {duration:.2f}s")
                
                result = {
                    "source": "copernicus_marine",
                    "current_speed_ms": current_speed,
                    "current_direction_deg": current_direction,
                    "sea_temp_c": sea_temp,
                    "timestamp": timestamp,
                    "available": True
                }
                
                # Cache the result
                _cmems_cache[cache_key] = {
                    "data": result,
                    "cached_at": start_time
                }
                
                return result
                
            except ImportError:
                logger.error("xarray not installed for Copernicus parsing")
                return {
                    "source": "copernicus_marine",
                    "available": False,
                    "note": "xarray required for NetCDF parsing"
                }
            except Exception as e:
                logger.error(f"NetCDF parsing error: {str(e)}")
                return None
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"Copernicus Marine API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        if e.response.status_code == 401:
            logger.error("Copernicus Marine authentication failed - check credentials")
        else:
            logger.error(f"Copernicus Marine HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Copernicus Marine error after {duration:.2f}s: {str(e)}")
        return None


async def health_check_copernicus() -> Dict[str, Any]:
    """
    Health check for Copernicus Marine service
    Tests availability with credentials
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with mid-Atlantic location
        result = await fetch_copernicus(30.0, -40.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and result.get("available"):
            return {"ok": True, "latency_ms": int(duration)}
        elif result:
            return {
                "ok": False,
                "latency_ms": int(duration),
                "error": result.get("note", "No data available")
            }
        else:
            return {"ok": False, "latency_ms": int(duration), "error": "No response"}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}
