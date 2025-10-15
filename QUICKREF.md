# SwellSense Quick Reference

## Project Structure Quick View

```
swellsense/
├── backend/                    # FastAPI Python backend
│   ├── main.py                # App entry point, CORS, lifespan
│   ├── database.py            # SQLAlchemy models & async engine
│   ├── routers/
│   │   └── forecast.py        # /api/forecast endpoints
│   └── scripts/
│       └── ingest_noaa.py     # NOAA buoy data fetcher
├── frontend/                   # Next.js React frontend
│   ├── pages/
│   │   ├── _app.tsx           # App wrapper, fonts, meta
│   │   └── index.tsx          # Landing page with forecast
│   ├── components/
│   │   ├── ForecastCard.tsx   # Surf condition display
│   │   └── AIChat.tsx         # AI chat placeholder
│   └── styles/
│       └── globals.css        # Tailwind + custom styles
├── docs/
│   ├── DEVELOPMENT.md         # Dev setup guide
│   └── DEPLOYMENT_STATUS.md   # Deployment reference
└── shared/                     # Shared constants & types
    ├── constants.py           # Python constants
    └── types.ts               # TypeScript interfaces
```

## Key Files & Their Purpose

### Backend

**`backend/main.py`**
- FastAPI app initialization
- CORS middleware configuration
- Router registration (forecast)
- Lifespan event (database init)
- Welcome, health, and info endpoints

**`backend/database.py`**
- Async SQLAlchemy engine setup
- SurfCondition model definition
- Database session management
- `get_db()` dependency for routes
- `init_db()` table creation

**`backend/routers/forecast.py`**
- GET `/api/forecast` - List recent conditions
- GET `/api/forecast/latest` - Most recent reading
- GET `/api/forecast/stats` - Statistical analysis
- Error handling and data serialization

**`backend/scripts/ingest_noaa.py`**
- Fetches NOAA NDBC buoy data
- Parses space-delimited text format
- Inserts into PostgreSQL via SQLAlchemy
- Duplicate detection
- CLI with --buoy-id argument

### Frontend

**`frontend/pages/index.tsx`**
- Landing page with hero section
- Email signup form
- ForecastCard integration
- AIChat placeholder
- useEffect for data fetching
- Auto-refresh every 5 minutes

**`frontend/components/ForecastCard.tsx`**
- Props: `data` (SurfCondition), `loading` (boolean)
- Loading skeleton animation
- Empty state with friendly message
- Wave height (ft), period (s), wind (mph)
- Surf quality indicator (Good/Fair/Poor)
- Ocean-themed gradient design

**`frontend/components/AIChat.tsx`**
- "Coming Soon" placeholder
- Example questions preview
- Disabled input field
- Future v0.3 implementation notes

## Common Commands

### Development

```bash
# Backend
cd backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev

# Run ingestion
cd backend
python scripts/ingest_noaa.py --buoy-id 41043
```

### Database

```bash
# Test connection
cd backend
python -c "from database import engine; import asyncio; asyncio.run(engine.dispose())"

# Initialize tables
cd backend
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

### Build & Deploy

```bash
# Frontend build
cd frontend
npm run build

# Frontend type check
npm run type-check

# Frontend lint
npm run lint
```

## API Quick Reference

### Base URL
- Local: `http://localhost:8000`
- Production: `https://api.swellsense.app` (future)

### Endpoints

| Method | Path | Description | Query Params |
|--------|------|-------------|--------------|
| GET | `/` | Welcome message | - |
| GET | `/health` | Health check | - |
| GET | `/api/info` | API information | - |
| GET | `/api/forecast` | Recent conditions | `limit`, `buoy_id` |
| GET | `/api/forecast/latest` | Most recent | `buoy_id` |
| GET | `/api/forecast/stats` | Statistics | `hours`, `buoy_id` |

### Response Format

All API responses follow this structure:

```typescript
{
  status: "success" | "error",
  data?: any,
  message?: string,
  count?: number
}
```

## Database Schema Reference

### surf_conditions Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | No | Primary key |
| timestamp | TIMESTAMP | No | Reading timestamp (UTC) |
| wave_height | FLOAT | Yes | Wave height in meters |
| wave_period | FLOAT | Yes | Wave period in seconds |
| wind_speed | FLOAT | Yes | Wind speed in m/s |
| tide_level | FLOAT | Yes | Tide level in meters |
| buoy_id | VARCHAR(10) | Yes | NOAA station ID |
| created_at | TIMESTAMP | No | Record insertion time |

**Indexes:**
- `idx_timestamp` on `timestamp` (DESC)
- `idx_buoy_id` on `buoy_id`

## Environment Variables

### Backend (.env)

```bash
# Required
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your_64_char_secret

# Optional
NOAA_BUOY_ID=41043
NOAA_API_KEY=your_key
OPENWEATHER_API_KEY=your_key
DEBUG=True
ENVIRONMENT=development
```

### Frontend (.env.local)

```bash
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_GA_ID=your_ga_id
NEXT_PUBLIC_MAPBOX_TOKEN=your_token
```

## TypeScript Types

### SurfCondition Interface

```typescript
interface SurfCondition {
  id: number;
  timestamp: string;
  wave_height: number | null;
  wave_period: number | null;
  wind_speed: number | null;
  tide_level: number | null;
  buoy_id: string | null;
  created_at?: string;
}
```

## Styling Classes (Tailwind)

### Custom Components

```css
.btn-primary          /* Blue primary button */
.btn-secondary        /* White secondary button */
.input-field          /* Standard input field */
.card                 /* White card with shadow */
.gradient-ocean       /* Blue ocean gradient */
```

### Ocean Theme Colors

```css
--color-brand-primary: #0ea5e9    /* Sky blue */
--color-brand-secondary: #06b6d4   /* Cyan */
```

## NOAA Buoy Data Format

### Text Format (space-delimited)

```
#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS  TIDE
2025 10 15 14 50  220  8.5 10.2  2.10  10.0   7.5 210 1013.2  18.5  20.1  15.0   MM    MM
```

### Parsed Fields

- **WVHT**: Wave height (meters) → Index 8
- **DPD**: Dominant wave period (seconds) → Index 9
- **WSPD**: Wind speed (m/s) → Index 6
- **MM**: Missing/No data

## Troubleshooting

### Backend won't start
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Verify asyncpg installed
pip install asyncpg greenlet

# Test import
python -c "from database import engine"
```

### Frontend build fails
```bash
# Clear cache
rm -rf .next node_modules
npm install

# Check TypeScript
npm run type-check
```

### Data ingestion fails
```bash
# Check buoy ID is valid
curl https://www.ndbc.noaa.gov/data/realtime2/41043.txt

# Verify DATABASE_URL
export DATABASE_URL="postgresql://..."
python scripts/ingest_noaa.py --buoy-id 41043
```

## Git Workflow

```bash
# Standard workflow
git checkout -b feature/my-feature
git add -A
git commit -m "✨ Add amazing feature"
git push origin feature/my-feature

# Emoji conventions
🌊 NOAA/data features
🤖 AI features
✨ New features
🔧 Configuration
🐛 Bug fixes
📝 Documentation
🎨 UI/styling
⚡ Performance
🔒 Security
```

## Useful Buoy Stations

| ID | Location | Region |
|----|----------|--------|
| 41043 | East of St. Augustine, FL | Atlantic |
| 46022 | Eel River, CA | Pacific |
| 51001 | NW Hawaii | Pacific |
| 44025 | Long Island, NY | Atlantic |
| 46026 | San Francisco, CA | Pacific |

Find more: https://www.ndbc.noaa.gov/

## Performance Targets

| Metric | Current | Target v0.3 |
|--------|---------|-------------|
| API Response Time | ~50ms | <25ms |
| Frontend Load | ~2s | <1s |
| Database Query | ~10ms | <5ms |
| Lighthouse Score | 85 | 95+ |

---

**Last Updated**: October 15, 2025
**Version**: v0.2-alpha
