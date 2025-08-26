'use client'

import { useState } from 'react'
import { Button } from './button'
import { Switch } from './switch'
import { Check, X } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import AuthModal from './AuthModal'

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const router = useRouter()
  const { data: session } = useSession()

  const plans = [
    {
      name: 'Starter',
      price: isAnnual ? 'Grátis' : 'Grátis',
      description: 'Perfeito para começar e testar a plataforma',
      features: [
        '100 validações/mês',
        'Upload até 1k linhas',
        'Regras básicas MELI',
        'Exportação CSV',
        'Suporte por email',
      ],
      notIncluded: [
        'Jobs assíncronos',
        'Webhooks',
        'API access',
        'Regras customizadas',
      ],
      cta: 'Criar conta grátis',
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
      price: isAnnual ? 'R$ 179' : 'R$ 199',
      period: '/mês',
      description: 'Para empresas que precisam escalar',
      features: [
        'Validações ilimitadas',
        'Upload até 100MB',
        'Todas as regras de marketplace',
        'Jobs assíncronos',
        'Webhooks & API',
        'Correções automáticas',
        'Histórico 90 dias',
        'Suporte prioritário',
      ],
      notIncluded: [
        'SSO/SAML',
        'Ambientes dedicados',
      ],
      cta: 'Assinar Pro',
      highlighted: true,
      badge: 'Mais popular',
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
      price: 'Personalizado',
      description: 'Soluções customizadas para grandes volumes',
      features: [
        'Tudo do Pro',
        'SSO/SAML',
        'Ambientes dedicados',
        'SLA garantido',
        'Regras customizadas',
        'Treinamento incluído',
        'Account manager dedicado',
        'Histórico ilimitado',
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
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Planos simples e transparentes
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
              Escolha o plano ideal para o seu negócio. Sem taxas escondidas.
            </p>
            
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

          <div className="mt-16 text-center">
            <p className="text-gray-400 text-sm">
              Precisa de mais informações?{' '}
              <a href="/faq" className="text-green-400 hover:underline">
                Veja nossas FAQs
              </a>{' '}
              ou{' '}
              <a href="mailto:contato@validahub.com" className="text-green-400 hover:underline">
                entre em contato
              </a>
            </p>
          </div>
        </div>
      </section>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </>
  )
}