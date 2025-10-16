# Railway 502 Error - Diagnosis

## Current Status (as of deployment 2becbe1)

**Symptoms:**
- Railway shows deployment status: SUCCESS
- App logs show: "Uvicorn running on http://0.0.0.0:8080"
- All external requests return: 502 "Application failed to respond"

**This indicates:** The container is running, FastAPI started successfully, but Railway's proxy can't reach the app.

## App Logs Confirm Success
```
Starting Container
INFO:     Started server process [2]
INFO:     Waiting for application startup.
INFO:main:⏸️  Global ingestion scheduler disabled (set ENABLE_SCHEDULER=true to enable)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

## Possible Causes

### 1. PORT Variable Mismatch
- **App listening on:** 8080 (from logs)
- **Railway expecting:** Probably 8080 (set by Railway automatically)
- **Dockerfile:** `CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Status:** This looks correct ✅

### 2. Health Check Configuration
Railway might be trying to health check a path that doesn't exist.

**Check in Railway Dashboard → Settings:**
- Healthcheck Path: Should be `/health` or `/` or empty
- Healthcheck Timeout: Should be at least 10 seconds
- Current healthcheck configuration might be wrong

### 3. Internal Port Configuration
Railway's "Port" setting might not match what the app is listening on.

**Check in Railway Dashboard → Settings:**
- Look for "Port" or "Internal Port" setting
- Should be: 8080 (or leave empty for auto-detect)

### 4. Network/Firewall Issue
The container's network might not be properly configured.

## How to Fix

### Option 1: Check Health Check Settings

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Click on "swellsense" service
3. Go to **Settings** tab
4. Scroll to "Health Check" section
5. **Either:**
   - Set Healthcheck Path to: `/health`
   - Set Healthcheck Timeout to: `30` seconds
   - **OR** Delete/disable healthcheck entirely

### Option 2: Verify Port Settings

1. In Railway Dashboard → Settings
2. Check "Variables" tab
3. Verify `PORT` is not manually set (let Railway auto-assign)
4. If manually set, delete it and redeploy

### Option 3: Try Different CMD Format

Update Dockerfile to use explicit port:

```dockerfile
# Instead of:
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

# Try:
CMD uvicorn main:app --host 0.0.0.0 --port 8080
```

Then redeploy.

### Option 4: Add Startup Probe

Railway might be terminating the container before it's ready.

In Railway Dashboard → Settings → Health Check:
- Enable "Startup Probe"
- Set timeout to 60 seconds

## Quick Test

Once you make changes, test immediately:

```bash
# Should return {"status":"healthy","service":"SwellSense API"}
curl https://api.swellsense.app/health

# Should return Facebook deletion status
curl "https://api.swellsense.app/api/facebook/data-deletion-status?id=test"
```

## Railway Dashboard URLs

- Main Dashboard: https://railway.app/dashboard
- Service Settings: https://railway.app/dashboard → cheerful-unity → swellsense → Settings
- Deployments: https://railway.app/dashboard → cheerful-unity → swellsense → Deployments

## Temporary Solution

While fixing Railway, use this URL for Facebook app:
```
https://swellsense.app/data-deletion
```

This frontend page is working and will get your Facebook app approved immediately!

## Most Likely Fix

Based on the symptoms, **the healthcheck is probably misconfigured**. Try:

1. Go to Settings → Delete or disable healthcheck
2. Redeploy
3. Test again

If that doesn't work, the internal port routing needs to be checked in Railway's network settings.
