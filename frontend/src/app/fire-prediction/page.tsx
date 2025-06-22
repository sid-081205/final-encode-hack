'use client'

import { useState, useEffect } from 'react'
import PredictionMap from '@/components/PredictionMap'
import PredictionFilterPanel from '@/components/PredictionFilterPanel'
import RecentPredictionsPanel from '@/components/RecentPredictionsPanel'
import PredictionMapStats from '@/components/PredictionMapStats'
import PredictionAnalysisModal from '@/components/PredictionAnalysisModal'

export interface PredictionData {
  id: string
  latitude: number
  longitude: number
  probability: number
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  predictedDate: string
  factors: string[]
  confidence: number
  region: string
  createdAt: string
}

export interface PredictionFilterState {
  region: string
  dateRange: 'next-7days' | 'next-14days' | 'next-30days' | 'custom'
  customStartDate?: string
  customEndDate?: string
  confidenceLevel: number
  includeWeather: boolean
  includeCropPattern: boolean
  includeHistorical: boolean
}

export default function FirePrediction() {
  const [predictions, setPredictions] = useState<PredictionData[]>([])
  const [filters, setFilters] = useState<PredictionFilterState>({
    region: 'all-northern-india',
    dateRange: 'next-7days',
    confidenceLevel: 70,
    includeWeather: true,
    includeCropPattern: true,
    includeHistorical: true
  })
  const [loading, setLoading] = useState(false)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)

  const handleFilterChange = (newFilters: PredictionFilterState) => {
    setFilters(newFilters)
  }

  const generatePredictions = async () => {
    setShowAnalysisModal(true)
  }

  const handlePredictionGenerated = (newPredictions: PredictionData[]) => {
    setPredictions(newPredictions)
    setShowAnalysisModal(false)
  }

  return (
    <div className="min-h-screen bg-ash-light">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-charcoal mb-2">fire prediction</h1>
          <p className="text-smoke-gray">ml-powered stubble burning prediction for northern india</p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Filter Panel */}
          <div className="col-span-3">
            <PredictionFilterPanel
              filters={filters}
              onFilterChange={handleFilterChange}
              onGeneratePredictions={generatePredictions}
              loading={loading}
            />
          </div>

          {/* Map Section */}
          <div className="col-span-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <PredictionMapStats predictions={predictions} />
              <div className="h-[600px]">
                <PredictionMap predictions={predictions} />
              </div>
            </div>
          </div>

          {/* Recent Predictions Panel */}
          <div className="col-span-3">
            <RecentPredictionsPanel predictions={predictions} />
          </div>
        </div>
      </div>

      {/* Analysis Modal */}
      <PredictionAnalysisModal
        isOpen={showAnalysisModal}
        onClose={() => setShowAnalysisModal(false)}
        filters={filters}
        onPredictionGenerated={handlePredictionGenerated}
      />
    </div>
  )
}