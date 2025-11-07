'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

interface MainLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Inicio', href: '/' },
  { name: 'Mapa', href: '/mapa' },
  { name: 'Pirámide', href: '/piramide' },
  { name: 'Comparador', href: '/comparador' },
  { name: 'Bono Demográfico', href: '/bono-demografico' },
]

export function MainLayout({ children }: MainLayoutProps) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <div className="mr-4 flex">
            <Link href="/" className="mr-6 flex items-center space-x-2">
              <span className="font-bold text-xl">Módulo de Población</span>
            </Link>
          </div>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            {navigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'transition-colors hover:text-foreground/80',
                  pathname === item.href
                    ? 'text-foreground'
                    : 'text-foreground/60'
                )}
              >
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="ml-auto flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">DNP Colombia</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Observatorio del Sistema de Ciudades - DNP Colombia
          </p>
          <p className="text-center text-sm text-muted-foreground md:text-right">
            Fuente: DANE - Proyecciones de Población 2018-2050
          </p>
        </div>
      </footer>
    </div>
  )
}
