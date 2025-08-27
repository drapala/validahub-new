'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { ArrowRight, X, Check, AlertCircle, FileSpreadsheet } from 'lucide-react'
import { Button } from './button'
import { useRouter } from 'next/navigation'

const Lottie = dynamic(() => import('lottie-react'), { ssr: false })

export default function PainGainVisualization() {
  const [isAnimating, setIsAnimating] = useState(false)
  const [showGain, setShowGain] = useState(false)
  const [cellAnimations, setCellAnimations] = useState<number[]>([])
  const router = useRouter()

  useEffect(() => {
    // Auto-animate every 5 seconds
    const interval = setInterval(() => {
      handleAnimation()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [showGain])

  const handleAnimation = () => {
    setIsAnimating(true)
    
    if (!showGain) {
      // Animate cells turning green one by one
      csvData.forEach((_, index) => {
        setTimeout(() => {
          setCellAnimations(prev => [...prev, index])
        }, 100 * index)
      })
      
      setTimeout(() => {
        setShowGain(true)
        setIsAnimating(false)
      }, 800)
    } else {
      setCellAnimations([])
      setTimeout(() => {
        setShowGain(false)
        setIsAnimating(false)
      }, 300)
    }
  }

  const csvData = [
    { 
      field: 'title', 
      errorValue: 'Produto Incrível Compre Agora!!!', 
      fixedValue: 'Produto Incrível - Entrega Imediata',
      error: 'Excesso de caracteres especiais',
      status: 'Título otimizado'
    },
    { 
      field: 'price', 
      errorValue: 'R$ 15,999.99', 
      fixedValue: '15999.99',
      error: 'Formato inválido', 
      status: 'Formato correto'
    },
    { 
      field: 'category_id', 
      errorValue: 'MLB1234', 
      fixedValue: 'MLB1055',
      error: 'Categoria inexistente', 
      status: 'Categoria válida'
    },
    { 
      field: 'brand', 
      errorValue: '', 
      fixedValue: 'Generic',
      error: 'Campo vazio', 
      status: 'Preenchido'
    },
    { 
      field: 'ean', 
      errorValue: '789012345678', 
      fixedValue: '7890123456789',
      error: 'EAN inválido', 
      status: 'EAN correto'
    },
  ]

  // Lottie animation data (simplified)
  const errorAnimationData = {
    v: "5.5.7",
    fr: 30,
    ip: 0,
    op: 60,
    w: 200,
    h: 200,
    nm: "Error Animation",
    ddd: 0,
    assets: [],
    layers: [{
      ddd: 0,
      ind: 1,
      ty: 4,
      nm: "Circle",
      sr: 1,
      ks: {
        o: { a: 0, k: 100 },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [100, 100, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: { 
          a: 1, 
          k: [
            { t: 0, s: [100, 100, 100] },
            { t: 30, s: [120, 120, 100] },
            { t: 60, s: [100, 100, 100] }
          ]
        }
      },
      ao: 0,
      shapes: [{
        ty: "el",
        p: { a: 0, k: [0, 0] },
        s: { a: 0, k: [80, 80] },
        nm: "Ellipse Path"
      }, {
        ty: "fl",
        c: { a: 0, k: [0.95, 0.2, 0.2, 1] },
        o: { a: 0, k: 100 },
        nm: "Fill"
      }],
      ip: 0,
      op: 60,
      st: 0,
      bm: 0
    }]
  }

  const successAnimationData = {
    ...errorAnimationData,
    layers: [{
      ...errorAnimationData.layers[0],
      shapes: [{
        ty: "el",
        p: { a: 0, k: [0, 0] },
        s: { a: 0, k: [80, 80] },
        nm: "Ellipse Path"
      }, {
        ty: "fl",
        c: { a: 0, k: [0.2, 0.95, 0.4, 1] },
        o: { a: 0, k: 100 },
        nm: "Fill"
      }]
    }]
  }

  return (
    <section className="py-24 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full mb-6">
            <AlertCircle className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-400 font-medium">
              Visualização em tempo real
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
            De <span className="text-red-400">stress</span> para 
            <span className="text-green-400"> confiança</span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Veja exatamente como o ValidaHub transforma seu CSV problemático 
            em um arquivo perfeito, pronto para publicação.
          </p>
        </div>

        {/* Main Visualization Container */}
        <div className="max-w-6xl mx-auto">
          <div className="relative bg-gradient-to-b from-gray-800/30 to-gray-900/30 border border-gray-700 rounded-3xl p-8 overflow-hidden">
            {/* Animation Toggle Button */}
            <button
              onClick={handleAnimation}
              className="absolute top-6 right-6 px-4 py-2 bg-purple-500/20 border border-purple-500/30 rounded-lg text-purple-400 hover:bg-purple-500/30 transition-colors text-sm font-medium z-20"
            >
              {showGain ? 'Ver Problema' : 'Ver Solução'}
            </button>

            {/* CSV Visualization */}
            <div className={`transition-all duration-500 ${isAnimating ? 'scale-95 opacity-50' : 'scale-100 opacity-100'}`}>
              {!showGain ? (
                // Pain State - CSV with errors
                <div className="space-y-6">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-20 h-20">
                      <Lottie animationData={errorAnimationData} loop={true} />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">CSV com Erros</h3>
                      <p className="text-red-400">5 erros críticos detectados</p>
                    </div>
                  </div>

                  <div className="bg-black/30 rounded-xl p-6 border border-red-500/20">
                    <div className="font-mono text-sm">
                      {/* CSV Header */}
                      <div className="flex gap-4 pb-3 mb-3 border-b border-gray-700 text-gray-500">
                        <span className="w-32">Campo</span>
                        <span className="flex-1">Valor</span>
                        <span className="w-64">Erro</span>
                      </div>
                      
                      {/* CSV Rows with Errors */}
                      {csvData.map((row, index) => (
                        <div 
                          key={index} 
                          className={`flex gap-4 py-3 rounded transition-all duration-500 ${
                            cellAnimations.includes(index) 
                              ? 'bg-green-950/30 scale-105' 
                              : 'hover:bg-red-950/20'
                          }`}
                        >
                          <span className="w-32 text-gray-400">{row.field}</span>
                          <span className={`flex-1 font-mono transition-all duration-500 ${
                            cellAnimations.includes(index) 
                              ? 'text-green-400 font-bold' 
                              : 'text-white bg-red-500/10 px-2 rounded'
                          }`}>
                            {cellAnimations.includes(index) ? row.fixedValue : (row.errorValue || '(vazio)')}
                          </span>
                          <span className={`w-64 flex items-center gap-2 transition-all duration-500 ${
                            cellAnimations.includes(index) 
                              ? 'text-green-400' 
                              : 'text-red-400'
                          }`}>
                            {cellAnimations.includes(index) ? (
                              <>
                                <Check className="w-4 h-4" />
                                {row.status}
                              </>
                            ) : (
                              <>
                                <X className="w-4 h-4" />
                                {row.error}
                              </>
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-4 text-gray-400">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                      <span>Anúncio será rejeitado</span>
                    </div>
                    <ArrowRight className="w-5 h-5" />
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                      <span>Vendas perdidas</span>
                    </div>
                  </div>
                </div>
              ) : (
                // Gain State - CSV fixed
                <div className="space-y-6">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-20 h-20">
                      <Lottie animationData={successAnimationData} loop={true} />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">CSV Validado e Corrigido</h3>
                      <p className="text-green-400">Pronto para publicação</p>
                    </div>
                  </div>

                  <div className="bg-black/30 rounded-xl p-6 border border-green-500/20">
                    <div className="font-mono text-sm">
                      {/* CSV Header */}
                      <div className="flex gap-4 pb-3 mb-3 border-b border-gray-700 text-gray-500">
                        <span className="w-32">Campo</span>
                        <span className="flex-1">Valor</span>
                        <span className="w-64">Status</span>
                      </div>
                      
                      {/* CSV Rows Fixed */}
                      {csvData.map((row, index) => (
                        <div key={index} className="flex gap-4 py-3 hover:bg-green-950/20 rounded transition-colors">
                          <span className="w-32 text-gray-400">{row.field}</span>
                          <span className="flex-1 text-white font-mono bg-green-500/10 px-2 rounded">{row.fixedValue}</span>
                          <span className="w-64 text-green-400 flex items-center gap-2">
                            <Check className="w-4 h-4" />
                            {row.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-4 text-gray-400">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                      <span>Anúncio aprovado</span>
                    </div>
                    <ArrowRight className="w-5 h-5" />
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span>Vendas garantidas</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Processing Animation Overlay */}
            {isAnimating && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10 rounded-3xl">
                <div className="text-center">
                  <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-white font-medium">Processando com ValidaHub...</p>
                </div>
              </div>
            )}
          </div>

          {/* Bottom CTA */}
          <div className="mt-12 text-center">
            <p className="text-2xl font-bold text-white mb-4">
              Arrasta. Solta. Pronto.
            </p>
            <p className="text-lg text-gray-400 mb-8">
              Seus CSVs validados e corrigidos em 30 segundos.
            </p>
            <Button 
              onClick={() => router.push('/upload')}
              className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
            >
              Testar com seu CSV mais problemático
              <ArrowRight className="inline ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}