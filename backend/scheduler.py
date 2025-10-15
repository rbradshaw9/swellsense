"""
Global Data Ingestion Scheduler for SwellSense

Runs all data ingestion scripts hourly:
- NOAA buoys
- StormGlass
- OpenWeatherMap
- WorldTides
- Met.no

Uses asyncio.gather() for parallel execution
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Tuple

from database import init_db, BuoyStation, AsyncSessionLocal
from sqlalchemy import select

# Import ingestion classes
from scripts.ingest_noaa import NOAABuoyIngester
from scripts.ingest_stormglass import StormGlassIngester
from scripts.ingest_openweather import OpenWeatherIngester
from scripts.ingest_tides import WorldTidesIngester
from scripts.ingest_metno import MetNoIngester

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Interval between ingestion runs (1 hour)
INGESTION_INTERVAL = 60 * 60  # 3600 seconds


class GlobalIngestionScheduler:
    """Coordinates all data ingestion sources"""
    
    def __init__(self):
        self.is_running = False
        self.task = None
        self.buoy_locations = []
    
    async def load_buoy_locations(self):
        """Load all buoy station locations from database"""
        async with AsyncSessionLocal() as db:
            stmt = select(BuoyStation)
            result = await db.execute(stmt)
            stations = result.scalars().all()
            
            self.buoy_locations = [
                (station.station_id, station.latitude, station.longitude)
                for station in stations
            ]
            
            logger.info(f"📍 Loaded {len(self.buoy_locations)} buoy locations")
    
    async def ingest_location(self, buoy_id: str, lat: float, lon: float) -> Dict[str, int]:
        """
        Run all ingestion sources for a single location in parallel
        
        Returns dict with counts per source
        """
        logger.info(f"🌍 Ingesting data for {buoy_id} ({lat}, {lon})")
        
        try:
            # Create ingesters
            noaa = NOAABuoyIngester(buoy_id)
            stormglass = StormGlassIngester(lat, lon, buoy_id)
            openweather = OpenWeatherIngester(lat, lon, buoy_id)
            tides = WorldTidesIngester(lat, lon, buoy_id)
            metno = MetNoIngester(lat, lon, buoy_id)
            
            # Run all in parallel
            results = await asyncio.gather(
                noaa.ingest_data(),
                stormglass.ingest_data(),
                openweather.ingest_data(),
                tides.ingest_data(),
                metno.ingest_data(),
                return_exceptions=True
            )
            
            # Parse results
            counts = {
                'noaa': results[0] if not isinstance(results[0], Exception) else 0,
                'stormglass': results[1] if not isinstance(results[1], Exception) else 0,
                'openweather': results[2] if not isinstance(results[2], Exception) else 0,
                'tides': results[3] if not isinstance(results[3], Exception) else 0,
                'metno': results[4] if not isinstance(results[4], Exception) else 0,
            }
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    source = ['noaa', 'stormglass', 'openweather', 'tides', 'metno'][i]
                    logger.error(f"❌ {source} failed for {buoy_id}: {result}")
            
            total = sum(c for c in counts.values() if isinstance(c, int))
            logger.info(f"✅ {buoy_id}: {total} total records ({counts})")
            
            return counts
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest {buoy_id}: {e}")
            return {}
    
    async def run_full_ingestion(self):
        """Run ingestion for all buoy locations"""
        logger.info("=" * 80)
        logger.info("🌊 GLOBAL DATA INGESTION STARTED")
        logger.info("=" * 80)
        
        start_time = datetime.utcnow()
        
        # Load buoy locations
        await self.load_buoy_locations()
        
        if not self.buoy_locations:
            logger.warning("⚠️  No buoy locations found in database")
            return
        
        # Process each location sequentially to avoid overwhelming APIs
        total_counts = {'noaa': 0, 'stormglass': 0, 'openweather': 0, 'tides': 0, 'metno': 0}
        
        for buoy_id, lat, lon in self.buoy_locations:
            counts = await self.ingest_location(buoy_id, lat, lon)
            
            for source, count in counts.items():
                if isinstance(count, int):
                    total_counts[source] += count
            
            # Small delay between locations
            await asyncio.sleep(3)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info(f"✅ INGESTION COMPLETE ({duration:.1f}s)")
        logger.info(f"📊 Total records: {sum(total_counts.values())}")
        logger.info(f"   NOAA: {total_counts['noaa']}")
        logger.info(f"   StormGlass: {total_counts['stormglass']}")
        logger.info(f"   OpenWeather: {total_counts['openweather']}")
        logger.info(f"   WorldTides: {total_counts['tides']}")
        logger.info(f"   Met.no: {total_counts['metno']}")
        logger.info("=" * 80)
    
    async def run_periodic_ingestion(self):
        """Run ingestion periodically"""
        logger.info(f"🚀 Starting periodic global ingestion (interval: {INGESTION_INTERVAL}s / 1 hour)")
        self.is_running = True
        
        while self.is_running:
            try:
                await self.run_full_ingestion()
                
                logger.info(f"⏰ Next ingestion in {INGESTION_INTERVAL / 3600} hour(s)")
                await asyncio.sleep(INGESTION_INTERVAL)
                
            except asyncio.CancelledError:
                logger.info("⏹️  Ingestion scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in ingestion loop: {e}")
                await asyncio.sleep(300)  # 5 minutes before retry
    
    def start(self):
        """Start the background ingestion scheduler"""
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.run_periodic_ingestion())
            logger.info("✅ Global ingestion scheduler started")
        else:
            logger.warning("⚠️  Scheduler already running")
    
    async def stop(self):
        """Stop the background ingestion scheduler"""
        if self.task and not self.task.done():
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            logger.info("⏹️  Global ingestion scheduler stopped")


# Global scheduler instance
global_scheduler = GlobalIngestionScheduler()


if __name__ == "__main__":
    async def main():
        await init_db()
        await global_scheduler.run_full_ingestion()
    
    asyncio.run(main())
