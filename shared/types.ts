// Shared TypeScript types for frontend
export interface SurfConditions {
  FLAT: 0;
  POOR: 1;
  FAIR: 2;
  GOOD: 3;
  EXCELLENT: 4;
  EPIC: 5;
}

export interface Location {
  latitude: number;
  longitude: number;
  country: string;
  region: string;
}

export interface SurfSpot {
  id: string;
  name: string;
  location: Location;
  characteristics: {
    break_type: 'beach' | 'reef' | 'point';
    skill_level: 'beginner' | 'intermediate' | 'advanced';
    ideal_swell_direction: string;
    ideal_wind_direction: string;
  };
}

export interface ForecastData {
  spot_id: string;
  timestamp: string;
  wave_height: number;
  wave_period: number;
  wave_direction: string;
  wind_speed: number;
  wind_direction: string;
  tide_height: number;
  condition_rating: number;
  ai_summary: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  skill_level: 'beginner' | 'intermediate' | 'advanced';
  favorite_spots: string[];
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}