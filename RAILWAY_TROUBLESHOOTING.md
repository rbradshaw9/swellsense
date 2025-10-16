# Railway Backend Troubleshooting

## Current Status
- **URL**: https://api.swellsense.app
- **Issue**: 502 errors (Application failed to respond)
- **Last Deploy**: fb00b2e - "Trigger Railway redeploy for Facebook data deletion endpoint"

## Quick Diagnosis

The 502 error means Railway successfully deployed the container, but the FastAPI application isn't starting or responding to health checks.

## Step-by-Step Fix

### 1. Check Railway Dashboard Logs
Go to: https://railway.app/dashboard
- Find "swellsense" service in "cheerful-unity" project
- Click "Deployments" tab
- Click on the latest deployment
- Check **Deploy Logs** for errors

Common errors to look for:
- `ModuleNotFoundError` - Missing Python package
- `ImportError` - Import issue with routers
- `DATABASE_URL` - Connection string errors
- Port binding errors

### 2. Verify Environment Variables

In Railway dashboard, check these are set:
```
DATABASE_URL=postgresql://neondb_owner:npg_yLWglz7t0SiK@ep-floral-base-adkze7qi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PORT=8000
ENABLE_SCHEDULER=false
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
FACEBOOK_APP_SECRET=your_fb_app_secret
```

### 3. Test Import Locally

Test if the facebook router imports correctly:
```bash
cd backend
python -c "from routers import facebook; print('✅ Facebook router OK')"
python -c "from main import app; print('✅ Main app OK')"
```

### 4. Check Dockerfile Copying

The Dockerfile copies `backend/` to `/app/backend/`. Verify the facebook router exists:
```dockerfile
# In Dockerfile:
COPY backend/ /app/backend/
```

Make sure `backend/routers/facebook.py` exists locally and is committed to git.

### 5. Manual Redeploy

In Railway dashboard:
1. Go to your service
2. Click "Deployments"
3. Find the latest deployment
4. Click the three dots (⋮)
5. Click "Redeploy"

### 6. Check Railway Build Logs

Look for these specific issues:

**Issue: Missing Dependencies**
```
ERROR: Could not find a version that satisfies the requirement
```
**Fix**: Add missing package to `backend/requirements.txt`

**Issue: Import Error**
```
ImportError: cannot import name 'facebook' from 'routers'
```
**Fix**: Verify `backend/routers/facebook.py` exists and is in git

**Issue: Port Binding**
```
[ERROR] Failed to bind to 0.0.0.0:8000
```
**Fix**: Check if Railway's PORT variable is set correctly

### 7. Test with Railway CLI

```bash
# Link to your project
cd /Users/ryanbradshaw/Git\ Projects/swellsense/swellsense
railway link

# View live logs
railway logs

# Force new deployment
railway up
```

## Common Fixes

### Fix 1: Facebook Router Not Found
If logs show `ImportError: cannot import name 'facebook'`:

```bash
# Verify file exists
ls -la backend/routers/facebook.py

# Verify it's in git
git ls-files backend/routers/facebook.py

# If not, re-add and push
git add backend/routers/facebook.py
git commit -m "Ensure facebook router is tracked"
git push origin main
```

### Fix 2: Database Connection
If logs show database errors:

```bash
# Test connection locally
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://neondb_owner:npg_yLWglz7t0SiK@ep-floral-base-adkze7qi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require')
    print('✅ DB connected')
    await conn.close()
asyncio.run(test())
"
```

### Fix 3: Missing Environment Variables
Railway might be missing critical env vars. Re-add them:

1. Go to Railway → Settings → Variables
2. Add any missing from the list in Step 2 above
3. Click "Redeploy"

## Test After Fix

Once Railway shows "Deployed" with no errors:

```bash
# Test health endpoint
curl https://api.swellsense.app/health

# Expected response:
# {"status":"healthy","service":"SwellSense API"}

# Test Facebook endpoint
curl https://api.swellsense.app/api/facebook/data-deletion-status?id=test

# Expected response:
# {"status":"completed","message":"Your data deletion request has been processed.",...}
```

## Emergency Fallback

If you can't fix Railway immediately, use the **Instructions URL** for Facebook:
```
https://swellsense.app/data-deletion
```

This page is working right now and satisfies Facebook's requirements!

## Next Steps After Fix

Once the backend is healthy:

1. ✅ Test Facebook data deletion callback:
   ```bash
   curl https://api.swellsense.app/api/facebook/data-deletion-status?id=test123
   ```

2. ✅ Update Facebook App Dashboard with:
   ```
   https://api.swellsense.app/api/facebook/data-deletion
   ```

3. ✅ Test from Facebook's webhook tester

---

**Need Help?**
Check Railway logs first - they usually tell you exactly what's wrong!
