"""
Utility functions for fetching and formatting global forecast data
Used by AI endpoint to build comprehensive context
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import math

from database import (
    MarineCondition,
    WeatherData,
    TideData,
    BuoyStation
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


async def fetch_global_forecast_context(
    db: AsyncSession,
    lat: float,
    lon: float,
    hours: int = 24
) -> Dict:
    """
    Fetch comprehensive forecast data from all sources for AI context
    
    Args:
        db: Database session
        lat: Latitude
        lon: Longitude
        hours: Forecast window in hours
    
    Returns:
        Formatted forecast context for AI prompts
    """
    try:
        now = datetime.utcnow()
        future = now + timedelta(hours=hours)
        radius = 0.5  # Search radius in degrees (~50km)
        
        # Find nearest buoy for location context
        buoy_stmt = select(BuoyStation)
        buoy_result = await db.execute(buoy_stmt)
        buoy_stations = buoy_result.scalars().all()
        
        nearest_buoy = None
        min_distance = float('inf')
        
        for station in buoy_stations:
            dist = calculate_distance(lat, lon, station.latitude, station.longitude)
            if dist < min_distance:
                min_distance = dist
                nearest_buoy = station
        
        # Query marine conditions
        marine_stmt = select(MarineCondition).where(
            and_(
                MarineCondition.timestamp >= now,
                MarineCondition.timestamp <= future,
                MarineCondition.latitude.between(lat - radius, lat + radius),
                MarineCondition.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(MarineCondition.timestamp).limit(48)
        
        marine_result = await db.execute(marine_stmt)
        marine_data = marine_result.scalars().all()
        
        # Query weather data
        weather_stmt = select(WeatherData).where(
            and_(
                WeatherData.timestamp >= now,
                WeatherData.timestamp <= future,
                WeatherData.latitude.between(lat - radius, lat + radius),
                WeatherData.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(WeatherData.timestamp).limit(40)
        
        weather_result = await db.execute(weather_stmt)
        weather_data = weather_result.scalars().all()
        
        # Query tide data
        tide_stmt = select(TideData).where(
            and_(
                TideData.timestamp >= now,
                TideData.timestamp <= future,
                TideData.latitude.between(lat - radius, lat + radius),
                TideData.longitude.between(lon - radius, lon + radius)
            )
        ).order_by(TideData.timestamp).limit(72)
        
        tide_result = await db.execute(tide_stmt)
        tide_data = tide_result.scalars().all()
        
        if not marine_data and not weather_data:
            return {
                "status": "no_data",
                "message": "No forecast data available for this location",
                "location": f"{lat}, {lon}"
            }
        
        # Aggregate data
        wave_heights = [m.wave_height for m in marine_data if m.wave_height]
        swell_periods = [m.swell_period for m in marine_data if m.swell_period]
        wave_directions = [m.wave_direction for m in marine_data if m.wave_direction]
        water_temps = [m.water_temperature for m in marine_data if m.water_temperature]
        
        wind_speeds = [w.wind_speed for w in weather_data if w.wind_speed]
        wind_gusts = [w.wind_gust for w in weather_data if w.wind_gust]
        wind_directions = [w.wind_direction for w in weather_data if w.wind_direction]
        
        tide_heights = [t.tide_height_meters for t in tide_data if t.tide_height_meters]
        tide_extremes = [t for t in tide_data if t.tide_type in ['High', 'Low']]
        
        # Determine tide trend
        tide_trend = "unknown"
        if len(tide_heights) >= 2:
            if tide_heights[0] < tide_heights[-1]:
                tide_trend = "rising"
            elif tide_heights[0] > tide_heights[-1]:
                tide_trend = "falling"
            else:
                tide_trend = "stable"
        
        # Get next tide extreme
        next_tide_extreme = None
        if tide_extremes:
            next_tide_extreme = {
                "type": tide_extremes[0].tide_type,
                "time": tide_extremes[0].timestamp.strftime("%H:%M UTC"),
                "height_m": round(tide_extremes[0].tide_height_meters, 2)
            }
        
        # Determine wind quality (offshore = good for surfing)
        wind_quality = "unknown"
        if wave_directions and wind_directions:
            avg_wave_dir = sum(wave_directions) / len(wave_directions)
            avg_wind_dir = sum(wind_directions) / len(wind_directions)
            
            # Offshore wind is opposite to wave direction (±45°)
            dir_diff = abs(avg_wave_dir - avg_wind_dir)
            if 135 <= dir_diff <= 225:
                wind_quality = "offshore (excellent)"
            elif 90 <= dir_diff < 135 or 225 < dir_diff <= 270:
                wind_quality = "cross-offshore (good)"
            elif 45 <= dir_diff < 90 or 270 < dir_diff <= 315:
                wind_quality = "cross-shore (fair)"
            else:
                wind_quality = "onshore (poor)"
        
        # Determine data sources
        sources = set()
        if marine_data:
            sources.update(m.source for m in marine_data)
        if weather_data:
            sources.add('openweather')
        if tide_data:
            sources.add('worldtides')
        
        # Build context
        context = {
            "status": "success",
            "location": nearest_buoy.region if nearest_buoy else f"{lat}, {lon}",
            "nearest_buoy": nearest_buoy.station_id if nearest_buoy else None,
            "distance_to_buoy_km": round(min_distance, 1) if nearest_buoy else None,
            "timestamp": now.isoformat() + "Z",
            "forecast_hours": hours,
            
            # Current conditions
            "wave_height_m": round(wave_heights[0], 2) if wave_heights else None,
            "wave_height_avg_m": round(sum(wave_heights) / len(wave_heights), 2) if wave_heights else None,
            "wave_height_trend": "increasing" if len(wave_heights) >= 3 and wave_heights[0] < wave_heights[2] else "decreasing" if len(wave_heights) >= 3 else "stable",
            
            "swell_period_s": round(swell_periods[0], 1) if swell_periods else None,
            "swell_period_avg_s": round(sum(swell_periods) / len(swell_periods), 1) if swell_periods else None,
            
            "swell_direction_deg": round(wave_directions[0], 0) if wave_directions else None,
            "swell_direction_text": get_direction_text(wave_directions[0]) if wave_directions else None,
            
            "wind_speed_ms": round(wind_speeds[0], 1) if wind_speeds else None,
            "wind_speed_kts": round(wind_speeds[0] * 1.944, 1) if wind_speeds else None,  # Convert m/s to knots
            "wind_gust_ms": round(wind_gusts[0], 1) if wind_gusts else None,
            "wind_direction_deg": round(wind_directions[0], 0) if wind_directions else None,
            "wind_direction_text": get_direction_text(wind_directions[0]) if wind_directions else None,
            "wind_quality": wind_quality,
            
            "water_temp_c": round(water_temps[0], 1) if water_temps else None,
            
            "tide_height_m": round(tide_heights[0], 2) if tide_heights else None,
            "tide_trend": tide_trend,
            "next_tide": next_tide_extreme,
            
            "data_sources": list(sources),
            "data_points": {
                "marine": len(marine_data),
                "weather": len(weather_data),
                "tide": len(tide_data)
            }
        }
        
        return context
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching forecast context: {str(e)}",
            "location": f"{lat}, {lon}"
        }


def get_direction_text(degrees: float) -> str:
    """Convert degrees to compass direction"""
    if degrees is None:
        return "unknown"
    
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    
    index = round(degrees / 22.5) % 16
    return directions[index]


def format_forecast_for_ai(context: Dict) -> str:
    """
    Format forecast context into natural language for AI prompt
    
    Args:
        context: Forecast context dictionary
    
    Returns:
        Formatted string for AI context
    """
    if context.get("status") != "success":
        return f"No forecast data available: {context.get('message', 'Unknown error')}"
    
    lines = [
        f"📍 Location: {context['location']}",
        f"⏰ Forecast Time: {context['timestamp']}",
        f"📊 Data Sources: {', '.join(context['data_sources'])}",
        "",
        "🌊 SURF CONDITIONS:",
    ]
    
    if context.get('wave_height_m'):
        lines.append(f"  • Wave Height: {context['wave_height_m']}m (avg: {context.get('wave_height_avg_m')}m, {context.get('wave_height_trend')})")
    
    if context.get('swell_period_s'):
        lines.append(f"  • Swell Period: {context['swell_period_s']}s (avg: {context.get('swell_period_avg_s')}s)")
    
    if context.get('swell_direction_text'):
        lines.append(f"  • Swell Direction: {context['swell_direction_deg']}° ({context['swell_direction_text']})")
    
    if context.get('wind_speed_kts'):
        lines.append(f"\n💨 WIND:")
        lines.append(f"  • Speed: {context['wind_speed_kts']} knots ({context['wind_speed_ms']} m/s)")
        if context.get('wind_gust_ms'):
            lines.append(f"  • Gusts: {context['wind_gust_ms']} m/s")
        if context.get('wind_direction_text'):
            lines.append(f"  • Direction: {context['wind_direction_deg']}° ({context['wind_direction_text']})")
        lines.append(f"  • Quality: {context['wind_quality']}")
    
    if context.get('tide_height_m') is not None:
        lines.append(f"\n🌊 TIDE:")
        lines.append(f"  • Current Height: {context['tide_height_m']}m ({context['tide_trend']})")
        if context.get('next_tide'):
            lines.append(f"  • Next {context['next_tide']['type']} Tide: {context['next_tide']['time']} at {context['next_tide']['height_m']}m")
    
    if context.get('water_temp_c'):
        lines.append(f"\n🌡️  Water Temperature: {context['water_temp_c']}°C")
    
    return "\n".join(lines)
