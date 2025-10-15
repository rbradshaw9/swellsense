"""
WorldTides API Ingestion Script for SwellSense

Fetches tide predictions and extremes
API Key: fdd2ee82-5406-4921-9471-d58ccd4b21ba

Usage:
    python ingest_tides.py --lat 33.63 --lon -118.00
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, TideData, init_db

API_KEY = "fdd2ee82-5406-4921-9471-d58ccd4b21ba"
BASE_URL = "https://www.worldtides.info/api/v3"


class WorldTidesIngester:
    """Fetches and stores WorldTides data"""
    
    def __init__(self, lat: float, lon: float, buoy_id: Optional[str] = None):
        self.lat = lat
        self.lon = lon
        self.buoy_id = buoy_id
    
    async def fetch_tides(self) -> Optional[Dict]:
        """Fetch tide extremes and heights from WorldTides"""
        try:
            now = datetime.utcnow()
            start = int(now.timestamp())
            end = int((now + timedelta(days=7)).timestamp())
            
            params = {
                "lat": self.lat,
                "lon": self.lon,
                "key": API_KEY,
                "start": start,
                "extremes": "",  # Get high/low tide times
                "heights": "",   # Get continuous height data
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"❌ Error fetching WorldTides data: {e}")
            return None
    
    def parse_tides(self, data: Dict) -> List[Dict]:
        """Parse WorldTides response"""
        if not data:
            return []
        
        conditions = []
        
        # Parse extremes (high/low tides)
        for extreme in data.get('extremes', []):
            try:
                timestamp = datetime.fromtimestamp(extreme['dt'], tz=timezone.utc)
                # Normalize to offset-naive UTC for PostgreSQL
                timestamp = timestamp.replace(tzinfo=None)
                
                condition = {
                    'source': 'worldtides',
                    'buoy_id': self.buoy_id,
                    'latitude': self.lat,
                    'longitude': self.lon,
                    'timestamp': timestamp,
                    'tide_height_meters': extreme['height'],
                    'tide_type': extreme['type'],  # 'High' or 'Low'
                }
                
                conditions.append(condition)
                
            except (ValueError, KeyError) as e:
                print(f"⚠️  Warning: Could not parse extreme: {e}")
                continue
        
        # Parse heights (continuous data points)
        for height_point in data.get('heights', [])[:72]:  # 3 days of hourly data
            try:
                timestamp = datetime.fromtimestamp(height_point['dt'])
                
                condition = {
                    'source': 'worldtides',
                    'buoy_id': self.buoy_id,
                    'latitude': self.lat,
                    'longitude': self.lon,
                    'timestamp': timestamp,
                    'tide_height_meters': height_point['height'],
                    'tide_type': None,
                }
                
                conditions.append(condition)
                
            except (ValueError, KeyError) as e:
                continue
        
        return conditions
    
    async def ingest_data(self) -> int:
        """Fetch and store tide data"""
        print(f"🌊 Fetching tide data for ({self.lat}, {self.lon})...")
        
        data = await self.fetch_tides()
        if not data:
            return 0
        
        conditions = self.parse_tides(data)
        print(f"📊 Parsed {len(conditions)} tide data points")
        
        if not conditions:
            return 0
        
        inserted_count = 0
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select
                
                for condition_data in conditions:
                    # Check for duplicates
                    stmt = select(TideData).where(
                        TideData.source == 'worldtides',
                        TideData.latitude == self.lat,
                        TideData.longitude == self.lon,
                        TideData.timestamp == condition_data['timestamp']
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        for key, value in condition_data.items():
                            if key != 'timestamp':
                                setattr(existing, key, value)
                        inserted_count += 1
                    else:
                        tide = TideData(**condition_data)
                        db.add(tide)
                        inserted_count += 1
                
                await db.commit()
                print(f"✅ Stored {inserted_count} tide data points")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Database error: {e}")
                return 0
        
        return inserted_count


async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest WorldTides data')
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--buoy-id', type=str, default=None)
    
    args = parser.parse_args()
    
    await init_db()
    
    ingester = WorldTidesIngester(args.lat, args.lon, args.buoy_id)
    await ingester.ingest_data()


if __name__ == "__main__":
    asyncio.run(main())
