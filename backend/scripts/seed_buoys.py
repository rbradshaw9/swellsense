"""
Seed buoy_stations table with NOAA buoy metadata
Run this once to populate the database with key buoy locations
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database import AsyncSessionLocal, BuoyStation, init_db
from sqlalchemy import select


BUOY_DATA = [
    {
        "station_id": "41043",
        "name": "East of St. Augustine, FL",
        "region": "Florida",
        "latitude": 29.2,
        "longitude": -79.9
    },
    {
        "station_id": "42085",
        "name": "Aguadilla, Western PR",
        "region": "Western Puerto Rico",
        "latitude": 18.4,
        "longitude": -67.2
    },
    {
        "station_id": "42059",
        "name": "Mona Passage",
        "region": "Puerto Rico",
        "latitude": 19.1,
        "longitude": -67.9
    },
    {
        "station_id": "42003",
        "name": "East of Pensacola, FL",
        "region": "Gulf of Mexico",
        "latitude": 25.9,
        "longitude": -85.6
    },
    {
        "station_id": "46023",
        "name": "Point Arena, CA",
        "region": "Northern California",
        "latitude": 38.8,
        "longitude": -123.8
    },
    {
        "station_id": "46218",
        "name": "Santa Barbara, CA",
        "region": "Southern California",
        "latitude": 34.5,
        "longitude": -120.8
    },
    {
        "station_id": "51201",
        "name": "Northwest Hawaii",
        "region": "Hawaii",
        "latitude": 24.4,
        "longitude": -162.3
    },
]


async def seed_buoys():
    """Seed the buoy_stations table with initial data"""
    # Initialize database (create tables if they don't exist)
    await init_db()
    
    async with AsyncSessionLocal() as session:
        print("🌊 Seeding buoy stations...")
        
        for buoy_data in BUOY_DATA:
            # Check if buoy already exists
            result = await session.execute(
                select(BuoyStation).where(BuoyStation.station_id == buoy_data["station_id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  ⏭️  Buoy {buoy_data['station_id']} ({buoy_data['name']}) already exists")
                continue
            
            # Create new buoy station
            buoy = BuoyStation(**buoy_data)
            session.add(buoy)
            print(f"  ✅ Added buoy {buoy_data['station_id']} - {buoy_data['name']} ({buoy_data['region']})")
        
        await session.commit()
        print("\n✨ Buoy seeding complete!")
        
        # Show all buoys
        result = await session.execute(select(BuoyStation))
        all_buoys = result.scalars().all()
        
        print(f"\n📍 Total buoys in database: {len(all_buoys)}")
        print("\nBuoy Stations:")
        print("-" * 80)
        for buoy in all_buoys:
            print(f"  {buoy.station_id:<8} | {buoy.name:<35} | {buoy.region:<25} | ({buoy.latitude}, {buoy.longitude})")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(seed_buoys())
