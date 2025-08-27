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
        <div className="bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-6">
          {/* Header with icon */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5 text-green-400" />
            </div>
            <h3 className="text-base font-semibold text-white">
              Cookies & Privacidade
            </h3>
            {/* Close button */}
            <button
              onClick={handleReject}
              className="ml-auto text-gray-500 hover:text-gray-300 transition-colors"
              aria-label="Fechar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <p className="text-sm text-gray-400 leading-relaxed mb-4">
            Usamos cookies para melhorar sua experiência. 
            Veja nossa{' '}
            <Link 
              href="/privacy" 
              className="text-green-400 hover:text-green-300 underline transition-colors"
            >
              Política de Privacidade
            </Link>
            {' '}e{' '}
            <Link 
              href="/terms" 
              className="text-green-400 hover:text-green-300 underline transition-colors"
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
              className="flex-1 px-4 py-2 text-sm border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white transition-all"
            >
              Essenciais
            </Button>
            <Button
              onClick={handleAccept}
              className="flex-1 px-4 py-2 text-sm bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold shadow-lg shadow-green-500/20 transition-all"
            >
              Aceitar tudo
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}