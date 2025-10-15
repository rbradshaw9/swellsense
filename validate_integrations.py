#!/usr/bin/env python3
"""
SwellSense Data Integration Validation Test
Tests ERA5 and NOAA GFS implementations
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_imports():
    """Test that all required libraries can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import cdsapi
        print("  ✅ cdsapi imported")
    except ImportError as e:
        print(f"  ❌ cdsapi import failed: {e}")
        return False
    
    try:
        import xarray
        print("  ✅ xarray imported")
    except ImportError as e:
        print(f"  ❌ xarray import failed: {e}")
        return False
    
    try:
        import netCDF4
        print("  ✅ netCDF4 imported")
    except ImportError as e:
        print(f"  ❌ netCDF4 import failed: {e}")
        return False
    
    try:
        import cfgrib
        print("  ✅ cfgrib imported")
    except ImportError as e:
        print(f"  ❌ cfgrib import failed: {e}")
        return False
    
    try:
        import eccodes
        print("  ✅ eccodes imported")
    except ImportError as e:
        print(f"  ❌ eccodes import failed: {e}")
        return False
    
    try:
        import pandas
        print("  ✅ pandas imported")
    except ImportError as e:
        print(f"  ❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("  ✅ numpy imported")
    except ImportError as e:
        print(f"  ❌ numpy import failed: {e}")
        return False
    
    try:
        import aiofiles
        print("  ✅ aiofiles imported")
    except ImportError as e:
        print(f"  ❌ aiofiles import failed: {e}")
        return False
    
    return True


async def test_fetchers():
    """Test that fetch modules can be imported"""
    print("\n🔍 Testing fetcher modules...")
    
    try:
        from utils.fetch_era5 import fetch_era5, health_check_era5
        print("  ✅ fetch_era5 imported successfully")
        print(f"     - fetch_era5: {fetch_era5.__doc__.split(chr(10))[0] if fetch_era5.__doc__ else 'No docstring'}")
        print(f"     - health_check_era5: {health_check_era5.__doc__.split(chr(10))[0] if health_check_era5.__doc__ else 'No docstring'}")
    except ImportError as e:
        print(f"  ❌ fetch_era5 import failed: {e}")
        return False
    
    try:
        from utils.fetch_noaa_gfs import fetch_noaa_gfs, health_check_noaa_gfs
        print("  ✅ fetch_noaa_gfs imported successfully")
        print(f"     - fetch_noaa_gfs: {fetch_noaa_gfs.__doc__.split(chr(10))[0] if fetch_noaa_gfs.__doc__ else 'No docstring'}")
        print(f"     - health_check_noaa_gfs: {health_check_noaa_gfs.__doc__.split(chr(10))[0] if health_check_noaa_gfs.__doc__ else 'No docstring'}")
    except ImportError as e:
        print(f"  ❌ fetch_noaa_gfs import failed: {e}")
        return False
    
    return True


async def test_era5_structure():
    """Test ERA5 implementation structure"""
    print("\n🔍 Testing ERA5 implementation...")
    
    from utils.fetch_era5 import fetch_era5
    import inspect
    
    # Check if it's async
    if asyncio.iscoroutinefunction(fetch_era5):
        print("  ✅ fetch_era5 is async")
    else:
        print("  ❌ fetch_era5 is not async")
        return False
    
    # Check source code for key features
    source = inspect.getsource(fetch_era5)
    
    if 'cdsapi' in source:
        print("  ✅ Uses cdsapi library")
    else:
        print("  ⚠️  Does not use cdsapi (may be mocked)")
    
    if 'reanalysis-era5-single-levels' in source:
        print("  ✅ Uses correct ERA5 dataset")
    else:
        print("  ❌ Does not use ERA5 dataset")
        return False
    
    if 'xarray' in source or 'xr' in source:
        print("  ✅ Uses xarray for parsing")
    else:
        print("  ⚠️  Does not use xarray")
    
    if 'asyncio.to_thread' in source:
        print("  ✅ Uses async I/O (asyncio.to_thread)")
    else:
        print("  ⚠️  May not be using proper async I/O")
    
    return True


async def test_noaa_gfs_structure():
    """Test NOAA GFS implementation structure"""
    print("\n🔍 Testing NOAA GFS implementation...")
    
    from utils.fetch_noaa_gfs import fetch_noaa_gfs
    import inspect
    
    # Check if it's async
    if asyncio.iscoroutinefunction(fetch_noaa_gfs):
        print("  ✅ fetch_noaa_gfs is async")
    else:
        print("  ❌ fetch_noaa_gfs is not async")
        return False
    
    # Check source code for key features
    source = inspect.getsource(fetch_noaa_gfs)
    
    if 'nomads.ncep.noaa.gov' in source:
        print("  ✅ Uses NOMADS endpoint")
    else:
        print("  ❌ Does not use NOMADS endpoint")
        return False
    
    if 'cfgrib' in source:
        print("  ✅ Uses cfgrib for GRIB2 parsing")
    else:
        print("  ⚠️  Does not use cfgrib")
    
    if 'HTSGW' in source:
        print("  ✅ Requests wave height (HTSGW)")
    else:
        print("  ⚠️  Does not request wave height")
    
    if 't00z' in source or 't06z' in source or 't12z' in source:
        print("  ✅ Handles model cycles")
    else:
        print("  ⚠️  May not handle model cycles")
    
    return True


async def test_health_checks():
    """Test health check functions"""
    print("\n🔍 Testing health checks...")
    
    from utils.fetch_era5 import health_check_era5
    from utils.fetch_noaa_gfs import health_check_noaa_gfs
    
    print("  ℹ️  Note: Health checks require environment variables and network access")
    print("  ℹ️  Skipping actual health check calls (would require CDSAPI_KEY)")
    
    if asyncio.iscoroutinefunction(health_check_era5):
        print("  ✅ health_check_era5 is async")
    else:
        print("  ❌ health_check_era5 is not async")
        return False
    
    if asyncio.iscoroutinefunction(health_check_noaa_gfs):
        print("  ✅ health_check_noaa_gfs is async")
    else:
        print("  ❌ health_check_noaa_gfs is not async")
        return False
    
    return True


async def main():
    """Run all validation tests"""
    print("=" * 70)
    print("SwellSense Data Integration Validation")
    print("=" * 70)
    
    results = []
    
    # Test 1: Imports
    results.append(("Dependencies", await test_imports()))
    
    # Test 2: Fetchers
    results.append(("Fetcher Modules", await test_fetchers()))
    
    # Test 3: ERA5
    results.append(("ERA5 Implementation", await test_era5_structure()))
    
    # Test 4: NOAA GFS
    results.append(("NOAA GFS Implementation", await test_noaa_gfs_structure()))
    
    # Test 5: Health Checks
    results.append(("Health Checks", await test_health_checks()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 All validation tests passed!")
        print("\nNext steps:")
        print("1. Set CDSAPI_KEY environment variable")
        print("2. Start server: uvicorn main:app --reload --port 8888")
        print("3. Test endpoints:")
        print("   - curl http://localhost:8888/api/forecast/health")
        print("   - curl http://localhost:8888/api/forecast/global?lat=37.77&lon=-122.42")
    else:
        print("⚠️  Some validation tests failed - review output above")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
