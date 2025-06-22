'use client'

import { Clock, MapPin, Thermometer, Zap } from 'lucide-react'
import { FireData, formatFireTime, formatFireDate, getConfidenceColor, getConfidenceBg, getPowerSeverityColor, getPowerSeverityBg, getPowerSeverityLabel } from '@/lib/api'

interface RecentFiresPanelProps {
  fires: FireData[]
}

export default function RecentFiresPanel({ fires }: RecentFiresPanelProps) {
  // Sort fires by acquisition time (most recent first)
  const sortedFires = [...fires].sort((a, b) => {
    const dateA = new Date(a.acq_datetime).getTime()
    const dateB = new Date(b.acq_datetime).getTime()
    return dateB - dateA
  })

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="font-semibold mb-3">recent fire detections</h3>
        <div className="text-xs text-smoke-gray mb-4">
          showing {sortedFires.length} fire{sortedFires.length !== 1 ? 's' : ''} detected
        </div>

        <div className="space-y-3 max-h-[500px] overflow-y-auto">
          {sortedFires.length === 0 ? (
            <div className="text-center py-8 text-smoke-gray">
              <div className="text-xs">no fires detected in the selected criteria</div>
            </div>
          ) : (
            sortedFires.map((fire) => (
              <div key={fire.id} className="fire-detection-tile min-h-[140px]">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2 flex-1">
                    <div className={`w-3 h-3 rounded-full bg-fire-red animate-pulse-fire flex-shrink-0`}></div>
                    <span className="font-medium text-xs truncate max-w-[120px]">fire #{fire.id}</span>
                  </div>
                </div>
                <div className="mb-3">
                  <div className={`inline-flex px-2 py-1 rounded text-xs border ${getPowerSeverityBg(fire.frp || 0)}`}>
                    <span className={getPowerSeverityColor(fire.frp || 0)}>
                      {getPowerSeverityLabel(fire.frp || 0)} severity
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-xs text-smoke-gray">
                    <MapPin className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{fire.latitude.toFixed(4)}, {fire.longitude.toFixed(4)}</span>
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-smoke-gray">
                    <Clock className="w-3 h-3 flex-shrink-0" />
                    <span className="truncate">{formatFireDate(fire.acq_date)} at {formatFireTime(fire.acq_date, fire.acq_time)}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex items-center space-x-1 text-xs">
                      <Thermometer className="w-3 h-3 text-fire-red flex-shrink-0" />
                      <span className="truncate">{fire.brightness.toFixed(1)}k</span>
                    </div>
                    
                    <div className="flex items-center space-x-1 text-xs">
                      <Zap className="w-3 h-3 text-blue-500 flex-shrink-0" />
                      <span className="truncate">{fire.confidence}% conf</span>
                    </div>
                  </div>

                  <div className="text-xs">
                    <span className="px-2 py-1 bg-gray-100 rounded text-smoke-gray truncate max-w-full inline-block">
                      {fire.source}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {sortedFires.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h4 className="font-semibold mb-3 text-xs">detection summary</h4>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-smoke-gray">total detections:</span>
              <span className="font-medium">{sortedFires.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">high confidence:</span>
              <span className="font-medium">
                {sortedFires.filter(f => f.confidence >= 80).length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">avg brightness:</span>
              <span className="font-medium">
                {(sortedFires.reduce((sum, f) => sum + f.brightness, 0) / sortedFires.length).toFixed(1)}k
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-smoke-gray">data sources:</span>
              <span className="font-medium">
                {Array.from(new Set(sortedFires.map(f => f.source))).length}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}