'use client'

import { useState, useEffect } from 'react'
import { RefreshCw, MapPin, Calendar, Satellite } from 'lucide-react'
import { FilterState } from '@/app/fire-detection/page'
import { apiClient } from '@/lib/api'

interface FilterPanelProps {
  filters: FilterState
  onFilterChange: (filters: FilterState) => void
  onRefresh: () => void
  loading: boolean
}

export default function FilterPanel({ filters, onFilterChange, onRefresh, loading }: FilterPanelProps) {
  const [dateRange, setDateRange] = useState<{min_date: string, max_date: string} | null>(null)

  useEffect(() => {
    // Fetch available date range on component mount
    const fetchDateRange = async () => {
      try {
        const response = await apiClient.getAvailableDateRange()
        setDateRange(response.available_range)
      } catch (error) {
        console.error('Failed to fetch date range:', error)
      }
    }
    fetchDateRange()
  }, [])
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

  const sources = [
    {
      key: 'MODIS' as const,
      label: 'modis',
      description: 'nasa terra/aqua moderate resolution imaging spectroradiometer'
    },
    {
      key: 'VIIRS' as const,
      label: 'viirs',
      description: 'visible infrared imaging radiometer suite from suomi npp/noaa-20'
    },
    {
      key: 'User Reported' as const,
      label: 'user reported',
      description: 'community-submitted fire reports and observations'
    }
  ]

  const handleRegionChange = (region: string) => {
    onFilterChange({ ...filters, region })
  }

  const handleDateRangeChange = (dateRange: '24hr' | '7day' | 'custom') => {
    onFilterChange({ ...filters, dateRange })
  }

  const handleSourceChange = (source: keyof FilterState['sources']) => {
    onFilterChange({
      ...filters,
      sources: {
        ...filters.sources,
        [source]: !filters.sources[source]
      }
    })
  }

  const handleCustomDateChange = (field: 'customStartDate' | 'customEndDate', value: string) => {
    onFilterChange({ ...filters, [field]: value })
  }

  return (
    <div className="space-y-4">
      <div className="filter-card">
        <h3 className="font-semibold mb-3 flex items-center">
          <MapPin className="w-4 h-4 mr-2" />
          region selection
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
          date range
        </h3>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              value="24hr"
              checked={filters.dateRange === '24hr'}
              onChange={(e) => handleDateRangeChange(e.target.value as '24hr')}
              className="mr-2"
            />
            last 24 hours
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="7day"
              checked={filters.dateRange === '7day'}
              onChange={(e) => handleDateRangeChange(e.target.value as '7day')}
              className="mr-2"
            />
            last 7 days
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="custom"
              checked={filters.dateRange === 'custom'}
              onChange={(e) => handleDateRangeChange(e.target.value as 'custom')}
              className="mr-2"
            />
            custom date range
          </label>
        </div>

        {filters.dateRange === 'custom' && (
          <div className="mt-3 space-y-2">
            {dateRange && (
              <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                <div className="text-blue-700 font-medium mb-1">📅 historical data available</div>
                <div className="text-blue-600">
                  {dateRange.min_date} to {dateRange.max_date}
                </div>
              </div>
            )}
            <div>
              <label className="block text-xs text-smoke-gray mb-1">start date</label>
              <input
                type="date"
                value={filters.customStartDate || ''}
                min={dateRange?.min_date}
                max={dateRange?.max_date}
                onChange={(e) => handleCustomDateChange('customStartDate', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-xs"
              />
            </div>
            <div>
              <label className="block text-xs text-smoke-gray mb-1">end date</label>
              <input
                type="date"
                value={filters.customEndDate || ''}
                min={dateRange?.min_date}
                max={dateRange?.max_date}
                onChange={(e) => handleCustomDateChange('customEndDate', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md text-xs"
              />
            </div>
          </div>
        )}
      </div>

      <div className="filter-card">
        <h3 className="font-semibold mb-3 flex items-center">
          <Satellite className="w-4 h-4 mr-2" />
          data sources
        </h3>
        <div className="space-y-3">
          {sources.map((source) => (
            <div key={source.key}>
              <label className="flex items-start">
                <input
                  type="checkbox"
                  checked={filters.sources[source.key]}
                  onChange={() => handleSourceChange(source.key)}
                  className="mr-2 mt-1"
                />
                <div>
                  <div className="font-medium">{source.label}</div>
                  <div className="text-xs text-smoke-gray mt-1">
                    {source.description}
                  </div>
                </div>
              </label>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onRefresh}
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center"
      >
        <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
        {loading ? 'refreshing...' : 'refresh data'}
      </button>
    </div>
  )
}