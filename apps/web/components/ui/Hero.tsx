'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { navigateToSection } from '@/lib/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
// AuthModal is temporarily commented out
// import { AuthModal } from '@/components/blocks/AuthModal'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Sparkles, X, Check, AlertCircle, XCircle, AlertTriangle } from 'lucide-react'

export default function Hero() {
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const [currentError, setCurrentError] = useState(0)
  const { data: session } = useSession()
  const router = useRouter()
  
  const errors = [
    { type: 'EAN/GTIN inválido', status: 'Validado e corrigido', severity: 'fatal' },
    { type: 'Categoria inexistente', status: 'Mapeada corretamente', severity: 'fatal' },
    { type: 'Título > 60 caracteres', status: 'Corrigido automaticamente', severity: 'critical' },
    { type: 'Preço com formatação errada', status: 'Formatado para MELI', severity: 'critical' },
    { type: 'Imagem sem resolução', status: 'Alertado antes do envio', severity: 'warning' }
  ]
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentError((prev) => (prev + 1) % errors.length)
    }, 2500)
    return () => clearInterval(interval)
  }, [])

  const handleStartNow = () => {
    navigateToSection('data')
  }

  const handleCalculateROI = () => {
    navigateToSection('calculator')
  }

  return (
    <>
      <section className="relative min-h-screen flex flex-col justify-start overflow-hidden pt-40 md:pt-52">
        {/* Background decorations */}
        <div className="absolute inset-0 bg-grid-white/[0.01] bg-[size:80px_80px]" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-green-500/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            {/* Main headline */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-wider mb-6">
              <motion.span
                className="text-white inline-block"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8, ease: "easeOut" }}
              >
                Com ValidaHub você economiza{' '}
              </motion.span>
              <motion.span 
                className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400 inline-block"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ 
                  duration: 0.6, 
                  delay: 0.1,
                  ease: "easeOut"
                }}
                style={{
                  filter: "drop-shadow(0 0 20px rgba(52, 211, 153, 0.2)) drop-shadow(0 0 40px rgba(52, 211, 153, 0.08))",
                  textShadow: "0 0 20px rgba(52, 211, 153, 0.25)",
                  display: "inline-block"
                }}
              >R$127/dia</motion.span>
            </h1>

            {/* Subheadline */}
            <motion.p 
              className="text-lg sm:text-xl text-gray-400 mb-10 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.4, ease: "easeOut" }}
            >
              Seus concorrentes perdem vendas. Você não.
            </motion.p>
            
            {/* Visual Error Animation */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 1.9, ease: "easeOut" }}
              className="mb-12"
            >
              <Card className="bg-black/30 border-gray-700 max-w-2xl mx-auto">
                <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center transition-colors duration-500 ${
                        errors[currentError].severity === 'fatal'
                          ? 'bg-red-500/20 border border-red-500/30' 
                          : errors[currentError].severity === 'critical'
                          ? 'bg-orange-500/20 border border-orange-500/30'
                          : 'bg-yellow-500/20 border border-yellow-500/30'
                      }`}>
                        {errors[currentError].severity === 'fatal' ? (
                          <XCircle className="w-6 h-6 text-red-400" />
                        ) : errors[currentError].severity === 'critical' ? (
                          <AlertCircle className="w-6 h-6 text-orange-400" />
                        ) : (
                          <AlertTriangle className="w-6 h-6 text-yellow-400" />
                        )}
                      </div>
                      <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full animate-ping ${
                        errors[currentError].severity === 'fatal'
                          ? 'bg-red-500' 
                          : errors[currentError].severity === 'critical'
                          ? 'bg-orange-500'
                          : 'bg-yellow-500'
                      }`}></div>
                    </div>
                    <div className="text-left">
                      <p className="text-sm text-gray-500">
                        {errors[currentError].severity === 'warning' ? 'Sugestão:' : 'Erro:'}
                      </p>
                      <p className="text-white font-semibold">{errors[currentError].type}</p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-600 mx-4" />
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm text-gray-500">ValidaHub:</p>
                      <p className="text-green-400 font-semibold">{errors[currentError].status}</p>
                    </div>
                    <div className="w-12 h-12 bg-gray-700/50 border border-gray-600 rounded-lg flex items-center justify-center">
                      <Check className="w-6 h-6 text-gray-400" />
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
            </motion.div>

            {/* CTA button and trust indicator container */}
            <div className="relative">
              {/* CTA button */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ 
                  duration: 0.6, 
                  delay: 2.5, 
                  ease: [0.21, 0.47, 0.32, 0.98],
                  scale: { type: "spring", damping: 15 }
                }}
                className="flex justify-center mb-6 pointer-events-none mt-8"
              >
                <button
                  onClick={handleStartNow}
                  className="group pointer-events-auto relative inline-flex items-center justify-center gap-2 
                    px-10 py-5 md:px-12 md:py-6 
                    text-lg md:text-xl font-bold text-white
                    bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500
                    rounded-2xl
                    shadow-lg shadow-green-500/25
                    transition-all duration-200 ease-out
                    hover:brightness-110 hover:shadow-xl hover:shadow-green-500/30 hover:-translate-y-0.5
                    active:translate-y-[1px] active:shadow-md
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/60 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-900
                    disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:brightness-100 disabled:hover:translate-y-0 disabled:active:translate-y-0
                    max-w-[380px] md:max-w-[450px] w-full"
                  aria-label="Validar catálogo CSV gratuitamente"
                >
                  Validar meu CSV grátis
                  <ArrowRight 
                    className="w-5 h-5 md:w-6 md:h-6 transition-transform duration-200 group-hover:translate-x-1" 
                    aria-hidden="true"
                  />
                </button>
              </motion.div>
            </div>

          </div>
        </div>

        {/* Trust indicator and scroll arrow container */}
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4">
          {/* Trust indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 2.2, ease: "easeOut" }}
          >
            <p className="text-sm text-gray-400 whitespace-nowrap">
              <span className="text-white font-semibold">1.247 sellers</span> já testaram
            </p>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ 
              opacity: 1, 
              y: [0, 10, 0]
            }}
            transition={{
              opacity: { duration: 0.6, delay: 3.2 },
              y: { 
                duration: 2,
                delay: 3.7,
                repeat: Infinity,
                repeatType: "loop",
                ease: "easeInOut"
              }
            }}
          >
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </motion.div>
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