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