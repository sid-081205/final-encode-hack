'use client'

import { Calendar, MapPin, Target, TrendingUp, Brain } from 'lucide-react'
import { PredictionData } from '@/app/fire-prediction/page'

interface RecentPredictionsPanelProps {
  predictions: PredictionData[]
}

export default function RecentPredictionsPanel({ predictions }: RecentPredictionsPanelProps) {
  // Sort predictions by creation time (most recent first) and then by probability (highest first)
  const sortedPredictions = [...predictions].sort((a, b) => {
    const dateA = new Date(a.createdAt).getTime()
    const dateB = new Date(b.createdAt).getTime()
    if (dateA !== dateB) return dateB - dateA
    return b.probability - a.probability
  })

  const formatDate = (dateString: string) => {
    if (!dateString) return 'unknown date'
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'unknown date'
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
  }

  const formatTime = (dateString: string) => {
    if (!dateString) return 'unknown time'
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'unknown time'
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    })
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'text-red-600'
      case 'high': return 'text-fire-red'
      case 'medium': return 'text-fire-orange'
      case 'low': return 'text-green-600'
      default: return 'text-smoke-gray'
    }
  }

  const getRiskBg = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'bg-red-100 border-red-200'
      case 'high': return 'bg-fire-red/10 border-fire-red/20'
      case 'medium': return 'bg-fire-orange/10 border-fire-orange/20'
      case 'low': return 'bg-green-100 border-green-200'
      default: return 'bg-gray-100 border-gray-200'
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    const baseClasses = "w-3 h-3 rounded-full animate-pulse"
    switch (riskLevel) {
      case 'critical': return `${baseClasses} bg-red-600`
      case 'high': return `${baseClasses} bg-fire-red`
      case 'medium': return `${baseClasses} bg-fire-orange`
      case 'low': return `${baseClasses} bg-green-600`
      default: return `${baseClasses} bg-gray-400`
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="font-semibold mb-3">recent predictions</h3>
        <div className="text-xs text-smoke-gray mb-4">
          showing {sortedPredictions.length} prediction{sortedPredictions.length !== 1 ? 's' : ''} generated
        </div>

        <div className="space-y-3 max-h-[500px] overflow-y-auto">
          {sortedPredictions.length === 0 ? (
            <div className="text-center py-8 text-smoke-gray">
              <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-xs">no predictions generated yet</div>
              <div className="text-xs mt-1">click generate predictions to start analysis</div>
            </div>
          ) : (
            sortedPredictions.map((prediction) => (
              <div key={prediction.id} className="fire-detection-tile">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={getRiskIcon(prediction.riskLevel)}></div>
                    <span className="font-medium text-xs">prediction #{prediction.id}</span>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs border ${getRiskBg(prediction.riskLevel)}`}>
                    <span className={getRiskColor(prediction.riskLevel)}>
                      {prediction.riskLevel} risk
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-xs text-smoke-gray">
                    <MapPin className="w-3 h-3" />
                    <span>{prediction.latitude.toFixed(4)}, {prediction.longitude.toFixed(4)}</span>
                  </div>


                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center space-x-1 text-xs">
                      <TrendingUp className="w-3 h-3 text-fire-red" />
                      <span>{prediction.probability}% prob</span>
                    </div>
                    
                    <div className="flex items-center space-x-1 text-xs">
                      <Target className="w-3 h-3 text-fire-orange" />
                      <span>{prediction.confidence}% conf</span>
                    </div>
                  </div>

                  <div className="text-xs">
                    <span className="px-2 py-1 bg-gray-100 rounded text-smoke-gray">
                      {prediction.region.replace('-', ' ')}
                    </span>
                  </div>

                  {prediction.factors.length > 0 && (
                    <div className="text-xs">
                      <div className="font-medium mb-1">risk factors:</div>
                      <div className="space-y-1">
                        {prediction.factors.map((factor, index) => (
                          <div key={index} className="flex items-start">
                            <div className="w-1 h-1 bg-smoke-gray rounded-full mt-1.5 mr-2 flex-shrink-0"></div>
                            <span className="text-smoke-gray">{factor}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {prediction.createdAt && formatDate(prediction.createdAt) !== 'unknown date' && formatTime(prediction.createdAt) !== 'unknown time' && (
                    <div className="text-xs text-smoke-gray pt-1 border-t border-gray-100">
                      generated {formatTime(prediction.createdAt)} on {formatDate(prediction.createdAt)}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {sortedPredictions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h4 className="font-semibold mb-3 text-xs">prediction summary</h4>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-smoke-gray">total predictions:</span>
              <span className="font-medium">{sortedPredictions.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">high risk areas:</span>
              <span className="font-medium">
                {sortedPredictions.filter(p => p.riskLevel === 'critical' || p.riskLevel === 'high').length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">avg probability:</span>
              <span className="font-medium">
                {Math.round(sortedPredictions.reduce((sum, p) => sum + p.probability, 0) / sortedPredictions.length)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">avg confidence:</span>
              <span className="font-medium">
                {Math.round(sortedPredictions.reduce((sum, p) => sum + p.confidence, 0) / sortedPredictions.length)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">regions covered:</span>
              <span className="font-medium">
                {Array.from(new Set(sortedPredictions.map(p => p.region))).length}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}