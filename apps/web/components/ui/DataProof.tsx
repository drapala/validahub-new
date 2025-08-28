'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion, AnimatePresence, useInView } from 'framer-motion'
import { 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  AlertTriangle, 
  Play,
  Pause,
  ArrowRight,
  Sparkles,
  TrendingUp
} from 'lucide-react'

// Real marketplace validation rules with severity levels
const VALIDATION_RULES = [
  {
    id: 1,
    field: 'EAN/GTIN',
    bad: '789012345678',
    good: '7890123456789',
    type: 'fatal' as const,
    rule: 'Dígito verificador inválido',
    impact: 'Bloqueio garantido',
    savings: 42 // R$/dia recuperados
  },
  {
    id: 2,
    field: 'Categoria',
    bad: 'Eletrônicos > Sem categoria',
    good: 'MLB1002 - Celulares',
    type: 'fatal' as const,
    rule: 'Categoria não mapeada',
    impact: 'Rejeição automática',
    savings: 38
  },
  {
    id: 3,
    field: 'Título',
    bad: 'CELULAR SAMSUNG PROMOÇÃO!!!',
    good: 'Samsung Galaxy A54 5G 128GB',
    type: 'critical' as const,
    rule: 'Termos promocionais proibidos',
    impact: '35% de rejeição',
    savings: 21
  },
  {
    id: 4,
    field: 'Preço',
    bad: 'R$ 2,499.00',
    good: 'R$ 2.499,00',
    type: 'critical' as const,
    rule: 'Formato USD incompatível',
    impact: '28% de falha',
    savings: 18
  },
  {
    id: 5,
    field: 'Estoque',
    bad: '1 unidade',
    good: '25 unidades',
    type: 'warning' as const,
    rule: 'Quantidade abaixo do ideal',
    impact: '-40% ranking',
    savings: 8
  },
  {
    id: 6,
    field: 'Descrição',
    bad: 'Celular novo.',
    good: 'Smartphone 6.4", 50MP, 6GB RAM',
    type: 'warning' as const,
    rule: 'Descrição muito curta',
    impact: '-25% conversão',
    savings: 5
  }
]

type TabType = 'all' | 'fatal' | 'critical' | 'warning' | 'fixed'

export default function DataProof() {
  const [fixedItems, setFixedItems] = useState<Set<number>>(new Set())
  const [activeTab, setActiveTab] = useState<TabType>('all')
  const [isSimulating, setIsSimulating] = useState(false)
  const [totalSavings, setTotalSavings] = useState(0)
  const [showSavingsFlash, setShowSavingsFlash] = useState(false)
  const [lastSavingsAmount, setLastSavingsAmount] = useState(0)
  
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: false, margin: "-200px" })

  // Auto-start simulation when in view
  useEffect(() => {
    if (isInView && fixedItems.size === 0) {
      setTimeout(() => startSimulation(), 500)
    }
  }, [isInView])

  // Count by type
  const counts = {
    fatal: VALIDATION_RULES.filter(r => r.type === 'fatal' && !fixedItems.has(r.id)).length,
    critical: VALIDATION_RULES.filter(r => r.type === 'critical' && !fixedItems.has(r.id)).length,
    warning: VALIDATION_RULES.filter(r => r.type === 'warning' && !fixedItems.has(r.id)).length,
    fixed: fixedItems.size
  }

  const toggleFix = (id: number) => {
    setFixedItems(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
        const rule = VALIDATION_RULES.find(r => r.id === id)
        if (rule) {
          setTotalSavings(current => Math.max(0, current - rule.savings))
        }
      } else {
        next.add(id)
        const rule = VALIDATION_RULES.find(r => r.id === id)
        if (rule) {
          setTotalSavings(current => current + rule.savings)
          // Show flash on 2nd and 4th fix
          if (next.size === 2 || next.size === 4) {
            setLastSavingsAmount(rule.savings)
            setShowSavingsFlash(true)
            setTimeout(() => setShowSavingsFlash(false), 2000)
          }
        }
      }
      return next
    })
  }

  const startSimulation = () => {
    if (isSimulating) {
      setIsSimulating(false)
      return
    }

    setIsSimulating(true)
    setFixedItems(new Set())
    setTotalSavings(0)

    VALIDATION_RULES.forEach((rule, index) => {
      setTimeout(() => {
        toggleFix(rule.id)
        if (index === VALIDATION_RULES.length - 1) {
          setTimeout(() => setIsSimulating(false), 300)
        }
      }, (index + 1) * 600)
    })
  }

  const resetAll = () => {
    setFixedItems(new Set())
    setTotalSavings(0)
    setIsSimulating(false)
  }

  // Filter rows based on active tab
  const getFilteredRows = () => {
    if (activeTab === 'all') return VALIDATION_RULES
    if (activeTab === 'fixed') return VALIDATION_RULES.filter(r => fixedItems.has(r.id))
    return VALIDATION_RULES.filter(r => 
      r.type === activeTab && !fixedItems.has(r.id)
    )
  }

  const filteredRows = getFilteredRows()

  return (
    <section 
      ref={sectionRef}
      className="py-20 relative overflow-hidden bg-white dark:bg-zinc-950"
      id="data"
      data-section="data"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-6xl mx-auto">
          
          {/* Header */}
          <div className="text-center mb-12">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-4xl sm:text-5xl font-bold text-zinc-900 dark:text-white mb-4"
            >
              Validação em tempo real
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-lg text-zinc-600 dark:text-zinc-300 max-w-2xl mx-auto"
            >
              Clique em uma linha ou rode a simulação para ver como corrigimos erros 
              e quanto isso te devolve por mês
            </motion.p>
          </div>

          {/* Main Card */}
          <Card className="relative overflow-hidden border-zinc-200 dark:border-zinc-800 
            bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md shadow-xl">
            
            {/* Savings Flash */}
            <AnimatePresence>
              {showSavingsFlash && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8, y: -20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: -20 }}
                  className="absolute top-4 right-4 z-20"
                >
                  <div className="flex items-center gap-2 px-4 py-2 rounded-full 
                    bg-emerald-50 dark:bg-emerald-950 border border-emerald-200 dark:border-emerald-800">
                    <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    <span className="text-sm font-bold text-emerald-700 dark:text-emerald-300">
                      +R${lastSavingsAmount}/dia recuperado
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <CardHeader className="pb-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                {/* Progress Bar */}
                <div className="flex-1 max-w-md">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      Progresso da correção
                    </span>
                    <span className="text-sm font-bold tabular-nums text-zinc-900 dark:text-white">
                      {fixedItems.size}/{VALIDATION_RULES.length} corrigidos
                    </span>
                  </div>
                  <div className="relative h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(fixedItems.size / VALIDATION_RULES.length) * 100}%` }}
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-500 to-emerald-400"
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  <Button
                    onClick={startSimulation}
                    variant="default"
                    className="bg-violet-600 dark:bg-emerald-600 hover:bg-violet-700 dark:hover:bg-emerald-700 text-white"
                    disabled={isSimulating && fixedItems.size > 0}
                  >
                    {isSimulating ? (
                      <>
                        <Pause className="w-4 h-4 mr-2" />
                        Pausar
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Simular correções ({6 - fixedItems.size})
                      </>
                    )}
                  </Button>
                  {fixedItems.size > 0 && (
                    <Button
                      onClick={resetAll}
                      variant="outline"
                      size="sm"
                    >
                      Resetar
                    </Button>
                  )}
                </div>
              </div>

              {/* Tabs */}
              <div className="flex items-center gap-1 mt-6 p-1 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
                <button
                  onClick={() => setActiveTab('all')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'all'
                      ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setActiveTab('fatal')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'fatal'
                      ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  Fatais ({counts.fatal})
                </button>
                <button
                  onClick={() => setActiveTab('critical')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'critical'
                      ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  Críticos ({counts.critical})
                </button>
                <button
                  onClick={() => setActiveTab('warning')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'warning'
                      ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  Alertas ({counts.warning})
                </button>
                <button
                  onClick={() => setActiveTab('fixed')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    activeTab === 'fixed'
                      ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm'
                      : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                  }`}
                >
                  Corrigidos ({counts.fixed})
                </button>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div className="divide-y divide-zinc-200 dark:divide-zinc-800">
                <AnimatePresence mode="popLayout">
                  {filteredRows.map((row) => {
                    const isFixed = fixedItems.has(row.id)
                    return (
                      <motion.div
                        key={row.id}
                        layout
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="group"
                      >
                        <button
                          onClick={() => toggleFix(row.id)}
                          className="w-full text-left px-6 py-4 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 
                            transition-colors duration-200"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 flex-1">
                              {/* Status Icon */}
                              <div className="relative">
                                <motion.div
                                  animate={{
                                    scale: isFixed ? [1, 1.2, 1] : 1,
                                    rotate: isFixed ? [0, 180, 360] : 0
                                  }}
                                  transition={{ duration: 0.5 }}
                                >
                                  {isFixed ? (
                                    <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-950 
                                      flex items-center justify-center">
                                      <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                                    </div>
                                  ) : (
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                      row.type === 'fatal'
                                        ? 'bg-red-100 dark:bg-red-950'
                                        : row.type === 'critical'
                                        ? 'bg-amber-100 dark:bg-amber-950'
                                        : 'bg-yellow-100 dark:bg-yellow-950'
                                    }`}>
                                      {row.type === 'fatal' ? (
                                        <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                                      ) : row.type === 'critical' ? (
                                        <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                                      ) : (
                                        <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                                      )}
                                    </div>
                                  )}
                                </motion.div>
                              </div>

                              {/* Field Info */}
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-1">
                                  <span className="font-semibold text-zinc-900 dark:text-white">
                                    {row.field}
                                  </span>
                                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                    isFixed
                                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                                      : row.type === 'fatal'
                                      ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                                      : row.type === 'critical'
                                      ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                                      : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300'
                                  }`}>
                                    {isFixed ? 'Corrigido' : row.rule}
                                  </span>
                                </div>

                                {/* Value Display */}
                                <div className="flex items-center gap-3">
                                  <AnimatePresence mode="wait">
                                    {!isFixed ? (
                                      <motion.div
                                        key="bad"
                                        initial={{ opacity: 1 }}
                                        exit={{ opacity: 0, filter: 'blur(4px)' }}
                                        className="flex items-center gap-2"
                                      >
                                        <span className="text-sm text-zinc-600 dark:text-zinc-400 line-through">
                                          {row.bad}
                                        </span>
                                      </motion.div>
                                    ) : (
                                      <motion.div
                                        key="good"
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="flex items-center gap-2"
                                      >
                                        <span className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">
                                          {row.good}
                                        </span>
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </div>
                              </div>
                            </div>

                            {/* Impact/Savings */}
                            <div className="text-right">
                              {isFixed ? (
                                <motion.div
                                  initial={{ opacity: 0, scale: 0.8 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  className="text-sm font-bold text-emerald-600 dark:text-emerald-400"
                                >
                                  +R${row.savings}/dia
                                </motion.div>
                              ) : (
                                <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                  {row.impact}
                                </div>
                              )}
                            </div>
                          </div>
                        </button>
                      </motion.div>
                    )
                  })}
                </AnimatePresence>
              </div>

              {/* Footer with Total Savings and CTAs */}
              <div className="px-6 py-4 bg-zinc-50 dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-800">
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="text-sm text-zinc-600 dark:text-zinc-400">
                        Total economizado
                      </div>
                      <div className="text-2xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
                        R${totalSavings}/dia
                      </div>
                    </div>
                    {totalSavings > 0 && (
                      <div className="text-sm text-zinc-500 dark:text-zinc-400">
                        = R${(totalSavings * 30).toLocaleString('pt-BR')}/mês
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => {
                        const section = document.querySelector('[data-section="features"]')
                        section?.scrollIntoView({ behavior: 'smooth' })
                      }}
                    >
                      Ver todas as regras
                    </Button>
                    <Button
                      className="bg-violet-600 dark:bg-emerald-600 hover:bg-violet-700 dark:hover:bg-emerald-700 text-white"
                      onClick={() => {
                        const section = document.querySelector('[data-section="calculator"]')
                        section?.scrollIntoView({ behavior: 'smooth' })
                      }}
                    >
                      Validar meu CSV agora
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}