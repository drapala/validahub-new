'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Cookie, Shield, X } from 'lucide-react'
import { Button } from './button'

export default function CookieBanner() {
  const [showBanner, setShowBanner] = useState(false)
  const [isClosing, setIsClosing] = useState(false)

  useEffect(() => {
    // Check if user has already made a choice
    const cookieConsent = localStorage.getItem('cookie-consent')
    
    // DESENVOLVIMENTO: Descomente a linha abaixo para sempre mostrar o banner
    // localStorage.removeItem('cookie-consent')
    
    if (!cookieConsent) {
      // Small delay to prevent flash on initial load
      setTimeout(() => setShowBanner(true), 1000)
    }
  }, [])

  const handleAccept = () => {
    localStorage.setItem('cookie-consent', 'accepted')
    localStorage.setItem('cookie-consent-date', new Date().toISOString())
    closeBanner()
    
    // Here you would initialize analytics/tracking
    console.log('Cookies accepted - initialize analytics')
  }

  const handleReject = () => {
    localStorage.setItem('cookie-consent', 'rejected')
    localStorage.setItem('cookie-consent-date', new Date().toISOString())
    closeBanner()
    
    // Here you would disable non-essential cookies
    console.log('Cookies rejected - only essential cookies')
  }

  const closeBanner = () => {
    setIsClosing(true)
    setTimeout(() => {
      setShowBanner(false)
      setIsClosing(false)
    }, 300)
  }

  if (!showBanner) return null

  return (
    <div 
      className={`fixed bottom-4 left-4 z-50 transition-all duration-300 ${
        isClosing ? 'translate-x-[-100%] opacity-0' : 'translate-x-0 opacity-100'
      }`}
    >
      <div className="w-[380px] max-w-[calc(100vw-2rem)]">
        <div className="dark:bg-zinc-900 dark:border-zinc-800 bg-white border-gray-200 rounded-2xl shadow-2xl p-6">
          {/* Header with icon */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 dark:bg-emerald-500/10 bg-violet-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5 dark:text-emerald-400 text-violet-600" />
            </div>
            <h3 className="text-base font-semibold dark:text-white text-gray-900">
              Cookies & Privacidade
            </h3>
            {/* Close button */}
            <button
              onClick={handleReject}
              className="ml-auto dark:text-zinc-500 dark:hover:text-zinc-300 text-gray-500 hover:text-gray-700 transition-colors"
              aria-label="Fechar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <p className="text-sm dark:text-zinc-400 text-gray-600 leading-relaxed mb-4">
            Usamos cookies para melhorar sua experiência. 
            Veja nossa{' '}
            <Link 
              href="/privacy" 
              className="dark:text-emerald-400 dark:hover:text-emerald-300 text-violet-600 hover:text-violet-700 underline transition-colors"
            >
              Política de Privacidade
            </Link>
            {' '}e{' '}
            <Link 
              href="/terms" 
              className="dark:text-emerald-400 dark:hover:text-emerald-300 text-violet-600 hover:text-violet-700 underline transition-colors"
            >
              Termos
            </Link>
            .
          </p>

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              onClick={handleReject}
              variant="outline"
              className="flex-1 px-4 py-2 text-sm dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white border-gray-300 text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-all"
            >
              Essenciais
            </Button>
            <Button
              onClick={handleAccept}
              className="flex-1 px-4 py-2 text-sm dark:bg-gradient-to-r dark:from-emerald-500 dark:to-teal-500 dark:hover:from-emerald-600 dark:hover:to-teal-600 bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600 text-white font-semibold dark:shadow-lg dark:shadow-emerald-500/20 shadow-lg shadow-violet-500/20 transition-all"
            >
              Aceitar tudo
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}