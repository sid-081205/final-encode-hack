const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface FireData {
  id: string
  latitude: number
  longitude: number
  brightness: number
  confidence: number
  acq_date: string
  acq_time: string
  acq_datetime: string
  source: 'MODIS' | 'VIIRS' | 'User Reported'
  frp?: number
  scan?: number
  track?: number
  state?: string
  district?: string
  created_at: string
}

export interface FireFilterRequest {
  region: string
  date_range: string
  custom_start_date?: string
  custom_end_date?: string
  sources: {
    MODIS: boolean
    VIIRS: boolean
    'User Reported': boolean
  }
}

export interface FireFilterResponse {
  fires: FireData[]
  total_count: number
  filtered_count: number
  region: string
  date_range: string
}

export interface ApiError {
  detail: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }))
        throw new Error(errorData.detail || 'API request failed')
      }

      return await response.json()
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('Network error or invalid response')
    }
  }

  async detectFires(filters: FireFilterRequest): Promise<FireFilterResponse> {
    return this.request<FireFilterResponse>('/api/fires/detect', {
      method: 'POST',
      body: JSON.stringify(filters),
    })
  }

  async getFireStatistics(region: string = 'all-northern-india', dateRange: string = '24hr') {
    return this.request(`/api/fires/statistics?region=${encodeURIComponent(region)}&date_range=${encodeURIComponent(dateRange)}`)
  }

  async getAvailableRegions() {
    return this.request('/api/fires/regions')
  }

  async getAvailableDateRange() {
    return this.request('/api/fires/date-range')
  }

  // Prediction API methods
  async generatePredictions(filters: any) {
    return this.request('/api/predictions/generate', {
      method: 'POST',
      body: JSON.stringify(filters),
    })
  }

  async getPredictionRegions() {
    return this.request('/api/predictions/regions')
  }

  async getPredictionFactors() {
    return this.request('/api/predictions/factors')
  }

  async getPredictionModelInfo() {
    return this.request('/api/predictions/model-info')
  }

  async predictionHealthCheck() {
    return this.request('/api/predictions/health')
  }

  async healthCheck() {
    return this.request('/api/fires/health')
  }
}

export const apiClient = new ApiClient()

// Utility functions
export const formatFireTime = (date: string, time: string): string => {
  try {
    const hour = time.slice(0, 2)
    const minute = time.slice(2, 4)
    return `${hour}:${minute}`
  } catch {
    return time
  }
}

export const formatFireDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric',
      month: 'short', 
      day: 'numeric' 
    })
  } catch {
    return dateString
  }
}

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return 'text-fire-red'
  if (confidence >= 60) return 'text-fire-orange'
  return 'text-fire-yellow'
}

export const getConfidenceBg = (confidence: number): string => {
  if (confidence >= 80) return 'bg-fire-red/10 border-fire-red/20'
  if (confidence >= 60) return 'bg-fire-orange/10 border-fire-orange/20'
  return 'bg-fire-yellow/10 border-fire-yellow/20'
}

export const getPowerSeverityColor = (frp: number): string => {
  if (frp >= 40) return 'text-red-600' // High power - red
  if (frp >= 10) return 'text-orange-600' // Medium power - orange
  return 'text-green-600' // Low power - green (fires <10 MW)
}

export const getPowerSeverityBg = (frp: number): string => {
  if (frp >= 40) return 'bg-red-100 border-red-200' // High power - red background
  if (frp >= 10) return 'bg-orange-100 border-orange-200' // Medium power - orange background
  return 'bg-green-100 border-green-200' // Low power - green background (fires <10 MW)
}

export const getPowerSeverityLabel = (frp: number): string => {
  if (frp >= 40) return 'high'
  if (frp >= 10) return 'medium'
  return 'low'
}