'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { DataSourceFooter } from './DataSourceFooter'
import { GlossaryModal } from '@/components/modals/GlossaryModal'

interface MainLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Inicio', href: '/' },
  { name: 'Mapa', href: '/mapa' },
  { name: 'Pirámide', href: '/piramide' },
  { name: 'Serie Tiempo', href: '/serie-tiempo' },
  { name: 'Indicadores', href: '/indicadores' },
  { name: 'Bono Demográfico', href: '/bono-demografico' },
  { name: 'Chat IA', href: '/chat' },
]

export function MainLayout({ children }: MainLayoutProps) {
  const pathname = usePathname()
  const [isGlossaryOpen, setIsGlossaryOpen] = useState(false)

  return (
    <div className="min-h-screen flex flex-col">
      {/* Gov.co Header Bar */}
      <div className="w-full bg-[#0943b5] py-[5px]">
        <div className="w-full max-w-[1280px] mx-auto px-4">
          <a href="https://www.gov.co/" target="_blank" rel="noopener noreferrer">
            <img
              src="https://www.dnp.gov.co/assets/logo_govco.svg"
              alt="Logo Gov.co"
              className="h-[27px] min-h-[27px] min-w-[135px]"
            />
          </a>
        </div>
      </div>

      {/* Main Header */}
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
            <button
              onClick={() => setIsGlossaryOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium bg-secondary hover:bg-secondary/80 transition-colors"
              title="Abrir glosario demográfico"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
              </svg>
              Glosario
            </button>
            <span className="text-sm text-muted-foreground">DNP Colombia</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        {children}
      </main>

      {/* DANE Data Source Footer */}
      <DataSourceFooter />

      {/* Glossary Modal */}
      <GlossaryModal open={isGlossaryOpen} onOpenChange={setIsGlossaryOpen} />
    </div>
  )
}
