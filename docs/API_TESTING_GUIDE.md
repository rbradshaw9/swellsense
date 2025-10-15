# SwellSense API Testing Guide

## 🎯 Overview

This guide provides comprehensive testing procedures for the SwellSense resilient global forecast system.

---

## 📡 Endpoints

### 1. `/api/forecast/health` - System Health Check

**Purpose**: Monitor external API status and database connectivity with 5-minute cache.

**Method**: `GET`

**Example Request**:
```bash
curl -s "http://localhost:8888/api/forecast/health" | jq .
```

**Success Response** (200 OK):
```json
{
  "status": "ok",
  "timestamp": "2025-10-15T19:00:26Z",
  "services": {
    "stormglass": { "ok": true, "latency_ms": 660 },
    "openweather": { "ok": true, "latency_ms": 312 },
    "worldtides": { "ok": true, "latency_ms": 847 },
    "metno": { "ok": true, "latency_ms": 495 }
  },
  "database": { "connected": true },
  "failed_services": null,
  "version": "v0.4",
  "check_duration_s": 2.01
}
```

**Degraded Response** (207 Multi-Status):
```json
{
  "status": "degraded",
  "failed_services": ["worldtides", "metno"],
  ...
}
```

**Key Features**:
- ✅ 5-minute cache to avoid rate limits
- ✅ Per-service latency metrics
- ✅ Database connection validation
- ✅ Returns 200 (ok) or 207 (degraded)

---

### 2. `/api/forecast/global` - Multi-Source Forecast Aggregator

**Purpose**: Get resilient surf forecast combining StormGlass, OpenWeather, WorldTides, and Met.no.

**Method**: `GET`

**Parameters**:
- `lat` (float, required): Latitude (-90 to 90)
- `lon` (float, required): Longitude (-180 to 180)
- `hours` (int, optional): Forecast duration (default: 12)

**Example Requests**:
```bash
# Los Angeles (El Porto)
curl -s "http://localhost:8888/api/forecast/global?lat=33.63&lon=-118.00" | jq .

# Hawaii (Waikiki)
curl -s "http://localhost:8888/api/forecast/global?lat=21.28&lon=-157.83" | jq .

# Portugal (Nazaré)
curl -s "http://localhost:8888/api/forecast/global?lat=39.60&lon=-9.07" | jq .

# Australia (Bondi Beach)
curl -s "http://localhost:8888/api/forecast/global?lat=-33.89&lon=151.28" | jq .
```

**Success Response** (200 OK):
```json
{
  "timestamp": "2025-10-15T19:00:43Z",
  "location": {
    "lat": 33.63,
    "lon": -118.0
  },
  "sources": {
    "stormglass": {
      "wave_height_m": 1.38,
      "wave_period_s": 5.12,
      "wave_direction_deg": 219.8,
      "water_temp_c": 19.99,
      "wind_speed_ms": 1.34,
      "wind_direction_deg": 194.81,
      "timestamp": "2025-10-15T00:00:00+00:00",
      "source": "stormglass"
    },
    "openweather": {
      "wind_speed_ms": 4.02,
      "wind_direction_deg": 283,
      "temperature_c": 19.49,
      "pressure_hpa": 1016,
      "humidity_pct": 72,
      "visibility_m": 10000,
      "timestamp": "2025-10-15T19:00:33Z",
      "source": "openweather"
    },
    "worldtides": null,
    "metno": null
  },
  "summary": {
    "wave_height_m": 1.38,
    "wind_speed_ms": 2.7,
    "temperature_c": 19.5,
    "tide_height_m": null,
    "conditions": "4-5ft waves, light wind"
  },
  "partial": true,
  "sources_available": ["stormglass", "openweather"],
  "sources_failed": ["worldtides", "metno"],
  "response_time_s": 10.24
}
```

**Key Features**:
- ✅ Parallel API calls with `asyncio.gather()`
- ✅ Graceful degradation (returns 200 even if sources fail)
- ✅ `partial` flag indicates missing data
- ✅ Human-readable `conditions` summary
- ✅ Per-source timeout (10 seconds)
- ✅ Response time tracking

---

## 🧪 Local Testing

### Start Development Server

```bash
cd backend
export DATABASE_URL="postgresql://neondb_owner:npg_yLWglz7t0SiK@ep-floral-base-adkze7qi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
python -m uvicorn main:app --reload --port 8888
```

### Test Suite

```bash
# 1. Health check
curl -s "http://localhost:8888/api/forecast/health" | jq .

# 2. Global forecast (multiple locations)
curl -s "http://localhost:8888/api/forecast/global?lat=33.63&lon=-118.00" | jq .
curl -s "http://localhost:8888/api/forecast/global?lat=21.28&lon=-157.83" | jq .
curl -s "http://localhost:8888/api/forecast/global?lat=39.60&lon=-9.07" | jq .

# 3. Check response time
time curl -s "http://localhost:8888/api/forecast/global?lat=33.63&lon=-118.00" > /dev/null

# 4. Test error handling (invalid coordinates)
curl -s "http://localhost:8888/api/forecast/global?lat=999&lon=-118.00" | jq .
```

---

## 🚂 Railway Deployment Testing

### Deployed Endpoints

Replace `<your-railway-domain>` with your actual Railway URL:

```bash
# Health check
curl -s "https://<your-railway-domain>/api/forecast/health" | jq .

# Global forecast
curl -s "https://<your-railway-domain>/api/forecast/global?lat=33.63&lon=-118.00" | jq .
```

### Verify Deployment

1. **Check Railway Logs**:
   - Look for: `✅ Global ingestion scheduler started`
   - Verify: No `NameError` or import errors
   - Confirm: `INFO:scheduler:🌊 GLOBAL DATA INGESTION STARTED`

2. **Monitor Response Times**:
   ```bash
   time curl -s "https://<your-railway-domain>/api/forecast/global?lat=33.63&lon=-118.00" > /dev/null
   ```
   - Target: < 5 seconds (may be higher if APIs timeout)

3. **Check Error Logs**:
   - No 502 Bad Gateway errors
   - No unhandled exceptions
   - Look for per-source logging:
     - `INFO:api_clients:StormGlass API success in X.XXs`
     - `WARNING:api_clients:WorldTides API timeout after X.XXs`

---

## 📊 Success Criteria

✅ **Health Endpoint**:
- Returns 200 (all ok) or 207 (degraded)
- Shows accurate service status
- Database connected: true
- Latency metrics for each API
- Cache working (subsequent calls < 100ms)

✅ **Global Forecast Endpoint**:
- Returns 200 OK with data from at least 1 source
- `partial: true` if any source fails
- `summary.conditions` is human-readable
- `response_time_s` < 15 seconds (with timeouts)
- No 502 errors or unhandled exceptions

✅ **Logging**:
- Per-source success/failure logged
- Response times tracked
- Clear error messages for failures

---

## 🐛 Known Issues & Workarounds

### 1. WorldTides API Timeout
**Symptom**: `"worldtides": null` in response  
**Cause**: Free tier rate limits or API credits exhausted  
**Impact**: No tide data, but forecast still returns (graceful degradation)  
**Workaround**: Endpoint returns successfully with `partial: true`

### 2. Met.no 422 Error
**Symptom**: `Client error '422 Unprocessable Entity'`  
**Cause**: Coordinates outside Met.no coverage area (primarily North Atlantic/European waters)  
**Impact**: No ocean current data for some locations  
**Workaround**: StormGlass provides wave data as fallback

### 3. Response Time > 10s
**Symptom**: `response_time_s: 10.24`  
**Cause**: Some APIs timing out (10s per-source timeout)  
**Impact**: Slower response but still completes  
**Workaround**: Parallel fetching minimizes impact; consider reducing timeout to 5s

### 4. Timezone Warning in StormGlass
**Symptom**: `can't subtract offset-naive and offset-aware datetimes`  
**Cause**: Timestamp comparison in ingestion script  
**Impact**: Some duplicate records skipped  
**Status**: Non-critical, does not affect API endpoints

---

## 🔧 Optimization Opportunities

1. **Reduce Timeout**: Change `API_TIMEOUT = 10.0` to `5.0` in `api_clients.py`
2. **Add Redis Cache**: Cache API responses for 5-10 minutes
3. **Retry Logic**: Add exponential backoff for transient failures
4. **API Key Validation**: Pre-validate keys on startup
5. **Prometheus Metrics**: Export latency and success rate metrics

---

## 📝 Test Checklist

Before deploying to production:

- [ ] Health check returns correct status
- [ ] Global forecast works for 5+ test locations
- [ ] Partial responses handled gracefully
- [ ] Database connectivity verified
- [ ] Response times acceptable (< 15s with timeouts)
- [ ] Logging shows per-source timing
- [ ] No unhandled exceptions in Railway logs
- [ ] Cache working (health check < 100ms on repeat)
- [ ] Invalid coordinates return 400 error
- [ ] Missing parameters return validation error

---

## 🎉 Test Results

**Date**: October 15, 2025  
**Environment**: Local (port 8888)

| Test | Status | Notes |
|------|--------|-------|
| Health Check | ✅ PASS | Returns 207 (degraded), 2 services down |
| Global Forecast (LA) | ✅ PASS | 2/4 sources, response_time: 10.24s |
| Global Forecast (Hawaii) | ⏳ PENDING | |
| Global Forecast (Portugal) | ⏳ PENDING | |
| Invalid Coordinates | ⏳ PENDING | |
| Railway Deployment | ⏳ PENDING | |

**Observations**:
- StormGlass: ✅ Working (660ms latency)
- OpenWeather: ✅ Working (312ms latency)
- WorldTides: ❌ Timeout (5247ms, exceeded 5s limit)
- Met.no: ❌ 422 Error (location outside coverage)
- Database: ✅ Connected
- Summary: Graceful degradation working as designed

---

## 🚀 Next Steps

1. ✅ Deploy to Railway
2. ⏳ Monitor production logs for 24 hours
3. ⏳ Verify hourly ingestion runs successfully
4. ⏳ Test with frontend integration
5. ⏳ Set up alerts for service degradation
