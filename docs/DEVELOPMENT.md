# SwellSense - Development Setup

Welcome to SwellSense development! This guide will help you get the project running locally.

## Quick Start

1. **Clone and setup backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your database URL
   python main.py
   ```

2. **Setup frontend (in new terminal):**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local if needed
   npm run dev
   ```

3. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Database Setup

### Neon Database (Already Configured)
Your Neon database is already set up! The connection string is in the `.env.example` files.
Just copy `backend/.env.example` to `backend/.env` to use it.

### Option 2: Supabase
1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project
3. Copy connection string to `DATABASE_URL` in backend/.env

### Option 3: Local PostgreSQL
1. Install PostgreSQL locally
2. Create database: `createdb swellsense_db`
3. Use: `DATABASE_URL=postgresql://username:password@localhost:5432/swellsense_db`

## Environment Variables

Copy the main `.env.example` to get started, then copy specific values to:
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration

**Generate a new SECRET_KEY (recommended for production):**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```
Replace the SECRET_KEY in your `.env` files with the generated value.

## Development Commands

**Backend:**
```bash
cd backend
python main.py              # Start dev server
pip install -r requirements.txt  # Install dependencies
```

**Frontend:**
```bash
cd frontend
npm run dev                 # Start dev server
npm run build              # Build for production
npm run lint               # Run linting
npm install                # Install dependencies
```

## Next Steps

Once you have the basic setup running:

1. **Add NOAA data integration** - We'll add endpoints to fetch real buoy data
2. **Implement AI chat assistant** - Add OpenAI integration for surf advice
3. **Add user authentication** - Set up user accounts and preferences
4. **Deploy to production** - Use Vercel for hosting

## Troubleshooting

**Backend won't start:**
- Check Python version (3.9+)
- Ensure virtual environment is activated
- Verify DATABASE_URL in .env

**Frontend won't start:**
- Check Node.js version (18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for port conflicts (default: 3000)

**Database connection issues:**
- Verify database URL format
- Check network connectivity
- Ensure database exists and credentials are correct

## Production Deployment

### Backend Deployment (Railway)

SwellSense backend is configured for seamless deployment on Railway.app.

**1. Setup Railway Project**

```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project (if already created on dashboard)
railway link
```

**2. Deploy from GitHub (Recommended)**

1. Go to [railway.app](https://railway.app) and create account
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `rbradshaw9/swellsense`
4. Railway auto-detects `railway.json` configuration

**3. Configure Environment Variables**

Add in Railway dashboard (Settings → Variables):

```bash
DATABASE_URL=postgresql://neondb_owner:npg_yLWglz7t0SiK@ep-floral-base-adkze7qi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
OPENAI_API_KEY=sk-proj-your-openai-key-here
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ENVIRONMENT=production
```

**4. Deployment Configuration**

Railway uses these files:
- `railway.json` - Build and deploy commands
- `Procfile` - Process definition (fallback)
- `backend/requirements.txt` - Python dependencies

**5. Verify Deployment**

Check logs in Railway dashboard:
```
INFO:     Started server process [123]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:$PORT
```

Test live API:
```bash
curl -X POST https://swellsense-production.up.railway.app/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I surf today?", "location": "western PR"}'
```

**6. Auto-Deployment**

Railway auto-deploys on every push to `main`:
```bash
git add .
git commit -m "Update backend"
git push origin main
```

**7. Manual Redeploy**

Via Railway CLI:
```bash
railway up
```

Via Dashboard:
- Go to Deployments → Click "Deploy"

**8. View Logs**

```bash
railway logs
```

Or view in Railway dashboard under Deployments → Logs

**9. Custom Domain**

1. Settings → Domains
2. Add custom domain: `api.swellsense.app`
3. Update DNS with provided records

### Frontend Deployment (Vercel)

Frontend deploys automatically to Vercel from `main` branch.

**Environment Variables (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://swellsense-production.up.railway.app
DATABASE_URL=<same-as-railway>
```

### Monitoring

**Railway Dashboard:**
- View metrics, logs, and deployment history
- Set up alerts for errors or downtime

**Health Check Endpoint:**
```bash
curl https://swellsense-production.up.railway.app/
# Returns: {"message": "Welcome to SwellSense API", "status": "operational"}
```