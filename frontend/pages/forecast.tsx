import type { NextPage } from 'next'
import Head from 'next/head'
import { useState, useEffect } from 'react'
import { WavesIcon, RefreshCw, Calendar, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../utils/api'
import WaveHeightChart from '../components/charts/WaveHeightChart'
import TideChart from '../components/charts/TideChart'
import WindCompass from '../components/charts/WindCompass'
import DataCard from '../components/charts/DataCard'
import ErrorBoundary from '../components/ErrorBoundary'

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
  const [forecastData, setForecastData] = useState<SurfCondition | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

  const fetchForecast = async () => {
    try {
      setRefreshing(true)
      setError(null)
      const result = await api.fetchLatestForecast()
      
      if (result.status === 'success' && result.data) {
        setForecastData(result.data)
        setLastUpdate(new Date())
        
        // Show success toast only on manual refresh (not on initial load)
        if (!loading) {
          toast.success('Forecast updated successfully')
        }
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

  // Fetch forecast data on mount
  useEffect(() => {
    fetchForecast()
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchForecast, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    fetchForecast()
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
        <div className="mx-auto max-w-7xl px-6 py-12">
          {/* Header */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-gradient-ocean rounded-xl shadow-lg">
                  <WavesIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-gray-900">Live Surf Forecast</h1>
                  <p className="text-sm text-gray-600 mt-1">Real-time conditions from NOAA buoys</p>
                </div>
              </div>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="inline-flex items-center px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh Forecast
              </button>
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
