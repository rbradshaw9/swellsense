"""
Met.no Ocean Forecast Ingestion Script for SwellSense

Fetches ocean forecast data from Norwegian Meteorological Institute
Free API - no key required, but proper User-Agent required

Usage:
    python ingest_metno.py --lat 33.63 --lon -118.00
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, MarineCondition, init_db

BASE_URL = "https://api.met.no/weatherapi/oceanforecast/2.0/complete"
USER_AGENT = "SwellSense/1.0 (ryan@swellsense.app)"


class MetNoIngester:
    """Fetches and stores Met.no ocean forecast data"""
    
    def __init__(self, lat: float, lon: float, buoy_id: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.buoy_id = buoy_id
    
    async def fetch_forecast(self) -> Optional[Dict]:
        """Fetch ocean forecast from Met.no"""
        try:
            params = {
                "lat": self.lat,
                "lon": self.lon,
            }
            
            headers = {
                "User-Agent": USER_AGENT
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(BASE_URL, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"❌ Error fetching Met.no data: {e}")
            return None
    
    def parse_forecast(self, data: Dict) -> List[Dict]:
        """Parse Met.no response"""
        if not data or 'properties' not in data:
            return []
        
        conditions = []
        
        timeseries = data['properties'].get('timeseries', [])
        
        for entry in timeseries[:48]:  # Next 48 hours
            try:
                timestamp = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                # Normalize to UTC with tzinfo=None for PostgreSQL
                if timestamp.tzinfo:
                    timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                
                instant_data = entry.get('data', {}).get('instant', {}).get('details', {})
                
                condition = {
                    'source': 'metno',
                    'buoy_id': self.buoy_id,
                    'latitude': self.lat,
                    'longitude': self.lon,
                    'timestamp': timestamp,
                    'wave_height': instant_data.get('sea_surface_wave_height'),  # meters
                    'wave_direction': instant_data.get('sea_surface_wave_from_direction'),  # degrees
                    'swell_period': instant_data.get('sea_surface_wave_period_at_variance_spectral_density_maximum'),  # seconds
                    'water_temperature': instant_data.get('sea_surface_temperature'),  # celsius
                    'current_speed': instant_data.get('sea_water_speed'),  # m/s
                }
                
                conditions.append(condition)
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Warning: Could not parse timeseries entry: {e}")
                continue
        
        return conditions
    
    async def ingest_data(self) -> int:
        """Fetch and store Met.no data"""
        print(f"🌊 Fetching Met.no ocean forecast for ({self.lat}, {self.lon})...")
        
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
                        MarineCondition.source == 'metno',
                        MarineCondition.latitude == self.lat,
                        MarineCondition.longitude == self.lon,
                        MarineCondition.timestamp == condition_data['timestamp']
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        for key, value in condition_data.items():
                            if key != 'timestamp':
                                setattr(existing, key, value)
                        inserted_count += 1
                    else:
                        condition = MarineCondition(**condition_data)
                        db.add(condition)
                        inserted_count += 1
                
                await db.commit()
                print(f"✅ Stored {inserted_count} Met.no forecast hours")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Database error: {e}")
                return 0
        
        return inserted_count


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest Met.no ocean forecast')
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--buoy-id', type=str, default=None)
    
    args = parser.parse_args()
    
    await init_db()
    
    ingester = MetNoIngester(args.lat, args.lon, args.buoy_id)
    await ingester.ingest_data()


if __name__ == "__main__":
    asyncio.run(main())
