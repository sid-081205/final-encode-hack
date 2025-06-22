'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { FireData } from '@/lib/api'

interface FireMapProps {
  fires: FireData[]
}

// Component to handle map bounds updates
function MapBounds({ fires }: { fires: FireData[] }) {
  const map = useMap()

  useEffect(() => {
    if (fires.length > 0) {
      const bounds = fires.map(fire => [fire.latitude, fire.longitude] as [number, number])
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [fires, map])

  return null
}

export default function FireMap({ fires }: FireMapProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="w-full h-full bg-gray-100 flex items-center justify-center">
        <div className="text-smoke-gray">loading map...</div>
      </div>
    )
  }

  // Default center for Northern India
  const defaultCenter: [number, number] = [30.0668, 75.8371]
  const defaultZoom = 7

  const getFireColor = (frp: number) => {
    // Simple Green, Orange, Red color scale with 40 MW red threshold
    if (frp >= 40) return '#DC2626' // High power - bright red
    if (frp >= 10) return '#FB923C' // Medium power - lighter orange
    return '#22C55E' // Low power - green (fires <10 MW)
  }

  const getFireSize = (frp: number) => {
    // Smaller sizing scale for all dots
    if (frp >= 40) return 10  // High power - red (smaller)
    if (frp >= 10) return 8   // Medium power - orange (smaller)
    return 6 // Low power - green (smaller but more of them)
  }

  const getBorderColor = (frp: number) => {
    // Subtle border colors for professional look
    if (frp >= 50) return '#FFFFFF' // White border for high severity
    if (frp >= 20) return '#FEF3C7' // Light yellow border for medium-high
    return '#F3F4F6' // Light gray border for lower severity
  }

  const getOpacity = (frp: number) => {
    // Less translucent, more opaque markers
    if (frp >= 50) return 1.0  // Fully opaque for high severity
    if (frp >= 20) return 0.95
    if (frp >= 10) return 0.9
    return 0.85  // Still quite opaque for low severity
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
      
      {fires.map((fire) => (
        <CircleMarker
          key={fire.id}
          center={[fire.latitude, fire.longitude]}
          radius={getFireSize(fire.frp || 0)}
          fillColor={getFireColor(fire.frp || 0)}
          color={getBorderColor(fire.frp || 0)}
          weight={1}
          opacity={getOpacity(fire.frp || 0)}
          fillOpacity={getOpacity(fire.frp || 0) * 0.95}
          className="fire-marker"
          bubblingMouseEvents={false}
          interactive={true}
        >
          <Popup>
            <div className="p-2 min-w-[200px]">
              <h4 className="font-semibold mb-2">fire detection #{fire.id}</h4>
              <div className="space-y-1 text-xs">
                <div><strong>location:</strong> {fire.latitude.toFixed(4)}, {fire.longitude.toFixed(4)}</div>
                <div><strong>brightness:</strong> {fire.brightness.toFixed(1)}k</div>
                <div><strong>confidence:</strong> {fire.confidence}%</div>
                <div><strong>source:</strong> {fire.source}</div>
                <div><strong>detected:</strong> {fire.acq_date} at {fire.acq_time.slice(0,2)}:{fire.acq_time.slice(2,4)}</div>
                {fire.frp && <div><strong>fire power:</strong> {fire.frp.toFixed(1)} mw</div>}
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
      
      <MapBounds fires={fires} />
    </MapContainer>
  )
}