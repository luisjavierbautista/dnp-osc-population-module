'use client'

import type { AreaGeografica } from '@/types/population'

interface AreaSelectProps {
  value: AreaGeografica
  onChange: (value: AreaGeografica) => void
  className?: string
}

export function AreaSelect({ value, onChange, className }: AreaSelectProps) {
  const areas: { value: AreaGeografica; label: string }[] = [
    { value: 'Total', label: 'Total' },
    { value: 'Cabecera Municipal', label: 'Cabecera Municipal' },
    { value: 'Centros Poblados y Rural Disperso', label: 'Centros Poblados y Rural Disperso' },
  ]

  return (
    <div className={className}>
      <label htmlFor="area-select" className="block text-sm font-medium mb-2">
        Área Geográfica
      </label>
      <select
        id="area-select"
        value={value}
        onChange={(e) => onChange(e.target.value as AreaGeografica)}
        className="w-full px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
      >
        {areas.map((area) => (
          <option key={area.value} value={area.value}>
            {area.label}
          </option>
        ))}
      </select>
    </div>
  )
}
