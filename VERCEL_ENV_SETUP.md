# 🚀 Vercel Environment Variables Setup

## Required for SwellSense Frontend Deployment

You need to add these environment variables in your **Vercel Dashboard**:

### 📍 How to Add Variables in Vercel:

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your **swellsense** project
3. Click **Settings** → **Environment Variables**
4. Add each variable below

---

## 🔐 Required Variables

### 1. Supabase URL
```
Name: NEXT_PUBLIC_SUPABASE_URL
Value: https://your-project.supabase.co
```
**Get it from**: Supabase Dashboard → Project Settings → API → Project URL

---

### 2. Supabase Anon Key
```
Name: NEXT_PUBLIC_SUPABASE_ANON_KEY  
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Get it from**: Supabase Dashboard → Project Settings → API → anon/public key

---

### 3. Backend API URL (Optional - for production)
```
Name: NEXT_PUBLIC_API_URL
Value: https://your-railway-backend.railway.app
```
**Note**: If not set, frontend will try to use localhost (dev mode)

---

## ⚙️ Steps to Get Supabase Credentials

### If you don't have a Supabase project yet:

1. **Go to [supabase.com](https://supabase.com)** and sign in
2. Click **"New Project"**
3. Fill in:
   - **Name**: SwellSense
   - **Database Password**: (save this somewhere safe)
   - **Region**: Choose closest to your users
4. Wait ~2 minutes for provisioning

### Get the credentials:

5. Go to **Settings** (⚙️ icon in sidebar)
6. Click **API** in the left menu
7. Copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **JWT Secret** → (needed for Railway backend - see below)

---

## 🔧 After Adding Variables in Vercel

1. Click **Save** for each variable
2. Go to **Deployments** tab
3. Click **⋯** on the latest deployment → **Redeploy**
4. ✅ Build should succeed now!

---

## 🗄️ Next: Run Database Migration

After environment variables are set, you need to create the database tables:

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Click **"New Query"**
3. Copy and paste the contents of `supabase_migration_profiles.sql`
4. Click **Run** (or press `Cmd/Ctrl + Enter`)
5. ✅ Tables created: `user_profiles`, `user_preferences`

---

## 🚂 Railway Backend Variables (Separate from Vercel)

These go in **Railway** dashboard for the backend:

```bash
SUPABASE_JWT_SECRET=your-jwt-secret-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key (⚠️ keep secret!)
```

**Get JWT Secret from**: Supabase → Settings → API → JWT Settings → JWT Secret  
**Get Service Key from**: Supabase → Settings → API → service_role key

---

## 📋 Quick Checklist

- [ ] Created Supabase project
- [ ] Added `NEXT_PUBLIC_SUPABASE_URL` to Vercel
- [ ] Added `NEXT_PUBLIC_SUPABASE_ANON_KEY` to Vercel
- [ ] Redeployed on Vercel
- [ ] Ran `supabase_migration_profiles.sql` in Supabase SQL Editor
- [ ] Added `SUPABASE_JWT_SECRET` to Railway backend
- [ ] Added `SUPABASE_URL` to Railway backend
- [ ] Added `SUPABASE_SERVICE_KEY` to Railway backend

---

## ❓ Troubleshooting

### Build still fails with "Missing Supabase environment variables"
- Make sure you saved the variables in Vercel
- Try redeploying (not just rebuilding)
- Check variable names are EXACT (case-sensitive)

### "Invalid API key" error
- Double-check you copied the **anon/public** key (not service_role)
- Make sure there's no extra whitespace

### Database queries fail
- Run the SQL migration in Supabase
- Check Row Level Security (RLS) policies are created
- Verify backend has JWT_SECRET set correctly
