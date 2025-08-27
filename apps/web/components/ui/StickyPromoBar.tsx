'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Rocket, Users, ArrowRight, Sparkles } from 'lucide-react'
import { Button } from './button'

export default function StickyPromoBar() {
  const [isVisible, setIsVisible] = useState(false)
  const [isDismissed, setIsDismissed] = useState(false)
  const [spotsLeft, setSpotsLeft] = useState(37) // Start at 37 to create urgency

  useEffect(() => {
    // Check if already dismissed in this session
    const dismissed = sessionStorage.getItem('promoBarDismissed')
    if (dismissed) {
      setIsDismissed(true)
      return
    }

    // Set up Intersection Observer for pricing section
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // Show when pricing section has been scrolled past (not intersecting anymore)
          if (!entry.isIntersecting && entry.boundingClientRect.top < 0 && !isDismissed) {
            setIsVisible(true)
          }
        })
      },
      { threshold: 0.1, rootMargin: '-100px 0px 0px 0px' }
    )

    // Observe pricing section
    const pricingSection = document.querySelector('[data-section="pricing"]')
    if (pricingSection) {
      observer.observe(pricingSection)
    }

    // Simulate spots being taken (decrease every 30 seconds)
    const timer = setInterval(() => {
      setSpotsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          return 1
        }
        return prev - 1
      })
    }, 30000) // Every 30 seconds someone "takes a spot"

    return () => {
      observer.disconnect()
      clearInterval(timer)
    }
  }, [isDismissed])

  const handleDismiss = () => {
    setIsVisible(false)
    setIsDismissed(true)
    sessionStorage.setItem('promoBarDismissed', 'true')
  }

  const handleCTA = () => {
    // Navigate to pricing with special offer
    const pricingSection = document.querySelector('[data-section="pricing"]')
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    
    // Store special offer in sessionStorage
    sessionStorage.setItem('specialOffer', 'lifetime47')
    
    handleDismiss()
  }

  if (isDismissed) return null

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 100, damping: 20 }}
          className="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-0"
        >
          <div className="bg-gradient-to-r from-purple-900 via-[#6B46C1] to-purple-900 shadow-2xl md:rounded-none rounded-2xl overflow-hidden border-t border-purple-600/50">
            {/* Animated shimmer effect */}
            <motion.div 
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -skew-x-12"
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            />
            
            {/* Subtle pattern overlay */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyem0wLTQwdjJIMjR2LTJoMTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
            
            <div className="relative px-4 py-3 md:py-4">
              <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                {/* Left side - Offer text */}
                <div className="flex items-center gap-3 text-white">
                  <div className="relative">
                    <div className="absolute inset-0 bg-orange-400 blur-xl opacity-40 animate-pulse" />
                    <Rocket className="w-6 h-6 text-orange-300 relative z-10" />
                  </div>
                  
                  <div className="flex flex-col md:flex-row md:items-center gap-1 md:gap-3">
                    <span className="text-sm md:text-base font-bold flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-orange-400/20 border border-orange-400/30 rounded-full text-xs text-orange-300">
                        <Users className="w-3 h-3" />
                        Apenas {spotsLeft} vagas
                      </span>
                      Primeiros 100 usuários:
                    </span>
                    <span className="text-sm md:text-base">
                      Plano Pro <span className="font-bold text-orange-300">vitalício</span> por{' '}
                      <span className="text-xl font-bold text-white">R$47/mês</span>
                      <span className="text-xs text-purple-300 line-through ml-2">R$97</span>
                    </span>
                  </div>
                </div>

                {/* Right side - CTA and close */}
                <div className="flex items-center gap-3">
                  <motion.div
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Button
                      onClick={handleCTA}
                      className="bg-[#FFA500] text-purple-900 hover:bg-[#FF8C00] font-bold px-4 md:px-6 py-2 text-sm md:text-base shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 group border-2 border-orange-600/30"
                    >
                      <Sparkles className="mr-2 w-4 h-4" />
                      Garantir meu lugar
                      <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </motion.div>
                  
                  <button
                    onClick={handleDismiss}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    aria-label="Fechar"
                  >
                    <X className="w-5 h-5 text-white/80 hover:text-white" />
                  </button>
                </div>
              </div>

              {/* Trust indicators */}
              <div className="absolute bottom-1 left-1/2 -translate-x-1/2 hidden md:flex items-center gap-2 text-xs text-purple-200">
                <span>✓ Cancele quando quiser</span>
                <span>•</span>
                <span>✓ Garantia de 30 dias</span>
                <span>•</span>
                <span>✓ Suporte prioritário</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}