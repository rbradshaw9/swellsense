"""
StormGlass API Ingestion Script for SwellSense

Fetches global marine forecast data from StormGlass.io
Provides wave height, swell period, wave direction, water temp, and current speed

Usage:
    python ingest_stormglass.py --lat 33.63 --lon -118.00
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, MarineCondition, init_db

API_KEY = "a37ba27c-a9f3-11f0-826e-0242ac130003-a37ba312-a9f3-11f0-826e-0242ac130003"
BASE_URL = "https://api.stormglass.io/v2/weather/point"


class StormGlassIngester:
    """Fetches and stores StormGlass marine forecast data"""
    
    def __init__(self, lat: float, lon: float, buoy_id: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.buoy_id = buoy_id
    
    async def fetch_forecast(self) -> Optional[Dict]:
        """Fetch marine forecast from StormGlass API"""
        try:
            params = {
                "lat": self.lat,
                "lng": self.lon,
                "params": "swellHeight,swellPeriod,waveDirection,waterTemperature,currentSpeed",
                "source": "noaa,sg",  # Use NOAA and StormGlass sources
            }
            
            headers = {
                "Authorization": API_KEY
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(BASE_URL, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"❌ Error fetching StormGlass data: {e}")
            return None
    
    def parse_forecast(self, data: Dict) -> List[Dict]:
        """Parse StormGlass response into conditions"""
        if not data or 'hours' not in data:
            return []
        
        conditions = []
        
        for hour in data['hours'][:24]:  # Next 24 hours
            try:
                timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))
                
                # Get first available source value
                def get_value(field: str) -> Optional[float]:
                    if field in hour and hour[field]:
                        values = hour[field]
                        if isinstance(values, dict):
                            # Try noaa first, then sg, then any available
                            return values.get('noaa') or values.get('sg') or next(iter(values.values()), None)
                        return values
                    return None
                
                condition = {
                    'source': 'stormglass',
                    'buoy_id': self.buoy_id,
                    'latitude': self.lat,
                    'longitude': self.lon,
                    'timestamp': timestamp,
                    'wave_height': get_value('swellHeight'),
                    'swell_period': get_value('swellPeriod'),
                    'wave_direction': get_value('waveDirection'),
                    'water_temperature': get_value('waterTemperature'),
                    'current_speed': get_value('currentSpeed'),
                }
                
                conditions.append(condition)
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Warning: Could not parse hour: {e}")
                continue
        
        return conditions
    
    async def ingest_data(self) -> int:
        """Fetch and store StormGlass data"""
        print(f"🌊 Fetching StormGlass forecast for ({self.lat}, {self.lon})...")
        
        data = await self.fetch_forecast()
        if not data:
            return 0
        
        conditions = self.parse_forecast(data)
        print(f"📊 Parsed {len(conditions)} forecast hours")
        
        if not conditions:
            return 0
        
        inserted_count = 0
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select
                
                for condition_data in conditions:
                    # Check for duplicates
                    stmt = select(MarineCondition).where(
                        MarineCondition.source == 'stormglass',
                        MarineCondition.latitude == self.lat,
                        MarineCondition.longitude == self.lon,
                        MarineCondition.timestamp == condition_data['timestamp']
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        # Update existing record
                        for key, value in condition_data.items():
                            if key != 'timestamp':
                                setattr(existing, key, value)
                        inserted_count += 1
                    else:
                        # Create new record
                        condition = MarineCondition(**condition_data)
                        db.add(condition)
                        inserted_count += 1
                
                await db.commit()
                print(f"✅ Stored {inserted_count} StormGlass forecast hours")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Database error: {e}")
                return 0
        
        return inserted_count


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest StormGlass marine forecast')
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--buoy-id', type=str, default=None)
    
    args = parser.parse_args()
    
    await init_db()
    
    ingester = StormGlassIngester(args.lat, args.lon, args.buoy_id)
    await ingester.ingest_data()


if __name__ == "__main__":
    asyncio.run(main())
