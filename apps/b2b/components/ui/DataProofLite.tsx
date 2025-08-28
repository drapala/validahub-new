'use client'

import React, { useState, useCallback } from 'react'
import { Check, AlertCircle } from 'lucide-react'
import { Button } from './button'

// Versão leve com apenas 4 linhas visíveis (reduz DOM nodes)
const VALIDATION_ROWS = [
  {
    field: "EAN/GTIN",
    bad: "789012345678",
    good: "7890123456789",
    status: "🔴 Rejeição automática → ✅ Aceito"
  },
  {
    field: "Título",
    bad: "CELULAR SAMSUNG!!!",
    good: "Samsung Galaxy A54 5G 128GB",
    status: "🟡 Penalidade SEO → ✅ Otimizado"
  },
  {
    field: "Preço",
    bad: "R$ 2,499.00",
    good: "R$ 2.499,00",
    status: "🔴 Formato incorreto → ✅ Aceito"
  },
  {
    field: "Categoria",
    bad: "Sem categoria",
    good: "MLB1002 - Celulares",
    status: "🔴 Bloqueio → ✅ Mapeada"
  }
]

export default function DataProofLite() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const [fixedRows, setFixedRows] = useState<Set<number>>(new Set())

  const handleMouseEnter = useCallback((index: number) => {
    setHoveredIndex(index)
    setFixedRows(prev => new Set([...prev, index]))
  }, [])

  const handleMouseLeave = useCallback(() => {
    setHoveredIndex(null)
  }, [])

  const handleScrollToPricing = useCallback(() => {
    const pricingSection = document.querySelector('[data-section="pricing"]')
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'auto' })
    }
  }, [])

  return (
    <div className="min-h-[600px] w-full text-neutral-100 p-6 md:p-10" data-section="data">
      <div className="mx-auto max-w-4xl">
        {/* Header simplificado */}
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold">
            Validação com <span className="text-green-400">regras reais</span>
          </h2>
          <p className="mt-3 text-lg text-neutral-300">
            Passe o mouse para ver a correção automática
          </p>
        </div>

        {/* Tabela simplificada */}
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="space-y-4">
            {VALIDATION_ROWS.map((row, index) => (
              <div
                key={index}
                onMouseEnter={() => handleMouseEnter(index)}
                onMouseLeave={handleMouseLeave}
                className={`
                  p-4 rounded-lg border-2 transition-all duration-300 cursor-pointer
                  ${fixedRows.has(index) 
                    ? 'border-green-500 bg-green-500/10' 
                    : 'border-gray-600 bg-gray-700/50 hover:border-yellow-500'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-white mb-2">{row.field}</div>
                    <div className="text-sm">
                      {hoveredIndex === index || fixedRows.has(index) ? (
                        <div className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-green-400" />
                          <span className="text-green-400">{row.good}</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 text-red-400" />
                          <span className="text-red-300 line-through">{row.bad}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">
                    {row.status}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Progress bar simplificado */}
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-400">Correções</span>
              <span className="text-green-400 font-semibold">
                {fixedRows.size}/{VALIDATION_ROWS.length}
              </span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-500"
                style={{ width: `${(fixedRows.size / VALIDATION_ROWS.length) * 100}%` }}
              />
            </div>
          </div>

          {/* CTA */}
          {fixedRows.size === VALIDATION_ROWS.length && (
            <div className="mt-6 text-center">
              <p className="text-green-400 font-semibold mb-4">
                ✅ Todos os erros corrigidos!
              </p>
              <Button
                onClick={handleScrollToPricing}
                className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400"
              >
                Corrigir meu CSV agora
              </Button>
            </div>
          )}
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Baseado em 1M+ de rejeições reais dos principais marketplaces
        </p>
      </div>
    </div>
  )
}