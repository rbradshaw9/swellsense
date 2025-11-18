# Supabase Setup - SwellSense

## ✅ Configuration Complete

**Project ID:** `mxxlxoizfqsidyyqxqtg`  
**Project URL:** `https://mxxlxoizfqsidyyqxqtg.supabase.co`  
**Database Password:** `V4#uZlziK*TZvU9O`

### Files Updated
- ✅ `mobile/services/auth.ts` - Anon key configured
- ✅ `backend/.env` - Service role key configured

### Next Steps

#### 1. Update Railway Environment Variables
Go to [Railway Dashboard](https://railway.app) → Your Project → Variables:

```
SUPABASE_URL=https://mxxlxoizfqsidyyqxqtg.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14eGx4b2l6ZnFzaWR5eXF4cXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NzMzNDQsImV4cCI6MjA3OTA0OTM0NH0.k8HAbhAFhnf11woAhChNoOx9S3uehdO8Z2hgZeB4p7Y
```

Then click **"Redeploy"**

#### 2. Test Mobile App

```bash
cd mobile
npx expo start
```

Press `i` for iOS simulator, then:
1. Try creating an account (Sign Up)
2. Log out and log back in
3. Test session logging

#### 3. Verify Backend Authentication

```bash
# Should return 401 Unauthorized (good - auth is working)
curl https://api.swellsense.app/api/sessions/stats
```

## API Keys Reference

**Anon Public Key** (for frontend):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14eGx4b2l6ZnFzaWR5eXF4cXRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NzMzNDQsImV4cCI6MjA3OTA0OTM0NH0.k8HAbhAFhnf11woAhChNoOx9S3uehdO8Z2hgZeB4p7Y
```

**Service Role Key** (for backend - KEEP SECRET):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14eGx4b2l6ZnFzaWR5eXF4cXRnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzQ3MzM0NCwiZXhwIjoyMDc5MDQ5MzQ0fQ.3sCDM8bs8m6BrhH3l9LthIqbgEMipk3jpfKOjKnY4-Q
```

## Supabase Dashboard

Access your project: https://supabase.com/dashboard/project/mxxlxoizfqsidyyqxqtg

- **Authentication**: View users, configure providers
- **Database**: Direct SQL access (Neon PostgreSQL is your actual data store)
- **API**: Test endpoints, view logs

## Database Architecture

- **User Data**: Stored in Supabase Auth
- **App Data**: Stored in Neon PostgreSQL
  - `surf_sessions` - Session logs
  - `alert_preferences` - User notification settings
  - `favorite_spots` - Saved surf spots
  - `alert_history` - Notification tracking

Connection managed via `user_id` foreign key referencing Supabase auth users.
