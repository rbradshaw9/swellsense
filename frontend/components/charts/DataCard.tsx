import React from 'react'
import { WavesIcon, Wind, Thermometer, TrendingUp } from 'lucide-react'

interface DataCardProps {
  icon: 'wave' | 'wind' | 'temp' | 'tide'
  title: string
  value: string | number
  unit: string
  subtitle?: string
  trend?: 'up' | 'down' | 'stable'
  quality?: 'excellent' | 'good' | 'fair' | 'poor'
  loading?: boolean
}

const DataCard: React.FC<DataCardProps> = ({ 
  icon, 
  title, 
  value, 
  unit, 
  subtitle, 
  trend,
  quality,
  loading = false 
}) => {
  // Loading state
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
        <div className="h-12 bg-gray-200 rounded w-32 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-20"></div>
      </div>
    )
  }

  // Icon selection
  const IconComponent = {
    wave: WavesIcon,
    wind: Wind,
    temp: Thermometer,
    tide: WavesIcon,
  }[icon]

  // Quality color mapping
  const qualityColors = {
    excellent: 'bg-green-50 border-green-200 text-green-700',
    good: 'bg-blue-50 border-blue-200 text-blue-700',
    fair: 'bg-amber-50 border-amber-200 text-amber-700',
    poor: 'bg-red-50 border-red-200 text-red-700',
  }

  const qualityBadge = quality ? (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${qualityColors[quality]}`}>
      {quality.charAt(0).toUpperCase() + quality.slice(1)}
    </span>
  ) : null

  // Trend indicator
  const trendIcon = trend ? (
    <span className={`inline-flex items-center ${
      trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
    }`}>
      <TrendingUp className={`w-4 h-4 ${trend === 'down' ? 'rotate-180' : trend === 'stable' ? 'rotate-90' : ''}`} />
    </span>
  ) : null

  return (
    <div className="card hover:shadow-md transition-shadow duration-200 backdrop-blur-sm bg-white/80">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-ocean rounded-lg">
            <IconComponent className="w-6 h-6 text-white" />
          </div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
        {qualityBadge}
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-4xl font-bold text-gray-900">
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
        <span className="text-lg text-gray-600">{unit}</span>
        {trendIcon}
      </div>

      {subtitle && (
        <p className="text-sm text-gray-600 mt-2">{subtitle}</p>
      )}
    </div>
  )
}

export default DataCard
