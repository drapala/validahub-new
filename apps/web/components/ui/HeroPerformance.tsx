'use client'

import { useState, useEffect, useCallback, memo } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRight, Check, AlertCircle } from 'lucide-react'

const errors = [
  { type: 'Título > 60 caracteres', status: 'Corrigido automaticamente' },
  { type: 'Preço com formatação errada', status: 'Formatado para MELI' },
  { type: 'EAN/GTIN inválido', status: 'Validado e corrigido' },
  { type: 'Categoria inexistente', status: 'Mapeada corretamente' },
  { type: 'Imagem sem resolução', status: 'Alertado antes do envio' }
]

const ErrorCard = memo(({ currentError }: { currentError: number }) => (
  <Card className="mb-16 bg-black/30 border-gray-700 max-w-2xl mx-auto">
    <CardContent className="p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-red-400" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
          </div>
          <div className="text-left">
            <p className="text-sm text-gray-500">Erro detectado:</p>
            <p className="text-white font-semibold">{errors[currentError].type}</p>
          </div>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-600 mx-4" />
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-gray-500">ValidaHub:</p>
            <p className="text-green-400 font-semibold">{errors[currentError].status}</p>
          </div>
          <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
            <Check className="w-6 h-6 text-green-400" />
          </div>
        </div>
      </div>
      <div className="mt-4 flex gap-1 justify-center">
        {errors.map((_, index) => (
          <div
            key={index}
            className={`h-1 w-8 rounded-full transition-all duration-300 ${
              index === currentError ? 'bg-green-400' : 'bg-gray-700'
            }`}
          />
        ))}
      </div>
    </CardContent>
  </Card>
))
ErrorCard.displayName = 'ErrorCard'

export default function HeroPerformance() {
  const [currentError, setCurrentError] = useState(0)
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  useEffect(() => {
    if (!mounted) return
    const interval = setInterval(() => {
      setCurrentError((prev) => (prev + 1) % errors.length)
    }, 2500)
    return () => clearInterval(interval)
  }, [mounted])

  const handleStartNow = useCallback(() => {
    const dataSection = document.querySelector('[data-section="data"]')
    if (dataSection) {
      dataSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [])

  const handleCalculateROI = useCallback(() => {
    const calculatorSection = document.querySelector('[data-section="calculator"]')
    if (calculatorSection) {
      calculatorSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [])

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/[0.01] bg-[size:80px_80px]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-green-500/10 rounded-full blur-3xl" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white tracking-tight mb-6 opacity-0 animate-fadeInUp">
            Cada produto rejeitado custa
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400"> R$127/dia </span>
            em vendas perdidas
          </h1>

          <p className="text-lg sm:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed opacity-0 animate-fadeInUp animation-delay-200">
            <span className="text-white font-semibold">3 milhões de sellers no Brasil</span> perdem 
            16h/mês corrigindo planilhas manualmente. Enquanto você lê isso, seus concorrentes 
            já validaram e publicaram com ValidaHub.
          </p>
          
          {mounted && (
            <div className="opacity-0 animate-fadeInUp animation-delay-400">
              <ErrorCard currentError={currentError} />
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <div className="relative group opacity-0 animate-fadeInUp animation-delay-600">
              <div className="absolute -inset-[1px] bg-gradient-to-r from-green-500 via-emerald-500 to-blue-500 rounded-lg opacity-75 group-hover:opacity-100 blur-sm transition duration-300" />
              <Button
                size="xl"
                onClick={handleStartNow}
                className="relative min-w-[250px] font-bold bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 text-white border-0 transition-transform duration-200 hover:scale-[1.02]"
              >
                Validar CSV agora (grátis)
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
              </Button>
            </div>
            
            <div className="opacity-0 animate-fadeInUp animation-delay-700">
              <Button
                size="xl"
                variant="outline"
                onClick={handleCalculateROI}
                className="min-w-[250px] border-red-500/50 text-red-300 hover:bg-red-500/10 transition-colors duration-200"
              >
                Calcular meu prejuízo agora
              </Button>
            </div>
          </div>

          <div className="mt-16 flex flex-col sm:flex-row gap-8 justify-center items-center text-gray-500 opacity-0 animate-fadeIn animation-delay-800">
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-400" />
              <span className="text-white font-semibold">30 segundos para validar</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-400" />
              <span className="text-white font-semibold">1.247 sellers já testaram</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-400" />
              <span className="text-white font-semibold">{'<'}3% de rejeição garantida</span>
            </div>
          </div>
        </div>
      </div>

      {mounted && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 opacity-0 animate-fadeIn animation-delay-1000">
          <svg className="w-6 h-6 text-gray-500 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      )}
      
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .animate-fadeInUp {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out forwards;
        }
        
        .animation-delay-200 { animation-delay: 200ms; }
        .animation-delay-400 { animation-delay: 400ms; }
        .animation-delay-600 { animation-delay: 600ms; }
        .animation-delay-700 { animation-delay: 700ms; }
        .animation-delay-800 { animation-delay: 800ms; }
        .animation-delay-1000 { animation-delay: 1s; }
      `}</style>
    </section>
  )
}