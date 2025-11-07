'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'

interface YearSliderProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  className?: string
}

export function YearSlider({
  value,
  onChange,
  min = 2018,
  max = 2050,
  step = 1,
  className,
}: YearSliderProps) {
  const [localValue, setLocalValue] = useState(value)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value)
    setLocalValue(newValue)
    onChange(newValue)
  }

  return (
    <div className={cn('w-full space-y-2', className)}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">Año</label>
        <span className="text-sm font-bold text-primary">{localValue}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={localValue}
        onChange={handleChange}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  )
}
