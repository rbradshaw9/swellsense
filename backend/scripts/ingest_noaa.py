"""
NOAA Buoy Data Ingestion Script for SwellSense

Fetches real-time buoy data from NOAA's NDBC (National Data Buoy Center)
and inserts surf conditions into the database.

Usage:
    python ingest_noaa.py --buoy-id 41043
    
Schedule with cron:
    0 */3 * * * cd /path/to/swellsense/backend && python scripts/ingest_noaa.py --buoy-id 41043
"""
import asyncio
import httpx
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal, SurfCondition, init_db


class NOAABuoyIngester:
    """Fetches and parses NOAA buoy data"""
    
    BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2"
    
    def __init__(self, buoy_id: str):
        self.buoy_id = buoy_id
        self.data_url = f"{self.BASE_URL}/{buoy_id}.txt"
    
    async def fetch_buoy_data(self) -> Optional[str]:
        """
        Fetch raw buoy data from NOAA NDBC
        
        Returns:
            Raw text data from the buoy station
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.data_url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as e:
            print(f"❌ Error fetching buoy data: {e}")
            return None
    
    def parse_buoy_data(self, raw_data: str) -> List[Dict]:
        """
        Parse NOAA buoy text format into structured data
        
        NOAA format (space-delimited):
        #YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS  TIDE
        #yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi    ft
        2025 01 15 14 50  220  8.5 10.2  2.10  10.0   7.5 210 1013.2  18.5  20.1  15.0   MM    MM
        
        Returns:
            List of parsed condition dictionaries
        """
        lines = raw_data.strip().split('\n')
        
        # Skip header lines (first 2 lines are headers)
        data_lines = [line for line in lines if not line.startswith('#')]
        
        conditions = []
        
        for line in data_lines[:10]:  # Process last 10 readings
            parts = line.split()
            
            if len(parts) < 9:
                continue
            
            try:
                # Parse timestamp
                year, month, day, hour, minute = map(int, parts[0:5])
                timestamp = datetime(year, month, day, hour, minute)
                
                # Parse measurements (handle 'MM' = missing data)
                def parse_float(value: str) -> Optional[float]:
                    try:
                        return float(value) if value != 'MM' else None
                    except ValueError:
                        return None
                
                wave_height = parse_float(parts[8]) if len(parts) > 8 else None  # WVHT in meters
                wave_period = parse_float(parts[9]) if len(parts) > 9 else None  # DPD in seconds
                wind_speed = parse_float(parts[6]) if len(parts) > 6 else None   # WSPD in m/s
                
                condition = {
                    'timestamp': timestamp,
                    'wave_height': wave_height,
                    'wave_period': wave_period,
                    'wind_speed': wind_speed,
                    'tide_level': None,  # Not typically in standard NOAA format
                    'buoy_id': self.buoy_id
                }
                
                conditions.append(condition)
                
            except (ValueError, IndexError) as e:
                print(f"⚠️  Warning: Could not parse line: {line[:50]}... ({e})")
                continue
        
        return conditions
    
    async def ingest_data(self) -> int:
        """
        Main ingestion workflow: fetch, parse, and store data
        
        Returns:
            Number of records inserted
        """
        print(f"🌊 Fetching buoy data for station {self.buoy_id}...")
        
        # Fetch raw data
        raw_data = await self.fetch_buoy_data()
        if not raw_data:
            print("❌ Failed to fetch buoy data")
            return 0
        
        print(f"✅ Retrieved {len(raw_data)} bytes of data")
        
        # Parse data
        conditions = self.parse_buoy_data(raw_data)
        print(f"📊 Parsed {len(conditions)} condition records")
        
        if not conditions:
            print("⚠️  No valid data to insert")
            return 0
        
        # Insert into database
        inserted_count = 0
        async with AsyncSessionLocal() as db:
            try:
                for condition_data in conditions:
                    # Check if record already exists (avoid duplicates)
                    from sqlalchemy import select
                    stmt = select(SurfCondition).where(
                        SurfCondition.timestamp == condition_data['timestamp'],
                        SurfCondition.buoy_id == condition_data['buoy_id']
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        print(f"⏭️  Skipping duplicate: {condition_data['timestamp']}")
                        continue
                    
                    # Create new record
                    condition = SurfCondition(**condition_data)
                    db.add(condition)
                    inserted_count += 1
                    print(f"✅ Inserted: {condition_data['timestamp']} - Wave: {condition_data['wave_height']}m, Wind: {condition_data['wind_speed']}m/s")
                
                await db.commit()
                print(f"\n🎉 Successfully inserted {inserted_count} new records!")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Database error: {e}")
                return 0
        
        return inserted_count


async def main():
    """Main entry point for the ingestion script"""
    parser = argparse.ArgumentParser(description='Ingest NOAA buoy data into SwellSense')
    parser.add_argument(
        '--buoy-id',
        type=str,
        default=os.getenv('NOAA_BUOY_ID', '41043'),
        help='NOAA buoy station ID (default: 41043 - East of St. Augustine, FL)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌊 SwellSense NOAA Buoy Data Ingestion")
    print("=" * 60)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Run ingestion
    ingester = NOAABuoyIngester(args.buoy_id)
    await ingester.ingest_data()
    
    print("=" * 60)
    print("✅ Ingestion complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
