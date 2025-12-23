'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { populationApi } from '@/services/api'
import { formatTerritory } from '@/utils/territoryFormatter'

type TerritoryLevel = 'DEPARTAMENTAL' | 'MUNICIPAL' | 'ALL'

interface TerritorySelectProps {
  value: string
  onChange: (value: string) => void
  nivel?: TerritoryLevel
  className?: string
}

export function TerritorySelect({ value, onChange, nivel: initialNivel = 'ALL', className = '' }: TerritorySelectProps) {
  const [nivel, setNivel] = useState<TerritoryLevel>(initialNivel)
  const [search, setSearch] = useState('')

  const { data: territories, isLoading } = useQuery({
    queryKey: ['territories', nivel, search],
    queryFn: () => populationApi.getTerritories({
      nivel: nivel === 'ALL' ? undefined : nivel,
      search: search || undefined,
      limit: 1000,
    }),
  })

  return (
    <div className="space-y-3">
      {/* Filtro por nivel */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Tipo de Territorio
        </label>
        <div className="flex gap-1">
          <button
            onClick={() => setNivel('ALL')}
            className={`flex-1 px-2 py-2 rounded-md text-xs ${
              nivel === 'ALL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Todos
          </button>
          <button
            onClick={() => setNivel('DEPARTAMENTAL')}
            className={`flex-1 px-2 py-2 rounded-md text-xs ${
              nivel === 'DEPARTAMENTAL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Deptos
          </button>
          <button
            onClick={() => setNivel('MUNICIPAL')}
            className={`flex-1 px-2 py-2 rounded-md text-xs ${
              nivel === 'MUNICIPAL'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary'
            }`}
          >
            Mpios
          </button>
        </div>
      </div>

      {/* Búsqueda */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Buscar
        </label>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Nombre o código..."
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      {/* Selector de territorio */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Territorio
        </label>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full px-3 py-2 border rounded-md ${className}`}
          disabled={isLoading}
        >
          {isLoading && <option>Cargando...</option>}
          {!isLoading && (
            <>
              {territories?.map((t) => (
                <option key={t.territorio_id} value={t.territorio_id}>
                  {formatTerritory(t)}
                </option>
              ))}
            </>
          )}
        </select>
        {territories && (
          <p className="text-xs text-muted-foreground mt-1">
            {territories.length} territorio{territories.length !== 1 ? 's' : ''} encontrado{territories.length !== 1 ? 's' : ''}
          </p>
        )}
      </div>
    </div>
  )
}
