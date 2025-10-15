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