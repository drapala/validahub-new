'use client'

import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ArrowRight, Home, DollarSign, Headphones, X, AlertTriangle, TrendingDown, Calculator, MessageSquare } from 'lucide-react'

export default function NotFound() {
  const router = useRouter()
  const [lostMoney, setLostMoney] = useState(5715)
  const [rejectedProducts, setRejectedProducts] = useState(47)
  const [validatedCatalogs, setValidatedCatalogs] = useState(3)
  const [seconds, setSeconds] = useState(60)

  useEffect(() => {
    // Easter egg para devs
    console.log("🔴 ERRO 404: Página não encontrada")
    console.log("🟢 SOLUÇÃO: ValidaHub.com.br")
    console.log("💡 Aliás, tá procurando trampo? hiring@validahub.com.br")

    const interval = setInterval(() => {
      setLostMoney(prev => prev + Math.floor(Math.random() * 100) + 50)
      setRejectedProducts(prev => prev + Math.floor(Math.random() * 3) + 1)
      setValidatedCatalogs(prev => prev + (Math.random() > 0.5 ? 1 : 0))
      setSeconds(prev => prev + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const handleValidateCSV = () => {
    router.push('/upload')
  }

  const handleGoHome = () => {
    router.push('/')
  }

  const handleCalculator = () => {
    router.push('/#calculator')
  }

  const handleSupport = () => {
    router.push('/support')
  }

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Background decorations */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-red-500/10 rounded-full blur-3xl animate-pulse" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* CSV quebrado com células piscando */}
          <div className="mb-8 inline-flex">
            <div className="relative">
              <div className="grid grid-cols-3 gap-1 p-4 bg-black/30 rounded-xl border border-red-500/30">
                {[...Array(9)].map((_, i) => (
                  <div 
                    key={i} 
                    className={`w-12 h-12 ${i % 3 === 0 ? 'bg-red-500/20 animate-pulse' : 'bg-gray-800'} rounded border ${i % 3 === 0 ? 'border-red-500' : 'border-gray-700'} flex items-center justify-center`}
                  >
                    {i % 3 === 0 && <X className="w-6 h-6 text-red-500" />}
                  </div>
                ))}
              </div>
              <div className="absolute -top-3 -right-3">
                <div className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full animate-bounce">
                  REJEITADO!
                </div>
              </div>
            </div>
          </div>

          {/* Headlines */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-black text-white mb-2">
            404 - Essa página foi rejeitada
          </h1>
          <p className="text-xl sm:text-2xl text-red-400 font-bold mb-8">
            (igual 27% dos seus produtos no MELI)
          </p>

          {/* Torção com comparação */}
          <div className="bg-black/40 rounded-xl p-6 border border-gray-700 mb-10 max-w-2xl mx-auto">
            <p className="text-lg text-gray-400 mb-4">A diferença?</p>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-left">
                <span className="text-gray-500">Página quebrada =</span>
                <span className="text-yellow-400 font-semibold">você perdeu 10 segundos</span>
              </div>
              <div className="flex items-center justify-between text-left">
                <span className="text-gray-500">Produto rejeitado =</span>
                <span className="text-red-400 font-bold text-xl">você perde R$127/dia</span>
              </div>
            </div>
            <p className="text-white font-bold mt-6 text-xl">
              Qual erro você prefere corrigir primeiro?
            </p>
          </div>

          {/* CTA Principal GIGANTE */}
          <Button
            size="lg"
            onClick={handleValidateCSV}
            className="w-full max-w-2xl bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold px-10 py-8 text-xl rounded-xl shadow-2xl shadow-green-500/30 transition-all duration-200 hover:shadow-3xl hover:shadow-green-500/40 group mb-12 hover:scale-105"
          >
            Validar meu catálogo antes de perder mais vendas
            <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-2 transition-transform" />
          </Button>

          {/* Contador de prejuízo em tempo real */}
          <div className="bg-red-950/30 rounded-xl p-6 border border-red-500/20 mb-12">
            <p className="text-red-400 font-bold text-lg mb-4">
              Enquanto você está aqui perdido, saiba que:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-black/40 rounded-lg p-4">
                <p className="text-3xl font-bold text-green-400">{validatedCatalogs}</p>
                <p className="text-sm text-gray-500 mt-1">
                  sellers validaram catálogos
                  <span className="block text-xs text-green-400">(economizando R${validatedCatalogs * 127})</span>
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

          {/* CTAs secundários com humor */}
          <div className="space-y-6">
            <p className="text-gray-400 font-semibold text-lg">
              Outras formas de parar de perder dinheiro:
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <Button
                variant="outline"
                onClick={handleGoHome}
                className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white group"
              >
                <Home className="mr-2 w-4 h-4" />
                <span>
                  Voltar pro início
                  <span className="block text-xs text-gray-500 group-hover:text-gray-400">(boring mas funciona)</span>
                </span>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleValidateCSV}
                className="border-green-600 text-green-400 hover:bg-green-950 hover:text-green-300 group"
              >
                <ArrowRight className="mr-2 w-4 h-4" />
                <span>
                  Testar o ValidaHub
                  <span className="block text-xs text-green-600 group-hover:text-green-500">(melhor escolha)</span>
                </span>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleCalculator}
                className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white group"
              >
                <Calculator className="mr-2 w-4 h-4" />
                <span>
                  Ver quanto você está perdendo
                  <span className="block text-xs text-gray-500 group-hover:text-gray-400">(spoiler: muito)</span>
                </span>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleSupport}
                className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white group"
              >
                <MessageSquare className="mr-2 w-4 h-4" />
                <span>
                  Reclamar no suporte
                  <span className="block text-xs text-gray-500 group-hover:text-gray-400">(a gente gosta de feedback)</span>
                </span>
              </Button>
            </div>
          </div>

          {/* Footer com provocação */}
          <div className="mt-16 p-6 bg-black/30 rounded-xl border border-gray-800">
            <p className="text-gray-500 text-sm">
              <span className="font-bold text-white">PS:</span> Sabe o que é pior que uma página 404?
            </p>
            <p className="text-red-400 font-semibold mt-2">
              Upload rejeitado depois de 3 dias esperando. 💀
            </p>
          </div>

          {/* Versão minimalista escondida (comentário para dev) */}
          {/* 
          <div className="mt-20 text-center">
            <p className="text-9xl font-black text-white/10">404</p>
            <p className="text-xl text-gray-600 mt-4">
              Essa página: rejeitada ❌<br/>
              Seus produtos: aprovados ✅
            </p>
            <Button className="mt-6">Fazer acontecer →</Button>
          </div>
          */}
        </div>
      </div>
    </section>
  )
}