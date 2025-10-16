"""
Open-Meteo Marine API Integration
Free, open-source global marine forecasts with excellent reliability
No API key required - perfect backup source when commercial APIs fail
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Open-Meteo Configuration
OPENMETEO_BASE_URL = "https://marine-api.open-meteo.com/v1/marine"
OPENMETEO_TIMEOUT = 10.0  # seconds
CACHE_TTL = 3600  # 1 hour

# Simple in-memory cache
_openmeteo_cache: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key (rounded to 0.1 degrees)"""
    lat_rounded = round(lat * 10) / 10
    lon_rounded = round(lon * 10) / 10
    return f"{lat_rounded},{lon_rounded}"


async def fetch_openmeteo(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch marine forecast from Open-Meteo API
    
    Open-Meteo provides free, high-quality weather and marine data
    with excellent global coverage and no API key requirement.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, period, direction, wind, temperature
    """
    start_time = datetime.utcnow()
    cache_key = _get_cache_key(lat, lon)
    
    # Check cache
    if cache_key in _openmeteo_cache:
        cached = _openmeteo_cache[cache_key]
        cache_age = (start_time - cached["cached_at"]).total_seconds()
        if cache_age < CACHE_TTL:
            logger.info(f"Open-Meteo cache hit (age: {cache_age:.0f}s)")
            return cached["data"]
    
    try:
        # Build query parameters (Open-Meteo doesn't support 'current' parameter)
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wave_height,wave_direction,wave_period,wind_wave_height,wind_wave_direction,wind_wave_period,swell_wave_height,swell_wave_direction,swell_wave_period",
            "forecast_hours": 1  # Just get current hour
        }
        
        async with httpx.AsyncClient(timeout=OPENMETEO_TIMEOUT) as client:
            response = await client.get(OPENMETEO_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Open-Meteo API success in {duration:.2f}s")
            
            # Extract current hour data (index 0)
            hourly = data.get("hourly", {})
            
            result = {
                "source": "openmeteo",
                "wave_height_m": hourly.get("wave_height", [None])[0],
                "wave_period_s": hourly.get("wave_period", [None])[0],
                "wave_direction_deg": hourly.get("wave_direction", [None])[0],
                "swell_height_m": hourly.get("swell_wave_height", [None])[0],
                "swell_period_s": hourly.get("swell_wave_period", [None])[0],
                "swell_direction_deg": hourly.get("swell_wave_direction", [None])[0],
                "wind_wave_height_m": hourly.get("wind_wave_height", [None])[0],
                "timestamp": hourly.get("time", [datetime.utcnow().isoformat() + "Z"])[0],
                "available": True
            }
            
            # Cache the result
            _openmeteo_cache[cache_key] = {
                "data": result,
                "cached_at": start_time
            }
            
            return result
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"Open-Meteo API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Open-Meteo API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Open-Meteo API error after {duration:.2f}s: {str(e)}")
        return None


async def health_check_openmeteo() -> Dict[str, Any]:
    """
    Health check for Open-Meteo service
    Tests availability of marine API
    """
    start_time = datetime.utcnow()
    
    try:
        # Test with mid-ocean location
        result = await fetch_openmeteo(0.0, 0.0)
        
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and result.get("available"):
            return {"ok": True, "latency_ms": int(duration)}
        else:
            return {"ok": False, "latency_ms": int(duration), "error": "No data available"}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}
