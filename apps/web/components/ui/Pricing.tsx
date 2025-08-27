'use client'

import { useState } from 'react'
import { Button } from './button'
import { Switch } from './switch'
import { Check, X, Zap, Rocket, Crown } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
// AuthModal is temporarily commented out
// import { AuthModal } from '@/components/blocks/AuthModal'

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const router = useRouter()
  const { data: session } = useSession()

  const plans = [
    {
      name: 'Free',
      price: isAnnual ? 'R$ 0' : 'R$ 0',
      description: 'Para testar com seu CSV mais problemático',
      features: [
        '1.000 validações grátis',
        'Detecta os 47 erros fatais',
        'Correções básicas automáticas',
        'Regras MELI + Amazon',
        'Download do CSV corrigido',
      ],
      notIncluded: [
        'API e Webhooks',
        'Histórico de jobs',
        'Suporte prioritário',
        'Multi-marketplace',
      ],
      cta: 'Testar grátis agora',
      highlighted: false,
      action: () => {
        if (session) {
          router.push('/upload')
        } else {
          setAuthMode('signup')
          setAuthModalOpen(true)
        }
      }
    },
    {
      name: 'Pro',
      price: isAnnual ? 'R$ 87' : 'R$ 97',
      period: '/mês',
      description: 'ROI positivo desde o primeiro mês',
      features: [
        'Validações ilimitadas',
        'Todos os marketplaces',
        'Correções automáticas avançadas',
        'API e Webhooks',
        'Histórico de 90 dias',
        'Suporte em até 2h',
        'Detecta e corrige 47+ erros',
        '2,8% taxa de rejeição garantida',
      ],
      notIncluded: [
        'Ambiente dedicado',
        'SLA customizado',
      ],
      cta: 'Começar Pro agora',
      highlighted: true,
      badge: 'Lucro garantido',
      action: () => {
        if (session) {
          router.push('/settings/billing?plan=pro')
        } else {
          setAuthMode('signup')
          setAuthModalOpen(true)
        }
      }
    },
    {
      name: 'Enterprise',
      price: 'R$ 297+',
      description: 'Para quem não pode errar',
      features: [
        'Tudo do Pro, mais:',
        'Ambiente dedicado isolado',
        'SLA 99.9% garantido',
        'Regras 100% customizadas',
        'API sem limite de rate',
        'Treinamento da sua equipe',
        'WhatsApp direto com suporte',
        'Compliance LGPD certificado',
      ],
      notIncluded: [],
      cta: 'Falar com vendas',
      highlighted: false,
      action: () => {
        window.location.href = 'mailto:vendas@validahub.com?subject=Plano Enterprise ValidaHub'
      }
    }
  ]

  return (
    <>
      <section id="pricing" className="py-20 bg-gray-800/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Custa menos que <span className="text-red-400">1 produto rejeitado</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              R$ 97/mês vs R$ 3.810/mês em vendas perdidas. 
              <span className="text-white font-semibold">Faça a conta.</span>
            </p>
            
            {/* Visual Summary of Plans */}
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
              <div className="bg-gray-800/50 rounded-xl p-6 text-center border border-gray-700">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">Free</h3>
                <p className="text-sm text-gray-400">Para Testar</p>
                <p className="text-xs text-gray-500 mt-2">1.000 validações</p>
              </div>
              
              <div className="bg-gradient-to-b from-green-500/20 to-green-500/10 rounded-xl p-6 text-center border-2 border-green-500/30 scale-105">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Rocket className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">Pro</h3>
                <p className="text-sm text-green-400 font-semibold">Para Escalar</p>
                <p className="text-xs text-gray-400 mt-2">Ilimitado + API</p>
              </div>
              
              <div className="bg-gray-800/50 rounded-xl p-6 text-center border border-gray-700">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Crown className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">Enterprise</h3>
                <p className="text-sm text-gray-400">Para Dominar</p>
                <p className="text-xs text-gray-500 mt-2">Dedicado + SLA</p>
              </div>
            </div>
            
            {/* Billing toggle */}
            <div className="flex items-center justify-center space-x-4">
              <span className={`text-sm ${!isAnnual ? 'text-white font-semibold' : 'text-gray-400'}`}>
                Mensal
              </span>
              <Switch
                checked={isAnnual}
                onCheckedChange={setIsAnnual}
                className="data-[state=checked]:bg-green-500"
              />
              <span className={`text-sm ${isAnnual ? 'text-white font-semibold' : 'text-gray-400'}`}>
                Anual
                <span className="ml-1 text-green-400 text-xs">(-10%)</span>
              </span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-2xl p-8 ${
                  plan.highlighted
                    ? 'bg-gradient-to-b from-green-500/10 to-gray-900 border-2 border-green-500 shadow-2xl shadow-green-500/20 scale-105'
                    : 'bg-gray-900 border border-gray-700'
                } transition-all duration-300 hover:shadow-xl`}
              >
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-green-500 text-white text-sm font-semibold px-4 py-1 rounded-full">
                    {plan.badge}
                  </div>
                )}

                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    {plan.period && (
                      <span className="text-gray-400 ml-1">{plan.period}</span>
                    )}
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start space-x-3">
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300 text-sm">{feature}</span>
                    </div>
                  ))}
                  {plan.notIncluded.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-start space-x-3 opacity-50">
                      <X className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-500 text-sm line-through">{feature}</span>
                    </div>
                  ))}
                </div>

                <Button
                  onClick={plan.action}
                  className={`w-full font-semibold py-3 ${
                    plan.highlighted
                      ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/20'
                      : 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-700'
                  }`}
                >
                  {plan.cta}
                </Button>
              </div>
            ))}
          </div>

          <div className="mt-16 text-center bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-2xl p-8 max-w-4xl mx-auto">
            <p className="text-2xl font-bold text-white mb-4">
              Garantia de 30 dias ou seu dinheiro de volta
            </p>
            <p className="text-gray-400">
              Se em 30 dias sua taxa de rejeição não cair pra menos de 5%, 
              devolvemos 100% do valor. <span className="text-white font-semibold">Sem perguntas.</span>
            </p>
          </div>
        </div>
      </section>

      {/* AuthModal temporarily disabled
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      /> */}
    </>
  )
}