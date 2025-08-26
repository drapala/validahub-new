'use client'

import { Trophy, TrendingUp, Shield, Star, Quote, ArrowRight, ShoppingCart, Store, Package, Truck, CreditCard } from 'lucide-react'
import { Button } from './button'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function SocialProof() {
  const router = useRouter()
  const [currentIndex, setCurrentIndex] = useState(0)
  
  const trustedCompanies = [
    { 
      name: 'MERCADO LIVRE', 
      logo: (
        <svg viewBox="0 0 134 41" className="w-32 h-10" fill="none">
          <rect width="134" height="41" rx="6" fill="#FFE600"/>
          <path d="M30 20.5C30 26.299 25.299 31 19.5 31C13.701 31 9 26.299 9 20.5C9 14.701 13.701 10 19.5 10C25.299 10 30 14.701 30 20.5Z" fill="#2D3277"/>
          <path d="M19.5 13C17.29 13 15.5 14.79 15.5 17C15.5 19.21 17.29 21 19.5 21C21.71 21 23.5 19.21 23.5 17C23.5 14.79 21.71 13 19.5 13ZM19.5 19C18.4 19 17.5 18.1 17.5 17C17.5 15.9 18.4 15 19.5 15C20.6 15 21.5 15.9 21.5 17C21.5 18.1 20.6 19 19.5 19Z" fill="white"/>
          <path d="M38 16H40L42.5 20L45 16H47V25H45V19L42.5 23L40 19V25H38V16ZM49 16H56V18H51V19.5H55V21.5H51V23H56V25H49V16ZM58 16H62C64 16 65.5 17 65.5 19C65.5 20.5 64.5 21.5 63 21.5L66 25H63.5L61 21.5H60V25H58V16ZM60 18V19.5H62C62.5 19.5 63 19.5 63 18.75C63 18 62.5 18 62 18H60ZM75 21C75 19 73.5 17.5 71.5 17.5C69.5 17.5 68 19 68 21C68 23 69.5 24.5 71.5 24.5C73 24.5 74.5 23.5 75 22H73C72.5 22.5 72 23 71.5 23C70.5 23 69.5 22 69.5 21C69.5 20 70.5 19 71.5 19C72 19 72.5 19.5 73 20H75V21ZM80 17.5H82L85 25H83L82.5 23.5H79.5L79 25H77L80 17.5ZM80.5 21.5H81.5L81 20L80.5 21.5ZM87 17.5H91C93 17.5 94.5 19 94.5 21C94.5 23 93 24.5 91 24.5H87V17.5ZM89 19.5V22.5H91C91.5 22.5 92.5 22 92.5 21C92.5 20 91.5 19.5 91 19.5H89ZM102 21C102 19 100.5 17.5 98.5 17.5C96.5 17.5 95 19 95 21C95 23 96.5 24.5 98.5 24.5C100.5 24.5 102 23 102 21ZM100 21C100 22 99 23 98 23C97 23 96 22 96 21C96 20 97 19 98 19C99 19 100 20 100 21ZM109 16H111V25H109V16ZM113 17.5H115V25H113V17.5ZM113 15H115V16.5H113V15ZM117 17.5H119L121 21L123 17.5H125L122 22.5L125 25H123L121 22L119 25H117L120 21L117 17.5Z" fill="#2D3277"/>
        </svg>
      )
    },
    { 
      name: 'MAGAZINE LUIZA', 
      logo: (
        <svg viewBox="0 0 134 41" className="w-32 h-10" fill="none">
          <rect width="134" height="41" rx="6" fill="#0086FF"/>
          <circle cx="20" cy="20.5" r="8" fill="white"/>
          <path d="M20 16.5C17.79 16.5 16 18.29 16 20.5C16 22.71 17.79 24.5 20 24.5C22.21 24.5 24 22.71 24 20.5C24 18.29 22.21 16.5 20 16.5Z" fill="#0086FF"/>
          <path d="M32 15H34L36 19L38 15H40V24H38V18L36 22L34 18V24H32V15ZM42 15H44L47 24H45L44.5 22H41.5L41 24H39L42 15ZM42.5 20H43.5L43 18L42.5 20ZM55 20H53V18H58V24H56V22C55.5 23 54.5 24 53 24C51 24 49 22.5 49 20C49 17.5 51 16 53 16C54.5 16 55.5 17 56 18H54C53.5 17.5 53 17.5 52.5 17.5C51.5 17.5 50.5 18.5 50.5 20C50.5 21.5 51.5 22.5 52.5 22.5C53.5 22.5 54.5 22 55 21V20ZM60 15H62L65 24H63L62.5 22H59.5L59 24H57L60 15ZM60.5 20H61.5L61 18L60.5 20ZM67 22H73V24H65V22L71 18H66V16H73V18L67 22ZM75 15H77V24H75V15ZM79 16H81L84 20V16H86V24H84L81 20V24H79V16ZM88 16H95V18H90V19H94V21H90V22H95V24H88V16ZM102 15H104V24H102V15ZM106 20C106 22.5 107.5 24 110 24C112.5 24 114 22.5 114 20V16H112V20C112 21.5 111.5 22.5 110 22.5C108.5 22.5 108 21.5 108 20V16H106V20ZM116 15H118V24H116V15ZM120 22H126V24H118V22L124 18H119V16H126V18L120 22ZM128 16H130L133 24H131L130.5 22H127.5L127 24H125L128 16Z" fill="white"/>
        </svg>
      )
    },
    { 
      name: 'B2W Digital', 
      logo: (
        <svg viewBox="0 0 134 41" className="w-32 h-10" fill="none">
          <rect width="134" height="41" rx="6" fill="#ED1C24"/>
          <path d="M25 16H30C32 16 34 17 34 19C34 20 33.5 21 32.5 21.5C33.5 22 34.5 23 34.5 24C34.5 26 32.5 27 30.5 27H25V16ZM27 18V20H29.5C30.5 20 31.5 19.5 31.5 19C31.5 18.5 30.5 18 29.5 18H27ZM27 22V25H30C31 25 32 24.5 32 23.5C32 22.5 31 22 30 22H27ZM37 25L42 20C43.5 18.5 44 17.5 44 16.5C44 14.5 42 13 39.5 13C37 13 35 14.5 35 17H37.5C37.5 15.5 38.5 15 39.5 15C40.5 15 41.5 15.5 41.5 16.5C41.5 17 41 17.5 40 18.5L35 23.5V27H44V25H37ZM46 16H49L51 23L53 16H56L58 23L60 16H63L60 27H57L55 20L53 27H50L47 16Z" fill="white"/>
          <path d="M70 16H75C78 16 80 18 80 21C80 24 78 26 75 26H70V16ZM72 18V24H75C77 24 78 23 78 21C78 19 77 18 75 18H72ZM82 16H84V26H82V16ZM95 21H93V19H98V26H96V24C95.5 25 94.5 26 93 26C91 26 89 24.5 89 22C89 19.5 91 18 93 18C94.5 18 95.5 19 96 20H94C93.5 19.5 93 19.5 92.5 19.5C91.5 19.5 90.5 20.5 90.5 22C90.5 23.5 91.5 24.5 92.5 24.5C93.5 24.5 94.5 24 95 23V21ZM100 16H102V26H100V16ZM104 16H111V18H108V26H106V18H104V16ZM113 16H115L118 26H116L115.5 24H112.5L112 26H110L113 16ZM113.5 22H114.5L114 19L113.5 22ZM120 16H122V24H126V26H120V16Z" fill="white"/>
        </svg>
      )
    },
    { 
      name: 'AMERICANAS', 
      logo: (
        <svg viewBox="0 0 134 41" className="w-32 h-10" fill="none">
          <rect width="134" height="41" rx="6" fill="#E60014"/>
          <path d="M18 26L21 17H23L26 26H24L23.5 24H20.5L20 26H18ZM21 22H23L22 19L21 22ZM27 17H29L31 22L33 17H35V26H33V21L31 25L29 21V26H27V17ZM37 17H43V19H39V20.5H42V22.5H39V24H43V26H37V17ZM45 17H49C51 17 52.5 18 52.5 20C52.5 21.5 51.5 22.5 50 22.5L53 26H50.5L48 22.5H47V26H45V17ZM47 19V20.5H49C49.5 20.5 50 20.5 50 20C50 19.5 49.5 19 49 19H47ZM55 17H57V26H55V17ZM65 22C65 20 63.5 18.5 61.5 18.5C59.5 18.5 58 20 58 22C58 24 59.5 25.5 61.5 25.5C63 25.5 64.5 24.5 65 23H63C62.5 23.5 62 24 61.5 24C60.5 24 59.5 23 59.5 22C59.5 21 60.5 20 61.5 20C62 20 62.5 20.5 63 21H65V22ZM67 26L70 17H72L75 26H73L72.5 24H69.5L69 26H67ZM70 22H72L71 19L70 22ZM77 17H79L82 21V17H84V26H82L79 22V26H77V17ZM86 26L89 17H91L94 26H92L91.5 24H88.5L88 26H86ZM89 22H91L90 19L89 22ZM101 19C101 17.5 99.5 16.5 98 16.5C96.5 16.5 95 17.5 95 19H97C97 18.5 97.5 18 98 18C98.5 18 99 18.5 99 19C99 19.5 98.5 20 97.5 20C96 20 95 21 95 22.5C95 24 96 25.5 98 25.5C99.5 25.5 100.5 24.5 101 23H99C98.5 23.5 98 24 97.5 24C97 24 96.5 23.5 96.5 23C96.5 22.5 97 22 97.5 22C99 22 101 21 101 19Z" fill="white"/>
        </svg>
      )
    },
    { 
      name: 'VIA', 
      logo: (
        <svg viewBox="0 0 134 41" className="w-32 h-10" fill="none">
          <rect width="134" height="41" rx="6" fill="#7B00E0"/>
          <path d="M45 16H48L51 25L54 16H57L52 28H50L45 16ZM59 16H61V28H59V16ZM64 28L69 16H71L76 28H73L72 25H68L67 28H64ZM69 23H71L70 19L69 23Z" fill="white"/>
          <circle cx="30" cy="20.5" r="8" stroke="white" strokeWidth="2" fill="none"/>
          <path d="M27 20.5L29 22.5L33 18.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      )
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
            Confiam no ValidaHub
          </h3>
          <div className="relative h-24 overflow-hidden">
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
                          {company.logo}
                        </div>
                      )
                    })}
                  </div>
                  
                  {/* Dots indicator */}
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex gap-2">
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