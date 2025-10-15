import React from 'react'
import { Compass, Wind } from 'lucide-react'

interface WindCompassProps {
  direction: number  // 0-360 degrees (0 = North)
  speed: number      // m/s
  gust?: number      // m/s (optional)
  loading?: boolean
  error?: Error | null
}

const WindCompass: React.FC<WindCompassProps> = ({ 
  direction, 
  speed, 
  gust,
  loading = false, 
  error = null 
}) => {
  // Loading state
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-6 h-6 bg-gray-200 rounded"></div>
          <div className="h-5 bg-gray-200 rounded w-32"></div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="w-48 h-48 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-center space-x-2 mb-2">
          <Wind className="w-5 h-5 text-red-600" />
          <h3 className="font-semibold text-red-900">Wind Compass Error</h3>
        </div>
        <p className="text-sm text-red-700">{error.message}</p>
      </div>
    )
  }

  // Convert m/s to mph and kts
  const speedMph = (speed * 2.237).toFixed(1)
  const speedKts = (speed * 1.944).toFixed(1)

  // Determine if wind is offshore (good for surfing)
  // Typically offshore = NE to SE (45° to 135°) or SW to NW (225° to 315°)
  const isOffshore = (direction >= 45 && direction <= 135) || (direction >= 225 && direction <= 315)
  
  // Wind strength classification
  let windStrength = 'Calm'
  let windColor = 'text-green-600'
  
  if (speed < 2) {
    windStrength = 'Calm'
    windColor = 'text-green-600'
  } else if (speed < 5) {
    windStrength = 'Light'
    windColor = 'text-green-600'
  } else if (speed < 10) {
    windStrength = 'Moderate'
    windColor = 'text-blue-600'
  } else if (speed < 15) {
    windStrength = 'Fresh'
    windColor = 'text-amber-600'
  } else {
    windStrength = 'Strong'
    windColor = 'text-red-600'
  }

  // Cardinal direction helper
  const getCardinalDirection = (deg: number) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    const index = Math.round(deg / 22.5) % 16
    return directions[index]
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-ocean rounded-lg">
            <Wind className="w-5 h-5 text-white" />
          </div>
          <h3 className="font-semibold text-gray-900">Wind Conditions</h3>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
          isOffshore ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
        }`}>
          {isOffshore ? 'Offshore' : 'Onshore'}
        </span>
      </div>

      <div className="flex flex-col items-center justify-center py-6">
        {/* Compass SVG */}
        <div className="relative w-48 h-48">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            {/* Outer circle */}
            <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" strokeWidth="2" />
            <circle cx="100" cy="100" r="80" fill="none" stroke="#f3f4f6" strokeWidth="1" />
            
            {/* Cardinal directions */}
            <text x="100" y="25" textAnchor="middle" className="text-sm font-semibold fill-gray-700">N</text>
            <text x="175" y="105" textAnchor="middle" className="text-sm font-semibold fill-gray-700">E</text>
            <text x="100" y="185" textAnchor="middle" className="text-sm font-semibold fill-gray-700">S</text>
            <text x="25" y="105" textAnchor="middle" className="text-sm font-semibold fill-gray-700">W</text>
            
            {/* Degree markers */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
              const rad = (deg - 90) * (Math.PI / 180)
              const x1 = 100 + 85 * Math.cos(rad)
              const y1 = 100 + 85 * Math.sin(rad)
              const x2 = 100 + 75 * Math.cos(rad)
              const y2 = 100 + 75 * Math.sin(rad)
              return (
                <line
                  key={deg}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="#d1d5db"
                  strokeWidth="2"
                />
              )
            })}
            
            {/* Wind direction arrow */}
            <g transform={`rotate(${direction} 100 100)`}>
              {/* Arrow shaft */}
              <line x1="100" y1="100" x2="100" y2="30" stroke="#0ea5e9" strokeWidth="3" />
              {/* Arrow head */}
              <polygon
                points="100,20 95,35 100,30 105,35"
                fill="#0ea5e9"
                className={windColor.replace('text-', 'fill-')}
              />
              {/* Arrow tail */}
              <circle cx="100" cy="100" r="8" fill="#0ea5e9" />
            </g>
          </svg>
        </div>

        {/* Wind Speed Display */}
        <div className="mt-6 text-center">
          <div className={`text-4xl font-bold ${windColor}`}>
            {speedMph}
            <span className="text-xl ml-1">mph</span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {speedKts} kts · {speed.toFixed(1)} m/s
          </div>
          <div className="flex items-center justify-center space-x-2 mt-3">
            <Compass className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-semibold text-gray-700">
              {getCardinalDirection(direction)} ({direction}°)
            </span>
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {windStrength}
          </div>
        </div>

        {/* Gust info if available */}
        {gust && gust > speed && (
          <div className="mt-4 px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-800">
              Gusts up to <span className="font-semibold">{(gust * 2.237).toFixed(1)} mph</span>
            </p>
          </div>
        )}
      </div>

      {/* Wind Quality for Surfing */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-start space-x-2">
          <div className={`w-2 h-2 rounded-full mt-1.5 ${isOffshore ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">
              {isOffshore ? 'Good for surfing' : 'Not ideal for surfing'}
            </p>
            <p className="text-xs text-gray-600 mt-0.5">
              {isOffshore 
                ? 'Offshore winds create clean, well-shaped waves' 
                : 'Onshore winds can make waves choppy and less organized'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WindCompass
