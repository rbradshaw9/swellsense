import React from 'react';
import { WavesIcon, Wind, Clock, TrendingUp } from 'lucide-react';

interface SurfCondition {
  id: number;
  timestamp: string;
  wave_height: number | null;
  wave_period: number | null;
  wind_speed: number | null;
  tide_level: number | null;
  buoy_id: string | null;
}

interface ForecastCardProps {
  data: SurfCondition | null;
  loading?: boolean;
}

const ForecastCard: React.FC<ForecastCardProps> = ({ data, loading = false }) => {
  // Loading state
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  // No data state
  if (!data) {
    return (
      <div className="card text-center">
        <div className="flex flex-col items-center justify-center py-8 space-y-4">
          <WavesIcon className="w-16 h-16 text-gray-300" />
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-700">No Forecast Data Yet</h3>
            <p className="text-sm text-gray-500">
              Surf conditions will appear here once data is available from NOAA buoys
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Convert m/s to mph for wind
  const windMph = data.wind_speed ? (data.wind_speed * 2.237).toFixed(1) : null;
  
  // Convert meters to feet for wave height
  const waveHeightFt = data.wave_height ? (data.wave_height * 3.281).toFixed(1) : null;

  return (
    <div className="card hover:shadow-lg transition-shadow duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-ocean rounded-lg">
            <WavesIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Current Conditions</h3>
            {data.buoy_id && (
              <p className="text-xs text-gray-500">Buoy Station {data.buoy_id}</p>
            )}
          </div>
        </div>
        <div className="flex items-center text-xs text-gray-500">
          <Clock className="w-4 h-4 mr-1" />
          {formatTime(data.timestamp)}
        </div>
      </div>

      {/* Conditions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Wave Height */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
          <div className="flex items-center space-x-2 mb-2">
            <WavesIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Wave Height</span>
          </div>
          <div className="space-y-1">
            {waveHeightFt ? (
              <>
                <p className="text-3xl font-bold text-blue-600">{waveHeightFt}</p>
                <p className="text-xs text-gray-500">feet ({data.wave_height?.toFixed(1)}m)</p>
              </>
            ) : (
              <p className="text-lg text-gray-400">No data</p>
            )}
          </div>
        </div>

        {/* Wave Period */}
        <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-100">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-cyan-600" />
            <span className="text-sm font-medium text-gray-700">Wave Period</span>
          </div>
          <div className="space-y-1">
            {data.wave_period ? (
              <>
                <p className="text-3xl font-bold text-cyan-600">{data.wave_period.toFixed(1)}</p>
                <p className="text-xs text-gray-500">seconds</p>
              </>
            ) : (
              <p className="text-lg text-gray-400">No data</p>
            )}
          </div>
        </div>

        {/* Wind Speed */}
        <div className="bg-sky-50 rounded-lg p-4 border border-sky-100">
          <div className="flex items-center space-x-2 mb-2">
            <Wind className="w-5 h-5 text-sky-600" />
            <span className="text-sm font-medium text-gray-700">Wind Speed</span>
          </div>
          <div className="space-y-1">
            {windMph ? (
              <>
                <p className="text-3xl font-bold text-sky-600">{windMph}</p>
                <p className="text-xs text-gray-500">mph ({data.wind_speed?.toFixed(1)} m/s)</p>
              </>
            ) : (
              <p className="text-lg text-gray-400">No data</p>
            )}
          </div>
        </div>
      </div>

      {/* Quality Indicator */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Surf Quality</span>
          {data.wave_height && data.wave_period ? (
            <div className="flex items-center space-x-2">
              {data.wave_height > 1.5 && data.wave_period > 8 ? (
                <>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-600">Good</span>
                </>
              ) : data.wave_height > 0.9 ? (
                <>
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm font-medium text-yellow-600">Fair</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-600">Poor</span>
                </>
              )}
            </div>
          ) : (
            <span className="text-sm text-gray-400">Calculating...</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForecastCard;
