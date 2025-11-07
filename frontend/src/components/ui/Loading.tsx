import { cn } from '@/lib/utils'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

export function Loading({ size = 'md', className, text }: LoadingProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }

  return (
    <div className={cn('flex flex-col items-center justify-center gap-2', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
          sizes[size]
        )}
      />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}

export function LoadingOverlay({ text = 'Cargando...' }: { text?: string }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-50">
      <Loading size="lg" text={text} />
    </div>
  )
}
