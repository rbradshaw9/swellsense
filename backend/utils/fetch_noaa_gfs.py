"""
NOAA GFS (Global Forecast System) / WaveWatch III Integration
Provides global wave and wind forecasts using NOAA's NOMADS GRIB2 data

Uses cfgrib/xarray for robust GRIB2 parsing
"""
import os
import httpx
import logging
import tempfile
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# NOAA NOMADS GFS/WaveWatch III endpoints
WAVEWATCH_BASE_URL = "https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl"
GFS_TIMEOUT = 15.0  # seconds (GRIB2 downloads can be slow)
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
    Fetch wave and wind forecast from NOAA GFS/WaveWatch III via GRIB2
    
    Uses NOMADS GRIB2 filtering to extract data for a small region around the coordinates.
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
        
        # If within 3 hours of cycle time, use previous cycle (data may not be ready)
        if (now - cycle_time).total_seconds() < 10800:
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
                
                # Download GRIB2 file
                async with httpx.AsyncClient(timeout=GFS_TIMEOUT) as client:
                    response = await client.get(WAVEWATCH_BASE_URL, params=params)
                    response.raise_for_status()
                    
                    # Check if we got actual GRIB2 data
                    content_type = response.headers.get('content-type', '')
                    if 'text/html' in content_type or len(response.content) < 100:
                        logger.warning(f"NOAA GFS: Invalid response for hour {forecast_hour}")
                        continue
                    
                    # Save to temporary file
                    temp_file = tempfile.NamedTemporaryFile(suffix='.grib2', delete=False)
                    temp_path = temp_file.name
                    await asyncio.to_thread(temp_file.write, response.content)
                    temp_file.close()
                    
                    try:
                        # Parse GRIB2 file using cfgrib/xarray
                        import xarray as xr
                        
                        # Open GRIB2 dataset
                        ds = await asyncio.to_thread(
                            xr.open_dataset,
                            temp_path,
                            engine='cfgrib',
                            backend_kwargs={'errors': 'ignore'}
                        )
                        
                        # Extract variables (use mean of bounding box)
                        wave_height = None
                        wave_direction = None
                        wave_period = None
                        wind_speed = None
                        
                        if 'HTSGW_surface' in ds:
                            wave_height = float(ds['HTSGW_surface'].mean().values)
                        
                        if 'WVDIR_surface' in ds:
                            wave_direction = float(ds['WVDIR_surface'].mean().values)
                        
                        if 'WVPER_surface' in ds:
                            wave_period = float(ds['WVPER_surface'].mean().values)
                        
                        if 'WIND_surface' in ds:
                            wind_speed = float(ds['WIND_surface'].mean().values)
                        
                        # Close dataset
                        ds.close()
                        
                        # Clean up temp file
                        await asyncio.to_thread(os.unlink, temp_path)
                        
                        duration = (datetime.utcnow() - start_time).total_seconds()
                        logger.info(f"NOAA GFS success in {duration:.2f}s (forecast hour: {forecast_hour}, wave_height={wave_height:.2f}m)")
                        
                        result = {
                            "source": "noaa_gfs",
                            "wave_height_m": round(wave_height, 2) if wave_height is not None else None,
                            "wave_period_s": round(wave_period, 1) if wave_period is not None else None,
                            "wave_direction_deg": round(wave_direction, 1) if wave_direction is not None else None,
                            "wind_speed_ms": round(wind_speed, 2) if wind_speed is not None else None,
                            "wind_direction_deg": None,  # Not directly available in WaveWatch III
                            "timestamp": (cycle_time + timedelta(hours=int(forecast_hour))).isoformat() + "Z",
                            "forecast_hour": forecast_hour,
                            "available": True
                        }
                        
                        # Cache the result
                        _gfs_cache[cache_key] = {
                            "data": result,
                            "cached_at": start_time
                        }
                        
                        return result
                        
                    except Exception as parse_error:
                        # Clean up temp file on parse error
                        try:
                            await asyncio.to_thread(os.unlink, temp_path)
                        except:
                            pass
                        logger.error(f"NOAA GFS parse error for hour {forecast_hour}: {parse_error}")
                        continue
                        
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
    Tests availability of WaveWatch III GRIB2 data
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
                "note": "Live GRIB2 parsed via cfgrib"
            }
        else:
            return {
                "ok": False,
                "latency_ms": int(duration),
                "note": "NOMADS service unavailable or GRIB2 parsing failed"
            }
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "ok": False,
            "latency_ms": int(duration),
            "error": str(e)[:100]
        }

