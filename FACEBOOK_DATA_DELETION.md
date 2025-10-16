# Facebook Data Deletion - Quick Reference

## For Facebook App Dashboard

You have **TWO options** for the Data Deletion field. Choose the one that works best for you:

---

## Option 1: Callback URL (RECOMMENDED) ⭐

### URL to enter in Facebook App Dashboard:
```
https://api.swellsense.app/api/facebook/data-deletion
```

### What it does:
- Facebook automatically POSTs to this endpoint when users delete the app
- Backend receives signed request, verifies authenticity, and processes deletion
- Returns confirmation URL and code to Facebook
- Fully automated - no manual intervention needed

### Requirements:
- Add `FACEBOOK_APP_SECRET` to your Railway environment variables
- Backend must be deployed and accessible
- Endpoint is already created in `backend/routers/facebook.py`

---

## Option 2: Instructions URL (ALTERNATIVE)

### URL to enter in Facebook App Dashboard:
```
https://swellsense.app/data-deletion
```

### What it does:
- Directs users to a page with instructions on how to delete their data
- Users can delete via account settings, email request, or removing Facebook app
- Manual process - users initiate deletion themselves

### Requirements:
- None - page is already deployed at `/data-deletion`
- Works immediately without backend setup

---

## Which Should You Use?

### Use Callback URL (Option 1) if:
✅ You want automated deletion handling
✅ Your backend is deployed on Railway/production
✅ You want full Facebook Platform Policy compliance
✅ You want to track deletion requests programmatically

### Use Instructions URL (Option 2) if:
✅ Your backend isn't deployed yet
✅ You want simpler setup
✅ You're okay with manual deletion requests
✅ You want to get the Facebook app approved quickly

---

## Setup Steps

### For Callback URL (Option 1):

1. **Deploy backend to Railway** (if not already deployed)

2. **Add environment variable to Railway:**
   ```
   FACEBOOK_APP_SECRET=your_facebook_app_secret
   ```

3. **Your Railway backend URL is:**
   ```
   https://api.swellsense.app
   ```

4. **Enter in Facebook App Dashboard:**
   ```
   https://api.swellsense.app/api/facebook/data-deletion
   ```

5. **Test it:**
   - Facebook will verify the endpoint is reachable
   - Check Railway logs when users delete the app

### For Instructions URL (Option 2):

1. **Enter in Facebook App Dashboard:**
   ```
   https://swellsense.app/data-deletion
   ```

2. **Done!** 
   - The page is already deployed via Vercel
   - Users will see clear deletion instructions

---

## Testing

### Test the Callback URL:
```bash
# Send a test signed request (from Facebook's webhook tester or your own script)
curl -X POST https://api.swellsense.app/api/facebook/data-deletion \
  -d "signed_request=test_signature.test_payload"
```

### Test the Instructions URL:
Just visit: https://swellsense.app/data-deletion

---

## Current Status

✅ Backend endpoint created: `/api/facebook/data-deletion`
✅ Frontend page created: `/data-deletion`
✅ Documentation updated: `FACEBOOK_APP_SETUP.md`
✅ All changes committed and pushed to GitHub
✅ Vercel will auto-deploy frontend page
⏳ Pending: Add to Facebook App Dashboard (your action)
⏳ Pending: Deploy backend to Railway (if using callback URL)

---

## Quick Answer for Your Question

**For Facebook App Dashboard, use one of these:**

1. **Callback URL** (automated): `https://api.swellsense.app/api/facebook/data-deletion`
2. **Instructions URL** (manual): `https://swellsense.app/data-deletion`

**I recommend starting with Option 2** (instructions URL) to get your Facebook app approved quickly, then switching to Option 1 (callback URL) once your backend is fully deployed.
