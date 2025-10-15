"""
Copernicus ERA5 (ECMWF) Reanalysis Integration
Provides high-quality global atmospheric and ocean reanalysis data
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

# ERA5 Configuration
ERA5_TIMEOUT = 10.0  # seconds
CACHE_TTL = 3600  # 1 hour

# Simple in-memory cache
_era5_cache: Dict[str, Dict[str, Any]] = {}

# Note: Full ERA5 access requires Copernicus Climate Data Store (CDS) API key
# For now, we'll use a mock implementation with the structure ready for integration
CDS_API_KEY = None  # Set this when you have a CDS API account


def _calculate_wind_speed(u: float, v: float) -> float:
    """Calculate wind speed from U and V components"""
    return math.sqrt(u**2 + v**2)


def _calculate_wind_direction(u: float, v: float) -> float:
    """Calculate wind direction from U and V components (meteorological convention)"""
    direction = math.degrees(math.atan2(-u, -v))
    if direction < 0:
        direction += 360
    return direction


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key for grid cell (rounded to 0.25 degrees - ERA5 resolution)"""
    lat_rounded = round(lat * 4) / 4
    lon_rounded = round(lon * 4) / 4
    return f"{lat_rounded},{lon_rounded}"


async def fetch_era5(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch atmospheric and ocean data from Copernicus ERA5
    
    ERA5 provides hourly reanalysis data at 0.25° resolution (~30km).
    Includes wind components and wave height from ECMWF's global model.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, wind speed/direction, or None on failure
    """
    start_time = datetime.utcnow()
    cache_key = _get_cache_key(lat, lon)
    
    # Check cache
    if cache_key in _era5_cache:
        cached = _era5_cache[cache_key]
        cache_age = (start_time - cached["cached_at"]).total_seconds()
        if cache_age < CACHE_TTL:
            logger.info(f"ERA5 cache hit (age: {cache_age:.0f}s)")
            return cached["data"]
    
    try:
        # ERA5 requires CDS API which needs authentication
        # For now, return a mock response with the correct structure
        # TODO: Implement actual CDS API integration when API key is available
        
        if CDS_API_KEY is None:
            # Mock implementation - simulates what would be returned
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"ERA5 API mock response in {duration:.2f}s (CDS API key not configured)")
            
            result = {
                "source": "era5",
                "wave_height_m": None,
                "wind_speed_ms": None,
                "wind_direction_deg": None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "available": False,
                "note": "ERA5 requires Copernicus CDS API key - mock data returned"
            }
            
            # Cache the result
            _era5_cache[cache_key] = {
                "data": result,
                "cached_at": start_time
            }
            
            return result
        
        # Real implementation (when CDS API key is available)
        # This would use the cdsapi library:
        # 
        # import cdsapi
        # 
        # c = cdsapi.Client()
        # 
        # c.retrieve(
        #     'reanalysis-era5-single-levels',
        #     {
        #         'product_type': 'reanalysis',
        #         'variable': [
        #             '10m_u_component_of_wind',
        #             '10m_v_component_of_wind',
        #             'significant_height_of_combined_wind_waves_and_swell'
        #         ],
        #         'year': datetime.utcnow().year,
        #         'month': datetime.utcnow().month,
        #         'day': datetime.utcnow().day,
        #         'time': f'{datetime.utcnow().hour}:00',
        #         'area': [lat + 0.25, lon - 0.25, lat - 0.25, lon + 0.25],
        #         'format': 'netcdf'
        #     }
        # )
        # 
        # Then parse the NetCDF file with xarray
        
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"ERA5 API timeout after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"ERA5 API error after {duration:.2f}s: {str(e)}")
        return None


async def health_check_era5() -> Dict[str, Any]:
    """
    Health check for ERA5 service
    Tests availability of Copernicus CDS API
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with a known location
        result = await fetch_era5(40.0, -70.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and result.get("available") is not False:
            return {"ok": True, "latency_ms": int(duration)}
        else:
            # Mock service returns data but marks as unavailable
            return {
                "ok": True, 
                "latency_ms": int(duration),
                "note": "Mock service - CDS API key not configured"
            }
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}


# Alternative: OpenDAP/THREDDS access to ERA5 (no API key required but slower)
async def fetch_era5_opendap(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Alternative ERA5 access via OpenDAP/THREDDS
    Slower but doesn't require CDS API key
    
    Note: This is an alternative implementation path
    """
    # This would use xarray to access ERA5 via OpenDAP
    # Example: https://cds.climate.copernicus.eu/thredds/dodsC/...
    # 
    # import xarray as xr
    # 
    # ds = xr.open_dataset('http://...')
    # data = ds.sel(latitude=lat, longitude=lon, method='nearest')
    # 
    # return {
    #     "wave_height_m": float(data['swh'].values),
    #     "wind_speed_ms": calculate_wind_speed(
    #         float(data['u10'].values),
    #         float(data['v10'].values)
    #     ),
    #     ...
    # }
    
    logger.info("ERA5 OpenDAP access not yet implemented")
    return None
