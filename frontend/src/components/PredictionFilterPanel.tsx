'use client'

import { Sparkles, MapPin, Calendar, Settings, History } from 'lucide-react'
import { PredictionFilterState } from '@/app/fire-prediction/page'

interface PredictionFilterPanelProps {
  filters: PredictionFilterState
  onFilterChange: (filters: PredictionFilterState) => void
  onGeneratePredictions: () => void
  loading: boolean
}

export default function PredictionFilterPanel({ 
  filters, 
  onFilterChange, 
  onGeneratePredictions, 
  loading 
}: PredictionFilterPanelProps) {
  const regions = [
    { value: 'all-northern-india', label: 'all of northern india' },
    { value: 'punjab', label: 'punjab' },
    { value: 'haryana', label: 'haryana' },
    { value: 'uttar-pradesh', label: 'uttar pradesh' },
    { value: 'delhi', label: 'delhi ncr' },
    { value: 'rajasthan', label: 'rajasthan' },
    { value: 'himachal-pradesh', label: 'himachal pradesh' },
    { value: 'uttarakhand', label: 'uttarakhand' },
    { value: 'chandigarh', label: 'chandigarh area' },
    { value: 'amritsar', label: 'amritsar area' },
    { value: 'ludhiana', label: 'ludhiana area' },
    { value: 'gurgaon', label: 'gurgaon area' },
  ]

  // Removed weather and crop pattern options - using only historical data

  const handleRegionChange = (region: string) => {
    onFilterChange({ ...filters, region })
  }

  const handleDateRangeChange = (dateRange: 'next-7days' | 'next-14days' | 'next-30days' | 'custom') => {
    onFilterChange({ ...filters, dateRange })
  }

  const handleConfidenceChange = (confidenceLevel: number) => {
    onFilterChange({ ...filters, confidenceLevel })
  }

  // Removed factor change handling - only using historical data

  const handleCustomDateChange = (field: 'customStartDate' | 'customEndDate', value: string) => {
    onFilterChange({ ...filters, [field]: value })
  }

  return (
    <div className="space-y-4">
      <div className="filter-card">
        <h3 className="font-semibold mb-3 flex items-center">
          <MapPin className="w-4 h-4 mr-2" />
          prediction region
        </h3>
        <select
          value={filters.region}
          onChange={(e) => handleRegionChange(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-md text-xs"
        >
          {regions.map((region) => (
            <option key={region.value} value={region.value}>
              {region.label}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-card">
        <h3 className="font-semibold mb-3 flex items-center">
          <Calendar className="w-4 h-4 mr-2" />
          prediction timeframe
        </h3>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              value="next-7days"
              checked={filters.dateRange === 'next-7days'}
              onChange={(e) => handleDateRangeChange(e.target.value as 'next-7days')}
              className="mr-2"
            />
            next 7 days
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="next-14days"
              checked={filters.dateRange === 'next-14days'}
              onChange={(e) => handleDateRangeChange(e.target.value as 'next-14days')}
              className="mr-2"
            />
            next 14 days
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="next-30days"
              checked={filters.dateRange === 'next-30days'}
              onChange={(e) => handleDateRangeChange(e.target.value as 'next-30days')}
              className="mr-2"
            />
            next 30 days
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="custom"
              checked={filters.dateRange === 'custom'}
              onChange={(e) => handleDateRangeChange(e.target.value as 'custom')}
              className="mr-2"
            />
            custom range
          </label>
        </div>

        {filters.dateRange === 'custom' && (
          <div className="mt-3 space-y-2">
            <div>
              <label className="block text-xs text-smoke-gray mb-1">start date</label>
              <input
                type="date"
                value={filters.customStartDate || ''}
                onChange={(e) => handleCustomDateChange('customStartDate', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-xs"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div>
              <label className="block text-xs text-smoke-gray mb-1">end date</label>
              <input
                type="date"
                value={filters.customEndDate || ''}
                onChange={(e) => handleCustomDateChange('customEndDate', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-xs"
                min={filters.customStartDate || new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>
        )}
      </div>

      <div className="filter-card">
        <h3 className="font-semibold mb-3 flex items-center">
          <Settings className="w-4 h-4 mr-2" />
          confidence threshold
        </h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-smoke-gray">minimum confidence</span>
            <span className="text-sm font-semibold">{filters.confidenceLevel}%</span>
          </div>
          <input
            type="range"
            min="50"
            max="95"
            step="5"
            value={filters.confidenceLevel}
            onChange={(e) => handleConfidenceChange(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-smoke-gray">
            <span>50%</span>
            <span>70%</span>
            <span>95%</span>
          </div>
        </div>
      </div>


      <button
        onClick={onGeneratePredictions}
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center"
      >
        <Sparkles className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
        {loading ? 'generating...' : 'generate predictions'}
      </button>

      <div className="filter-card">
        <h4 className="font-semibold mb-2 text-xs">model information</h4>
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-smoke-gray">algorithm:</span>
            <span className="font-medium">historical pattern analysis</span>
          </div>
          <div className="flex justify-between">
            <span className="text-smoke-gray">accuracy:</span>
            <span className="font-medium">85.0%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-smoke-gray">data source:</span>
            <span className="font-medium">321k+ fire records</span>
          </div>
          <div className="flex justify-between">
            <span className="text-smoke-gray">analysis:</span>
            <span className="font-medium">seasonal patterns only</span>
          </div>
        </div>
      </div>
    </div>
  )
}