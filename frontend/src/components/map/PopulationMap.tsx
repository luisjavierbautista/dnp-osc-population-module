'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import type { GeoJSONProps } from 'react-leaflet'
import { formatNumber, formatPercentage, formatDecimal } from '@/lib/utils'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet default icon issue with Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface PopulationMapProps {
  geojsonData: any
  variable: string
  onFeatureClick?: (territorioId: string) => void
}

export function PopulationMap({ geojsonData, variable, onFeatureClick }: PopulationMapProps) {
  const [map, setMap] = useState<L.Map | null>(null)

  // Colombia center coordinates
  const center: [number, number] = [4.5709, -74.2973]
  const zoom = 6

  // Get color based on value
  const getColor = (value: number | null, variable: string): string => {
    if (value === null || value === undefined) return '#cccccc'

    // Define color scales for different variables
    if (variable === 'poblacion_total') {
      return value > 5000000 ? '#800026'
        : value > 2000000 ? '#BD0026'
        : value > 1000000 ? '#E31A1C'
        : value > 500000 ? '#FC4E2A'
        : value > 250000 ? '#FD8D3C'
        : value > 100000 ? '#FEB24C'
        : value > 50000 ? '#FED976'
        : '#FFEDA0'
    } else if (variable === 'pct_urbana') {
      const pct = value * 100 // Convert to percentage
      return pct > 90 ? '#08519c'
        : pct > 80 ? '#3182bd'
        : pct > 70 ? '#6baed6'
        : pct > 60 ? '#9ecae1'
        : pct > 50 ? '#c6dbef'
        : pct > 40 ? '#deebf7'
        : '#f7fbff'
    } else if (variable === 'envejecimiento') {
      return value > 100 ? '#54278f'
        : value > 80 ? '#756bb1'
        : value > 60 ? '#9e9ac8'
        : value > 40 ? '#bcbddc'
        : value > 20 ? '#dadaeb'
        : '#f2f0f7'
    } else if (variable === 'dependencia') {
      return value > 80 ? '#a50f15'
        : value > 70 ? '#de2d26'
        : value > 60 ? '#fb6a4a'
        : value > 50 ? '#fc9272'
        : value > 40 ? '#fcbba1'
        : '#fee5d9'
    }

    return '#cccccc'
  }

  // Format value based on variable type
  const formatValue = (value: number | null, variable: string): string => {
    if (value === null || value === undefined) return 'Sin datos'

    if (variable === 'poblacion_total') {
      return formatNumber(value)
    } else if (variable === 'pct_urbana') {
      return formatPercentage(value * 100)
    } else if (variable === 'envejecimiento' || variable === 'dependencia') {
      return formatDecimal(value)
    }

    return value.toString()
  }

  // Style function for GeoJSON
  const style = (feature: any) => {
    const value = feature?.properties?.value
    return {
      fillColor: getColor(value, variable),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7,
    }
  }

  // Highlight feature on hover
  const highlightFeature = (e: L.LeafletMouseEvent) => {
    const layer = e.target
    layer.setStyle({
      weight: 3,
      color: '#666',
      fillOpacity: 0.9,
    })
    layer.bringToFront()
  }

  // Reset highlight
  const resetHighlight = (e: L.LeafletMouseEvent) => {
    const layer = e.target
    layer.setStyle(style(layer.feature))
  }

  // Click handler
  const onEachFeature = (feature: any, layer: L.Layer) => {
    const properties = feature.properties
    const value = properties?.value
    const territorioId = properties?.territorio_id
    const nombre = properties?.DPTO_CNOMBRE || properties?.MPIO_CNOMBRE || properties?.nombre || 'Desconocido'

    // Bind popup
    layer.bindPopup(`
      <div class="p-2">
        <h3 class="font-bold text-sm mb-1">${nombre}</h3>
        <p class="text-xs">
          <strong>Valor:</strong> ${formatValue(value, variable)}
        </p>
        ${territorioId ? `<p class="text-xs text-gray-500">Código: ${territorioId}</p>` : ''}
      </div>
    `)

    // Add event listeners
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: () => {
        if (onFeatureClick && territorioId) {
          onFeatureClick(territorioId)
        }
      },
    })
  }

  // Fit bounds when geojson loads
  useEffect(() => {
    if (map && geojsonData) {
      const geoJsonLayer = L.geoJSON(geojsonData)
      const bounds = geoJsonLayer.getBounds()
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] })
      }
    }
  }, [map, geojsonData])

  if (!geojsonData) {
    return (
      <div className="h-full flex items-center justify-center bg-muted rounded-lg">
        <p className="text-muted-foreground">Cargando mapa...</p>
      </div>
    )
  }

  return (
    <div className="h-full rounded-lg overflow-hidden relative">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        ref={setMap}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          data={geojsonData}
          style={style}
          onEachFeature={onEachFeature}
          key={JSON.stringify(geojsonData)} // Force re-render when data changes
        />
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-6 right-6 bg-white p-4 rounded-lg shadow-lg z-[1000]">
        <h4 className="text-sm font-semibold mb-2">Leyenda</h4>
        <div className="space-y-1">
          {variable === 'poblacion_total' && (
            <>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#800026' }}></div>
                <span>&gt; 5M</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#BD0026' }}></div>
                <span>2M - 5M</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#E31A1C' }}></div>
                <span>1M - 2M</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FC4E2A' }}></div>
                <span>500K - 1M</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FD8D3C' }}></div>
                <span>250K - 500K</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FEB24C' }}></div>
                <span>100K - 250K</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FED976' }}></div>
                <span>50K - 100K</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FFEDA0' }}></div>
                <span>&lt; 50K</span>
              </div>
            </>
          )}
          {variable === 'pct_urbana' && (
            <>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#08519c' }}></div>
                <span>&gt; 90%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#3182bd' }}></div>
                <span>80-90%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#6baed6' }}></div>
                <span>70-80%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#9ecae1' }}></div>
                <span>60-70%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#c6dbef' }}></div>
                <span>50-60%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#deebf7' }}></div>
                <span>40-50%</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: '#f7fbff' }}></div>
                <span>&lt; 40%</span>
              </div>
            </>
          )}
          {(variable === 'envejecimiento' || variable === 'dependencia') && (
            <>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#54278f' : '#a50f15' }}></div>
                <span>Alto</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#756bb1' : '#de2d26' }}></div>
                <span>Medio-Alto</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#9e9ac8' : '#fb6a4a' }}></div>
                <span>Medio</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#bcbddc' : '#fc9272' }}></div>
                <span>Medio-Bajo</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#dadaeb' : '#fcbba1' }}></div>
                <span>Bajo</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: variable === 'envejecimiento' ? '#f2f0f7' : '#fee5d9' }}></div>
                <span>Muy Bajo</span>
              </div>
            </>
          )}
          <div className="flex items-center gap-2 text-xs mt-2 pt-2 border-t">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#cccccc' }}></div>
            <span>Sin datos</span>
          </div>
        </div>
      </div>
    </div>
  )
}
