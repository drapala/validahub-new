'use client'

import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ArrowRight } from 'lucide-react'

export default function NotFound() {
  const router = useRouter()
  const [validatedCatalogs, setValidatedCatalogs] = useState(13)
  const [rejectedProducts, setRejectedProducts] = useState(79)
  const [lostMoney, setLostMoney] = useState(7558)
  const [seconds, setSeconds] = useState(77)

  useEffect(() => {
    const interval = setInterval(() => {
      setValidatedCatalogs(prev => prev + (Math.random() > 0.7 ? 1 : 0))
      setRejectedProducts(prev => prev + Math.floor(Math.random() * 2) + 1)
      setLostMoney(prev => prev + Math.floor(Math.random() * 100) + 50)
      setSeconds(prev => prev + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const handleValidateCSV = () => {
    router.push('/upload')
  }

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Background decorations */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          {/* Headlines */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-black text-white mb-2">
            404 - Essa página foi rejeitada
          </h1>
          <p className="text-xl sm:text-2xl text-red-400 font-bold mb-12">
            (igual 27% dos seus produtos no MELI)
          </p>

          {/* Comparação */}
          <div className="bg-black/40 rounded-xl p-8 border border-gray-700 mb-12 max-w-2xl mx-auto">
            <p className="text-lg text-gray-400 mb-6">A diferença?</p>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-left">
                <span className="text-gray-500">Página quebrada =</span>
                <span className="text-yellow-400 font-semibold">você perdeu 10 segundos</span>
              </div>
              <div className="flex items-center justify-between text-left">
                <span className="text-gray-500">Produto rejeitado =</span>
                <span className="text-red-400 font-bold text-xl">você perde R$127/dia</span>
              </div>
            </div>
            <p className="text-white font-bold mt-8 text-xl">
              Qual erro você prefere corrigir primeiro?
            </p>
          </div>

          {/* CTA Principal */}
          <Button
            size="lg"
            onClick={handleValidateCSV}
            className="w-full max-w-2xl bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold px-10 py-8 text-xl rounded-xl shadow-2xl shadow-green-500/30 transition-all duration-200 hover:shadow-3xl hover:shadow-green-500/40 group mb-12 hover:scale-105"
          >
            Validar meu catálogo antes de perder mais vendas
            <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-2 transition-transform" />
          </Button>

          {/* Contador em tempo real */}
          <div className="bg-red-950/30 rounded-xl p-6 border border-red-500/20">
            <p className="text-red-400 font-bold text-lg mb-6">
              Enquanto você está aqui perdido, saiba que:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-black/40 rounded-lg p-4">
                <p className="text-3xl font-bold text-green-400">{validatedCatalogs}</p>
                <p className="text-sm text-gray-500 mt-1">
                  sellers validaram catálogos
                  <span className="block text-xs text-green-400">(economizando R${(validatedCatalogs * 127).toLocaleString('pt-BR')})</span>
                </p>
              </div>
              <div className="bg-black/40 rounded-lg p-4">
                <p className="text-3xl font-bold text-red-400">{rejectedProducts}</p>
                <p className="text-sm text-gray-500 mt-1">
                  produtos rejeitados no MELI
                  <span className="block text-xs text-red-400">(sem ValidaHub)</span>
                </p>
              </div>
              <div className="bg-black/40 rounded-lg p-4">
                <p className="text-3xl font-bold text-orange-400">R${lostMoney.toLocaleString('pt-BR')}</p>
                <p className="text-sm text-gray-500 mt-1">
                  em vendas perdidas
                  <span className="block text-xs text-orange-400">(últimos {seconds}s)</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}