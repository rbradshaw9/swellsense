"""
API client utilities for external forecast data sources
Handles timeouts, retries, and graceful error handling
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# API Configuration
STORMGLASS_API_KEY = "a37ba27c-a9f3-11f0-826e-0242ac130003-a37ba312-a9f3-11f0-826e-0242ac130003"
OPENWEATHER_API_KEY = "52556d5a7d10d05471f877a4a8a96330"
WORLDTIDES_API_KEY = "fdd2ee82-5406-4921-9471-d58ccd4b21ba"

# Timeout settings
API_TIMEOUT = 10.0  # seconds
HEALTH_CHECK_TIMEOUT = 5.0  # seconds


async def fetch_stormglass(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch marine forecast from StormGlass API
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave height, period, direction, water temp, etc. or None on failure
    """
    start_time = datetime.utcnow()
    
    try:
        url = "https://api.stormglass.io/v2/weather/point"
        params = {
            "lat": lat,
            "lng": lon,
            "params": "waveHeight,wavePeriod,waveDirection,waterTemperature,windSpeed,windDirection"
        }
        headers = {"Authorization": STORMGLASS_API_KEY}
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"StormGlass API success in {duration:.2f}s")
            
            # Extract first hour forecast
            if data.get("hours"):
                hour = data["hours"][0]
                return {
                    "wave_height_m": hour.get("waveHeight", {}).get("sg"),
                    "wave_period_s": hour.get("wavePeriod", {}).get("sg"),
                    "wave_direction_deg": hour.get("waveDirection", {}).get("sg"),
                    "water_temp_c": hour.get("waterTemperature", {}).get("sg"),
                    "wind_speed_ms": hour.get("windSpeed", {}).get("sg"),
                    "wind_direction_deg": hour.get("windDirection", {}).get("sg"),
                    "timestamp": hour.get("time"),
                    "source": "stormglass"
                }
            
            return None
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"StormGlass API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"StormGlass API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"StormGlass API error after {duration:.2f}s: {str(e)}")
        return None


async def fetch_openweather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data from OpenWeatherMap API
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wind, temperature, pressure, or None on failure
    """
    start_time = datetime.utcnow()
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"OpenWeather API success in {duration:.2f}s")
            
            return {
                "wind_speed_ms": data.get("wind", {}).get("speed"),
                "wind_direction_deg": data.get("wind", {}).get("deg"),
                "temperature_c": data.get("main", {}).get("temp"),
                "pressure_hpa": data.get("main", {}).get("pressure"),
                "humidity_pct": data.get("main", {}).get("humidity"),
                "visibility_m": data.get("visibility"),
                "timestamp": datetime.utcfromtimestamp(data.get("dt", 0)).isoformat() + "Z",
                "source": "openweather"
            }
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"OpenWeather API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"OpenWeather API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"OpenWeather API error after {duration:.2f}s: {str(e)}")
        return None


async def fetch_worldtides(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch tide data from WorldTides API
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with tide heights and extremes, or None on failure
    """
    start_time = datetime.utcnow()
    
    try:
        url = "https://www.worldtides.info/api/v3"
        params = {
            "heights": "",
            "extremes": "",
            "lat": lat,
            "lon": lon,
            "key": WORLDTIDES_API_KEY
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"WorldTides API success in {duration:.2f}s")
            
            result = {
                "source": "worldtides",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            # Current tide height
            if data.get("heights"):
                result["current_tide_m"] = data["heights"][0].get("height")
                result["tide_timestamp"] = datetime.utcfromtimestamp(
                    data["heights"][0].get("dt", 0)
                ).isoformat() + "Z"
            
            # Next extremes (high/low tides)
            if data.get("extremes"):
                result["extremes"] = [
                    {
                        "type": ext.get("type"),
                        "height_m": ext.get("height"),
                        "time": datetime.utcfromtimestamp(ext.get("dt", 0)).isoformat() + "Z"
                    }
                    for ext in data["extremes"][:4]  # Next 4 extremes
                ]
            
            return result
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"WorldTides API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"WorldTides API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"WorldTides API error after {duration:.2f}s: {str(e)}")
        return None


async def fetch_metno(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch ocean forecast from Met.no API (free, no API key required)
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with wave and sea conditions, or None on failure
    """
    start_time = datetime.utcnow()
    
    try:
        url = "https://api.met.no/weatherapi/oceanforecast/2.0/complete"
        params = {
            "lat": lat,
            "lon": lon
        }
        headers = {
            "User-Agent": "SwellSense/1.0 (surf forecasting app)"
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(f"Met.no API success in {duration:.2f}s")
            
            # Extract first time period
            if data.get("properties", {}).get("timeseries"):
                ts = data["properties"]["timeseries"][0]
                instant = ts.get("data", {}).get("instant", {}).get("details", {})
                
                return {
                    "wave_height_m": instant.get("sea_surface_wave_height"),
                    "wave_period_s": instant.get("sea_surface_wave_period_at_variance_spectral_density_maximum"),
                    "wave_direction_deg": instant.get("sea_surface_wave_from_direction"),
                    "sea_temp_c": instant.get("sea_water_temperature"),
                    "current_speed_ms": instant.get("sea_water_speed"),
                    "current_direction_deg": instant.get("sea_water_to_direction"),
                    "timestamp": ts.get("time"),
                    "source": "metno"
                }
            
            return None
            
    except httpx.TimeoutException:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.warning(f"Met.no API timeout after {duration:.2f}s")
        return None
    except httpx.HTTPStatusError as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Met.no API HTTP error {e.response.status_code} after {duration:.2f}s")
        return None
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Met.no API error after {duration:.2f}s: {str(e)}")
        return None


# Health check functions (lightweight)

async def health_check_stormglass() -> Dict[str, Any]:
    """Test StormGlass API availability"""
    start_time = datetime.utcnow()
    
    try:
        # Use a known location for health check
        url = "https://api.stormglass.io/v2/weather/point"
        params = {"lat": 33.63, "lng": -118.00, "params": "waveHeight"}
        headers = {"Authorization": STORMGLASS_API_KEY}
        
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {"ok": True, "latency_ms": int(duration)}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}


async def health_check_openweather() -> Dict[str, Any]:
    """Test OpenWeatherMap API availability"""
    start_time = datetime.utcnow()
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": 33.63, "lon": -118.00, "appid": OPENWEATHER_API_KEY}
        
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {"ok": True, "latency_ms": int(duration)}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}


async def health_check_worldtides() -> Dict[str, Any]:
    """Test WorldTides API availability"""
    start_time = datetime.utcnow()
    
    try:
        url = "https://www.worldtides.info/api/v3"
        params = {"lat": 33.63, "lon": -118.00, "key": WORLDTIDES_API_KEY}
        
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {"ok": True, "latency_ms": int(duration)}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}


async def health_check_metno() -> Dict[str, Any]:
    """Test Met.no API availability"""
    start_time = datetime.utcnow()
    
    try:
        url = "https://api.met.no/weatherapi/oceanforecast/2.0/complete"
        params = {"lat": 33.63, "lon": -118.00}
        headers = {"User-Agent": "SwellSense/1.0 (health check)"}
        
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {"ok": True, "latency_ms": int(duration)}
            
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {"ok": False, "latency_ms": int(duration), "error": str(e)[:100]}
