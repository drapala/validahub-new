'use client'

import { useState, useEffect } from 'react'
import { Button } from './button'
// AuthModal is temporarily commented out
// import { AuthModal } from '@/components/blocks/AuthModal'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Sparkles, X, Check, AlertCircle } from 'lucide-react'

export default function Hero() {
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const [currentError, setCurrentError] = useState(0)
  const { data: session } = useSession()
  const router = useRouter()
  
  const errors = [
    { type: 'Título > 60 caracteres', status: 'Corrigido automaticamente' },
    { type: 'Preço com formatação errada', status: 'Formatado para MELI' },
    { type: 'EAN/GTIN inválido', status: 'Validado e corrigido' },
    { type: 'Categoria inexistente', status: 'Mapeada corretamente' },
    { type: 'Imagem sem resolução', status: 'Alertado antes do envio' }
  ]
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentError((prev) => (prev + 1) % errors.length)
    }, 2500)
    return () => clearInterval(interval)
  }, [])

  const handleStartNow = () => {
    if (session) {
      router.push('/upload')
    } else {
      setAuthMode('signup')
      setAuthModalOpen(true)
    }
  }

  const handleViewPlans = () => {
    router.push('/pricing')
  }

  return (
    <>
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
        {/* Background decorations */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-green-500/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full mb-8">
              <svg className="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-red-400 font-medium">
                15-30% dos seus produtos são rejeitados todo mês
              </span>
            </div>

            {/* Main headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 tracking-tight">
              Cada produto rejeitado custa
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400"> R$127/dia </span>
              em vendas perdidas
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-gray-400 mb-6 max-w-3xl mx-auto leading-relaxed">
              <span className="text-white font-semibold">3 milhões de sellers no Brasil</span> perdem 
              16h/mês corrigindo planilhas manualmente. Enquanto você lê isso, seus concorrentes 
              já validaram e publicaram com ValidaHub.
            </p>
            
            {/* Visual Error Animation */}
            <div className="mb-10 bg-black/30 rounded-xl p-6 border border-gray-700 max-w-2xl mx-auto">
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
            </div>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={handleStartNow}
                className="min-w-[250px] bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold px-8 py-6 text-lg rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
              >
                Validar CSV agora (grátis)
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button
                size="lg"
                variant="outline"
                onClick={handleViewPlans}
                className="min-w-[250px] border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white font-semibold px-8 py-6 text-lg rounded-lg transition-all duration-200"
              >
                Continuar perdendo vendas
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="mt-16 flex flex-col sm:flex-row gap-8 justify-center items-center text-gray-500">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-white font-semibold">30 segundos para validar</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-white font-semibold">1.247 sellers já testaram</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-white font-semibold">2,8% de rejeição média</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* AuthModal temporarily disabled
      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      /> */}
    </>
  )
}