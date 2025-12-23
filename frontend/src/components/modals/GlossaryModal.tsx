'use client'

import { useState, useEffect, useMemo } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { GLOSSARY_TERMS, CATEGORY_LABELS, getTermsByCategory, type GlossaryTerm } from '@/data/glossaryTerms'

interface GlossaryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function GlossaryModal({ open, onOpenChange }: GlossaryModalProps) {
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<GlossaryTerm['category'] | 'all'>('all')
  const [selectedTerm, setSelectedTerm] = useState<GlossaryTerm | null>(null)

  // Filter terms based on search and category
  const filteredTerms = useMemo(() => {
    let terms = selectedCategory === 'all'
      ? GLOSSARY_TERMS
      : getTermsByCategory(selectedCategory)

    if (search.trim()) {
      const lowerSearch = search.toLowerCase()
      terms = terms.filter(term =>
        term.term.toLowerCase().includes(lowerSearch) ||
        term.definition.toLowerCase().includes(lowerSearch) ||
        term.id.toLowerCase().includes(lowerSearch)
      )
    }

    return terms
  }, [search, selectedCategory])

  // Reset search when modal closes
  useEffect(() => {
    if (!open) {
      setSearch('')
      setSelectedCategory('all')
      setSelectedTerm(null)
    }
  }, [open])

  // Keyboard shortcut: ESC to go back from term detail
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selectedTerm) {
        e.preventDefault()
        setSelectedTerm(null)
      }
    }

    if (open) {
      window.addEventListener('keydown', handleKeyDown)
      return () => window.removeEventListener('keydown', handleKeyDown)
    }
  }, [open, selectedTerm])

  const handleTermClick = (term: GlossaryTerm) => {
    setSelectedTerm(term)
  }

  const handleRelatedTermClick = (termId: string) => {
    const term = GLOSSARY_TERMS.find(t => t.id === termId)
    if (term) {
      setSelectedTerm(term)
    }
  }

  const getCategoryColor = (category: GlossaryTerm['category']) => {
    const colors = {
      indicator: 'bg-blue-100 text-blue-800 border-blue-200',
      concept: 'bg-green-100 text-green-800 border-green-200',
      geographic: 'bg-orange-100 text-orange-800 border-orange-200',
      data: 'bg-purple-100 text-purple-800 border-purple-200',
    }
    return colors[category]
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[85vh] p-0 flex flex-col overflow-hidden">
        <DialogHeader className="px-6 pt-6 pb-4 border-b flex-shrink-0">
          <DialogTitle className="text-2xl">Glosario Demográfico</DialogTitle>
          <DialogDescription>
            Términos, conceptos e indicadores clave del análisis poblacional
          </DialogDescription>
        </DialogHeader>

        <div className="px-6 py-4 space-y-4 flex-shrink-0">
          {/* Search bar */}
          <div>
            <Input
              type="text"
              placeholder="Buscar término o concepto..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full"
              autoFocus
            />
          </div>

          {/* Category filters */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              Todos ({GLOSSARY_TERMS.length})
            </button>
            {(Object.keys(CATEGORY_LABELS) as GlossaryTerm['category'][]).map((category) => {
              const count = getTermsByCategory(category).length
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary hover:bg-secondary/80'
                  }`}
                >
                  {CATEGORY_LABELS[category]} ({count})
                </button>
              )
            })}
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 min-h-0 overflow-y-auto px-6 pb-6">
          {selectedTerm ? (
            // Term detail view
            <div className="space-y-4">
              <button
                onClick={() => setSelectedTerm(null)}
                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
              >
                ← Volver a la lista
              </button>

              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <h3 className="text-2xl font-bold flex-1">{selectedTerm.term}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getCategoryColor(selectedTerm.category)}`}>
                    {CATEGORY_LABELS[selectedTerm.category]}
                  </span>
                </div>

                <p className="text-base text-muted-foreground leading-relaxed">
                  {selectedTerm.definition}
                </p>

                {selectedTerm.examples && selectedTerm.examples.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-semibold mb-2">Ejemplos:</h4>
                    <ul className="space-y-2">
                      {selectedTerm.examples.map((example, idx) => (
                        <li key={idx} className="text-sm text-muted-foreground flex gap-2">
                          <span className="text-primary">•</span>
                          <span>{example}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedTerm.relatedTerms && selectedTerm.relatedTerms.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-semibold mb-2">Términos relacionados:</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedTerm.relatedTerms.map((termId) => {
                        const relatedTerm = GLOSSARY_TERMS.find(t => t.id === termId)
                        if (!relatedTerm) return null
                        return (
                          <button
                            key={termId}
                            onClick={() => handleRelatedTermClick(termId)}
                            className="px-3 py-1 rounded-full text-sm bg-secondary hover:bg-secondary/80 transition-colors"
                          >
                            {relatedTerm.term}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            // Terms list view
            <div className="space-y-2">
              {filteredTerms.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p className="text-lg">No se encontraron términos</p>
                  <p className="text-sm mt-1">Intenta con otra búsqueda o categoría</p>
                </div>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-3">
                    {filteredTerms.length} término{filteredTerms.length !== 1 ? 's' : ''} encontrado{filteredTerms.length !== 1 ? 's' : ''}
                  </p>

                  {filteredTerms.map((term) => (
                    <button
                      key={term.id}
                      onClick={() => handleTermClick(term)}
                      className="w-full text-left p-4 rounded-lg border hover:border-primary hover:bg-accent transition-all group"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 space-y-1">
                          <h4 className="font-semibold group-hover:text-primary transition-colors">
                            {term.term}
                          </h4>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {term.definition}
                          </p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium border whitespace-nowrap ${getCategoryColor(term.category)}`}>
                          {CATEGORY_LABELS[term.category]}
                        </span>
                      </div>
                    </button>
                  ))}
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t bg-muted/30 flex-shrink-0">
          <p className="text-xs text-muted-foreground text-center">
            Presiona <kbd className="px-1.5 py-0.5 bg-background border rounded text-xs">ESC</kbd> para {selectedTerm ? 'volver' : 'cerrar'}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}
