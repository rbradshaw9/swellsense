"""
Test all forecast data sources to identify issues
Usage: python scripts/test_all_sources.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.fetch_noaa_erddap import fetch_noaa_erddap
from utils.fetch_noaa_gfs import fetch_noaa_gfs
from utils.fetch_era5 import fetch_era5
from utils.fetch_openmeteo import fetch_openmeteo
from utils.fetch_copernicus import fetch_copernicus
from utils.api_clients import fetch_metno

# Test coordinates (Huntington Beach, CA)
LAT = 33.6
LON = -118.0

async def test_source(name, fetch_func):
    """Test a single data source"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    try:
        result = await fetch_func(LAT, LON)
        
        if result is None:
            print(f"❌ {name}: Returned None")
        elif isinstance(result, dict):
            if result.get("available") is False:
                print(f"❌ {name}: Not available")
                if "error" in result:
                    print(f"   Error: {result['error']}")
                if "note" in result:
                    print(f"   Note: {result['note']}")
            else:
                print(f"✅ {name}: Working!")
                # Show key data
                for key in ['wave_height_m', 'wave_period_s', 'wind_speed_ms', 'current_speed_ms']:
                    if key in result and result[key] is not None:
                        print(f"   {key}: {result[key]}")
        else:
            print(f"⚠️  {name}: Unexpected type: {type(result)}")
            
    except Exception as e:
        print(f"❌ {name}: Exception - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Test all sources"""
    print(f"\n🧪 Testing all forecast sources")
    print(f"📍 Location: {LAT}°N, {LON}°W (Huntington Beach, CA)\n")
    
    # Test each source
    await test_source("NOAA ERDDAP", fetch_noaa_erddap)
    await test_source("NOAA GFS (GribStream)", fetch_noaa_gfs)
    await test_source("ERA5 (Copernicus CDS)", fetch_era5)
    await test_source("Open-Meteo", fetch_openmeteo)
    await test_source("Copernicus Marine", fetch_copernicus)
    await test_source("Met.no", fetch_metno)
    
    print(f"\n{'='*60}")
    print("✅ Testing complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
