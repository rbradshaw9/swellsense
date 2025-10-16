"""
NOAA ERDDAP/THREDDS WaveWatch III Integration
Provides stable global wave forecasts using NOAA's THREDDS data server
Replaces the unreliable CGI filter_wave_multi.pl endpoint
"""
import httpx
import logging
import io
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# NOAA THREDDS/ERDDAP Configuration
# Using NOAA's NOMADS operational WaveWatch III data via OPeNDAP
# Note: The DODS endpoint uses OPeNDAP protocol directly (no /ncss or /dodsC prefix)
THREDDS_BASE_URL = "https://nomads.ncep.noaa.gov/dods/wave/gfswave.global_30m"
ERDDAP_TIMEOUT = 10.0  # seconds
CACHE_TTL = 3600  # 1 hour in seconds

# Simple in-memory cache
_erddap_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for grid cell (rounded to 0.5 degrees)"""
    lat_rounded = round(lat * 2) / 2
    lon_rounded = round(lon * 2) / 2
    return f"{lat_rounded},{lon_rounded}"


async def fetch_noaa_erddap(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch wave forecast from NOAA WaveWatch III via THREDDS/ERDDAP
    
    Uses NetCDF Subset Service (NCSS) to retrieve global wave data.
    More reliable than the CGI filter endpoint.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, period, direction, or None on failure
    """
    start_time = datetime.utcnow()
    cache_key = _get_cache_key(lat, lon)
    
    # Check cache
    if cache_key in _erddap_cache:
        cached = _erddap_cache[cache_key]
        cache_age = (start_time - cached["cached_at"]).total_seconds()
        if cache_age < CACHE_TTL:
            logger.info(f"NOAA ERDDAP cache hit (age: {cache_age:.0f}s)")
            return cached["data"]
    
    try:
        # Define bounding box (1-degree around point)
        north = min(90, lat + 1)
        south = max(-90, lat - 1)
        east = min(180, lon + 1)
        west = max(-180, lon - 1)
        
        # Build NCSS query parameters
        params = {
            "var": "HTSGW,WVPER,WVDIR,WIND",  # Significant wave height, period, direction, wind
            "north": north,
            "south": south,
            "east": east,
            "west": west,
            "time": "latest",
            "accept": "netcdf"
        }
        
        async with httpx.AsyncClient(timeout=ERDDAP_TIMEOUT) as client:
            response = await client.get(THREDDS_BASE_URL, params=params)
            response.raise_for_status()
            
            # Parse NetCDF response
            try:
                import xarray as xr
                
                # Open NetCDF from bytes - h5netcdf can read BytesIO
                ds = xr.open_dataset(io.BytesIO(response.content), engine='h5netcdf')
                
                # Extract variables (take mean if multiple grid points)
                wave_height = None
                wave_period = None
                wave_direction = None
                wind_speed = None
                
                if "HTSGW" in ds.variables:
                    wave_height = float(ds["HTSGW"].mean().values)
                    
                if "WVPER" in ds.variables:
                    wave_period = float(ds["WVPER"].mean().values)
                    
                if "WVDIR" in ds.variables:
                    wave_direction = float(ds["WVDIR"].mean().values)
                    
                if "WIND" in ds.variables:
                    wind_speed = float(ds["WIND"].mean().values)
                
                # Get timestamp from data
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
                logger.info(f"NOAA ERDDAP API success in {duration:.2f}s")
                
                result = {
                    "source": "noaa_erddap",
                    "wave_height_m": wave_height,
                    "wave_period_s": wave_period,
                    "wave_direction_deg": wave_direction,
                    "wind_speed_ms": wind_speed,
                    "timestamp": timestamp,
                    "available": True
                }
                
                # Cache the result
                _erddap_cache[cache_key] = {
                    "data": result,
                    "cached_at": start_time
                }
                
                return result
                
            except ImportError as e:
                logger.error(f"xarray not installed: {str(e)}")
                logger.info("Install with: pip install xarray netCDF4")
                
                # Return mock response indicating xarray is needed
                result = {
                    "source": "noaa_erddap",
                    "wave_height_m": None,
                    "wave_period_s": None,
                    "wave_direction_deg": None,
                    "wind_speed_ms": None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "available": False,
                    "note": "xarray library required for NetCDF parsing - install with: pip install xarray netCDF4"
                }
                return result
                
            except Exception as e:
                logger.error(f"NetCDF parsing error: {str(e)}")
                return None
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"NOAA ERDDAP API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA ERDDAP API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"NOAA ERDDAP API error after {duration:.2f}s: {str(e)}")
        return None


async def health_check_noaa_erddap() -> Dict[str, Any]:
    """
    Health check for NOAA ERDDAP/THREDDS service
    Tests availability of WaveWatch III NetCDF data
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with equator location (always has data)
        result = await fetch_noaa_erddap(0.0, 0.0)
        
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
