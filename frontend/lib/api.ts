/**
 * Centralized API client for SwellSense frontend
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ForecastData {
  timestamp: string
  location: {
    lat: number
    lon: number
  }
  sources: {
    stormglass?: any
    openweather?: any
    worldtides?: any
    metno?: any
    noaa_erddap?: any
    noaa_gfs?: any
    era5?: any
    openmeteo?: any
    copernicus_marine?: any
  }
  summary: {
    wave_height_m?: number
    wind_speed_ms?: number
    temperature_c?: number
    tide_height_m?: number
    conditions: string
  }
  partial: boolean
  sources_available: string[]
  sources_failed: string[] | null
  response_time_s: number
}

export interface AIQueryRequest {
  query: string
  location?: string
  latitude?: number
  longitude?: number
  skill_level?: 'beginner' | 'intermediate' | 'advanced'
}

export interface AIQueryResponse {
  query: string
  recommendation: string
  confidence: number
  explanation: string
  data_timestamp?: string
  station_used?: string
  region?: string
}

export interface HealthStatus {
  status: 'ok' | 'degraded'
  timestamp: string
  services: {
    [key: string]: {
      ok: boolean
      latency_ms?: number
      error?: string
      note?: string
    }
  }
  database: {
    connected: boolean
  }
  failed_services: string[] | null
  version: string
  check_duration_s: number
}

class APIClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  /**
   * Fetch global forecast for a location
   */
  async fetchGlobalForecast(lat: number, lon: number, hours: number = 12): Promise<ForecastData> {
    const response = await fetch(
      `${this.baseURL}/api/forecast/global?lat=${lat}&lon=${lon}&hours=${hours}`
    )
    
    if (!response.ok) {
      throw new Error(`Forecast fetch failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Fetch latest buoy data
   */
  async fetchLatestForecast(buoyId?: string): Promise<any> {
    const url = buoyId 
      ? `${this.baseURL}/api/forecast/latest?buoy_id=${buoyId}`
      : `${this.baseURL}/api/forecast/latest`
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Latest forecast fetch failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Fetch forecast statistics
   */
  async fetchForecastStats(hours: number = 24, buoyId?: string): Promise<any> {
    const params = new URLSearchParams({ hours: hours.toString() })
    if (buoyId) params.append('buoy_id', buoyId)
    
    const response = await fetch(`${this.baseURL}/api/forecast/stats?${params}`)
    
    if (!response.ok) {
      throw new Error(`Stats fetch failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Query the AI surf advisor
   */
  async queryAI(request: AIQueryRequest): Promise<AIQueryResponse> {
    const response = await fetch(`${this.baseURL}/api/ai/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    
    if (!response.ok) {
      throw new Error(`AI query failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Get system health status
   */
  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseURL}/api/forecast/health`)
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Get API info
   */
  async getInfo(): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/info`)
    
    if (!response.ok) {
      throw new Error(`Info fetch failed: ${response.statusText}`)
    }
    
    return response.json()
  }
}

// Export singleton instance
export const api = new APIClient()

// Export class for custom instances
export default APIClient
