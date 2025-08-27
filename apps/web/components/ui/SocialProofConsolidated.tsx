'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trophy, TrendingUp, Shield, Star, Quote, ChevronLeft, ChevronRight, Users, Clock, Target } from 'lucide-react'
import { Button } from './button'

export default function SocialProofConsolidated() {
  const [currentSlide, setCurrentSlide] = useState(0)
  
  const slides = [
    // Slide 1: Números Impactantes
    {
      type: 'stats',
      title: '7 das 10 maiores agências já migraram',
      subtitle: 'Os números falam por si',
      stats: [
        { value: '1.247', label: 'Sellers ativos', trend: '+23% este mês', icon: TrendingUp },
        { value: '2.8%', label: 'Taxa de rejeição média', trend: 'vs 15-30% sem ValidaHub', icon: Shield },
        { value: '4.9', label: 'Nota média', trend: '347 avaliações', icon: Star },
      ]
    },
    // Slide 2: Depoimento 1
    {
      type: 'testimonial',
      name: 'Carlos Eduardo',
      company: 'Magazine Luiza Seller',
      role: 'Head de E-commerce',
      quote: 'Redução de 92% no tempo de correção. Nossas vendas subiram 18% em 2 meses.',
      metric: '+R$ 47.000/mês',
      avatar: '👨‍💼'
    },
    // Slide 3: Depoimento 2
    {
      type: 'testimonial',
      name: 'Ana Silva',
      company: 'Netshoes Partner',
      role: 'Gerente de Catálogo',
      quote: 'Antes perdíamos 3 dias por semana corrigindo CSVs. Agora é 30 segundos.',
      metric: '16h → 30seg',
      avatar: '👩‍💼'
    },
    // Slide 4: Depoimento 3
    {
      type: 'testimonial',
      name: 'Roberto Mendes',
      company: 'B2W Marketplace',
      role: 'Coordenador',
      quote: 'ROI em 7 dias. Economizamos R$ 8.400/mês só em retrabalho.',
      metric: 'ROI 700%',
      avatar: '👨‍💻'
    },
    // Slide 5: Profissional vs Amador
    {
      type: 'comparison',
      title: 'Você é profissional ou amador?',
      professional: [
        'Valida antes de publicar',
        'Taxa de rejeição < 5%',
        'Publica em escala',
        'ROI garantido'
      ],
      amateur: [
        'Descobre erros após rejeição',
        'Taxa de rejeição 15-30%',
        'Perde tempo corrigindo',
        'Prejuízo mensal'
      ]
    }
  ]

  // Auto-advance carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length)
    }, 8000) // 8 seconds per slide
    return () => clearInterval(timer)
  }, [])

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length)
  }

  const goToSlide = (index: number) => {
    setCurrentSlide(index)
  }

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-green-950/5 to-transparent" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-6">
            <Trophy className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Prova Social
            </span>
          </div>
        </div>

        {/* Carousel Container */}
        <div className="max-w-5xl mx-auto">
          <div className="relative">
            {/* Slides */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className="min-h-[400px]"
              >
                {slides[currentSlide].type === 'stats' && (
                  <div>
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-2 text-center">
                      {slides[currentSlide].title}
                    </h2>
                    <p className="text-xl text-gray-400 mb-12 text-center">{slides[currentSlide].subtitle}</p>
                    <div className="grid md:grid-cols-3 gap-8">
                      {slides[currentSlide].stats?.map((stat, idx) => {
                        const Icon = stat.icon
                        return (
                          <motion.div
                            key={idx}
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: idx * 0.1 }}
                            className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-8 text-center"
                          >
                            <Icon className="w-12 h-12 text-green-400 mx-auto mb-4" />
                            <div className="text-5xl font-bold text-white mb-2">{stat.value}</div>
                            <div className="text-gray-400">{stat.label}</div>
                            <div className="text-sm text-green-400 mt-2">{stat.trend}</div>
                          </motion.div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {slides[currentSlide].type === 'testimonial' && (
                  <div className="max-w-3xl mx-auto">
                    <div className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-8 relative">
                      <Quote className="absolute top-6 right-6 w-12 h-12 text-green-400/20" />
                      <div className="flex items-start gap-6">
                        <div className="text-5xl">{slides[currentSlide].avatar}</div>
                        <div className="flex-1">
                          <p className="text-xl text-gray-300 mb-6 italic">
                            "{slides[currentSlide].quote}"
                          </p>
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-semibold text-white">{slides[currentSlide].name}</div>
                              <div className="text-sm text-gray-400">{slides[currentSlide].company}</div>
                              <div className="text-xs text-gray-500">{slides[currentSlide].role}</div>
                            </div>
                            <div className="text-3xl font-bold text-green-400">
                              {slides[currentSlide].metric}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {slides[currentSlide].type === 'comparison' && (
                  <div>
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-12 text-center">
                      {slides[currentSlide].title}
                    </h2>
                    <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                      <div className="bg-gradient-to-b from-green-500/10 to-green-500/5 border-2 border-green-500/30 rounded-2xl p-8">
                        <h3 className="text-2xl font-bold text-green-400 mb-6 flex items-center gap-2">
                          <Target className="w-6 h-6" />
                          Profissional
                        </h3>
                        <ul className="space-y-3">
                          {slides[currentSlide].professional?.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                              <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mt-0.5">
                                <div className="w-2 h-2 rounded-full bg-green-400" />
                              </div>
                              <span className="text-gray-300">{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="bg-gradient-to-b from-red-500/10 to-red-500/5 border border-red-500/30 rounded-2xl p-8">
                        <h3 className="text-2xl font-bold text-red-400 mb-6 flex items-center gap-2">
                          <Clock className="w-6 h-6" />
                          Amador
                        </h3>
                        <ul className="space-y-3">
                          {slides[currentSlide].amateur?.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                              <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center mt-0.5">
                                <div className="w-2 h-2 rounded-full bg-red-400" />
                              </div>
                              <span className="text-gray-400">{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>

            {/* Navigation Arrows */}
            <button
              onClick={prevSlide}
              className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-12 md:-translate-x-16 p-3 bg-gray-800/50 border border-gray-700 rounded-full hover:bg-gray-700/50 transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={nextSlide}
              className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-12 md:translate-x-16 p-3 bg-gray-800/50 border border-gray-700 rounded-full hover:bg-gray-700/50 transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-white" />
            </button>

            {/* Dots Indicator */}
            <div className="flex justify-center gap-2 mt-8">
              {slides.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => goToSlide(idx)}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    idx === currentSlide 
                      ? 'w-8 bg-green-400' 
                      : 'w-2 bg-gray-600 hover:bg-gray-500'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <Button
            onClick={() => {
              const dataSection = document.querySelector('[data-section="data"]')
              if (dataSection) {
                dataSection.scrollIntoView({ behavior: 'smooth' })
              }
            }}
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20"
          >
            Ver demonstração ao vivo
          </Button>
        </div>
      </div>
    </section>
  )
}