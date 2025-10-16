# Railway Deployment Troubleshooting Guide
**Date:** October 16, 2024  
**Issue:** Backend returning 502 errors despite correct Dockerfile configuration  
**Status:** Requires manual Railway dashboard intervention

---

## Current Situation

### ✅ What's Working
- **Backend code:** Tested locally on port 8888 - works perfectly
  ```bash
  curl http://localhost:8888/health
  # Returns: {"status":"healthy","service":"SwellSense API"}
  ```
- **Dockerfile:** Correctly configured with dynamic PORT
  ```dockerfile
  WORKDIR /app/backend
  CMD sh -c "uvicorn main:app --host 0.0.0.0 --port $PORT"
  ```
- **Git commits:** All pushed to origin/main successfully
  - `ab49b2c`: Fix PORT variable usage
  - `e09f06e`: Clean up railway.json and clarify Dockerfile

### ❌ What's NOT Working
- **Railway deployment:** Still returning 502 errors
  ```bash
  curl -I https://api.swellsense.app/health
  # Returns: HTTP/2 502 Application failed to respond
  ```
- **Timeline:** 502 errors persist 90+ seconds after pushing commit e09f06e (13:28)

---

## Root Cause Analysis

Railway is either:
1. **Not detecting the new commits** from GitHub
2. **Caching an old Docker image** from previous builds
3. **Stuck in a failed deployment state** requiring manual intervention
4. **Missing environment variables** that cause startup failure

---

## Immediate Action Required

### Step 1: Check Railway Dashboard

Go to: **https://railway.app/dashboard**

1. **Select your project:** swellsense
2. **Select your service:** backend (or whatever it's named)
3. **Check Deployments tab:**
   - Is there a deployment for commit `e09f06e`?
   - If yes, what's its status? (Building/Deploying/Failed/Success)
   - If no, Railway hasn't detected the push yet

### Step 2: View Deployment Logs

If a deployment exists for `e09f06e`:
1. Click on the deployment
2. Go to **"Logs"** tab
3. Look for:
   ```
   ✅ GOOD: INFO: Uvicorn running on http://0.0.0.0:<dynamic_port>
   ❌ BAD:  INFO: Uvicorn running on http://0.0.0.0:8080
   ```
4. Check for any **ERROR** or **WARNING** messages
5. Look for the **healthcheck** results

### Step 3: Verify Environment Variables

In Railway Dashboard → Your Service → **Variables**:

**Required Variables:**
```bash
DATABASE_URL=postgresql://neondb_owner:...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_JWT_SECRET=...
OPENAI_API_KEY=sk-proj-...
SECRET_KEY=...
ALGORITHM=HS256
ENVIRONMENT=production
```

**Check:**
- [ ] All variables are set
- [ ] No typos in variable names
- [ ] DATABASE_URL has correct connection string
- [ ] PORT is NOT manually set (let Railway auto-assign)

### Step 4: Manual Redeploy

If deployment exists but is stuck or failed:

**Option A: Redeploy from Dashboard**
1. Go to **Deployments** tab
2. Find commit `e09f06e`
3. Click **three dots (...)** → **Redeploy**

**Option B: Trigger via Git**
```bash
cd /Users/ryanbradshaw/Git\ Projects/swellsense/swellsense
git commit --allow-empty -m "chore: trigger Railway redeploy"
git push origin main
```

**Option C: Railway CLI** (if installed)
```bash
railway up --service backend
```

---

## Expected Results After Successful Deployment

### 1. Railway Logs Should Show:
```
Starting Container
INFO:     Started server process [X]
INFO:     Waiting for application startup.
INFO:main:⏸️  Global ingestion scheduler disabled
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7XXX  <-- DYNAMIC PORT
INFO:     100.64.0.2:XXXXX - "GET /health HTTP/1.1" 200 OK
```

**Key indicators:**
- ✅ Port is **dynamic** (like 7823, 7456, NOT 8080 or 8000)
- ✅ Health check returns **200 OK**
- ✅ No "Application failed to respond" messages

### 2. External Endpoints Should Work:
```bash
# Health check
curl -I https://api.swellsense.app/health
# Expected: HTTP/2 200 OK

# Root endpoint
curl https://api.swellsense.app/
# Expected: {"message":"Welcome to SwellSense API 🌊",...}

# API info
curl https://api.swellsense.app/api/info
# Expected: {"name":"SwellSense API","version":"1.0.0",...}

# Forecast health
curl https://api.swellsense.app/api/forecast/health
# Expected: {"status":"ok" or "degraded",...}
```

---

## If Railway Deployment Succeeds But Still 502

This suggests a **routing or proxy issue**:

### Check Railway Service Settings

1. **Public Networking:**
   - Verify service has a **public domain** assigned
   - Check if custom domain `api.swellsense.app` is properly configured
   - Ensure DNS records point to Railway

2. **Health Check Settings:**
   ```json
   Path: /health
   Timeout: 30 seconds
   ```
   - If timeout is too short, increase to 60s
   - Try temporarily disabling healthcheck to see if service becomes accessible

3. **Port Configuration:**
   - Verify no manual PORT override in Variables
   - Railway should auto-assign PORT
   - Check if service is listening on internal port correctly

---

## Common Railway Issues & Solutions

### Issue 1: "Deployment succeeded but 502 persists"
**Solution:** Check if healthcheck is timing out before app fully starts
- Go to Settings → Health Check → Increase timeout to 60s
- Or temporarily disable healthcheck

### Issue 2: "Logs show port 8080 instead of dynamic port"
**Solution:** Railway is using cached image
- Delete all deployments
- Trigger fresh deploy: `git commit --allow-empty && git push`

### Issue 3: "No deployment for latest commit"
**Solution:** GitHub webhook not working
- Go to Settings → Integrations → GitHub
- Disconnect and reconnect repository
- Or manually trigger deployment

### Issue 4: "Build succeeds but container crashes on startup"
**Solution:** Check environment variables
- Missing DATABASE_URL or other critical vars
- Check logs for `connection refused` or `401 unauthorized` errors

---

## Next Steps After Railway Fix

Once backend is confirmed working:

### 1. Verify All Endpoints
```bash
# Run these commands to verify:
curl -I https://api.swellsense.app/health
curl https://api.swellsense.app/
curl https://api.swellsense.app/api/info
curl https://api.swellsense.app/api/forecast/health
curl "https://api.swellsense.app/api/facebook/data-deletion-status?id=test"
```

### 2. Fix Frontend API URL

**Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select `swellsense` project
3. Go to **Settings** → **Environment Variables**
4. Add or verify:
   ```
   NEXT_PUBLIC_API_URL=https://api.swellsense.app
   ```
5. Apply to: **Production**, **Preview**, **Development**
6. Redeploy frontend if needed

### 3. Test Frontend Pages
- https://swellsense.app/forecast (should load surf data)
- https://swellsense.app/account (should load user profile)

### 4. Clean Up Duplicate Files
```bash
cd /Users/ryanbradshaw/Git\ Projects/swellsense/swellsense
git rm frontend/lib/api.ts
git commit -m "chore: remove duplicate frontend/lib/api.ts"
git push origin main
```

### 5. Final Verification Commit
```bash
git commit --allow-empty -m "chore: finalize Railway backend deployment stability (dynamic port verified)

✅ Railway deployment successful
✅ Backend responding on all endpoints
✅ Frontend API connectivity verified
✅ Infrastructure audit complete"
git push origin main
```

---

## Support Resources

- **Railway Docs:** https://docs.railway.app/
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app/
- **Project Repo:** https://github.com/rbradshaw9/swellsense

---

## Summary

**Current Status:** Code is correct, Railway deployment needs manual intervention

**Your Action Required:**
1. Log into Railway dashboard
2. Check deployment status for commit `e09f06e`
3. Review logs for errors
4. Manually trigger redeploy if needed
5. Verify dynamic PORT is being used (not 8080)

**Expected Timeline:** Once redeployed, backend should be online in 2-3 minutes

**Files Modified Today:**
- `Dockerfile` - Fixed to use `$PORT` directly
- `railway.json` - Removed ignored `startCommand`
- `CODEBASE_AUDIT_2024-10-16.md` - Comprehensive audit report
- `RAILWAY_DEPLOYMENT_GUIDE.md` - This troubleshooting guide

---

**Last Updated:** October 16, 2024 13:35 EDT  
**Next Update:** After Railway deployment verification
