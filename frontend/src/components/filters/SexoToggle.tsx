'use client'

import { cn } from '@/lib/utils'
import type { Sexo } from '@/types/population'

interface SexoToggleProps {
  value: Sexo
  onChange: (value: Sexo) => void
  className?: string
}

export function SexoToggle({ value, onChange, className }: SexoToggleProps) {
  const options: { value: Sexo; label: string }[] = [
    { value: 'T', label: 'Total' },
    { value: 'H', label: 'Hombres' },
    { value: 'M', label: 'Mujeres' },
  ]

  return (
    <div className={className}>
      <label className="block text-sm font-medium mb-2">Sexo</label>
      <div className="inline-flex rounded-md shadow-sm" role="group">
        {options.map((option, index) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              'px-4 py-2 text-sm font-medium border transition-colors',
              index === 0 && 'rounded-l-md',
              index === options.length - 1 && 'rounded-r-md',
              index !== 0 && 'border-l-0',
              value === option.value
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-background text-foreground border-input hover:bg-accent'
            )}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}
