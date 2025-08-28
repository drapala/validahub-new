'use client'

import { MessageCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function WhatsAppFloat() {
  const [isVisible, setIsVisible] = useState(false)
  
  useEffect(() => {
    // Aparece após 2 segundos
    const timer = setTimeout(() => setIsVisible(true), 2000)
    return () => clearTimeout(timer)
  }, [])
  
  const handleClick = () => {
    // Número do WhatsApp com mensagem pré-definida
    const phoneNumber = '5511999999999' // Substitua pelo número real
    const message = encodeURIComponent('Olá! Vi o ValidaHub e gostaria de saber mais sobre a plataforma.')
    window.open(`https://wa.me/${phoneNumber}?text=${message}`, '_blank')
  }
  
  if (!isVisible) return null
  
  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 z-50 group animate-in fade-in slide-in-from-bottom-5 duration-500"
      aria-label="Conversar no WhatsApp"
    >
      {/* Ícone pulsante */}
      <div className="relative">
        {/* Pulse rings */}
        <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-25" />
        <div className="absolute inset-0 bg-green-500 rounded-full animate-ping animation-delay-200 opacity-20" />
        
        {/* Main button */}
        <div className="relative w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-full shadow-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
          <MessageCircle className="w-7 h-7 text-white fill-white" />
        </div>
        
        {/* Badge "Atendimento" */}
        <div className="absolute -top-2 -right-2 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full animate-pulse">
          Online
        </div>
      </div>
      
      {/* Tooltip on hover */}
      <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
        <div className="bg-gray-900 text-white text-xs px-3 py-2 rounded-lg whitespace-nowrap shadow-xl">
          Fale conosco no WhatsApp
          <div className="absolute top-full right-6 w-0 h-0 border-t-4 border-t-gray-900 border-x-4 border-x-transparent" />
        </div>
      </div>
    </button>
  )
}