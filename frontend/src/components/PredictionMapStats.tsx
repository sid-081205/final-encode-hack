'use client'

import { Brain, Target, TrendingUp, AlertTriangle } from 'lucide-react'
import { PredictionData } from '@/app/fire-prediction/page'

interface PredictionMapStatsProps {
  predictions: PredictionData[]
}

export default function PredictionMapStats({ predictions }: PredictionMapStatsProps) {
  const totalPredictions = predictions.length
  const criticalRiskPredictions = predictions.filter(pred => pred.riskLevel === 'critical').length
  const highRiskPredictions = predictions.filter(pred => pred.riskLevel === 'high').length
  const averageConfidence = predictions.length > 0 
    ? Math.round(predictions.reduce((sum, pred) => sum + pred.confidence, 0) / predictions.length)
    : 0
  const averageProbability = predictions.length > 0 
    ? Math.round(predictions.reduce((sum, pred) => sum + pred.probability, 0) / predictions.length)
    : 0

  const stats = [
    {
      icon: <Brain className="w-5 h-5" />,
      label: 'predictions',
      value: totalPredictions.toString(),
      color: 'text-fire-red'
    },
    {
      icon: <AlertTriangle className="w-5 h-5" />,
      label: 'high risk areas',
      value: (criticalRiskPredictions + highRiskPredictions).toString(),
      color: 'text-fire-orange'
    },
    {
      icon: <Target className="w-5 h-5" />,
      label: 'avg confidence',
      value: `${averageConfidence}%`,
      color: 'text-fire-yellow'
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      label: 'avg probability',
      value: `${averageProbability}%`,
      color: 'text-smoke-gray'
    }
  ]

  const getRiskDistribution = () => {
    const critical = predictions.filter(p => p.riskLevel === 'critical').length
    const high = predictions.filter(p => p.riskLevel === 'high').length
    const medium = predictions.filter(p => p.riskLevel === 'medium').length
    const low = predictions.filter(p => p.riskLevel === 'low').length
    return { critical, high, medium, low }
  }

  const riskDistribution = getRiskDistribution()

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="grid grid-cols-4 gap-4 mb-4">
        {stats.map((stat, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className={`${stat.color}`}>
              {stat.icon}
            </div>
            <div>
              <div className="text-lg font-semibold text-charcoal">
                {stat.value}
              </div>
              <div className="text-xs text-smoke-gray uppercase tracking-wider">
                {stat.label}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {totalPredictions > 0 && (
        <div className="space-y-3">
          {/* Risk Distribution */}
          <div className="bg-ash-light rounded-lg p-3">
            <h4 className="text-xs font-semibold mb-2">risk level distribution</h4>
            <div className="grid grid-cols-4 gap-2 text-xs">
              {riskDistribution.critical > 0 && (
                <div className="text-center">
                  <div className="text-red-600 font-semibold">{riskDistribution.critical}</div>
                  <div className="text-smoke-gray">critical</div>
                </div>
              )}
              {riskDistribution.high > 0 && (
                <div className="text-center">
                  <div className="text-fire-red font-semibold">{riskDistribution.high}</div>
                  <div className="text-smoke-gray">high</div>
                </div>
              )}
              {riskDistribution.medium > 0 && (
                <div className="text-center">
                  <div className="text-fire-orange font-semibold">{riskDistribution.medium}</div>
                  <div className="text-smoke-gray">medium</div>
                </div>
              )}
              {riskDistribution.low > 0 && (
                <div className="text-center">
                  <div className="text-green-600 font-semibold">{riskDistribution.low}</div>
                  <div className="text-smoke-gray">low</div>
                </div>
              )}
            </div>
          </div>

          {/* Alert Banner */}
          {(riskDistribution.critical > 0 || riskDistribution.high > 0) && (
            <div className="bg-fire-red/10 border border-fire-red/20 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-fire-red" />
                <span className="text-xs font-semibold text-fire-red">high risk alert</span>
              </div>
              <div className="text-xs text-charcoal mt-1">
                {riskDistribution.critical > 0 && riskDistribution.high > 0 
                  ? `${riskDistribution.critical} critical and ${riskDistribution.high} high risk predictions identified`
                  : riskDistribution.critical > 0 
                  ? `${riskDistribution.critical} critical risk prediction${riskDistribution.critical > 1 ? 's' : ''} identified`
                  : `${riskDistribution.high} high risk prediction${riskDistribution.high > 1 ? 's' : ''} identified`
                }
              </div>
            </div>
          )}
        </div>
      )}

      {totalPredictions === 0 && (
        <div className="text-center py-4 text-smoke-gray">
          <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <div className="text-xs">no predictions generated yet</div>
          <div className="text-xs mt-1">use the generate predictions button to analyze fire risk</div>
        </div>
      )}
    </div>
  )
}