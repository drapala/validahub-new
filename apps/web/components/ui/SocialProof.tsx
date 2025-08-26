'use client'

import { Trophy, TrendingUp, Shield, Star, Quote, ArrowRight } from 'lucide-react'
import { Button } from './button'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import Image from 'next/image'

export default function SocialProof() {
  const router = useRouter()
  const [currentIndex, setCurrentIndex] = useState(0)
  
  const trustedCompanies = [
    { 
      name: 'Mercado Livre', 
      logo: '/logos/mercadolivre.png',
      width: 140,
      height: 40
    },
    { 
      name: 'Magazine Luiza', 
      logo: '/logos/magalu.png',
      width: 120,
      height: 40
    },
    { 
      name: 'Americanas', 
      logo: '/logos/Lojas_Americanas_Logo.svg',
      width: 140,
      height: 35
    },
    { 
      name: 'Amazon', 
      logo: '/logos/amazon.png',
      width: 100,
      height: 30
    },
    { 
      name: 'Shopee', 
      logo: '/logos/shopee.png',
      width: 120,
      height: 40
    },
    { 
      name: 'Submarino', 
      logo: '/logos/submarino.png',
      width: 130,
      height: 35
    },
    { 
      name: 'Via', 
      logo: '/logos/via.png',
      width: 100,
      height: 40
    },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % trustedCompanies.length)
    }, 2000) // Change every 2 seconds

    return () => clearInterval(interval)
  }, [trustedCompanies.length])
  
  const testimonials = [
    {
      name: "Carlos Eduardo",
      company: "Magazine Luiza Seller",
      role: "Head de E-commerce",
      quote: "Redução de 92% no tempo de correção. Nossas vendas subiram 18% em 2 meses.",
      metric: "+R$ 47.000/mês"
    },
    {
      name: "Ana Silva",  
      company: "Netshoes Partner",
      role: "Gerente de Catálogo",
      quote: "Antes perdíamos 3 dias por semana corrigindo CSVs. Agora é 30 segundos.",
      metric: "16h → 30seg"
    },
    {
      name: "Roberto Mendes",
      company: "B2W Marketplace", 
      role: "Coordenador",
      quote: "ROI em 7 dias. Economizamos R$ 8.400/mês só em retrabalho.",
      metric: "ROI 700%"
    }
  ]
  

  return (
    <section className="py-24 bg-black relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-green-950/10 to-transparent" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-6">
            <Trophy className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Os profissionais usam ValidaHub
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            7 das 10 maiores agências de marketplace
            <span className="block text-green-400">já migraram para ValidaHub</span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Enquanto amadores perdem tempo com erros bestas, 
            <span className="text-white font-semibold"> profissionais validam e publicam em escala.</span>
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-8 text-center">
            <TrendingUp className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <div className="text-5xl font-bold text-white mb-2">1.247</div>
            <div className="text-gray-400">Sellers ativos</div>
            <div className="text-sm text-green-400 mt-2">+23% este mês</div>
          </div>
          
          <div className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-8 text-center">
            <Shield className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <div className="text-5xl font-bold text-white mb-2">2.8%</div>
            <div className="text-gray-400">Taxa de rejeição média</div>
            <div className="text-sm text-red-400 mt-2">vs 15-30% sem ValidaHub</div>
          </div>
          
          <div className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-8 text-center">
            <Star className="w-12 h-12 text-green-400 mx-auto mb-4" />
            <div className="text-5xl font-bold text-white mb-2">4.9</div>
            <div className="text-gray-400">Nota média</div>
            <div className="text-sm text-gray-500 mt-2">347 avaliações</div>
          </div>
        </div>

        {/* Trusted Companies Carousel */}
        <div className="mt-16 mb-16">
          <h3 className="text-xl font-semibold text-gray-400 text-center mb-8">
            Resultados para vendedores de grandes marketplaces
          </h3>
          <div className="relative h-32 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-gray-900/50 to-gray-800/30 rounded-2xl border border-gray-700">
              <div className="flex items-center justify-center h-full">
                <div className="relative w-full max-w-4xl">
                  {/* Carousel Items */}
                  <div className="flex items-center justify-center gap-8">
                    {trustedCompanies.map((company, index) => {
                      const isActive = index === currentIndex
                      const isPrev = index === (currentIndex - 1 + trustedCompanies.length) % trustedCompanies.length
                      const isNext = index === (currentIndex + 1) % trustedCompanies.length
                      
                      return (
                        <div
                          key={index}
                          className={`absolute transition-all duration-500 transform ${
                            isActive 
                              ? 'opacity-100 scale-125 z-20 translate-x-0' 
                              : isPrev
                              ? 'opacity-30 scale-90 -translate-x-56 z-10'
                              : isNext
                              ? 'opacity-30 scale-90 translate-x-56 z-10'
                              : 'opacity-0 scale-75 z-0'
                          }`}
                        >
                          {company.name === 'Amazon' ? (
                            <div className="bg-white/90 rounded-lg px-4 py-2">
                              <Image
                                src={company.logo}
                                alt={company.name}
                                width={company.width}
                                height={company.height}
                                className="object-contain"
                                priority={index === 0}
                              />
                            </div>
                          ) : (
                            <Image
                              src={company.logo}
                              alt={company.name}
                              width={company.width}
                              height={company.height}
                              className="object-contain"
                              priority={index === 0}
                            />
                          )}
                        </div>
                      )
                    })}
                  </div>
                  
                  {/* Dots indicator */}
                  <div className="absolute left-1/2 transform -translate-x-1/2 flex gap-2" style={{ top: 'calc(100% + 2rem)' }}>
                    {trustedCompanies.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentIndex(index)}
                        className={`w-2 h-2 rounded-full transition-all ${
                          index === currentIndex
                            ? 'bg-green-400 w-6'
                            : 'bg-gray-600 hover:bg-gray-500'
                        }`}
                        aria-label={`Go to slide ${index + 1}`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="mt-20">
          <h3 className="text-3xl font-bold text-white text-center mb-12">
            Resultados reais, sem hype
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index}
                className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-6 hover:border-green-500/30 transition-all"
              >
                <Quote className="w-8 h-8 text-green-400/30 mb-4" />
                <p className="text-gray-300 mb-6 italic">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center justify-between border-t border-gray-800 pt-4">
                  <div>
                    <div className="font-semibold text-white">{testimonial.name}</div>
                    <div className="text-sm text-gray-400">{testimonial.company}</div>
                    <div className="text-xs text-gray-500">{testimonial.role}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-400">{testimonial.metric}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Logos Section */}
        <div className="mt-20 text-center">
          <p className="text-gray-400 mb-8">Confiam no ValidaHub:</p>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-60">
            {/* Mercado Livre */}
            <svg className="h-10" viewBox="0 0 134 30" fill="currentColor">
              <text x="0" y="20" className="text-gray-400 font-bold text-lg">MERCADO LIVRE</text>
            </svg>
            {/* Magazine Luiza */}
            <svg className="h-10" viewBox="0 0 120 30" fill="currentColor">
              <text x="0" y="20" className="text-gray-400 font-bold text-lg">MAGALU</text>
            </svg>
            {/* B2W */}
            <svg className="h-10" viewBox="0 0 60 30" fill="currentColor">
              <text x="0" y="20" className="text-gray-400 font-bold text-lg">B2W</text>
            </svg>
            {/* Americanas */}
            <svg className="h-10" viewBox="0 0 120 30" fill="currentColor">
              <text x="0" y="20" className="text-gray-400 font-bold text-lg">AMERICANAS</text>
            </svg>
            {/* Via Varejo */}
            <svg className="h-10" viewBox="0 0 100 30" fill="currentColor">
              <text x="0" y="20" className="text-gray-400 font-bold text-lg">VIA VAREJO</text>
            </svg>
          </div>
        </div>
        
        {/* CTA Intermediário */}
        <div className="mt-16 text-center">
          <Button
            onClick={() => router.push('/upload')}
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
          >
            Testar grátis com 1.000 validações
            <ArrowRight className="inline ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>

        {/* Bottom Badge */}
        <div className="mt-16 text-center">
          <div className="inline-flex flex-col items-center gap-4 p-8 bg-gradient-to-b from-green-950/20 to-green-950/10 border border-green-500/20 rounded-2xl">
            <div className="text-3xl font-bold text-white">
              Você é <span className="text-green-400">profissional</span> ou <span className="text-red-400">amador</span>?
            </div>
            <p className="text-gray-400 max-w-2xl">
              Profissionais não arriscam. Eles validam, corrigem e publicam com confiança.
              Amadores descobrem os erros quando o anúncio é rejeitado.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}