# 🎨 SwellSense Frontend Roadmap
**Last Updated**: October 15, 2025  
**Status**: Foundation Complete, Polish Phase Next

---

## 📊 Current State

### ✅ **What's Working**
- Clean Apple-style UI with Tailwind CSS
- Responsive layouts (mobile, tablet, desktop)
- Live forecast data from backend API
- Basic loading states (skeletons)
- Navigation between pages (/, /forecast, /ai)
- Environment variable configuration (NEXT_PUBLIC_API_URL)

### ⚠️ **What Needs Work**
- No data visualizations (charts missing)
- AI chat is placeholder only
- No error boundaries
- Limited API integration (only forecast.tsx)
- No map for buoy locations
- Missing 24-hour forecast trends
- No tide predictions chart

---

## 🚀 Phase 1: Core Visualizations (Week 1)

### 1. Wave Height Chart Component
**Priority**: 🔴 Critical  
**File**: `components/charts/WaveHeightChart.tsx`

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { format } from 'date-fns'

interface WaveDataPoint {
  timestamp: string
  waveHeight: number
  windSpeed: number
}

export default function WaveHeightChart({ data }: { data: WaveDataPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="timestamp" 
          tickFormatter={(time) => format(new Date(time), 'ha')}
          stroke="#6b7280"
        />
        <YAxis 
          label={{ value: 'Wave Height (ft)', angle: -90, position: 'insideLeft' }}
          stroke="#6b7280"
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'white', 
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem'
          }}
          labelFormatter={(time) => format(new Date(time), 'MMM d, ha')}
        />
        <Line 
          type="monotone" 
          dataKey="waveHeight" 
          stroke="#0ea5e9" 
          strokeWidth={2}
          dot={{ fill: '#0ea5e9', r: 3 }}
          name="Wave Height"
        />
        <Line 
          type="monotone" 
          dataKey="windSpeed" 
          stroke="#06b6d4" 
          strokeWidth={2}
          dot={{ fill: '#06b6d4', r: 3 }}
          name="Wind Speed"
          yAxisId="right"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

**Integration**: Add to `/forecast` page below current conditions

---

### 2. Tide Prediction Chart
**Priority**: 🔴 Critical  
**File**: `components/charts/TideChart.tsx`

```tsx
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { format } from 'date-fns'

interface TideDataPoint {
  timestamp: string
  height: number
  type?: 'high' | 'low'
}

export default function TideChart({ data }: { data: TideDataPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="tideGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1}/>
          </linearGradient>
        </defs>
        <XAxis 
          dataKey="timestamp" 
          tickFormatter={(time) => format(new Date(time), 'ha')}
        />
        <YAxis label={{ value: 'Tide Height (ft)', angle: -90, position: 'insideLeft' }} />
        <Tooltip 
          labelFormatter={(time) => format(new Date(time), 'MMM d, h:mm a')}
          formatter={(value: number) => [`${value.toFixed(1)} ft`, 'Tide Height']}
        />
        <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
        <Area 
          type="monotone" 
          dataKey="height" 
          stroke="#06b6d4" 
          strokeWidth={2}
          fill="url(#tideGradient)" 
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
```

**Integration**: Add dedicated "Tides" section on `/forecast` page

---

### 3. Wind Direction Compass
**Priority**: 🟡 Medium  
**File**: `components/charts/WindCompass.tsx`

```tsx
interface WindCompassProps {
  direction: number  // 0-360 degrees
  speed: number      // m/s or mph
  unit?: 'mph' | 'ms' | 'kts'
}

export default function WindCompass({ direction, speed, unit = 'mph' }: WindCompassProps) {
  const isOffshore = (direction >= 45 && direction <= 135) || (direction >= 225 && direction <= 315)
  const compassColor = isOffshore ? 'text-green-600' : 'text-blue-600'
  
  return (
    <div className="relative w-32 h-32">
      {/* Compass circle */}
      <svg className="w-full h-full" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="2" />
        
        {/* Cardinal directions */}
        <text x="50" y="15" textAnchor="middle" className="text-xs fill-gray-600">N</text>
        <text x="85" y="52" textAnchor="middle" className="text-xs fill-gray-600">E</text>
        <text x="50" y="90" textAnchor="middle" className="text-xs fill-gray-600">S</text>
        <text x="15" y="52" textAnchor="middle" className="text-xs fill-gray-600">W</text>
        
        {/* Wind arrow */}
        <g transform={`rotate(${direction} 50 50)`}>
          <polygon 
            points="50,20 55,40 50,35 45,40" 
            className={compassColor}
            fill="currentColor"
          />
          <line x1="50" y1="40" x2="50" y2="70" stroke="currentColor" strokeWidth="2" />
        </g>
      </svg>
      
      {/* Speed display */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span className={`text-2xl font-bold ${compassColor}`}>
          {speed.toFixed(1)}
        </span>
        <span className="text-xs text-gray-500">{unit}</span>
      </div>
    </div>
  )
}
```

**Integration**: Add to current conditions card on `/forecast`

---

## 🗺️ Phase 2: Interactive Features (Week 2)

### 4. Buoy Location Map
**Priority**: 🟡 Medium  
**Technology**: Mapbox GL JS or React-Leaflet

```bash
npm install react-leaflet leaflet
npm install --save-dev @types/leaflet
```

**File**: `components/maps/BuoyMap.tsx`

```tsx
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

interface Buoy {
  id: string
  name: string
  lat: number
  lon: number
  waveHeight?: number
  status: 'active' | 'inactive'
}

export default function BuoyMap({ buoys, onBuoyClick }: { 
  buoys: Buoy[], 
  onBuoyClick: (buoy: Buoy) => void 
}) {
  return (
    <MapContainer 
      center={[33.0, -118.0]} 
      zoom={6} 
      className="h-96 rounded-lg border border-gray-200"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {buoys.map(buoy => (
        <Marker 
          key={buoy.id} 
          position={[buoy.lat, buoy.lon]}
          eventHandlers={{
            click: () => onBuoyClick(buoy)
          }}
        >
          <Popup>
            <div className="text-sm">
              <h3 className="font-semibold">{buoy.name}</h3>
              <p className="text-gray-600">Buoy {buoy.id}</p>
              {buoy.waveHeight && (
                <p className="text-blue-600 font-medium">
                  {buoy.waveHeight.toFixed(1)} ft waves
                </p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
```

**Integration**: Create new `/map` page or embed in `/forecast`

---

### 5. Location Search & Autocomplete
**Priority**: 🟡 Medium  
**Technology**: Google Places API or Mapbox Geocoding

```tsx
import { useState } from 'react'
import { MapPin, Search } from 'lucide-react'

export default function LocationSearch({ onLocationSelect }: {
  onLocationSelect: (lat: number, lon: number, name: string) => void
}) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  
  const handleSearch = async (searchQuery: string) => {
    // Call geocoding API
    const response = await fetch(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${searchQuery}.json?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`
    )
    const data = await response.json()
    setResults(data.features)
  }
  
  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            if (e.target.value.length > 2) handleSearch(e.target.value)
          }}
          placeholder="Search surf breaks, beaches, buoys..."
          className="input-field pl-10"
        />
      </div>
      
      {results.length > 0 && (
        <div className="absolute top-full mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 z-10">
          {results.map((result) => (
            <button
              key={result.id}
              onClick={() => {
                const [lon, lat] = result.center
                onLocationSelect(lat, lon, result.place_name)
                setResults([])
                setQuery('')
              }}
              className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-gray-900">{result.place_name}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## 🤖 Phase 3: AI Chat Integration (Week 3)

### 6. Functional AI Chat
**Priority**: 🔴 Critical  
**File**: Update `components/ui/ChatBox.tsx`

```tsx
import { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { api, AIQueryResponse } from '@/lib/api'
import toast from 'react-hot-toast'

export default function ChatBox() {
  const [messages, setMessages] = useState<{role: 'user' | 'ai', text: string}[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return
    
    const userMessage = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMessage }])
    setLoading(true)
    
    try {
      const response = await api.queryAI({ 
        query: userMessage,
        skill_level: 'intermediate'  // Get from user profile later
      })
      
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: response.recommendation 
      }])
    } catch (error) {
      toast.error('Failed to get AI response. Please try again.')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="card h-[600px] flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-blue-400" />
            <p>Ask me anything about surf conditions!</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Input */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about surf conditions..."
          disabled={loading}
          className="input-field pr-12"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  )
}
```

---

## 🎯 Phase 4: Polish & UX (Week 4)

### 7. Error Boundaries
**File**: `components/ErrorBoundary.tsx`

```tsx
import { Component, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }
  
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
  }
  
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      
      return (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">Something went wrong</h3>
              <p className="text-sm text-red-700 mt-1">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 btn-primary bg-red-600 hover:bg-red-700"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      )
    }
    
    return this.props.children
  }
}
```

**Integration**: Wrap pages in `_app.tsx`

---

### 8. Toast Notifications
**Already added**: `react-hot-toast` in dependencies

**File**: `pages/_app.tsx`

```tsx
import { Toaster } from 'react-hot-toast'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#1f2937',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  )
}
```

---

### 9. React Query for Data Fetching
**Already added**: `@tanstack/react-query` in dependencies

**File**: `pages/_app.tsx`

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

function MyApp({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  }))
  
  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
      <Toaster />
    </QueryClientProvider>
  )
}
```

**Usage in pages**:
```tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

function ForecastPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['forecast', lat, lon],
    queryFn: () => api.fetchGlobalForecast(lat, lon),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  })
  
  if (isLoading) return <LoadingSkeleton />
  if (error) return <ErrorMessage error={error} />
  
  return <ForecastCard data={data} />
}
```

---

## 📅 Implementation Timeline

### Week 1: Core Visualizations
- [ ] Install recharts, date-fns
- [ ] Create WaveHeightChart component
- [ ] Create TideChart component
- [ ] Create WindCompass component
- [ ] Integrate charts into /forecast page

### Week 2: Interactive Features
- [ ] Install react-leaflet
- [ ] Create BuoyMap component
- [ ] Create LocationSearch component
- [ ] Add /map page or embed in /forecast
- [ ] Fetch buoy locations from backend

### Week 3: AI Chat Integration
- [ ] Update ChatBox component
- [ ] Connect to /api/ai/query endpoint
- [ ] Add message history
- [ ] Add suggested questions
- [ ] Add typing indicators

### Week 4: Polish & UX
- [ ] Add ErrorBoundary components
- [ ] Integrate react-hot-toast
- [ ] Set up React Query
- [ ] Add loading skeletons everywhere
- [ ] Add retry mechanisms
- [ ] Test offline behavior

---

## 🎨 Design System Enhancements

### Color Palette
```css
/* Primary */
--blue-600: #2563eb;
--cyan-500: #06b6d4;
--cyan-600: #0891b2;

/* Semantic */
--success: #10b981;  /* Good surf conditions */
--warning: #f59e0b;  /* Moderate conditions */
--danger: #ef4444;   /* Unsafe conditions */

/* Neutrals */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-600: #4b5563;
--gray-900: #111827;
```

### Typography
```css
/* Headings */
h1: text-4xl font-bold (36px)
h2: text-2xl font-semibold (24px)
h3: text-lg font-semibold (18px)

/* Body */
body: text-base (16px)
small: text-sm (14px)
tiny: text-xs (12px)
```

### Spacing
```css
/* Card padding */
card: p-6 (24px)

/* Section spacing */
section: mb-12 (48px)

/* Component gaps */
gap: space-y-4 or gap-4 (16px)
```

---

## 🚀 Future Enhancements (Backlog)

### Advanced Features
- [ ] **Spot Ratings** - 1-10 star system for surf quality
- [ ] **Skill Recommendations** - Beginner/Intermediate/Advanced tags
- [ ] **Photo Gallery** - User-submitted surf photos
- [ ] **Session Logging** - Track your surf sessions
- [ ] **Forecasts Comparison** - Compare multiple locations
- [ ] **Push Notifications** - Alert when conditions are good
- [ ] **Offshore/Onshore Indicators** - Wind direction relative to beach
- [ ] **Swell Direction Arrows** - Visual swell direction on map
- [ ] **Best Time to Surf** - AI-predicted optimal window
- [ ] **Crowd Prediction** - How busy will the break be?

### Performance
- [ ] **Service Worker** - Offline functionality
- [ ] **Image Optimization** - Next.js Image component
- [ ] **Code Splitting** - Dynamic imports for charts
- [ ] **CDN Assets** - Host static assets on Vercel CDN

### Analytics
- [ ] **Plausible Analytics** - Privacy-friendly tracking
- [ ] **Error Tracking** - Sentry integration
- [ ] **Performance Monitoring** - Vercel Analytics

---

## 📊 Success Metrics

### User Experience
- Page load time < 2s
- Time to interactive < 3s
- Lighthouse score > 90
- Zero blocking errors

### Functionality
- All 9 data sources showing in forecast
- Charts render without lag
- AI chat responds in < 5s
- Map loads in < 2s

### Design
- Consistent spacing and colors
- Responsive on all devices (mobile, tablet, desktop)
- Accessible (WCAG AA compliant)
- Smooth animations and transitions

---

**Roadmap Status**: 🟡 In Progress  
**Next Milestone**: Week 1 - Core Visualizations  
**Target Completion**: 4 weeks from October 15, 2025
