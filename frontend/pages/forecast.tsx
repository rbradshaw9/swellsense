import type { NextPage } from 'next'
import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import dynamic from 'next/dynamic'
import { WavesIcon, RefreshCw, Calendar, AlertTriangle, MapPin, Navigation, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import WaveHeightChart from '../components/charts/WaveHeightChart'
import TideChart from '../components/charts/TideChart'
import WindCompass from '../components/charts/WindCompass'
import DataCard from '../components/charts/DataCard'
import ErrorBoundary from '../components/ErrorBoundary'

// Dynamic import for MapPR (client-side only due to Leaflet)
const MapPR = dynamic(() => import('../components/MapPR'), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-[450px] bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading map...</p>
      </div>
    </div>
  )
})

interface SurfCondition {
  id: number;
  timestamp: string;
  wave_height: number | null;
  wave_period: number | null;
  wind_speed: number | null;
  tide_level: number | null;
  buoy_id: string | null;
}

const Forecast: NextPage = () => {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  
  // Default location: Aguadilla, Puerto Rico (Crash Boat)
  const DEFAULT_COORDS = { lat: 18.4589, lon: -67.1672 }
  const DEFAULT_SPOT_NAME = "Aguadilla - Crash Boat"

  const [forecastData, setForecastData] = useState<SurfCondition | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedSpot, setSelectedSpot] = useState<{ name: string; lat: number; lon: number }>({ 
    name: DEFAULT_SPOT_NAME, 
    lat: DEFAULT_COORDS.lat, 
    lon: DEFAULT_COORDS.lon 
  })
  // Geolocation deferred to v2
  // const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null)
  
  // AI Forecast state
  const [aiSummary, setAiSummary] = useState<string | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)
  const [rawForecastData, setRawForecastData] = useState<any>(null)

  // Mock data for charts - replace with real API data later
  const generateMockWaveData = () => {
    const now = new Date()
    return Array.from({ length: 24 }, (_, i) => {
      const timestamp = new Date(now.getTime() + i * 60 * 60 * 1000)
      return {
        timestamp: timestamp.toISOString(),
        waveHeight: 2 + Math.sin(i / 3) * 1.5 + Math.random() * 0.5,
        wavePeriod: 8 + Math.sin(i / 4) * 2 + Math.random() * 1,
      }
    })
  }

  const generateMockTideData = () => {
    const now = new Date()
    const data: Array<{ timestamp: string; height: number; type?: 'high' | 'low' }> = Array.from({ length: 48 }, (_, i) => {
      const timestamp = new Date(now.getTime() + i * 30 * 60 * 1000) // 30-min intervals
      const hour = i * 0.5
      const height = 3 * Math.sin((hour / 6) * Math.PI) // Two tide cycles per day
      return {
        timestamp: timestamp.toISOString(),
        height: height,
      }
    })
    
    // Mark high and low tides
    data.forEach((point, i) => {
      if (i > 0 && i < data.length - 1) {
        const prev = data[i - 1].height
        const curr = point.height
        const next = data[i + 1].height
        
        if (curr > prev && curr > next && curr > 2) {
          point.type = 'high'
        } else if (curr < prev && curr < next && curr < -2) {
          point.type = 'low'
        }
      }
    })
    
    return data
  }

  const fetchForecast = async (lat?: number, lon?: number) => {
    try {
      setRefreshing(true)
      setError(null)
      
      // Use provided lat/lon, or fall back to selectedSpot, or default to Aguadilla
      const targetLat = lat || selectedSpot.lat
      const targetLon = lon || selectedSpot.lon
      
      // Always use global forecast API with coordinates
      const result = await api.fetchGlobalForecast(targetLat, targetLon, 24)
      
      if (result && result.summary) {
        // Store raw forecast data for AI interpretation
        setRawForecastData(result)
        
        // Map ForecastData to SurfCondition for display
        const mappedData: SurfCondition = {
          id: Date.now(),
          timestamp: result.timestamp,
          wave_height: result.summary.wave_height_m || null,
          wave_period: null, // Not available in summary yet
          wind_speed: result.summary.wind_speed_ms || null,
          tide_level: result.summary.tide_height_m || null,
          buoy_id: null,
        }
        
        setForecastData(mappedData)
        setLastUpdate(new Date())
        
        // Show success toast only on manual refresh (not on initial load)
        if (!loading) {
          toast.success('Forecast updated successfully')
        }
        
        // Fetch AI interpretation after successful forecast load
        await fetchAIInterpretation(result)
      }
    } catch (err) {
      console.error('Error fetching forecast:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch forecast data'
      setError(errorMessage)
      toast.error('Error fetching forecast')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const fetchAIInterpretation = async (forecastData: any) => {
    try {
      setAiLoading(true)
      setAiError(null)
      
      // Check localStorage cache first (avoid redundant API calls)
      const cacheKey = `ai-forecast-${forecastData.location.lat}-${forecastData.location.lon}-${new Date(forecastData.timestamp).toDateString()}`
      const cached = localStorage.getItem(cacheKey)
      
      if (cached) {
        const cachedData = JSON.parse(cached)
        // Cache valid for 6 hours
        if (Date.now() - cachedData.timestamp < 6 * 60 * 60 * 1000) {
          setAiSummary(cachedData.summary)
          setAiLoading(false)
          return
        }
      }
      
      // Fetch fresh AI interpretation
      const interpretation = await api.interpretForecast(forecastData)
      
      if (interpretation && interpretation.summary) {
        setAiSummary(interpretation.summary)
        
        // Cache the result
        localStorage.setItem(cacheKey, JSON.stringify({
          summary: interpretation.summary,
          timestamp: Date.now()
        }))
      }
    } catch (err) {
      console.error('Error fetching AI interpretation:', err)
      setAiError('AI forecast unavailable — try again later.')
    } finally {
      setAiLoading(false)
    }
  }

  const handleSpotSelect = (spot: { name: string; lat: number; lon: number }) => {
    setSelectedSpot(spot)
    fetchForecast(spot.lat, spot.lon)
    toast.success(`Loading forecast for ${spot.name}`)
  }

  const handleUseMyLocation = () => {
    // Geolocation deferred to v2
    toast('Location services coming soon!', {
      icon: '📍',
      duration: 3000,
    })
    
    /* DEFERRED TO V2
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser')
      return
    }

    toast.loading('Getting your location...')
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setUserLocation({ lat: latitude, lon: longitude })
        setSelectedSpot({ name: 'Your Location', lat: latitude, lon: longitude })
        fetchForecast(latitude, longitude)
        toast.dismiss()
        toast.success('Using your current location')
      },
      (error) => {
        toast.dismiss()
        toast.error('Unable to get your location')
        console.error('Geolocation error:', error)
      }
    )
    */
  }

  // Protect route - redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      toast.error('Please sign in to view forecasts')
      router.push('/login?redirect=/forecast')
    }
  }, [user, authLoading, router])

  // Fetch forecast data on mount with default Aguadilla coordinates
  useEffect(() => {
    fetchForecast(DEFAULT_COORDS.lat, DEFAULT_COORDS.lon)
    
    // Refresh every 5 minutes using current selectedSpot coordinates
    const interval = setInterval(() => {
      fetchForecast(selectedSpot.lat, selectedSpot.lon)
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    fetchForecast(selectedSpot.lat, selectedSpot.lon)
  }

  // Convert m/s to mph for display
  const waveHeightFt = forecastData?.wave_height ? (forecastData.wave_height * 3.281).toFixed(1) : '--'
  const windSpeedMph = forecastData?.wind_speed ? (forecastData.wind_speed * 2.237).toFixed(1) : '--'
  const tideLevelFt = forecastData?.tide_level ? (forecastData.tide_level * 3.281).toFixed(1) : '--'

  // Determine wave quality based on height
  const getWaveQuality = (heightM: number | null) => {
    if (!heightM) return undefined
    const heightFt = heightM * 3.281
    if (heightFt >= 4 && heightFt <= 8) return 'excellent'
    if (heightFt >= 2 && heightFt < 4) return 'good'
    if (heightFt >= 1 && heightFt < 2) return 'fair'
    return 'poor'
  }

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-500 via-blue-600 to-blue-700 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-white animate-spin mx-auto mb-4" />
          <p className="text-white text-lg">Checking authentication...</p>
        </div>
      </div>
    )
  }

  // Don't render if not authenticated (will redirect)
  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Live Forecast - SwellSense</title>
        <meta 
          name="description" 
          content="Real-time surf conditions from NOAA buoys. Wave height, period, wind speed, and surf quality ratings." 
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="mx-auto max-w-7xl px-3 sm:px-4 md:px-6 py-6 sm:py-8 md:py-12">
          {/* Header */}
          <div className="mb-6 sm:mb-8 md:mb-12">
            <div className="flex items-start sm:items-center justify-between mb-4 flex-col sm:flex-row gap-3 sm:gap-4">
              <div className="flex items-center space-x-2 sm:space-x-3">
                <div className="p-2 sm:p-3 bg-gradient-ocean rounded-xl shadow-lg">
                  <WavesIcon className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">
                    <span className="flex items-center gap-1.5 sm:gap-2">
                      <MapPin className="w-5 h-5 sm:w-6 sm:w-8 md:h-8 text-blue-600" />
                      <span className="break-words">
                        {selectedSpot.name === DEFAULT_SPOT_NAME 
                          ? 'Aguadilla, PR' 
                          : selectedSpot.name}
                      </span>
                    </span>
                  </h1>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">
                    {selectedSpot.lat.toFixed(4)}°N, {Math.abs(selectedSpot.lon).toFixed(4)}°W
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleUseMyLocation}
                  className="inline-flex items-center px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                >
                  <Navigation className="w-4 h-4 mr-2" />
                  My Location
                </button>
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="inline-flex items-center px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
            </div>

            {/* Last Update */}
            {lastUpdate && (
              <div className="flex items-center text-sm text-gray-500">
                <Calendar className="w-4 h-4 mr-1.5" />
                Last updated: {lastUpdate.toLocaleTimeString('en-US', { 
                  hour: 'numeric', 
                  minute: '2-digit',
                  hour12: true 
                })}
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-semibold text-red-900">Failed to load forecast</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}
          </div>

          {/* Interactive Surf Spot Map */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">Puerto Rico Surf Spots</h2>
              <p className="text-sm text-gray-600">Click a marker to view forecast</p>
            </div>
            <MapPR onSpotSelect={handleSpotSelect} selectedSpot={selectedSpot} />
          </div>

          {/* Wrap main content in ErrorBoundary */}
          <ErrorBoundary>
            {/* Current Conditions Data Cards */}
            <div className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Current Conditions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <DataCard
                  icon="wave"
                  title="Wave Height"
                  value={waveHeightFt}
                  unit="ft"
                  subtitle={forecastData?.wave_period ? `${forecastData.wave_period.toFixed(1)}s period` : undefined}
                  quality={getWaveQuality(forecastData?.wave_height || null)}
                  loading={loading}
                />
                <DataCard
                  icon="wind"
                  title="Wind Speed"
                  value={windSpeedMph}
                  unit="mph"
                  subtitle={forecastData?.wind_speed ? `${(forecastData.wind_speed * 1.944).toFixed(1)} kts` : undefined}
                  loading={loading}
                />
                <DataCard
                  icon="temp"
                  title="Water Temp"
                  value="68"
                  unit="°F"
                  subtitle="Comfortable"
                  loading={loading}
                />
                <DataCard
                  icon="tide"
                  title="Tide Height"
                  value={tideLevelFt}
                  unit="ft"
                  subtitle="Rising"
                  trend="up"
                  loading={loading}
                />
              </div>
            </div>

            {/* Wind Compass */}
            <div className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Wind Conditions</h2>
              <div className="max-w-md mx-auto">
                <WindCompass
                  direction={270}  // W - replace with real data
                  speed={forecastData?.wind_speed || 5}
                  gust={forecastData?.wind_speed ? forecastData.wind_speed * 1.2 : undefined}
                  loading={loading}
                />
              </div>
            </div>

            {/* Charts Section */}
            <div className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">24-Hour Forecast</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <WaveHeightChart
                  data={generateMockWaveData()}
                  loading={loading}
                />
                <TideChart
                  data={generateMockTideData()}
                  loading={loading}
                />
              </div>
            </div>

            {/* AI-Powered Forecast Summary */}
            <div className="mb-12">
              <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 p-8">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-gradient-ocean rounded-lg">
                    <span className="text-2xl">🧠</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">SwellSense AI Forecast</h2>
                    <p className="text-sm text-gray-600">48-hour AI-powered surf outlook</p>
                  </div>
                </div>

                {aiLoading ? (
                  <div className="space-y-4">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                      <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6 mb-3"></div>
                      <div className="h-4 bg-gray-200 rounded w-4/5 mb-3"></div>
                      <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    </div>
                    <p className="text-sm text-gray-500 italic text-center mt-6">
                      Generating AI forecast summary...
                    </p>
                  </div>
                ) : aiError ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center">
                    <p className="text-amber-800 font-medium">⚠️ {aiError}</p>
                    <button
                      onClick={() => rawForecastData && fetchAIInterpretation(rawForecastData)}
                      className="mt-4 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium"
                    >
                      Try Again
                    </button>
                  </div>
                ) : aiSummary ? (
                  <div className="prose prose-lg max-w-none">
                    <div className="text-gray-800 leading-relaxed whitespace-pre-line">
                      {aiSummary}
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <p className="italic">AI forecast will appear after data loads...</p>
                  </div>
                )}

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <p className="text-xs text-gray-500 text-center">
                    🤖 Powered by OpenAI GPT-4 • Analysis based on real-time NOAA and global forecast data
                  </p>
                </div>
              </div>
            </div>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                <h3 className="font-semibold text-gray-900 mb-2">📊 Data Source</h3>
                <p className="text-sm text-gray-700">
                  Live data from NOAA National Data Buoy Center (NDBC). 
                  Buoy stations provide wave height, period, wind speed, and more.
                </p>
              </div>
              <div className="bg-cyan-50 rounded-xl p-6 border border-cyan-200">
                <h3 className="font-semibold text-gray-900 mb-2">🔄 Update Frequency</h3>
                <p className="text-sm text-gray-700">
                  Conditions update every 3 hours from NOAA. 
                  This page auto-refreshes every 5 minutes to stay current.
                </p>
              </div>
            </div>
          </ErrorBoundary>
        </div>
      </div>
    </>
  )
}

export default Forecast
