"""
Copernicus ERA5 (ECMWF) Reanalysis Integration
Provides high-quality global atmospheric and ocean reanalysis data via CDS API

Requires CDSAPI_KEY environment variable
"""
import os
import asyncio
import logging
import tempfile
import math
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ERA5 Configuration
ERA5_TIMEOUT = 60.0  # CDS API can be slow (60 seconds)
CACHE_TTL = 3600  # 1 hour

# Simple in-memory cache
_era5_cache: Dict[str, Dict[str, Any]] = {}

# Get CDS API key from environment
CDSAPI_KEY = os.getenv("CDSAPI_KEY")


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


async def fetch_era5(lat: float, lon: float, when: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch atmospheric and ocean data from Copernicus ERA5 via CDS API
    
    ERA5 provides hourly reanalysis data at 0.25° resolution (~30km).
    Includes wind components and wave height from ECMWF's global model.
    
    Args:
        lat: Latitude
        lon: Longitude
        when: Optional datetime for historical data (defaults to 5 days ago for latest available)
    
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
    
    # Check if API key is configured
    if not CDSAPI_KEY:
        logger.warning("ERA5 CDS API key not configured - set CDSAPI_KEY environment variable")
        result = {
            "source": "era5",
            "wave_height_m": None,
            "wave_period_s": None,
            "wave_direction_deg": None,
            "wind_speed_ms": None,
            "wind_direction_deg": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "available": False,
            "note": "ERA5 requires CDSAPI_KEY environment variable"
        }
        return result
    
    try:
        # Import cdsapi (only if key is available)
        try:
            import cdsapi
            import xarray as xr
        except ImportError as e:
            logger.error(f"ERA5 dependencies not installed: {e}")
            return None
        
        # Run blocking CDS API call in thread pool
        def retrieve_era5_data():
            """Synchronous CDS API retrieval (runs in thread pool)"""
            c = cdsapi.Client(
                url="https://cds.climate.copernicus.eu/api/v2",
                key=CDSAPI_KEY,
                verify=True
            )
            
            # Create temp file for NetCDF
            temp_file = tempfile.NamedTemporaryFile(suffix='.nc', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Calculate bounding box (small 0.5° box around point)
            north = min(90, lat + 0.25)
            south = max(-90, lat - 0.25)
            west = lon - 0.25
            east = lon + 0.25
            
            # Get current UTC time (ERA5 has ~5 day delay for final data)
            if when is not None:
                # Use provided datetime
                target_time = when
            else:
                # Use data from 5 days ago to ensure availability
                now = datetime.utcnow()
                target_time = now - timedelta(days=5)
            
            # Retrieve ERA5 reanalysis data
            c.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '10m_u_component_of_wind',
                        '10m_v_component_of_wind',
                        'significant_height_of_combined_wind_waves_and_swell',
                        'mean_wave_direction',
                        'mean_wave_period'
                    ],
                    'year': str(target_time.year),
                    'month': f"{target_time.month:02d}",
                    'day': f"{target_time.day:02d}",
                    'time': f"{target_time.hour:02d}:00",
                    'area': [north, west, south, east],  # N, W, S, E
                    'format': 'netcdf'
                },
                temp_path
            )
            
            return temp_path
        
        # Run CDS API call in thread pool (non-blocking)
        temp_path = await asyncio.wait_for(
            asyncio.to_thread(retrieve_era5_data),
            timeout=ERA5_TIMEOUT
        )
        
        # Parse NetCDF file asynchronously
        try:
            import xarray as xr
            
            # Load dataset
            ds = await asyncio.to_thread(xr.open_dataset, temp_path)
            
            # Extract mean values from the bounding box
            wave_height = float(ds['swh'].mean().values) if 'swh' in ds else None
            wave_period = float(ds['mwp'].mean().values) if 'mwp' in ds else None
            wave_direction = float(ds['mwd'].mean().values) if 'mwd' in ds else None
            u_wind = float(ds['u10'].mean().values) if 'u10' in ds else None
            v_wind = float(ds['v10'].mean().values) if 'v10' in ds else None
            
            # Calculate wind speed and direction
            wind_speed = None
            wind_direction = None
            if u_wind is not None and v_wind is not None:
                wind_speed = _calculate_wind_speed(u_wind, v_wind)
                wind_direction = _calculate_wind_direction(u_wind, v_wind)
            
            # Close dataset
            ds.close()
            
            # Clean up temp file
            await asyncio.to_thread(os.unlink, temp_path)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"ERA5 success in {duration:.2f}s (wave_height={wave_height:.2f}m)")
            
            result = {
                "source": "era5",
                "wave_height_m": round(wave_height, 2) if wave_height is not None else None,
                "wave_period_s": round(wave_period, 1) if wave_period is not None else None,
                "wave_direction_deg": round(wave_direction, 1) if wave_direction is not None else None,
                "wind_speed_ms": round(wind_speed, 2) if wind_speed is not None else None,
                "wind_direction_deg": round(wind_direction, 1) if wind_direction is not None else None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "available": True
            }
            
            # Cache the result
            _era5_cache[cache_key] = {
                "data": result,
                "cached_at": start_time
            }
            
            return result
            
        except Exception as e:
            # Clean up temp file on error
            try:
                await asyncio.to_thread(os.unlink, temp_path)
            except:
                pass
            raise e
        
    except asyncio.TimeoutError:
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
    
    # Check if API key is configured
    if not CDSAPI_KEY:
        return {
            "ok": False,
            "latency_ms": 0,
            "note": "CDSAPI_KEY not configured"
        }
    
    try:
        # Test with a known location (mid-Atlantic)
        result = await fetch_era5(40.0, -30.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and result.get("available"):
            return {
                "ok": True,
                "latency_ms": int(duration),
                "note": "Live data retrieved via CDS API"
            }
        else:
            return {
                "ok": False,
                "latency_ms": int(duration),
                "note": "CDS API key configured but data unavailable"
            }
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "ok": False,
            "latency_ms": int(duration),
            "error": str(e)[:100]
        }

