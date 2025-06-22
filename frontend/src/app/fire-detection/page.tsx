'use client'

import { useState, useEffect } from 'react'
import { Plus, AlertTriangle } from 'lucide-react'
import FireMap from '@/components/FireMap'
import FilterPanel from '@/components/FilterPanel'
import RecentFiresPanel from '@/components/RecentFiresPanel'
import MapStats from '@/components/MapStats'
import UserReportForm, { UserReportData } from '@/components/UserReportForm'
import { apiClient, FireData, FireFilterRequest } from '@/lib/api'

export interface FilterState {
  region: string
  dateRange: '24hr' | '7day' | 'custom'
  customStartDate?: string
  customEndDate?: string
  sources: {
    MODIS: boolean
    VIIRS: boolean
    'User Reported': boolean
  }
}

export default function FireDetection() {
  const [fires, setFires] = useState<FireData[]>([])
  const [filteredFires, setFilteredFires] = useState<FireData[]>([])
  const [filters, setFilters] = useState<FilterState>({
    region: 'all-northern-india',
    dateRange: '24hr',
    sources: {
      MODIS: true,
      VIIRS: true,
      'User Reported': false
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showReportForm, setShowReportForm] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportSuccess, setReportSuccess] = useState<string | null>(null)

  useEffect(() => {
    // Load initial data
    handleRefresh()
  }, [])

  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters)
  }

  const handleRefresh = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Validate custom date range if selected
      if (filters.dateRange === 'custom') {
        if (!filters.customStartDate || !filters.customEndDate) {
          throw new Error('Please select both start and end dates for custom range')
        }
        
        const startDate = new Date(filters.customStartDate)
        const endDate = new Date(filters.customEndDate)
        const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
        
        if (daysDiff > 31) {
          throw new Error('Date range cannot exceed 31 days')
        }
        
        if (startDate > endDate) {
          throw new Error('Start date must be before end date')
        }
      }
      
      // Prepare filter request
      const filterRequest: FireFilterRequest = {
        region: filters.region,
        date_range: filters.dateRange,
        custom_start_date: filters.customStartDate,
        custom_end_date: filters.customEndDate,
        sources: filters.sources
      }

      // Call API
      const response = await apiClient.detectFires(filterRequest)
      
      // Update state with API response
      setFires(response.fires)
      setFilteredFires(response.fires)
      
      console.log(`Loaded ${response.fires.length} fires for region ${response.region}`)
      
    } catch (err) {
      console.error('Error fetching fires:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch fire data')
      setFires([])
      setFilteredFires([])
    } finally {
      setLoading(false)
    }
  }

  const handleUserReport = async (reportData: UserReportData) => {
    setReportLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.reportFire(reportData)
      setReportSuccess(`Report submitted successfully! Report ID: ${response.id}`)
      setShowReportForm(false)
      
      // If user reports are enabled, refresh the data to show the new report
      if (filters.sources['User Reported']) {
        handleRefresh()
      }
      
      // Clear success message after 5 seconds
      setTimeout(() => setReportSuccess(null), 5000)
      
    } catch (err) {
      console.error('Error submitting report:', err)
      setError(err instanceof Error ? err.message : 'Failed to submit report')
    } finally {
      setReportLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ash-light">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-charcoal mb-2">fire detection</h1>
              <p className="text-smoke-gray">real-time monitoring of active fires in northern india</p>
            </div>
            
            {/* Report Button */}
            <button
              onClick={() => setShowReportForm(true)}
              className="flex items-center space-x-2 bg-fire-red hover:bg-fire-red/90 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-sm"
            >
              <Plus className="w-5 h-5" />
              <span>Report Fire</span>
            </button>
          </div>
          
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">⚠️ {error}</p>
            </div>
          )}
          
          {reportSuccess && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 text-sm">✅ {reportSuccess}</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Filter Panel */}
          <div className="col-span-3">
            <FilterPanel
              filters={filters}
              onFilterChange={handleFilterChange}
              onRefresh={handleRefresh}
              loading={loading}
            />
          </div>

          {/* Map Section */}
          <div className="col-span-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <MapStats fires={filteredFires} />
              <div className="h-[600px]">
                <FireMap fires={filteredFires} />
              </div>
            </div>
          </div>

          {/* Recent Fires Panel */}
          <div className="col-span-3">
            <RecentFiresPanel fires={filteredFires} />
          </div>
        </div>
      </div>
      
      {/* User Report Form Modal */}
      <UserReportForm
        isOpen={showReportForm}
        onClose={() => setShowReportForm(false)}
        onSubmit={handleUserReport}
        loading={reportLoading}
      />
    </div>
  )
}