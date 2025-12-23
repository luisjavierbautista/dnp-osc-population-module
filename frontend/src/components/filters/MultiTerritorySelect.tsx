'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { populationApi } from '@/services/api'
import { formatTerritory } from '@/utils/territoryFormatter'

type TerritoryLevel = 'DEPARTAMENTAL' | 'MUNICIPAL' | 'ALL'

interface Territory {
  territorio_id: string
  nombre: string
  nivel: string
  dp?: string
  mpio?: string
}

interface MultiTerritorySelectProps {
  value: string[]
  onChange: (value: string[]) => void
  onTerritoriesLoaded?: (territories: Territory[]) => void
  maxSelections?: number
  className?: string
}

export function MultiTerritorySelect({
  value,
  onChange,
  onTerritoriesLoaded,
  maxSelections = 10,
  className = ''
}: MultiTerritorySelectProps) {
  const [nivel, setNivel] = useState<TerritoryLevel>('ALL')
  const [search, setSearch] = useState('')

  const { data: territories, isLoading } = useQuery({
    queryKey: ['territories', nivel, search],
    queryFn: () => populationApi.getTerritories({
      nivel: nivel === 'ALL' ? undefined : nivel,
      search: search || undefined,
      limit: 100, // Show first 100 results
    }),
  })

  // Notify parent when territories are loaded
  useEffect(() => {
    if (territories && onTerritoriesLoaded) {
      onTerritoriesLoaded(territories)
    }
  }, [territories, onTerritoriesLoaded])

  const toggleTerritory = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((t) => t !== id))
    } else {
      if (value.length < maxSelections) {
        onChange([...value, id])
      }
    }
  }

  const handleSelectAll = () => {
    if (!territories) return
    const visibleIds = territories.slice(0, maxSelections).map(t => t.territorio_id)
    onChange(visibleIds)
  }

  const handleClearAll = () => {
    onChange([])
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Level filter */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Tipo de Territorio
        </label>
        <div className="flex gap-2">
          <button
            onClick={() => setNivel('ALL')}
            className={`flex-1 px-3 py-2 rounded-md text-xs ${
              nivel === 'ALL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Todos
          </button>
          <button
            onClick={() => setNivel('DEPARTAMENTAL')}
            className={`flex-1 px-3 py-2 rounded-md text-xs ${
              nivel === 'DEPARTAMENTAL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Deptos
          </button>
          <button
            onClick={() => setNivel('MUNICIPAL')}
            className={`flex-1 px-3 py-2 rounded-md text-xs ${
              nivel === 'MUNICIPAL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Mpios
          </button>
        </div>
      </div>

      {/* Search */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Buscar
        </label>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Nombre o código..."
          className="w-full px-3 py-2 text-sm border rounded-md"
        />
      </div>

      {/* Selection controls */}
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium">
          Territorios ({value.length}/{maxSelections})
        </label>
        <div className="flex gap-1">
          <button
            onClick={handleSelectAll}
            disabled={isLoading || !territories || territories.length === 0}
            className="text-xs px-2 py-1 text-primary hover:underline disabled:opacity-50"
          >
            Seleccionar todos
          </button>
          <button
            onClick={handleClearAll}
            disabled={value.length === 0}
            className="text-xs px-2 py-1 text-destructive hover:underline disabled:opacity-50"
          >
            Limpiar
          </button>
        </div>
      </div>

      {/* Territory list */}
      <div className="border rounded-md max-h-64 overflow-y-auto">
        {isLoading && (
          <div className="p-4 text-sm text-center text-muted-foreground">
            Cargando...
          </div>
        )}

        {!isLoading && territories && territories.length === 0 && (
          <div className="p-4 text-sm text-center text-muted-foreground">
            No se encontraron territorios
          </div>
        )}

        {!isLoading && territories && territories.length > 0 && (
          <div className="space-y-1 p-2">
            {territories.map((territorio) => (
              <label
                key={territorio.territorio_id}
                className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-accent ${
                  value.includes(territorio.territorio_id) ? 'bg-accent/50' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={value.includes(territorio.territorio_id)}
                  onChange={() => toggleTerritory(territorio.territorio_id)}
                  disabled={!value.includes(territorio.territorio_id) && value.length >= maxSelections}
                  className="rounded"
                />
                <span className="text-sm flex-1">
                  {formatTerritory(territorio)}
                </span>
              </label>
            ))}
          </div>
        )}
      </div>

      {territories && territories.length > 0 && (
        <p className="text-xs text-muted-foreground">
          Mostrando {Math.min(territories.length, 100)} de {territories.length} territorios
        </p>
      )}
    </div>
  )
}
