'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { PredictionData } from '@/app/fire-prediction/page'

interface PredictionMapProps {
  predictions: PredictionData[]
}

// Component to handle map bounds updates
function MapBounds({ predictions }: { predictions: PredictionData[] }) {
  const map = useMap()

  useEffect(() => {
    if (predictions.length > 0) {
      const bounds = predictions.map(pred => [pred.latitude, pred.longitude] as [number, number])
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [predictions, map])

  return null
}

export default function PredictionMap({ predictions }: PredictionMapProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="w-full h-full bg-gray-100 flex items-center justify-center">
        <div className="text-smoke-gray">loading prediction map...</div>
      </div>
    )
  }

  // Default center for Northern India
  const defaultCenter: [number, number] = [30.0668, 75.8371]
  const defaultZoom = 7

  const getConfidenceColor = (confidence: number) => {
    // Green, orange, red color scheme matching fire detection page
    if (confidence >= 80) return '#DC2626' // High confidence - bright red
    if (confidence >= 60) return '#FB923C' // Medium confidence - lighter orange
    return '#22C55E' // Low confidence - green
  }

  const getPredictionSize = (confidence: number) => {
    // Size based on confidence level matching detection page
    if (confidence >= 80) return 10  // High confidence - red (bigger)
    if (confidence >= 60) return 8   // Medium confidence - orange
    return 6 // Low confidence - green (smaller)
  }

  const getOpacity = (confidence: number) => {
    // Less translucent, more opaque markers like detection page
    if (confidence >= 80) return 1.0  // Fully opaque for high confidence
    if (confidence >= 60) return 0.95
    return 0.9  // Still quite opaque for low confidence
  }

  const getBorderColor = (confidence: number) => {
    // White border for professional look like detection page
    return '#FFFFFF'
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return 'not available'
      }
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return 'not available'
    }
  }

  const formatCreatedDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return 'not available'
      }
      return date.toLocaleString()
    } catch {
      return 'not available'
    }
  }

  return (
    <MapContainer
      center={defaultCenter}
      zoom={defaultZoom}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {predictions.map((prediction) => (
        <CircleMarker
          key={prediction.id}
          center={[prediction.latitude, prediction.longitude]}
          radius={getPredictionSize(prediction.confidence)}
          fillColor={getConfidenceColor(prediction.confidence)}
          color={getBorderColor(prediction.confidence)}
          weight={1}
          opacity={getOpacity(prediction.confidence)}
          fillOpacity={getOpacity(prediction.confidence) * 0.95}
          className="prediction-marker"
          bubblingMouseEvents={false}
          interactive={true}
        >
          <Popup>
            <div className="p-2 min-w-[220px]">
              <h4 className="font-semibold mb-2 flex items-center">
                prediction #{prediction.id}
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  prediction.riskLevel === 'critical' ? 'bg-red-100 text-red-800' :
                  prediction.riskLevel === 'high' ? 'bg-orange-100 text-orange-800' :
                  prediction.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {prediction.riskLevel} risk
                </span>
              </h4>
              <div className="space-y-1 text-xs">
                <div><strong>location:</strong> {prediction.latitude.toFixed(4)}, {prediction.longitude.toFixed(4)}</div>
                <div><strong>region:</strong> {prediction.region.replace('-', ' ')}</div>
                <div><strong>fire probability:</strong> {prediction.probability}%</div>
                <div><strong>model confidence:</strong> {prediction.confidence}%</div>
                <div><strong>predicted date:</strong> {formatDate(prediction.predictedDate)}</div>
                <div><strong>generated:</strong> {formatCreatedDate(prediction.createdAt)}</div>
                
                {prediction.factors.length > 0 && (
                  <div className="mt-2">
                    <strong>risk factors:</strong>
                    <ul className="mt-1 space-y-1">
                      {prediction.factors.map((factor, index) => (
                        <li key={index} className="text-xs">
                          • {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
      
      <MapBounds predictions={predictions} />
    </MapContainer>
  )
}