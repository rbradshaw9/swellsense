"""
OpenWeatherMap API Ingestion Script for SwellSense

Fetches weather forecast data including wind, temperature, pressure
API Key: 52556d5a7d10d05471f877a4a8a96330

Usage:
    python ingest_openweather.py --lat 33.63 --lon -118.00
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, WeatherData, init_db

API_KEY = "52556d5a7d10d05471f877a4a8a96330"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


class OpenWeatherIngester:
    """Fetches and stores OpenWeatherMap forecast data"""
    
    def __init__(self, lat: float, lon: float, buoy_id: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.buoy_id = buoy_id
    
    async def fetch_forecast(self) -> Optional[Dict]:
        """Fetch weather forecast from OpenWeatherMap"""
        try:
            params = {
                "lat": self.lat,
                "lon": self.lon,
                "appid": API_KEY,
                "units": "metric",  # Celsius, m/s
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"❌ Error fetching OpenWeather data: {e}")
            return None
    
    def parse_forecast(self, data: Dict) -> List[Dict]:
        """Parse OpenWeatherMap response"""
        if not data or 'list' not in data:
            return []
        
        conditions = []
        
        for item in data['list'][:40]:  # 5 days of 3-hour forecasts
            try:
                timestamp = datetime.fromtimestamp(item['dt'])
                
                wind = item.get('wind', {})
                main = item.get('main', {})
                weather_list = item.get('weather', [])
                
                condition = {
                    'source': 'openweather',
                    'buoy_id': self.buoy_id,
                    'latitude': self.lat,
                    'longitude': self.lon,
                    'timestamp': timestamp,
                    'wind_speed': wind.get('speed'),  # m/s
                    'wind_gust': wind.get('gust'),
                    'wind_direction': wind.get('deg'),
                    'temperature': main.get('temp'),  # celsius
                    'pressure': main.get('pressure'),  # hPa
                    'visibility': item.get('visibility'),  # meters
                    'description': weather_list[0]['description'] if weather_list else None,
                }
                
                conditions.append(condition)
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Warning: Could not parse forecast item: {e}")
                continue
        
        return conditions
    
    async def ingest_data(self) -> int:
        """Fetch and store OpenWeather data"""
        print(f"☁️  Fetching OpenWeather forecast for ({self.lat}, {self.lon})...")
        
        data = await self.fetch_forecast()
        if not data:
            return 0
        
        conditions = self.parse_forecast(data)
        print(f"📊 Parsed {len(conditions)} forecast periods")
        
        if not conditions:
            return 0
        
        inserted_count = 0
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select
                
                for condition_data in conditions:
                    # Check for duplicates
                    stmt = select(WeatherData).where(
                        WeatherData.source == 'openweather',
                        WeatherData.latitude == self.lat,
                        WeatherData.longitude == self.lon,
                        WeatherData.timestamp == condition_data['timestamp']
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        for key, value in condition_data.items():
                            if key != 'timestamp':
                                setattr(existing, key, value)
                        inserted_count += 1
                    else:
                        weather = WeatherData(**condition_data)
                        db.add(weather)
                        inserted_count += 1
                
                await db.commit()
                print(f"✅ Stored {inserted_count} OpenWeather forecast periods")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Database error: {e}")
                return 0
        
        return inserted_count


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest OpenWeatherMap forecast')
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--buoy-id', type=str, default=None)
    
    args = parser.parse_args()
    
    await init_db()
    
    ingester = OpenWeatherIngester(args.lat, args.lon, args.buoy_id)
    await ingester.ingest_data()


if __name__ == "__main__":
    asyncio.run(main())
