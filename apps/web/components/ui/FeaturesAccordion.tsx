'use client'

import { Zap, TrendingDown, CheckCircle2, Users, AlertCircle } from 'lucide-react'
import { Button } from './button'

export default function FeaturesAccordion() {
  
  const features = [
    {
      icon: TrendingDown,
      title: '<3% de rejeição garantida',
      subtitle: 'Ou devolvemos 100% do seu dinheiro',
      proof: 'Média atual: 2.8% (1.247 sellers)',
      highlight: true
    },
    {
      icon: Zap,
      title: 'Correção em 30 segundos',
      subtitle: 'Seu CSV pronto sem retrabalho',
      proof: '92% menos erros manuais'
    },
    {
      icon: AlertCircle,
      title: 'Zero custo de integração',
      subtitle: 'Upload, valida, baixa. Pronto.',
      proof: 'Setup em menos de 5 minutos'
    },
    {
      icon: Users,
      title: 'API para times grandes',
      subtitle: '10.000 produtos por minuto',
      proof: 'SDK Python, Node, PHP'
    }
  ]

  return (
    <section className="py-20 relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header - mais direto */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-white">
            Menos rejeição.
            <span className="block text-green-400">Mais vendas.</span>
          </h2>
        </div>

        {/* Cards simples - todos abertos */}
        <div className="max-w-4xl mx-auto grid gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon
            
            return (
              <div
                key={index}
                className={`rounded-xl p-5 transition-all duration-200 ${
                  feature.highlight 
                    ? 'bg-gradient-to-r from-green-500/10 to-green-500/5 border-2 border-green-500/30' 
                    : 'bg-neutral-900/40 border border-neutral-800/50 hover:border-neutral-700'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className={`p-2 rounded-lg flex-shrink-0 ${
                    feature.highlight ? 'bg-green-500/20' : 'bg-neutral-800'
                  }`}>
                    <Icon className={`w-5 h-5 ${
                      feature.highlight ? 'text-green-400' : 'text-neutral-400'
                    }`} />
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-1">
                      <div>
                        <h3 className={`text-lg font-bold ${
                          feature.highlight ? 'text-green-400' : 'text-white'
                        }`}>
                          {feature.title}
                        </h3>
                        <p className="text-sm text-neutral-400 mt-0.5">
                          {feature.subtitle}
                        </p>
                      </div>
                    </div>
                    
                    {/* Proof */}
                    <div className="flex items-center gap-2 mt-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                      <span className="text-xs text-neutral-500">
                        {feature.proof}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* CTA simplificado */}
        <div className="mt-12 text-center">
          <p className="text-neutral-400 mb-4">
            Junte-se aos 1.247 sellers que já reduziram rejeições
          </p>
          <Button
            onClick={() => {
              const pricingSection = document.querySelector('[data-section="pricing"]')
              if (pricingSection) {
                pricingSection.scrollIntoView({ behavior: 'smooth' })
              }
            }}
            className="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg"
          >
            Testar gratuitamente
          </Button>
        </div>
      </div>
    </section>
  )
}