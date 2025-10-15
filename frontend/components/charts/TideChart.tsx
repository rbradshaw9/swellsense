import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { format } from 'date-fns'
import { WavesIcon } from 'lucide-react'

interface TideDataPoint {
  timestamp: string
  height: number
  type?: 'high' | 'low'
}

interface TideChartProps {
  data: TideDataPoint[]
  loading?: boolean
  error?: Error | null
}

const TideChart: React.FC<TideChartProps> = ({ data, loading = false, error = null }) => {
  // Loading state
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-6 h-6 bg-gray-200 rounded"></div>
          <div className="h-5 bg-gray-200 rounded w-32"></div>
        </div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-center space-x-2 mb-2">
          <WavesIcon className="w-5 h-5 text-red-600" />
          <h3 className="font-semibold text-red-900">Tide Chart Error</h3>
        </div>
        <p className="text-sm text-red-700">{error.message}</p>
      </div>
    )
  }

  // No data state
  if (!data || data.length === 0) {
    return (
      <div className="card bg-gray-50">
        <div className="flex items-center space-x-2 mb-2">
          <WavesIcon className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-gray-700">Tide Predictions</h3>
        </div>
        <div className="h-64 flex items-center justify-center">
          <p className="text-sm text-gray-500">No tide data available</p>
        </div>
      </div>
    )
  }

  // Find high and low tides
  const tideExtremes = data.filter(d => d.type === 'high' || d.type === 'low')

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-xs text-gray-600 mb-1">
            {format(new Date(point.timestamp), 'MMM d, HH:mm')}
          </p>
          <p className="text-sm font-semibold text-cyan-600">
            Tide: {payload[0].value.toFixed(1)} ft
          </p>
          {point.type && (
            <p className="text-xs text-gray-500 mt-1">
              {point.type === 'high' ? '↑ High Tide' : '↓ Low Tide'}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  // Custom dot for tide extremes
  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props
    if (payload.type === 'high') {
      return (
        <circle cx={cx} cy={cy} r={5} fill="#06b6d4" stroke="white" strokeWidth={2} />
      )
    } else if (payload.type === 'low') {
      return (
        <circle cx={cx} cy={cy} r={5} fill="#f59e0b" stroke="white" strokeWidth={2} />
      )
    }
    return null
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-ocean rounded-lg">
            <WavesIcon className="w-5 h-5 text-white" />
          </div>
          <h3 className="font-semibold text-gray-900">Tide Predictions</h3>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
            <span className="text-gray-600">High</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <span className="text-gray-600">Low</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="tideGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
              <stop offset="50%" stopColor="#06b6d4" stopOpacity={0.1} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={(time: string) => format(new Date(time), 'HH:mm')}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            stroke="#d1d5db"
          />
          <YAxis
            label={{ value: 'Tide Height (ft)', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            stroke="#d1d5db"
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
          <Area
            type="natural"
            dataKey="height"
            stroke="#06b6d4"
            strokeWidth={2}
            fill="url(#tideGradient)"
            dot={<CustomDot />}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Tide Extremes Summary */}
      {tideExtremes.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            {tideExtremes.slice(0, 4).map((tide, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  {format(new Date(tide.timestamp), 'HH:mm')}
                </span>
                <span className={`font-semibold ${tide.type === 'high' ? 'text-cyan-600' : 'text-amber-600'}`}>
                  {tide.type === 'high' ? '↑' : '↓'} {tide.height.toFixed(1)} ft
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TideChart
