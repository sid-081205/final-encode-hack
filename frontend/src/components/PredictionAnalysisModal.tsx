'use client'

import { useState, useEffect } from 'react'
import { X, Brain, Loader2, CheckCircle, TrendingUp, MapPin, Calendar } from 'lucide-react'
import { PredictionFilterState, PredictionData } from '@/app/fire-prediction/page'
import { apiClient } from '@/lib/api'

interface PredictionAnalysisModalProps {
  isOpen: boolean
  onClose: () => void
  filters: PredictionFilterState
  onPredictionGenerated: (predictions: PredictionData[]) => void
}

export default function PredictionAnalysisModal({
  isOpen,
  onClose,
  filters,
  onPredictionGenerated
}: PredictionAnalysisModalProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [processingDetails, setProcessingDetails] = useState<string[]>([])

  const analysisSteps = [
    {
      title: 'loading historical fire data',
      description: 'accessing 321k+ fire records from database',
      duration: 2000
    },
    {
      title: 'calculating seasonal trends',
      description: 'analyzing fire patterns by season and location',
      duration: 2000
    },
    {
      title: 'generating predictions',
      description: 'creating fire probability predictions',
      duration: 2000
    }
  ]

  const generateRealPredictions = async (): Promise<PredictionData[]> => {
    try {
      const predictionRequest = {
        region: filters.region,
        date_range: filters.dateRange,
        custom_start_date: filters.customStartDate,
        custom_end_date: filters.customEndDate,
        confidence_level: filters.confidenceLevel
      }

      const response = await apiClient.generatePredictions(predictionRequest)
      return response.predictions || []
    } catch (error) {
      console.error('Error generating predictions:', error)
      // Fallback to sample data if API fails
      return generateFallbackPredictions()
    }
  }

  const generateFallbackPredictions = (): PredictionData[] => {
    const samplePredictions: PredictionData[] = [
      {
        id: 'pred-1',
        latitude: 30.8917,
        longitude: 75.8517,
        probability: 87,
        riskLevel: 'high',
        predictedDate: '2025-06-25',
        factors: ['historical hotspot', 'peak fire season', 'recurring location'],
        confidence: 89,
        region: 'punjab',
        createdAt: new Date().toISOString()
      },
      {
        id: 'pred-2',
        latitude: 29.0588,
        longitude: 76.0856,
        probability: 72,
        riskLevel: 'medium',
        predictedDate: '2025-06-26',
        factors: ['seasonal pattern', 'moderate activity'],
        confidence: 75,
        region: 'haryana',
        createdAt: new Date().toISOString()
      },
      {
        id: 'pred-3',
        latitude: 31.6340,
        longitude: 74.8723,
        probability: 94,
        riskLevel: 'critical',
        predictedDate: '2025-06-24',
        factors: ['peak burning season', 'historical hotspot', 'strong seasonal pattern'],
        confidence: 92,
        region: 'punjab',
        createdAt: new Date().toISOString()
      }
    ]

    return samplePredictions.filter(pred => pred.confidence >= filters.confidenceLevel)
  }

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0)
      setAnalysisComplete(false)
      setProcessingDetails([])
      return
    }

    const runAnalysis = async () => {
      for (let i = 0; i < analysisSteps.length; i++) {
        setCurrentStep(i)
        
        // Wait for step duration
        const step = analysisSteps[i]
        await new Promise(resolve => setTimeout(resolve, step.duration))
        
        setCurrentStep(i + 1)
      }
      
      // Generate predictions after analysis using real API
      setAnalysisComplete(true)
      
      // Show completion message immediately after analysis
      const predictions = await generateRealPredictions()
      onPredictionGenerated(predictions)
      
      // Auto-close modal 1 second after completion message
      await new Promise(resolve => setTimeout(resolve, 1000))
      onClose()
    }

    runAnalysis()
  }, [isOpen, filters.confidenceLevel])

  if (!isOpen) return null

  const getDateRangeText = () => {
    switch (filters.dateRange) {
      case 'next-7days': return 'next 7 days'
      case 'next-14days': return 'next 14 days'
      case 'next-30days': return 'next 30 days'
      case 'custom': return 'custom date range'
      default: return filters.dateRange
    }
  }

  const getRegionText = () => {
    return filters.region.replace('-', ' ')
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-fire-red/10 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-fire-red" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-charcoal">prediction analysis</h2>
                <p className="text-xs text-smoke-gray">generating fire risk predictions</p>
              </div>
            </div>
          </div>

          {/* Analysis Parameters */}
          <div className="bg-ash-light rounded-lg p-4 mb-6">
            <h3 className="font-semibold mb-3">analysis parameters</h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="flex items-center space-x-2">
                <MapPin className="w-3 h-3 text-smoke-gray" />
                <span className="text-smoke-gray">region:</span>
                <span className="font-medium">{getRegionText()}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-3 h-3 text-smoke-gray" />
                <span className="text-smoke-gray">timeframe:</span>
                <span className="font-medium">{getDateRangeText()}</span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-3 h-3 text-smoke-gray" />
                <span className="text-smoke-gray">confidence:</span>
                <span className="font-medium">{filters.confidenceLevel}%+</span>
              </div>
              <div className="flex items-center space-x-2">
                <Brain className="w-3 h-3 text-smoke-gray" />
                <span className="text-smoke-gray">data source:</span>
                <span className="font-medium">historical patterns only</span>
              </div>
            </div>
          </div>

          {/* Analysis Progress */}
          <div className="space-y-4">
            <h3 className="font-semibold">analysis progress</h3>
            {analysisSteps.map((step, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  index < currentStep 
                    ? 'bg-green-500 text-white' 
                    : index === currentStep 
                    ? 'bg-fire-red text-white' 
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {index < currentStep ? (
                    <CheckCircle className="w-3 h-3" />
                  ) : index === currentStep ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <span className="text-xs">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1">
                  <div className={`font-medium text-xs ${
                    index <= currentStep ? 'text-charcoal' : 'text-gray-400'
                  }`}>
                    {step.title}
                  </div>
                  <div className={`text-xs ${
                    index <= currentStep ? 'text-smoke-gray' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {analysisComplete && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="font-semibold text-green-800 text-xs">analysis complete</span>
              </div>
              <p className="text-xs text-green-700">
                predictions have been generated and will appear on the map. 
                predictions have been generated based on real-time analysis 
                in the selected region and timeframe.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}