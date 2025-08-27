'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Cookie, Shield, FileText, X } from 'lucide-react'
import { Button } from './button'
import Link from 'next/link'

export default function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    // Check if user already consented
    const consent = localStorage.getItem('cookieConsent')
    
    if (!consent) {
      // Show after 2 seconds on page load
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [])

  const handleAcceptAll = () => {
    localStorage.setItem('cookieConsent', JSON.stringify({
      necessary: true,
      analytics: true,
      marketing: true,
      timestamp: new Date().toISOString()
    }))
    setIsVisible(false)
  }

  const handleAcceptNecessary = () => {
    localStorage.setItem('cookieConsent', JSON.stringify({
      necessary: true,
      analytics: false,
      marketing: false,
      timestamp: new Date().toISOString()
    }))
    setIsVisible(false)
  }

  const handleReject = () => {
    localStorage.setItem('cookieConsent', JSON.stringify({
      necessary: true, // Always true as they're necessary
      analytics: false,
      marketing: false,
      timestamp: new Date().toISOString()
    }))
    setIsVisible(false)
  }

  if (!isVisible) return null

  return (
    <>
      {/* Blur overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 backdrop-blur-sm bg-black/20 z-40"
        onClick={() => {}}
      />
      
      <AnimatePresence>
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="fixed bottom-4 left-4 right-4 md:left-6 md:right-auto md:max-w-md z-50"
        >
        <div className="bg-gray-900 border border-green-500/30 rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Cookie className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="font-bold text-white">Cookies & Privacidade</h3>
            </div>
            <button
              onClick={() => setIsVisible(false)}
              className="p-1 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4">
            <p className="text-sm text-gray-300 mb-4">
              Usamos cookies para melhorar sua experiência, analisar nosso tráfego e personalizar conteúdo. 
              Ao continuar, você concorda com nossos{' '}
              <Link href="/terms" className="text-green-400 hover:text-green-300 underline">
                Termos de Serviço
              </Link>
              {' '}e{' '}
              <Link href="/privacy" className="text-green-400 hover:text-green-300 underline">
                Política de Privacidade
              </Link>.
            </p>

            {/* Cookie Types */}
            <AnimatePresence>
              {showDetails && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mb-4 space-y-3 overflow-hidden"
                >
                  <div className="p-3 bg-gray-800/50 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Shield className="w-4 h-4 text-green-400 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-white">Essenciais</h4>
                        <p className="text-xs text-gray-400 mt-1">
                          Necessários para o funcionamento do site. Não podem ser desativados.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-800/50 rounded-lg">
                    <div className="flex items-start gap-2">
                      <FileText className="w-4 h-4 text-blue-400 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-white">Analytics</h4>
                        <p className="text-xs text-gray-400 mt-1">
                          Nos ajudam a entender como você usa o site e melhorar sua experiência.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-800/50 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Cookie className="w-4 h-4 text-orange-400 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-white">Marketing</h4>
                        <p className="text-xs text-gray-400 mt-1">
                          Usados para personalizar anúncios e medir eficácia de campanhas.
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs text-green-400 hover:text-green-300 mb-4"
            >
              {showDetails ? 'Ocultar detalhes' : 'Ver detalhes dos cookies'}
            </button>

            {/* Actions */}
            <div className="space-y-3">
              <Button
                onClick={handleAcceptAll}
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3"
              >
                Permitir cookies para melhorar sua experiência
              </Button>
              <div className="text-left">
                <button
                  onClick={handleAcceptNecessary}
                  className="text-xs text-gray-500 hover:text-gray-400 underline underline-offset-2 transition-colors"
                >
                  Continuar apenas com os essenciais
                </button>
              </div>
            </div>

            {/* LGPD Compliance */}
            <div className="mt-4 pt-4 border-t border-gray-800">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Shield className="w-3 h-3" />
                <span>Em conformidade com a LGPD e GDPR</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
    </>
  )
}