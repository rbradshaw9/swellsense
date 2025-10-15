# SwellSense 🌊

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/rbradshaw9/swellsense)
[![Deploy Status](https://img.shields.io/badge/deploy-vercel-blue)](https://swellsense.vercel.app)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/next.js-15.5-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.9-blue.svg)](https://www.typescriptlang.org/)

An AI-powered surf forecasting and assistant app that analyzes real-time data from buoys, tides, and wind patterns to predict optimal surf conditions for surfers worldwide.

## Overview

SwellSense leverages advanced machine learning algorithms and comprehensive oceanographic data to provide accurate surf forecasting and personalized recommendations. By analyzing data from NOAA buoys, tide stations, and meteorological services, SwellSense delivers precise surf predictions tailored to your skill level and preferred surf spots.

Whether you're a beginner looking for gentle waves or an experienced surfer seeking the perfect barrel, SwellSense helps you make informed decisions about when and where to surf.

## Quick Start

Get SwellSense running locally in 2 minutes:

```bash
# 1. Start the backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload

# 2. Start the frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access your app:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features

### 🎯 Core Features
- **Real-time Surf Forecasting**: 7-day detailed surf predictions with wave height, period, and direction
- **AI-Powered Recommendations**: Personalized surf spot suggestions based on your skill level and preferences
- **Multi-Source Data Integration**: Combines buoy data, tide information, wind patterns, and weather conditions
- **Interactive Maps**: Visual representation of surf conditions across different locations
- **Spot Ratings**: AI-generated surf quality scores from 1-10 for each location

### 📱 Smart Features
- **Push Notifications**: Alerts for optimal surf conditions at your favorite spots
- **Session Tracking**: Log your surf sessions and track improvements
- **Community Insights**: Share and discover surf reports from local surfers
- **Offline Mode**: Access forecasts and maps without internet connectivity
- **Weather Integration**: Comprehensive weather data including UV index and storm tracking

### 🤖 AI Assistant
- **Natural Language Queries**: Ask questions like "Where's the best surf this weekend?"
- **Condition Analysis**: Detailed explanations of why conditions are favorable or not
- **Skill-Based Recommendations**: Suggestions tailored to beginner, intermediate, or advanced surfers
- **Safety Alerts**: Warnings about dangerous conditions, strong currents, or severe weather

## Tech Stack

### Backend
- **Python 3.9+** - Core application logic
- **FastAPI** - REST API framework
- **PostgreSQL** - Primary database (Neon or Supabase)
- **Redis** - Caching and real-time data storage
- **Celery** - Background task processing for data collection
- **TensorFlow/Scikit-learn** - Machine learning models for surf prediction

### Frontend
- **Next.js 14** - React framework with TypeScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Axios** - HTTP client for API communication

### Data Sources & APIs
- **NOAA Buoy Data** - Real-time wave and weather measurements
- **NOAA Tides & Currents** - Tide predictions and water levels
- **OpenWeatherMap** - Weather forecasting and wind data
- **Surfline API** - Additional surf condition data

### ML/AI Architecture
- **Model Training**: Machine learning models will be developed in `/backend/ai/`
- **OpenAI Integration**: GPT-4 for natural language surf recommendations
- **TensorFlow/Scikit-learn**: Predictive models for wave forecasting
- **Future**: Custom neural networks for surf quality prediction

### Hosting & Infrastructure
- **Vercel** - Frontend hosting and API routes
- **Neon/Supabase** - PostgreSQL database hosting
- **GitHub Actions** - CI/CD pipeline

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Node.js 18+ and npm/yarn
- PostgreSQL database (Neon or Supabase account)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rbradshaw9/swellsense.git
   cd swellsense
   ```

2. **Set up backend environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and API keys
   ```

4. **Start the backend server**
   ```bash
   # Development mode with auto-reload
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Or run directly
   python main.py
   ```

   The API will be available at:
   - **API Root**: `http://localhost:8000`
   - **Interactive Docs (Swagger)**: `http://localhost:8000/docs`
   - **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`

5. **Database Connection (Neon)**
   
   SwellSense uses Neon's serverless PostgreSQL. Your `DATABASE_URL` in `.env` should look like:
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
   
   The connection uses async SQLAlchemy with `asyncpg` driver for optimal performance.
   SSL is automatically handled by the asyncpg driver.

6. **Run NOAA Data Ingestion**
   
   Populate the database with real surf data:
   ```bash
   python scripts/ingest_noaa.py --buoy-id 41043
   
   # Schedule with cron (every 3 hours)
   0 */3 * * * cd /path/to/backend && python scripts/ingest_noaa.py --buoy-id 41043
   ```

### Frontend Setup

1. **Set up frontend environment**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Deployment

### Deploy to Vercel

**Important:** The current `vercel.json` configuration deploys only the **frontend** to Vercel. The backend will be deployed separately (e.g., Railway, Render, or AWS Lambda) in future versions.

1. **Deploy Frontend via GitHub Integration (Recommended)**
   - Connect your GitHub repo to Vercel
   - Vercel will automatically deploy the Next.js frontend
   - Set environment variables in Vercel dashboard

2. **Deploy via Vercel CLI**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

**Note:** The `vercel.json` includes backend configuration for future serverless deployment, but currently only the frontend builds successfully.

**Required Environment Variables in Vercel:**

Set these in your Vercel project dashboard:

**Required:**
- `DATABASE_URL` - Your Neon PostgreSQL connection string (already configured)
- `SECRET_KEY` - JWT secret key for authentication (generate one below)
- `NEXT_PUBLIC_API_URL` - Your API URL (will be auto-generated)

**Generate a SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```
Copy the output and use it as your `SECRET_KEY` in Vercel.

**Optional:**
- `NOAA_API_KEY` - NOAA data access key (for future features)
- `OPENWEATHER_API_KEY` - Weather data API key (for future features)

**Project Structure:**
- Frontend deploys from `/frontend` directory (Next.js)
- Backend currently runs separately (future: serverless functions)

### Deploy Backend to Railway

**SwellSense FastAPI backend is configured for seamless deployment on Railway.app**

Railway provides:
- Automatic deployments from GitHub
- Built-in PostgreSQL and environment variables
- Free tier with 500 hours/month
- Zero-config Python/FastAPI support

#### 1. Initial Setup

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `rbradshaw9/swellsense`
   - Railway will detect the configuration files:
     - `start.sh` - Startup script
     - `railway.json` - Build configuration
     - `Procfile` - Process definition (fallback)

3. **Configure Environment Variables**
   
   Add these in Railway dashboard (Settings → Variables):
   
   ```bash
   DATABASE_URL=postgresql://neondb_owner:npg_yLWglz7t0SiK@ep-floral-base-adkze7qi-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   OPENAI_API_KEY=sk-proj-your-key-here
   SECRET_KEY=ZtUp_q7nOio0sVnd3Hsau_zhuHiHnwWITIEJM9ci5qawq5x1ivByWfOWHNnDcngT1_w5r2Augu9YdpxTybXpNg
   PORT=8000
   ```
   
   **Note**: Railway automatically injects the `PORT` variable, but you can set it explicitly if needed.

4. **Deploy**
   - Railway will automatically:
     1. Run `pip install -r backend/requirements.txt`
     2. Execute `./start.sh` to start uvicorn
   - Your API will be live at: `https://swellsense-production.up.railway.app`

#### 2. Verify Deployment

Check Railway logs (Deployments → View Logs) for successful startup:
```
INFO:     Started server process [123]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:<port>
```

**Troubleshooting**: If you see "Script start.sh not found" error:
- Ensure `start.sh` is executable: `chmod +x start.sh`
- Verify `start.sh` is committed to git
- Check Railway logs for detailed error messages

Test the live API:
```bash
# Health check
curl https://swellsense-production.up.railway.app/

# AI query with location
curl -X POST https://swellsense-production.up.railway.app/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I surf today?", "location": "western PR"}'
```

Expected response:
```json
{
  "query": "Should I surf today?",
  "recommendation": "Great conditions for intermediate surfers...",
  "confidence": 0.85,
  "station_used": "42085",
  "region": "Western Puerto Rico"
}
```

#### 3. Redeploy

**Automatic Deployment:**
Railway auto-deploys on every push to `main`:
```bash
git add .
git commit -m "Update backend"
git push origin main
```

**Manual Deployment:**
- Via Railway Dashboard: Deployments → Click "Deploy"
- Via Railway CLI:
  ```bash
  npm install -g @railway/cli
  railway login
  railway up
  ```

**View Logs:**
```bash
# Via CLI
railway logs

# Or in Railway dashboard: Deployments → View Logs
```

#### 4. Custom Domain (Optional)

1. Go to Settings → Domains
2. Add custom domain: `api.swellsense.app`
3. Update DNS records as instructed

#### Deployment Files

- **`start.sh`**: Executable startup script for Railway
- **`railway.json`**: Build and deploy configuration
- **`Procfile`**: Process definition (fallback)
- **`backend/requirements.txt`**: Python dependencies
- **`backend/main.py`**: FastAPI application entry point

### Database Setup

**Using Neon:**
1. Create account at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy connection string to `DATABASE_URL`

**Using Supabase:**
1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy connection string to `DATABASE_URL`

## API Documentation

Once the backend is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Available Endpoints

#### Forecast Endpoints

**GET /api/forecast**
- Get recent surf conditions from the database
- Query parameters:
  - `limit` (int, default: 24): Number of records to return
  - `buoy_id` (str, optional): Filter by specific buoy station
- Returns: List of surf condition records with timestamps, wave height, period, wind speed

**GET /api/forecast/latest**
- Get the most recent surf condition reading
- Query parameters:
  - `buoy_id` (str, optional): Filter by specific buoy station
- Returns: Single most recent surf condition record

**GET /api/forecast/stats**
- Get statistical summary of surf conditions over a time period
- Query parameters:
  - `hours` (int, default: 24): Number of hours to analyze
  - `buoy_id` (str, optional): Filter by specific buoy station
- Returns: Statistics including average, min, max wave height and wind speed

#### AI Query Endpoint

**POST /api/ai/query**
- Get intelligent surf recommendations powered by OpenAI and real-time NOAA data
- **Multi-Buoy Support**: Automatically selects the best buoy based on location
- Request body:
  ```json
  {
    "query": "Should I surf today?",
    "location": "western PR",
    "skill_level": "intermediate"
  }
  ```
- Parameters:
  - `query` (string, required): Natural language question about surf conditions
  - `location` (string, optional): Location name ("western PR", "Florida", "California")
  - `latitude` (float, optional): Latitude coordinate for nearest buoy
  - `longitude` (float, optional): Longitude coordinate for nearest buoy
  - `skill_level` (string, optional): "beginner", "intermediate", or "advanced" (default: "intermediate")
- Returns:
  ```json
  {
    "query": "Where should I surf right now?",
    "recommendation": "Head to Jobos Beach or Playa Punta Higuero...",
    "confidence": 0.75,
    "explanation": "The current wave height of 2.0ft is suitable for intermediate surfers...",
    "data_timestamp": "2025-10-15T16:00:00",
    "station_used": "42085",
    "region": "Western Puerto Rico"
  }
  ```

**Example Usage:**
```bash
# Query with location string
curl -X POST http://localhost:8000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Where should I surf tomorrow?", "location": "western PR", "skill_level": "beginner"}'

# Query with coordinates (finds nearest buoy)
curl -X POST http://localhost:8000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Are conditions good right now?", "latitude": 18.4, "longitude": -67.2}'

# Query with default location
curl -X POST http://localhost:8000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I surf today?"}'
```

**Supported Regions:**
| Region | Buoy ID | Location |
|--------|---------|----------|
| Florida | 41043 | East of St. Augustine, FL |
| Western Puerto Rico | 42085 | Aguadilla |
| Puerto Rico | 42059 | Mona Passage |
| Gulf of Mexico | 42003 | East of Pensacola, FL |
| Northern California | 46023 | Point Arena, CA |
| Southern California | 46218 | Santa Barbara, CA |
| Hawaii | 51201 | Northwest Hawaii |

**Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (get it at https://platform.openai.com/api-keys)
- Required for AI-powered recommendations

**How it works:**
1. Fetches latest surf conditions from Neon database (wave height, period, wind speed)
2. Analyzes 24-hour trends and data quality
3. Builds contextual prompt with NOAA buoy data and user's skill level
4. Sends prompt to OpenAI GPT-4o-mini for intelligent analysis
5. Returns structured JSON with personalized surf recommendations

### NOAA Data Ingestion

The project includes a background script to fetch and ingest real-time buoy data from NOAA:

```bash
# Run manually
cd backend
python scripts/ingest_noaa.py --buoy-id 41043

# Schedule with cron (every 3 hours)
0 */3 * * * cd /path/to/swellsense/backend && python scripts/ingest_noaa.py --buoy-id 41043
```

**Environment Variables:**
- `NOAA_BUOY_ID`: Default buoy station (e.g., 41043 for East of St. Augustine, FL)
- Find your buoy at: https://www.ndbc.noaa.gov/

**How it works:**
1. Fetches real-time data from NOAA NDBC in text format
2. Parses wave height, wave period, wind speed measurements
3. Inserts new records into the surf_conditions table
4. Automatically skips duplicates to avoid redundant data

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_forecast.py
```

### Frontend Tests
```bash
# Run React Native tests
npm test

# Run with coverage
npm test -- --coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## Next Steps: v0.2 Milestone

The next major update will focus on **real surf data and AI recommendations**:

🌊 **NOAA Data Ingestion**
- Connect to NOAA buoy network for live wave data
- Parse and store wave height, period, and direction
- Historical data analysis for trend predictions

🤖 **AI Surf Advisor** 
- Integrate OpenAI for intelligent surf recommendations
- Natural language explanations: "Why are conditions good?"
- Personalized advice based on surfer skill level

📊 **Smart Forecasting**
- Combine buoy data with tide predictions
- Generate actionable surf quality scores
- "Best time to surf today" recommendations

## Roadmap

### v0.1: Foundation ✅ (October 2025)
- [x] Project structure and landing page
- [x] FastAPI backend with CORS
- [x] Next.js frontend with Tailwind CSS
- [x] Vercel deployment configuration
- [x] Environment setup and documentation

### v0.2: Core Data & AI 🚧 (In Progress - November 2025)
- [x] **NOAA Buoy Data Integration**
  - ✅ Real-time wave height, period, direction from NDBC
  - ✅ Automated data ingestion script
  - ✅ PostgreSQL storage with SQLAlchemy
  - [ ] Historical data analysis
  - [ ] Multiple buoy station support
- [x] **Forecast API Endpoints**
  - ✅ `/api/forecast` - Recent surf conditions
  - ✅ `/api/forecast/latest` - Most recent reading
  - ✅ `/api/forecast/stats` - Statistical summaries
- [x] **Frontend Forecast Display**
  - ✅ ForecastCard component with ocean-themed UI
  - ✅ Real-time data fetching
  - ✅ Wave height, period, wind speed display
  - ✅ Surf quality indicator
- [ ] **AI Surf Advisor** (Next Phase)
  - [ ] OpenAI integration for surf recommendations
  - [ ] Natural language surf condition explanations
  - [ ] Personalized advice based on skill level
  - ✅ Placeholder UI component added

### v0.3: Enhanced Features (Q1 2026)
- [ ] User authentication and profiles
- [ ] Favorite surf spots
- [ ] Push notifications for optimal conditions
- [ ] Advanced machine learning models

### Phase 3: AI Assistant (Q2 2026)
- [ ] Natural language processing
- [ ] Conversational AI interface
- [ ] Advanced personalization
- [ ] Predictive analytics
- [ ] Safety alert system

### Phase 4: Platform Expansion (Q3 2026)
- [ ] Mobile app (React Native)
- [ ] Desktop app
- [ ] API for third-party developers
- [ ] International expansion
- [ ] Premium subscription features

### Future Enhancements
- [ ] Apple Watch / WearOS integration
- [ ] Augmented reality surf condition overlay
- [ ] Integration with surf gear and wetsuit recommendations
- [ ] Social features and surf buddy matching
- [ ] Surf coaching and technique analysis using computer vision

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NOAA** for providing comprehensive oceanographic data
- **OpenWeatherMap** for weather forecasting services
- The surfing community for inspiration and feedback
- Contributors and beta testers

## Support

- 📧 Email: support@swellsense.app
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/swellsense/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/swellsense/discussions)
- 🌐 Website: [swellsense.app](https://swellsense.app)

---

**Made with 🏄‍♂️ by surfers, for surfers**