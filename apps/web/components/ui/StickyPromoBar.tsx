'use client'

import { useState, useEffect, useRef } from 'react'
import { X, Sparkles, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function StickyPromoBar() {
  const [isVisible, setIsVisible] = useState(true)
  const [hasScrolled, setHasScrolled] = useState(false)
  const bannerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Verifica se já foi fechado antes
    const dismissed = localStorage.getItem('promo-bar-dismissed')
    if (dismissed) {
      setIsVisible(false)
    }

    // Detecta scroll para adicionar sombra
    const handleScroll = () => {
      setHasScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Atualiza a CSS variable quando a visibilidade muda
  useEffect(() => {
    const height = isVisible ? 40 : 0
    document.documentElement.style.setProperty('--promo-h', `${height}px`)
    
    return () => {
      // Reset quando o componente desmontar
      document.documentElement.style.setProperty('--promo-h', '0px')
    }
  }, [isVisible])

  const handleDismiss = () => {
    setIsVisible(false)
    localStorage.setItem('promo-bar-dismissed', 'true')
    // Opcional: expirar após 7 dias
    setTimeout(() => {
      localStorage.removeItem('promo-bar-dismissed')
    }, 7 * 24 * 60 * 60 * 1000)
  }

  if (!isVisible) return null

  return (
    <div 
      className={`
        fixed top-0 left-0 right-0 z-[60] h-10
        dark:bg-gradient-to-r dark:from-emerald-600 dark:via-teal-600 dark:to-emerald-600
        bg-gradient-to-r from-purple-600 via-violet-600 to-purple-600
        dark:border-b dark:border-emerald-700/50
        border-b border-purple-700/50
        transition-shadow duration-200
        ${hasScrolled ? 'dark:shadow-lg dark:shadow-emerald-500/20 shadow-lg shadow-purple-500/20' : ''}
      `}
    >
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.1)_50%,transparent_75%)] bg-[length:20px_20px] animate-[slide_3s_linear_infinite]" />
      </div>

      <div className="relative h-full flex items-center justify-center px-4">
        <div className="flex items-center gap-3">
          {/* Sparkle icon */}
          <Sparkles className="w-4 h-4 dark:text-emerald-200 text-purple-200 animate-pulse" />
          
          {/* Message */}
          <p className="text-sm font-medium text-white">
            <span className="hidden sm:inline">🎉 Oferta limitada: </span>
            <span className="font-bold">1.000 validações grátis</span>
            <span className="hidden sm:inline"> para novos usuários</span>
          </p>

          {/* CTA */}
          <Link
            href="/signup"
            className="inline-flex items-center gap-1 px-3 py-1 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full text-xs font-semibold text-white transition-all group"
          >
            <span className="hidden sm:inline">Começar agora</span>
            <span className="sm:hidden">Começar</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {/* Close button */}
        <button
          onClick={handleDismiss}
          className="absolute right-2 p-1.5 dark:text-emerald-200 dark:hover:text-white text-purple-200 hover:text-white hover:bg-white/10 rounded-full transition-all"
          aria-label="Fechar promoção"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Bottom glow effect */}
      <div className="absolute bottom-0 left-0 right-0 h-px dark:bg-gradient-to-r dark:from-transparent dark:via-emerald-300/50 dark:to-transparent bg-gradient-to-r from-transparent via-purple-300/50 to-transparent" />
    </div>
  )
}

/* Add this to your global CSS for the slide animation */
const slideAnimation = `
@keyframes slide {
  0% {
    transform: translateX(-20px);
  }
  100% {
    transform: translateX(20px);
  }
}
`