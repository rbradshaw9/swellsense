# 🚀 Phase 10: User Profiles Setup Guide

## What Was Just Implemented

✅ **Backend** (Python/FastAPI):
- Extended `/api/user/profile` endpoint (GET + POST)
- Username availability check endpoint
- Supabase Python client integration
- Full profile + preferences CRUD

✅ **Frontend** (Next.js/React):
- Editable account page with real-time validation
- Profile fields: username, name, home spot
- Preferences: units, skill level, board type, AI persona, notifications
- Beautiful ocean gradient UI

✅ **Database Schema**:
- `user_profiles` table with username, name, home_spot, role
- `user_preferences` table with all user settings
- Row Level Security (RLS) policies
- Admin seeding SQL

---

## 🔧 Required Setup Steps

### Step 1: Create Supabase Project (if not done yet)

1. Go to [supabase.com](https://supabase.com)
2. Sign in with GitHub
3. Click **"New Project"**
4. Fill in:
   - **Name**: SwellSense
   - **Database Password**: (create a strong password and save it)
   - **Region**: Choose closest to you (e.g., `us-east-1`)
5. Click **"Create new project"**
6. Wait ~2 minutes for provisioning

### Step 2: Run Database Migration

1. In Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **"New Query"**
3. Open the file: `supabase_migration_profiles.sql` (in your project root)
4. **Copy the entire file contents** (200+ lines)
5. **Paste** into the SQL Editor
6. Click **Run** (or press `Cmd/Ctrl + Enter`)
7. ✅ You should see: **"Success. No rows returned"**

**Verify Tables Created:**
- Click **Database** → **Tables** in sidebar
- You should see:
  - ✅ `user_profiles`
  - ✅ `user_preferences`

### Step 3: Get Supabase Credentials

1. In Supabase dashboard, go to **Settings** (⚙️ icon)
2. Click **API** in the left menu
3. Copy these values:

```bash
# Project URL
SUPABASE_URL=https://xxxxx.supabase.co

# anon/public key (for frontend)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# service_role key (for backend - keep secret!)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

4. Go to **Settings** → **API** → **JWT Settings**
5. Copy:

```bash
# JWT Secret (for backend token verification)
SUPABASE_JWT_SECRET=your-super-secret-jwt-key-here
```

### Step 4: Add Environment Variables to Vercel (Frontend)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your **swellsense** project
3. Click **Settings** → **Environment Variables**
4. Add these variables:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxxx.supabase.co` | Production, Preview, Development |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1...` | Production, Preview, Development |

5. Click **Save**

### Step 5: Add Environment Variables to Railway (Backend)

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Select your **swellsense-backend** service
3. Click **Variables** tab
4. Add these variables:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://... (should already exist)
OPENAI_API_KEY=sk-proj-... (should already exist)
```

5. Railway will automatically redeploy

### Step 6: Redeploy Frontend

1. Go back to Vercel dashboard
2. Click **Deployments** tab
3. Click **⋯** on latest deployment → **Redeploy**
4. Wait for build to complete (~2 minutes)

---

## 🧪 Testing the Profile System

### Test 1: View Profile

1. Go to your deployed site: `https://swellsense.vercel.app`
2. Click **Sign In** (or **Account** if already logged in)
3. Navigate to **Account** page
4. You should see:
   - ✅ Your email
   - ✅ Editable username, name, home spot fields
   - ✅ Preference dropdowns (units, skill level, etc.)

### Test 2: Edit Profile

1. Click **Edit** button (top right of Profile card)
2. Change username to something unique (e.g., `surferbro123`)
3. Watch for the ✓ or ✗ icon (username availability check)
4. Fill in:
   - **Name**: Your name
   - **Home Spot**: Your local surf spot
5. Change preferences:
   - **Units**: Imperial or Metric
   - **Skill Level**: Your level
   - **Board Type**: Your preferred board
   - **AI Assistant Style**: How you want AI to talk
6. Click **Save**
7. ✅ You should see: **"Profile updated successfully!"** toast

### Test 3: Username Validation

1. Click **Edit** again
2. Try to set username to something short (1-2 characters)
3. ❌ You should see: "Username must be at least 3 characters"
4. Try a username that's already taken
5. ❌ You should see red ✗ icon
6. Try a unique username
7. ✅ You should see green ✓ icon

### Test 4: Preferences Persistence

1. Sign out
2. Sign back in
3. Go to **Account** page
4. ✅ All your profile data and preferences should still be there

---

## 🔐 Admin Account

The SQL migration automatically created an admin account:

```
Email: rbradshaw@gmail.com
Password: SiR43Tx2-
Role: admin
```

**To login:**
1. Go to login page
2. Enter email: `rbradshaw@gmail.com`
3. Enter password: `SiR43Tx2-`
4. ✅ You should be logged in with admin role

**Change password:**
1. In Supabase dashboard → **Authentication** → **Users**
2. Find `rbradshaw@gmail.com`
3. Click **⋯** → **Reset Password**
4. Send reset link or set manually

---

## 📊 Database Structure

### `user_profiles` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Foreign key to auth.users |
| `username` | varchar(30) | Unique username |
| `name` | varchar(100) | Full name |
| `home_spot` | varchar(100) | Favorite surf spot |
| `avatar_url` | text | Profile picture URL |
| `role` | varchar(20) | User role (authenticated/admin) |
| `created_at` | timestamp | Account creation date |
| `updated_at` | timestamp | Last profile update |

### `user_preferences` Table

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | uuid | Foreign key to auth.users |
| `units` | varchar(20) | imperial or metric |
| `skill_level` | varchar(20) | beginner/intermediate/advanced/expert |
| `board_type` | varchar(20) | shortboard/longboard/funboard/fish/gun |
| `favorite_spots` | text[] | Array of favorite spot names |
| `notifications` | boolean | Email notifications on/off |
| `ai_persona` | varchar(20) | AI assistant style |
| `created_at` | timestamp | Preferences creation date |
| `updated_at` | timestamp | Last preferences update |

---

## 🐛 Troubleshooting

### Railway Build Fails: "Script start.sh not found"

The error you saw is because Railway's Railpack couldn't find the start script. This is fixed by:

1. **Dockerfile is configured** ✅ - Railway will use this
2. **Dockerfile now uses PORT env var** ✅ - Fixed in latest commit
3. **Railway should redeploy automatically** - Watch the dashboard

If it still fails:
1. Go to Railway dashboard → Your service
2. Click **Settings** → **Build & Deploy**
3. Ensure **Builder** is set to `Dockerfile`
4. **Root Directory** should be `/` (not `/backend`)

### Frontend: "Missing Supabase environment variables"

- Add the env vars to Vercel (see Step 4 above)
- Redeploy on Vercel

### Backend: "Supabase client not initialized"

- Add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` to Railway (see Step 5)
- Check Railway logs for errors

### Profile fetch fails: "No auth token"

- Make sure you're logged in
- Try signing out and back in
- Check browser console for errors

### Username already taken (but it's yours)

- This is normal! The system prevents duplicate usernames
- If it's YOUR username, it will let you keep it (doesn't show error)

---

## 🎉 Success Checklist

- [ ] Supabase project created
- [ ] SQL migration ran successfully
- [ ] `user_profiles` and `user_preferences` tables exist
- [ ] Environment variables added to Vercel
- [ ] Environment variables added to Railway
- [ ] Frontend redeployed on Vercel
- [ ] Backend redeployed on Railway
- [ ] Can view account page
- [ ] Can edit profile and save
- [ ] Username availability check works
- [ ] Preferences persist after logout/login
- [ ] Admin account (`rbradshaw@gmail.com`) works

---

## 📝 Next Steps

With profiles working, you can now:

1. **Personalize AI responses** based on skill level and AI persona
2. **Save favorite spots** in the preferences
3. **Send email notifications** for optimal conditions
4. **Track sessions** (future feature)
5. **Leaderboards** by home spot (future feature)

---

## 🆘 Need Help?

If something isn't working:

1. Check Railway logs (dashboard → service → Deployments → View logs)
2. Check Vercel logs (dashboard → project → Deployments → click deployment → View Function Logs)
3. Check browser console (F12 → Console tab)
4. Check Supabase logs (dashboard → Logs & Analytics)

Common issues:
- **Missing env vars** → Add them in Vercel/Railway
- **SQL migration errors** → Check you copied the entire file
- **Build failures** → Check Dockerfile syntax, Railway builder settings
- **Auth errors** → Verify JWT_SECRET matches between frontend and backend
