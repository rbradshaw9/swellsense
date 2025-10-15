import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Custom surfboard marker icon
const surfboardIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0ea5e9" stroke="white" stroke-width="2">
      <ellipse cx="12" cy="12" rx="3" ry="10" />
    </svg>
  `),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

interface SurfSpot {
  id: number
  name: string
  lat: number
  lon: number
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

interface MapPRProps {
  onSpotSelect: (spot: { name: string; lat: number; lon: number }) => void
  selectedSpot?: { name: string; lat: number; lon: number } | null
}

// Component to handle map recenter
function RecenterMap({ center }: { center: [number, number] }) {
  const map = useMap()
  
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  
  return null
}

const MapPR: React.FC<MapPRProps> = ({ onSpotSelect, selectedSpot }) => {
  const [surfSpots, setSurfSpots] = useState<SurfSpot[]>([])
  const [loading, setLoading] = useState(true)
  const [center, setCenter] = useState<[number, number]>([18.4, -67.0])

  useEffect(() => {
    // Load surf spots from JSON file
    fetch('/data/surf_spots.json')
      .then(res => res.json())
      .then(data => {
        setSurfSpots(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading surf spots:', err)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    // Update center when selected spot changes
    if (selectedSpot) {
      setCenter([selectedSpot.lat, selectedSpot.lon])
    }
  }, [selectedSpot])

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-700 bg-green-100'
      case 'intermediate': return 'text-yellow-700 bg-yellow-100'
      case 'advanced': return 'text-red-700 bg-red-100'
      default: return 'text-gray-700 bg-gray-100'
    }
  }

  const getDifficultyEmoji = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '🟢'
      case 'intermediate': return '🟡'
      case 'advanced': return '🔴'
      default: return '⚪'
    }
  }

  if (loading) {
    return (
      <div className="w-full h-[450px] bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading surf spots...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-[450px] bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <MapContainer 
        center={center} 
        zoom={9} 
        scrollWheelZoom={true}
        className="h-full w-full z-0"
        zoomControl={true}
      >
        <RecenterMap center={center} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {surfSpots.map((spot) => (
          <Marker
            key={spot.id}
            position={[spot.lat, spot.lon]}
            icon={surfboardIcon}
            eventHandlers={{
              click: () => {
                onSpotSelect({ name: spot.name, lat: spot.lat, lon: spot.lon })
              },
            }}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <h3 className="font-bold text-gray-900 mb-2 text-base">
                  {spot.name}
                </h3>
                <p className="text-sm text-gray-700 mb-2">
                  {spot.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(spot.difficulty)}`}>
                    {getDifficultyEmoji(spot.difficulty)} {spot.difficulty}
                  </span>
                  <button
                    onClick={() => onSpotSelect({ name: spot.name, lat: spot.lat, lon: spot.lon })}
                    className="text-xs px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    View Forecast
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

export default MapPR
