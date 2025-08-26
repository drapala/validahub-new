'use client'

import { Trophy, TrendingUp, Shield, Star, Quote, ArrowRight } from 'lucide-react'
import { Button } from './button'
import { useRouter } from 'next/navigation'

export default function SocialProof() {
  const router = useRouter()
  
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
  
  const topSellers = [
    "Magazine Luiza Official Store",
    "Casas Bahia Marketplace", 
    "Via Varejo",
    "B2W Digital",
    "Americanas S.A.",
    "Netshoes",
    "Dafiti Group",
    "Mercado Livre Gold"
  ]

  const agencies = [
    "E-commerce Group",
    "Rocket Commerce",
    "Agência Magis",
    "Nuvemshop Partners",
    "VTEX IO",
    "Tray Corp",
    "Loja Integrada Pro"
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

        {/* Companies Grid */}
        <div className="grid md:grid-cols-2 gap-12">
          {/* Top Sellers */}
          <div>
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              Power Sellers que confiam
            </h3>
            <div className="space-y-3">
              {topSellers.map((seller, index) => (
                <div 
                  key={index}
                  className="flex items-center gap-3 p-3 bg-gray-900/50 border border-gray-800 rounded-lg hover:border-green-500/30 transition-colors"
                >
                  <div className="w-8 h-8 bg-green-500/10 rounded flex items-center justify-center">
                    <span className="text-xs font-bold text-green-400">{index + 1}</span>
                  </div>
                  <span className="text-gray-300">{seller}</span>
                  {index < 3 && (
                    <span className="ml-auto text-xs bg-yellow-500/10 text-yellow-400 px-2 py-1 rounded">
                      TOP
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Agencies */}
          <div>
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              Agências certificadas
            </h3>
            <div className="space-y-3">
              {agencies.map((agency, index) => (
                <div 
                  key={index}
                  className="flex items-center gap-3 p-3 bg-gray-900/50 border border-gray-800 rounded-lg hover:border-blue-500/30 transition-colors"
                >
                  <div className="w-8 h-8 bg-blue-500/10 rounded flex items-center justify-center">
                    <Shield className="w-4 h-4 text-blue-400" />
                  </div>
                  <span className="text-gray-300">{agency}</span>
                  <span className="ml-auto text-xs bg-blue-500/10 text-blue-400 px-2 py-1 rounded">
                    PRO
                  </span>
                </div>
              ))}
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