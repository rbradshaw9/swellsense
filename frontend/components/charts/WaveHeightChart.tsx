import React from 'react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { format } from 'date-fns'
import { WavesIcon } from 'lucide-react'

interface WaveDataPoint {
  timestamp: string
  waveHeight: number
  wavePeriod?: number
}

interface WaveHeightChartProps {
  data: WaveDataPoint[]
  loading?: boolean
  error?: Error | null
}

const WaveHeightChart: React.FC<WaveHeightChartProps> = ({ data, loading = false, error = null }) => {
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
          <h3 className="font-semibold text-red-900">Wave Height Chart Error</h3>
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
          <h3 className="font-semibold text-gray-700">Wave Height Chart</h3>
        </div>
        <div className="h-64 flex items-center justify-center">
          <p className="text-sm text-gray-500">No wave height data available</p>
        </div>
      </div>
    )
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-xs text-gray-600 mb-1">
            {format(new Date(payload[0].payload.timestamp), 'MMM d, HH:mm')}
          </p>
          <p className="text-sm font-semibold text-blue-600">
            Wave Height: {payload[0].value.toFixed(1)} ft
          </p>
          {payload[1] && (
            <p className="text-sm font-semibold text-cyan-600">
              Period: {payload[1].value.toFixed(1)} sec
            </p>
          )}
        </div>
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
          <h3 className="font-semibold text-gray-900">Wave Height Forecast</h3>
        </div>
        <span className="text-xs text-gray-500">Next 24 hours</span>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="periodGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.2} />
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
            yAxisId="left"
            label={{ value: 'Wave Height (ft)', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            stroke="#d1d5db"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ value: 'Period (sec)', angle: 90, position: 'insideRight', style: { fontSize: 12, fill: '#6b7280' } }}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            stroke="#d1d5db"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: 12 }}
            iconType="line"
          />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="waveHeight"
            stroke="#0ea5e9"
            strokeWidth={2}
            fill="url(#waveGradient)"
            name="Wave Height"
            dot={{ fill: '#0ea5e9', r: 3 }}
          />
          {data[0]?.wavePeriod !== undefined && (
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="wavePeriod"
              stroke="#06b6d4"
              strokeWidth={2}
              name="Wave Period"
              dot={{ fill: '#06b6d4', r: 3 }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default WaveHeightChart
