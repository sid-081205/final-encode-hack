'use client'

import { Flame, TrendingUp, AlertTriangle, Eye } from 'lucide-react'
import { FireData } from '@/lib/api'

interface MapStatsProps {
  fires: FireData[]
}

export default function MapStats({ fires }: MapStatsProps) {
  const totalFires = fires.length
  const highConfidenceFires = fires.filter(fire => fire.confidence >= 80).length
  const averageConfidence = fires.length > 0 
    ? Math.round(fires.reduce((sum, fire) => sum + fire.confidence, 0) / fires.length)
    : 0
  const totalFirePower = fires
    .filter(fire => fire.frp)
    .reduce((sum, fire) => sum + (fire.frp || 0), 0)

  const stats = [
    {
      icon: <Flame className="w-5 h-5" />,
      label: 'active fires',
      value: totalFires.toString(),
      color: 'text-fire-red'
    },
    {
      icon: <AlertTriangle className="w-5 h-5" />,
      label: 'high confidence',
      value: highConfidenceFires.toString(),
      color: 'text-fire-orange'
    },
    {
      icon: <Eye className="w-5 h-5" />,
      label: 'avg confidence',
      value: `${averageConfidence}%`,
      color: 'text-fire-yellow'
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      label: 'total fire power',
      value: `${totalFirePower.toFixed(1)} mw`,
      color: 'text-smoke-gray'
    }
  ]

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="grid grid-cols-4 gap-4">
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
      
      {totalFires > 0 && (
        <div className="mt-4 p-3 bg-fire-red/5 rounded-lg border border-fire-red/20">
          <div className="flex items-center space-x-2">
            <Flame className="w-4 h-4 text-fire-red" />
            <span className="text-xs text-charcoal">
              {totalFires} active fire{totalFires !== 1 ? 's' : ''} detected in the selected region and time range
            </span>
          </div>
        </div>
      )}
    </div>
  )
}