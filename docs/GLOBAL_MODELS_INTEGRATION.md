# Global Forecast Models Integration

## 🌍 Overview

SwellSense now includes **6 data sources** for comprehensive worldwide surf forecasting:

### Regional APIs (High Resolution, Limited Coverage)
1. **StormGlass** - Marine forecasts (requires paid subscription)
2. **OpenWeatherMap** - Weather data (free tier available)
3. **WorldTides** - Tide predictions (free tier available)
4. **Met.no** - Ocean forecasts (free, North Atlantic/European waters)

### Global Models (Lower Resolution, Worldwide Coverage)
5. **NOAA GFS/WaveWatch III** - Global wave model (~30km resolution)
6. **Copernicus ERA5** - ECMWF reanalysis (~25km resolution)

---

## 🎯 Why Global Models?

**Problem**: Regional APIs have coverage gaps and rate limits
- StormGlass: Requires paid subscription ($50+/month)
- Met.no: Only covers North Atlantic and European waters
- WorldTides: Free tier has strict rate limits

**Solution**: Global models provide fallback coverage
- **NOAA GFS**: Free, updated 4x daily, covers entire globe
- **ERA5**: Historical reanalysis + near-real-time, 0.25° resolution

**Result**: SwellSense **never** returns empty forecasts - always has at least one data source.

---

## 📊 Data Source Hierarchy

```
/api/forecast/global?lat=X&lon=Y
│
├─ Regional APIs (parallel fetch)
│  ├─ StormGlass ────────→ Wave height, period, direction
│  ├─ OpenWeatherMap ────→ Wind, temperature, pressure
│  ├─ WorldTides ────────→ Tide heights and extremes
│  └─ Met.no ────────────→ Ocean currents, sea temperature
│
├─ Global Models (parallel fetch)
│  ├─ NOAA GFS/WW3 ──────→ Wave height, period, wind
│  └─ ERA5 ──────────────→ Wind components, wave height
│
└─ Aggregator
   ├─ Average available wave heights
   ├─ Average available wind speeds
   ├─ Generate human-readable summary
   └─ Return partial=true if any source failed
```

---

## 🔧 Implementation Status

### NOAA GFS/WaveWatch III
**Status**: ⚠️ **Mock Implementation**

**What Works**:
- ✅ HTTP requests to NOMADS GRIB2 filter API
- ✅ Grid cell caching (1-hour TTL)
- ✅ Timeout handling (8 seconds)
- ✅ Health check endpoint

**What's Needed**:
- ❌ GRIB2 parsing library (`pygrib` or `cfgrib`)
- ❌ Extract actual values from GRIB2 files

**GRIB2 File Structure**:
```
HTSGW = Significant Wave Height (meters)
WIND  = Wind Speed (m/s)
WVDIR = Wave Direction (degrees)
WVPER = Wave Period (seconds)
```

**To Enable**:
```bash
# Install GRIB2 parser
pip install pygrib  # or: pip install cfgrib xarray

# Update fetch_noaa_gfs.py to parse GRIB2 response
# Set available=True when data is successfully parsed
```

**Example URL**:
```
https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl?
  file=multi_1.glo_30m.t00z.f000.grib2
  &lev_surface=on
  &var_HTSGW=on
  &var_WIND=on
  &leftlon=270&rightlon=272
  &toplat=34&bottomlat=32
```

---

### Copernicus ERA5
**Status**: ⚠️ **Mock Implementation**

**What Works**:
- ✅ Grid cell caching (1-hour TTL)
- ✅ Timeout handling (10 seconds)
- ✅ Health check endpoint
- ✅ Wind speed/direction calculations from U/V components

**What's Needed**:
- ❌ Copernicus CDS API account (free)
- ❌ CDS API key configuration
- ❌ `cdsapi` Python library

**To Enable**:
```bash
# 1. Create Copernicus account
https://cds.climate.copernicus.eu/user/register

# 2. Get API key
https://cds.climate.copernicus.eu/api-how-to

# 3. Install library
pip install cdsapi

# 4. Configure credentials
echo "url: https://cds.climate.copernicus.eu/api/v2" > ~/.cdsapirc
echo "key: YOUR_UID:YOUR_API_KEY" >> ~/.cdsapirc

# 5. Set in fetch_era5.py
CDS_API_KEY = "YOUR_UID:YOUR_API_KEY"

# 6. Uncomment real implementation code
```

**Variables**:
- `10m_u_component_of_wind` → U wind (m/s)
- `10m_v_component_of_wind` → V wind (m/s)
- `significant_height_of_combined_wind_waves_and_swell` → Wave height (m)

**Alternative**: OpenDAP/THREDDS access (no API key, but slower)

---

## 🧪 Testing

### Test Locations

```bash
# Sydney, Australia (Southern Hemisphere)
curl -s "http://localhost:8888/api/forecast/global?lat=-33.86&lon=151.20" | jq .

# Puerto Rico (Caribbean)
curl -s "http://localhost:8888/api/forecast/global?lat=18.47&lon=-67.15" | jq .

# San Francisco (West Coast USA)
curl -s "http://localhost:8888/api/forecast/global?lat=37.77&lon=-122.42" | jq .

# Nazaré, Portugal (North Atlantic)
curl -s "http://localhost:8888/api/forecast/global?lat=39.60&lon=-9.07" | jq .
```

### Expected Response

```json
{
  "timestamp": "2025-10-15T19:10:58Z",
  "location": {"lat": -33.86, "lon": 151.2},
  "sources": {
    "stormglass": null,
    "openweather": {...},
    "worldtides": {...},
    "metno": null,
    "noaa_gfs": {
      "source": "noaa_gfs",
      "available": false,
      "note": "GRIB2 parsing not yet implemented"
    },
    "era5": {
      "source": "era5",
      "available": false,
      "note": "ERA5 requires CDS API key"
    }
  },
  "summary": {
    "wave_height_m": null,
    "wind_speed_ms": 0.45,
    "temperature_c": 15.36,
    "conditions": "No wave data available"
  },
  "partial": true,
  "sources_available": ["openweather", "worldtides"],
  "sources_failed": ["stormglass", "metno", "noaa_gfs", "era5"],
  "response_time_s": 2.34
}
```

---

## 📈 Production Deployment Checklist

### Phase 1: Current State ✅
- [x] Mock implementations deployed
- [x] Health checks functional
- [x] 6-source aggregation working
- [x] Graceful fallback to available sources

### Phase 2: NOAA GFS Integration
- [ ] Install `pygrib` or `cfgrib` in Dockerfile
- [ ] Test GRIB2 file download and parsing
- [ ] Extract wave height, period, wind from GRIB2
- [ ] Set `available=True` in response
- [ ] Verify 1-hour caching works
- [ ] Test with multiple locations

### Phase 3: ERA5 Integration
- [ ] Create Copernicus CDS account
- [ ] Generate API key
- [ ] Install `cdsapi` in Dockerfile
- [ ] Configure credentials (environment variable or .cdsapirc)
- [ ] Implement NetCDF parsing with xarray
- [ ] Calculate wind speed/direction from U/V components
- [ ] Set `available=True` in response
- [ ] Test with historical dates

### Phase 4: Optimization
- [ ] Add Redis cache (replace in-memory cache)
- [ ] Implement retry logic with exponential backoff
- [ ] Add Prometheus metrics for model accuracy
- [ ] Compare regional vs global model predictions
- [ ] Tune aggregation weights based on accuracy

---

## 🎯 Success Criteria

### Minimum (Current)
- ✅ At least 1 data source returns data (OpenWeather)
- ✅ Response time < 15 seconds
- ✅ No unhandled exceptions
- ✅ Health check reports all 6 services

### Target (Phase 2)
- ✅ NOAA GFS returns wave data for any location
- ✅ At least 2 sources available worldwide
- ✅ Response time < 10 seconds
- ✅ 95% uptime for global models

### Ideal (Phase 3)
- ✅ ERA5 provides backup for NOAA GFS
- ✅ 3+ sources available for most locations
- ✅ Response time < 5 seconds with caching
- ✅ 99% uptime with redundant fallbacks

---

## 📚 References

- [NOAA NOMADS GRIB Filter](https://nomads.ncep.noaa.gov/)
- [WaveWatch III Documentation](https://polar.ncep.noaa.gov/waves/wavewatch/)
- [Copernicus CDS API](https://cds.climate.copernicus.eu/api-how-to)
- [ERA5 Documentation](https://confluence.ecmwf.int/display/CKB/ERA5)
- [pygrib Documentation](https://jswhit.github.io/pygrib/)
- [cfgrib Documentation](https://github.com/ecmwf/cfgrib)

---

## 🚀 Next Steps

1. **Enable NOAA GFS**:
   ```bash
   pip install pygrib
   # Update fetch_noaa_gfs.py to parse GRIB2
   ```

2. **Enable ERA5**:
   ```bash
   # Get CDS API key from Copernicus
   pip install cdsapi
   # Set CDS_API_KEY in fetch_era5.py
   ```

3. **Test & Deploy**:
   ```bash
   # Test locally
   curl "http://localhost:8888/api/forecast/global?lat=0&lon=0" | jq .
   
   # Deploy to Railway
   git push origin main
   ```

4. **Monitor**:
   - Check Railway logs for NOAA GFS success rate
   - Verify ERA5 data freshness
   - Compare model vs regional API accuracy
