'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function WhatsAppFloatPremium() {
  const [isVisible, setIsVisible] = useState(false)
  const [showPeek, setShowPeek] = useState(false)
  const phoneNumber = '5512992442448' // número real com DDI
  const message = 'Olá! Quero saber mais sobre o ValidaHub 🙂'
  
  useEffect(() => {
    // Aparece após 2 segundos
    const timer = setTimeout(() => setIsVisible(true), 2000)
    
    // Mostra tooltip peek uma vez só
    if (!localStorage.getItem('vh__wa_seen')) {
      const peekTimer = setTimeout(() => {
        setShowPeek(true)
        const hidePeekTimer = setTimeout(() => {
          setShowPeek(false)
          localStorage.setItem('vh__wa_seen', '1')
        }, 5000)
        return () => clearTimeout(hidePeekTimer)
      }, 3000)
      return () => {
        clearTimeout(timer)
        clearTimeout(peekTimer)
      }
    }
    
    return () => clearTimeout(timer)
  }, [])
  
  const handleClick = () => {
    // Analytics
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('wa_bubble_click'))
    }
  }
  
  const href = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ duration: 0.4, type: "spring", stiffness: 260, damping: 20 }}
          className="fixed z-50 right-4 bottom-4 md:right-6 md:bottom-6"
        >
          {/* Tooltip Peek */}
          <AnimatePresence>
            {showPeek && (
              <motion.div
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.3 }}
                className="absolute right-[72px] bottom-3 whitespace-nowrap"
              >
                <div className="rounded-2xl bg-zinc-900 dark:bg-zinc-800 text-white text-sm px-4 py-2.5 shadow-xl">
                  Precisa de ajuda? Fale com a gente.
                  <div className="absolute top-1/2 -translate-y-1/2 -right-2 w-0 h-0 
                    border-t-[6px] border-t-transparent
                    border-b-[6px] border-b-transparent
                    border-l-[8px] border-l-zinc-900 dark:border-l-zinc-800" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* WhatsApp Button */}
          <motion.a
            href={href}
            target="_blank"
            rel="noopener"
            onClick={handleClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="Falar no WhatsApp"
            className="relative flex items-center justify-center w-14 h-14 md:w-[60px] md:h-[60px] rounded-full
                       bg-emerald-500 text-white shadow-xl
                       ring-2 ring-emerald-300/50 hover:ring-emerald-400/60
                       transition-all duration-150 ease-out
                       hover:shadow-2xl hover:shadow-emerald-500/20
                       focus:outline-none focus-visible:ring-4 focus-visible:ring-emerald-400/70"
          >
            {/* WhatsApp Icon SVG */}
            <svg viewBox="0 0 32 32" className="w-7 h-7 md:w-8 md:h-8" aria-hidden="true">
              <path 
                fill="currentColor" 
                d="M19.1 17.4c-.3-.2-1.7-.8-1.9-.9-.3-.1-.5-.2-.7.2s-.8.9-1 .9-.5 0-.8-.2a7.7 7.7 0 0 1-2.3-1.9 8.6 8.6 0 0 1-1.4-2.1c-.1-.3 0-.4.2-.6l.5-.6c.1-.1.1-.2.2-.4s0-.3 0-.4c0-.2-.7-1.7-.9-2.4s-.5-.6-.7-.6h-.6a1.2 1.2 0 0 0-.9.4 3.7 3.7 0 0 0-1.1 2.7 6.5 6.5 0 0 0 1.4 3.4 14.8 14.8 0 0 0 5.7 5.2 12.7 12.7 0 0 0 3.8 1.4 3.3 3.3 0 0 0 2.1-.4 2.7 2.7 0 0 0 1-1.7c.1-.9.1-1.6 0-1.7s-.3-.2-.6-.3z"
              />
              <path 
                fill="currentColor" 
                d="M27.6 16a11.6 11.6 0 1 0-22.6 5.7L4 28l6.4-1.7A11.6 11.6 0 0 0 27.6 16m-2 0A9.6 9.6 0 0 1 10.4 24l-.7.2-.4.1-3.8 1 1-3.7.1-.4.2-.7A9.6 9.6 0 1 1 25.6 16"
              />
            </svg>
            <span className="sr-only">Abrir conversa no WhatsApp</span>
            
            {/* Badge de novo/ativo */}
            <span className="absolute -top-1 -right-1">
              <span className="relative flex w-3 h-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full w-3 h-3 bg-white"></span>
              </span>
            </span>
          </motion.a>
        </motion.div>
      )}
    </AnimatePresence>
  )
}