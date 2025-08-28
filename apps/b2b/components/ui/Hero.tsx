'use client'

import { useState, useEffect } from 'react'
import { motion, useReducedMotion, useAnimation, animate } from 'framer-motion'
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
  const [savingsAmount, setSavingsAmount] = useState(0)
  const [cardResolved, setCardResolved] = useState(false)
  const { data: session } = useSession()
  const router = useRouter()
  const shouldReduceMotion = useReducedMotion()
  
  const cardControls = useAnimation()
  const ctaControls = useAnimation()
  
  const errors = [
    { type: 'EAN/GTIN inválido', status: 'Validado e corrigido', severity: 'fatal' },
    { type: 'Categoria inexistente', status: 'Mapeada corretamente', severity: 'fatal' },
    { type: 'Título > 60 caracteres', status: 'Corrigido automaticamente', severity: 'critical' },
    { type: 'Preço com formatação errada', status: 'Formatado para MELI', severity: 'critical' },
    { type: 'Imagem sem resolução', status: 'Alertado antes do envio', severity: 'warning' }
  ]
  
  // Coreografia sequencial
  useEffect(() => {
    const runSequence = async () => {
      if (shouldReduceMotion) {
        setSavingsAmount(127)
        setCardResolved(true)
        return
      }
      
      // 1. Card entra
      await cardControls.start("enter")
      
      // 2. Após 1s, resolve o erro
      await new Promise(resolve => setTimeout(resolve, 1000))
      await cardControls.start("resolve")
      setCardResolved(true)
      
      // 3. Anima o valor economizado
      await animate(0, 127, {
        duration: 0.9,
        onUpdate: v => setSavingsAmount(Math.round(v))
      })
      
      // 4. CTA aparece
      ctaControls.start("pop")
    }
    
    runSequence()
    
    // Continua ciclando os erros
    const interval = setInterval(() => {
      setCurrentError((prev) => (prev + 1) % errors.length)
    }, 3500)
    return () => clearInterval(interval)
  }, [shouldReduceMotion, cardControls, ctaControls])

  const handleStartNow = () => {
    navigateToSection('data')
  }

  const handleCalculateROI = () => {
    navigateToSection('calculator')
  }

  return (
    <>
      <section className="relative min-h-screen flex flex-col justify-start overflow-hidden pt-24 md:pt-32">
        {/* Background decorations adaptativas */}
        <div className="absolute inset-0 dark:bg-grid-white/[0.01] bg-grid-black/[0.02] bg-[size:80px_80px]" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] 
          dark:bg-green-500/10 bg-violet-500/5 
          rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            {/* Main headline */}
            <h1 className="hero-headline mb-4">
              <motion.span
                className="dark:text-white text-black inline-block"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
              >
                Com ValidaHub você economiza{' '}
              </motion.span>
              <motion.span 
                className="text-transparent bg-clip-text inline-block
                  bg-gradient-to-r from-violet-600 to-violet-500 dark:from-emerald-500 dark:to-emerald-400
                  tabular-nums font-bold"
                initial={{ opacity: 0 }}
                animate={{ 
                  opacity: savingsAmount > 0 ? 1 : 0,
                  filter: savingsAmount === 127 ? [
                    "drop-shadow(0 0 0px currentColor)",
                    "drop-shadow(0 0 20px currentColor)",
                    "drop-shadow(0 0 10px currentColor)"
                  ] : "drop-shadow(0 0 0px currentColor)"
                }}
                transition={{ 
                  duration: 0.6,
                  filter: { duration: 0.8 }
                }}
                style={{
                  display: "inline-block"
                }}
              >R${savingsAmount}/dia</motion.span>
            </h1>

            {/* Subheadline com ponte causal */}
            <motion.p 
              className="font-inter text-xl leading-7 font-normal dark:text-white/60 text-black/60 mb-6 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5, ease: "easeOut" }}
            >
              Corrigimos erros que viram rejeição. Rejeição = dinheiro perdido.
            </motion.p>
            
            {/* Visual Error Animation - Premium Card with Elevation */}
            <motion.div
              initial="hidden"
              animate={cardControls}
              variants={{
                hidden: { opacity: 0, y: 8 },
                enter: { opacity: 1, y: 0, transition: { duration: 0.5 } },
                resolve: { transition: { duration: 0.4 } }
              }}
              whileHover={{ scale: shouldReduceMotion ? 1 : 1.02 }}
              className="mb-8"
            >
              <div 
                className="relative max-w-2xl mx-auto rounded-2xl overflow-hidden"
                style={{
                  background: 'var(--vh-surface-card)',
                  backdropFilter: `blur(var(--vh-blur-card))`,
                  WebkitBackdropFilter: `blur(var(--vh-blur-card))`,
                  border: '1px solid var(--vh-border-subtle)',
                  boxShadow: 'var(--vh-shadow-m)'
                }}
              >
                {/* Spotlight effect for light theme */}
                <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
                  <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-radial from-violet-500 to-transparent blur-3xl" />
                </div>
                
                <div className="relative p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <motion.div 
                        className="relative"
                        whileHover={shouldReduceMotion ? {} : { rotate: [0, -5, 5, -5, 0] }}
                        transition={{ duration: 0.5 }}
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          errors[currentError].severity === 'fatal'
                            ? 'bg-[var(--vh-error-bg)] border border-[var(--vh-error-border)]' 
                            : errors[currentError].severity === 'critical'
                            ? 'bg-[var(--vh-warning-bg)] border border-[var(--vh-warning-border)]'
                            : 'bg-[var(--vh-warning-bg)] border border-[var(--vh-warning-border)]'
                        }`}>
                          {errors[currentError].severity === 'fatal' ? (
                            <XCircle className="w-6 h-6" style={{ color: 'var(--vh-error-fg)' }} />
                          ) : errors[currentError].severity === 'critical' ? (
                            <AlertCircle className="w-6 h-6" style={{ color: 'var(--vh-warning-fg)' }} />
                          ) : (
                            <AlertTriangle className="w-6 h-6" style={{ color: 'var(--vh-warning-fg)' }} />
                          )}
                        </div>
                        <motion.div 
                          className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full ${
                            errors[currentError].severity === 'fatal'
                              ? 'bg-[var(--vh-error-fg)]' 
                              : 'bg-[var(--vh-warning-fg)]'
                          }`}
                          animate={shouldReduceMotion ? {} : { scale: [1, 1.5, 1] }}
                          transition={{ duration: 1, repeat: Infinity }}
                        />
                      </motion.div>
                      <div className="text-left">
                        <p className="text-xs font-medium" style={{ color: 'var(--vh-text-muted)' }}>
                          {errors[currentError].severity === 'warning' ? 'Sugestão:' : 'Erro detectado:'}
                        </p>
                        <p className="font-semibold" style={{ color: 'var(--vh-text-primary)' }}>
                          {errors[currentError].type}
                        </p>
                      </div>
                    </div>
                    
                    <motion.div
                      animate={shouldReduceMotion ? {} : { x: [0, 5, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <ArrowRight className="w-5 h-5 text-violet-500 dark:text-emerald-500" />
                    </motion.div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xs font-medium" style={{ color: 'var(--vh-text-muted)' }}>
                          ValidaHub:
                        </p>
                        <p className="font-semibold text-violet-600 dark:text-emerald-400">
                          {errors[currentError].status}
                        </p>
                        {cardResolved && (
                          <motion.p 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xs mt-1 text-violet-500/70 dark:text-emerald-400/70"
                          >
                            Evita ~R$127/dia de perda
                          </motion.p>
                        )}
                      </div>
                      <motion.div 
                        className="w-12 h-12 rounded-xl flex items-center justify-center"
                        style={{
                          background: cardResolved ? 'rgb(16 185 129 / 0.1)' : 'var(--vh-success-bg)',
                          border: cardResolved ? '1px solid rgb(16 185 129 / 0.3)' : '1px solid var(--vh-success-border)'
                        }}
                        whileHover={shouldReduceMotion ? {} : { scale: 1.1 }}
                        animate={cardResolved ? { scale: [1, 1.2, 1] } : {}}
                        transition={{ 
                          rotate: { duration: 2, delay: currentError * 0.5, ease: "easeInOut" },
                          scale: { duration: 0.4 }
                        }}
                      >
                        <Check className={`w-6 h-6 ${cardResolved ? 'text-emerald-500' : ''}`} style={{ color: cardResolved ? undefined : 'var(--vh-success-fg)' }} />
                      </motion.div>
                    </div>
                  </div>
                  
                  {/* Progress indicators */}
                  <div className="mt-4 flex gap-1.5 justify-center">
                    {errors.map((_, index) => (
                      <motion.div
                        key={index}
                        className="h-1 rounded-full overflow-hidden"
                        initial={{ width: 24 }}
                        animate={{ 
                          width: index === currentError ? 40 : 24,
                          opacity: index === currentError ? 1 : 0.3
                        }}
                        transition={{ duration: 0.3 }}
                        style={{
                          background: index === currentError 
                            ? cardResolved ? 'rgb(16 185 129)' : 'rgb(124 58 237)' 
                            : 'var(--vh-border-default)'
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>

            {/* CTA button and trust indicator container */}
            <div className="relative">
              {/* Premium CTA button - Violeta unificado */}
              <motion.div
                initial={{ scale: 0.98, opacity: 0 }}
                animate={ctaControls}
                variants={{
                  pop: { 
                    scale: 1, 
                    opacity: 1, 
                    transition: { 
                      type: "spring", 
                      stiffness: 260, 
                      damping: 18 
                    }
                  }
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex justify-center mb-4 pointer-events-none mt-6"
              >
                <button
                  onClick={handleStartNow}
                  className="pointer-events-auto relative inline-flex items-center justify-center gap-2.5 
                    px-6 py-3 md:px-8 md:py-4
                    text-base md:text-lg font-semibold text-white
                    rounded-2xl bg-violet-600 dark:bg-emerald-600
                    shadow-lg ring-2 ring-violet-400/30 dark:ring-emerald-400/30 hover:ring-violet-400/50 dark:hover:ring-emerald-400/50
                    focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70
                    transition-all duration-300 ease-out
                    hover:-translate-y-0.5
                    active:translate-y-[1px]
                    disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:active:translate-y-0
                    max-w-[400px] w-full
                    font-sans"
                  aria-label="Validar catálogo CSV e ver economia"
                >
                  <span className="relative z-10">Validar meu CSV e ver minha economia</span>
                  <motion.span 
                    className="relative z-10"
                    animate={shouldReduceMotion ? {} : { x: [0, 3, 0] }}
                    transition={{ 
                      duration: 1.5, 
                      repeat: Infinity,
                      repeatDelay: 1
                    }}
                  >
                    →
                  </motion.span>
                </button>
              </motion.div>
            </div>

          </div>
        </div>

        {/* Trust indicator and scroll arrow container - positioned higher */}
        <div className="absolute bottom-16 md:bottom-20 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4">
          {/* Trust indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 2.2, ease: "easeOut" }}
          >
            <p className="text-sm dark:text-gray-400 text-gray-600 whitespace-nowrap">
              <span className="dark:text-white text-gray-900 font-semibold">1.247 sellers</span> já testaram
            </p>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ 
              opacity: 1, 
              y: shouldReduceMotion ? 0 : [0, 8, 0]
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
            className="flex flex-col items-center gap-1"
          >
            <svg className="w-5 h-5 dark:text-gray-400 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            <span className="text-xs dark:text-gray-500 text-gray-400 mt-1">scroll</span>
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