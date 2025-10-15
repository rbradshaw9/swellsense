"""
Background task service for SwellSense
Handles automatic NOAA buoy data ingestion every 3 hours
"""
import asyncio
import logging
from datetime import datetime
from typing import List

from database import AsyncSessionLocal, SurfCondition, init_db
from scripts.ingest_noaa import NOAABuoyIngester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# List of buoy stations to ingest
BUOY_STATIONS = [
    "41043",  # East of St. Augustine, FL
    "42085",  # Western Puerto Rico
    "42059",  # Eastern Puerto Rico  
    "42003",  # Eastern Gulf of Mexico
    "46023",  # Northern California
    "46218",  # Southern California
    "51201",  # Hawaii
]

# Ingestion interval (3 hours in seconds)
INGESTION_INTERVAL = 3 * 60 * 60  # 10800 seconds


class IngestionService:
    """Background service for periodic NOAA data ingestion"""
    
    def __init__(self, buoy_stations: List[str] = None):
        self.buoy_stations = buoy_stations or BUOY_STATIONS
        self.is_running = False
        self.task = None
    
    async def ingest_all_buoys(self):
        """Ingest data from all configured buoy stations"""
        logger.info(f"🌊 Starting ingestion for {len(self.buoy_stations)} buoy stations")
        total_inserted = 0
        
        for buoy_id in self.buoy_stations:
            try:
                logger.info(f"📡 Processing buoy {buoy_id}...")
                ingester = NOAABuoyIngester(buoy_id)
                count = await ingester.ingest_data()
                total_inserted += count
                logger.info(f"✅ Buoy {buoy_id}: {count} records inserted")
                
                # Small delay between buoys to avoid overwhelming NOAA servers
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error ingesting buoy {buoy_id}: {e}")
                continue
        
        logger.info(f"🎉 Ingestion complete! Total records inserted: {total_inserted}")
        return total_inserted
    
    async def run_periodic_ingestion(self):
        """Run ingestion periodically every 3 hours"""
        logger.info(f"🚀 Starting periodic ingestion service (interval: {INGESTION_INTERVAL}s / 3 hours)")
        self.is_running = True
        
        while self.is_running:
            try:
                # Run ingestion
                await self.ingest_all_buoys()
                
                # Wait for next interval
                logger.info(f"⏰ Next ingestion in {INGESTION_INTERVAL / 3600} hours")
                await asyncio.sleep(INGESTION_INTERVAL)
                
            except asyncio.CancelledError:
                logger.info("⏹️  Ingestion service cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in ingestion loop: {e}")
                # Wait a bit before retrying on error
                await asyncio.sleep(300)  # 5 minutes
    
    def start(self):
        """Start the background ingestion service"""
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.run_periodic_ingestion())
            logger.info("✅ Ingestion service started")
        else:
            logger.warning("⚠️  Ingestion service already running")
    
    async def stop(self):
        """Stop the background ingestion service"""
        if self.task and not self.task.done():
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            logger.info("⏹️  Ingestion service stopped")


# Global service instance
ingestion_service = IngestionService()
