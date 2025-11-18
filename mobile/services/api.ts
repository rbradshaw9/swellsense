/**
 * API Client for SwellSense Backend
 * Connects to https://api.swellsense.app
 */

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Local development
  : 'https://api.swellsense.app';  // Production

export interface Session {
  id?: number;
  spot_name: string;
  latitude?: number;
  longitude?: number;
  session_date: string;  // ISO 8601
  duration_minutes?: number;
  waves_caught?: number;
  rating?: number;  // 1-10
  board_type?: string;
  wave_height_ft?: number;
  swell_period_sec?: number;
  wind_speed_mph?: number;
  wind_direction?: string;
  tide?: string;
  crowd_level?: string;
  notes?: string;
  photo_urls?: string[];
}

export interface SessionStats {
  total_sessions: number;
  total_waves_caught: number;
  total_hours: number;
  average_rating: number;
  favorite_spot: string | null;
  favorite_board: string | null;
  spots_surfed: number;
  best_conditions: any | null;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Session endpoints
  async createSession(session: Session): Promise<Session> {
    return this.request<Session>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify(session),
    });
  }

  async getSessions(params?: {
    limit?: number;
    offset?: number;
    spot_name?: string;
    min_rating?: number;
  }): Promise<Session[]> {
    const query = new URLSearchParams();
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    if (params?.spot_name) query.append('spot_name', params.spot_name);
    if (params?.min_rating) query.append('min_rating', params.min_rating.toString());
    
    const queryString = query.toString();
    const endpoint = `/api/sessions${queryString ? `?${queryString}` : ''}`;
    
    return this.request<Session[]>(endpoint);
  }

  async getSessionStats(): Promise<SessionStats> {
    return this.request<SessionStats>('/api/sessions/stats');
  }

  async updateSession(id: number, updates: Partial<Session>): Promise<Session> {
    return this.request<Session>(`/api/sessions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  async deleteSession(id: number): Promise<void> {
    await this.request(`/api/sessions/${id}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }
}

export const api = new ApiClient();
