'use client'

import { useState } from 'react'
import { Button } from './button'
import AuthModal from './AuthModal'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Sparkles } from 'lucide-react'

export default function Hero() {
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const { data: session } = useSession()
  const router = useRouter()

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
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-8">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-400 font-medium">
                Nova versão 2.0 disponível
              </span>
            </div>

            {/* Main headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 tracking-tight">
              Valide e corrija seus
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400"> catálogos CSV </span>
              com qualidade e velocidade
            </h1>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
              Regras canônicas por marketplace, correções automáticas e exportação 
              pronta para publicação. Economize horas de trabalho manual e publique 
              com confiança.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={handleStartNow}
                className="min-w-[200px] bg-green-500 hover:bg-green-600 text-white font-semibold px-8 py-6 text-lg rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
              >
                Começar agora
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button
                size="lg"
                variant="outline"
                onClick={handleViewPlans}
                className="min-w-[200px] border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white font-semibold px-8 py-6 text-lg rounded-lg transition-all duration-200"
              >
                Ver planos
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="mt-16 flex flex-col sm:flex-row gap-8 justify-center items-center text-gray-500">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Setup em 2 minutos</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Sem cartão de crédito</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>+1000 validações grátis</span>
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

      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </>
  )
}