# SwellSense Environment Variables

This document describes all environment variables required for the SwellSense application.

## Frontend Environment Variables (Vercel / Next.js)

Add these to your Vercel project settings or `.env.local` file:

### Supabase Authentication
```bash
# Supabase Project URL
# Get from: Supabase Dashboard → Project Settings → API → Project URL
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co

# Supabase Anonymous/Public Key
# Get from: Supabase Dashboard → Project Settings → API → Project API keys → anon/public
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Configuration
```bash
# Backend API URL
# Development: http://localhost:8000
# Production: https://your-railway-app.railway.app
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Environment Variables (Railway / FastAPI)

Add these to your Railway service environment variables or `.env` file:

### Database
```bash
# PostgreSQL connection string from Neon/Railway/Supabase
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

### Supabase Authentication
```bash
# Supabase JWT Secret (for token verification)
# Get from: Supabase Dashboard → Project Settings → API → JWT Settings → JWT Secret
SUPABASE_JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters

# Supabase Project URL
SUPABASE_URL=https://your-project.supabase.co

# Supabase Service Role Key (for admin operations)
# Get from: Supabase Dashboard → Project Settings → API → service_role key
# ⚠️ NEVER expose this key in frontend code
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### OpenAI API
```bash
# OpenAI API Key for AI forecast interpretation and chat
OPENAI_API_KEY=sk-proj-...
```

### External APIs
```bash
# NOAA API key (optional - public endpoints don't require it)
NOAA_API_KEY=your-noaa-api-key

# Weather API key (if using weather services)
WEATHER_API_KEY=your-weather-api-key
```

---

## How to Get Supabase Credentials

### 1. Create a Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in project details
4. Wait for database provisioning (~2 minutes)

### 2. Get API Credentials
Navigate to: **Project Settings** → **API**

You'll find:
- **Project URL**: `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_URL`
- **anon/public key**: `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **service_role key**: `SUPABASE_SERVICE_KEY` (⚠️ Keep secret!)

### 3. Get JWT Secret
Navigate to: **Project Settings** → **API** → **JWT Settings**

Copy the **JWT Secret** value for `SUPABASE_JWT_SECRET`

---

## Environment Setup by Platform

### Local Development

**Frontend:**
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your values
npm run dev
```

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your values
uvicorn main:app --reload
```

### Vercel (Frontend)

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add each `NEXT_PUBLIC_*` variable
3. Redeploy if needed

### Railway (Backend)

1. Go to Railway Dashboard → Your Service → Variables
2. Click "New Variable"
3. Add each backend variable
4. Railway will auto-redeploy

---

## Security Best Practices

### ✅ DO:
- Use `NEXT_PUBLIC_*` prefix only for client-safe values
- Keep `SUPABASE_SERVICE_KEY` and `OPENAI_API_KEY` in backend only
- Use different Supabase projects for dev/staging/production
- Rotate JWT secrets periodically
- Enable Row Level Security (RLS) in Supabase

### ❌ DON'T:
- Commit `.env` or `.env.local` files to Git
- Expose service role keys in frontend code
- Share production credentials in team chats
- Use the same API keys across environments

---

## Verification Checklist

### Frontend Ready:
- [ ] `NEXT_PUBLIC_SUPABASE_URL` set
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` set
- [ ] `NEXT_PUBLIC_API_URL` points to backend
- [ ] Can load `/login` page without errors

### Backend Ready:
- [ ] `DATABASE_URL` connects successfully
- [ ] `SUPABASE_JWT_SECRET` matches Supabase project
- [ ] `OPENAI_API_KEY` valid and has credits
- [ ] `/docs` endpoint loads Swagger UI
- [ ] `/api/user/verify` returns 401 without token

### Authentication Working:
- [ ] Can sign up new user in Supabase
- [ ] Can log in with credentials
- [ ] Token persists across page refreshes
- [ ] Protected routes redirect to `/login`
- [ ] Backend `/api/user/profile` returns user data with valid token

---

## Troubleshooting

### "Missing Supabase environment variables"
**Frontend Error**: Check `.env.local` has both `NEXT_PUBLIC_SUPABASE_*` variables

### "Authentication not configured"
**Backend Error**: `SUPABASE_JWT_SECRET` not set or incorrect

### "Invalid authentication token"
**Backend Error**: JWT secret mismatch between frontend Supabase project and backend `SUPABASE_JWT_SECRET`

### "CORS error when calling backend"
Check `NEXT_PUBLIC_API_URL` matches where backend is running

---

## Example .env Files

### Frontend `.env.local` (Development)
```bash
NEXT_PUBLIC_SUPABASE_URL=https://abc123.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiYzEyMyIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjk5OTk5OTk5LCJleHAiOjIwMTU1NzU5OTl9.example
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend `.env` (Development)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/swellsense
SUPABASE_JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiYzEyMyIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE2OTk5OTk5OTksImV4cCI6MjAxNTU3NTk5OX0.example
OPENAI_API_KEY=sk-proj-example123
```
