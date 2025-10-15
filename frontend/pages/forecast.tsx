import type { NextPage } from 'next'
import Head from 'next/head'
import { useState, useEffect } from 'react'
import { WavesIcon, RefreshCw, Calendar } from 'lucide-react'
import ForecastCard from '../components/ui/ForecastCard'
import { api } from '../utils/api'

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

  const fetchForecast = async () => {
    try {
      setRefreshing(true)
      const result = await api.fetchLatestForecast()
      
      if (result.status === 'success' && result.data) {
        setForecastData(result.data)
        setLastUpdate(new Date())
      }
    } catch (error) {
      console.error('Error fetching forecast:', error)
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
                Refresh
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
          </div>

          {/* Current Conditions */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Current Conditions</h2>
            <ForecastCard data={forecastData} loading={loading} />
          </div>

          {/* 24-Hour Overview (Coming Soon) */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">24-Hour Overview</h2>
            <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-200 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-4">
                <Calendar className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Hourly forecast charts, tide predictions, and 7-day extended outlook
              </p>
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
        </div>
      </div>
    </>
  )
}

export default Forecast
