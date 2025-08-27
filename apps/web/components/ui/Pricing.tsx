'use client'

import { useState, useEffect } from 'react'
import { navigateToSection } from '@/lib/navigation'
import { Button } from './button'
import { Switch } from './switch'
import { Badge } from './badge'
import { Check, X, Zap, Rocket, Crown, ShieldCheck } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
// AuthModal is temporarily commented out
// import { AuthModal } from '@/components/blocks/AuthModal'

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const [isPricingVisible, setIsPricingVisible] = useState(false)
  const [calculatedLoss, setCalculatedLoss] = useState<number | null>(null)
  const [hasROIAccess, setHasROIAccess] = useState(false)
  const router = useRouter()
  const { data: session } = useSession()

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsPricingVisible(entry.isIntersecting)
        })
      },
      { threshold: 0.1 }
    )

    const pricingSection = document.getElementById('pricing')
    if (pricingSection) {
      observer.observe(pricingSection)
    }

    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    // Check if user has already provided email/whatsapp
    const stored = localStorage.getItem("vh_roi_access")
    if (stored) {
      try {
        const { ok, exp } = JSON.parse(stored)
        if (ok && exp > Date.now()) {
          setHasROIAccess(true)
        }
      } catch (e) {
        // Invalid data, ignore
      }
    }
    
    // Clear the stored calculation on page load to force recalculation
    // This ensures users always interact with the calculator
    sessionStorage.removeItem('roiCalculation')
    setCalculatedLoss(null)
    
    // Listen for updates from ROI calculator
    const handleROIUpdate = (event: any) => {
      if (event.detail) {
        if (event.detail.monthlyLoss) {
          setCalculatedLoss(event.detail.monthlyLoss)
        }
        if (event.detail.hasAccess) {
          setHasROIAccess(true)
        }
      }
    }
    
    window.addEventListener('roiCalculationUpdated', handleROIUpdate)
    
    return () => {
      window.removeEventListener('roiCalculationUpdated', handleROIUpdate)
    }
  }, [])

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
        'Taxa de rejeição menor que 3% garantida',
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
      price: 'Consulte-nos',
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
      cta: 'Falar no WhatsApp',
      highlighted: false,
      action: () => {
        window.open('https://wa.me/5511999999999?text=Olá! Gostaria de saber mais sobre o plano Enterprise do ValidaHub', '_blank')
      }
    }
  ]

  return (
    <>
      <section id="pricing" className="py-20 relative scroll-mt-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Custa menos que <span className="text-red-400">1 produto rejeitado</span>
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
              R$ 97/mês vs{' '}
              {calculatedLoss && hasROIAccess ? (
                <>
                  <span className="text-red-400 font-semibold">
                    R$ {calculatedLoss.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}/mês
                  </span>{' '}
                  em vendas perdidas.
                  <span className="text-white font-semibold"> Seu cálculo real.</span>
                </>
              ) : calculatedLoss && !hasROIAccess ? (
                <>
                  <span className="inline-flex items-center gap-2">
                    <span className="text-red-400 font-semibold blur-sm select-none">
                      R$ {calculatedLoss.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}/mês
                    </span>
                    <button
                      onClick={() => navigateToSection('calculator')}
                      className="text-red-400 hover:text-red-300 underline underline-offset-2 text-sm font-medium transition-colors duration-200"
                    >
                      Veja o valor real →
                    </button>
                  </span>{' '}
                  em vendas perdidas.
                </>
              ) : (
                <>
                  <span className="inline-flex items-center gap-2">
                    <span className="text-red-400 font-semibold blur-sm select-none">
                      R$ ???/mês
                    </span>
                    <button
                      onClick={() => navigateToSection('calculator')}
                      className="text-red-400 hover:text-red-300 underline underline-offset-2 text-sm font-medium transition-colors duration-200"
                    >
                      Descubra sua perda →
                    </button>
                  </span>{' '}
                  em vendas perdidas.
                </>
              )}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto justify-items-center">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`relative w-full max-w-sm rounded-2xl p-8 transition-all duration-300 group ${
                  plan.highlighted
                    ? 'bg-gradient-to-b from-green-500/10 to-gray-900 border-2 border-green-500 shadow-2xl shadow-green-500/20 md:hover:scale-[1.02] md:hover:-translate-y-1 md:hover:shadow-[0_10px_30px_rgba(38,217,157,0.3)] md:hover:border-green-400'
                    : 'bg-gray-900 border border-gray-700 md:hover:-translate-y-0.5 md:hover:shadow-[0_5px_15px_rgba(255,255,255,0.1)]'
                }`}
              >
                {/* Glow effect for Pro plan */}
                {plan.highlighted && (
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-green-500/20 via-emerald-500/20 to-green-500/20 blur-xl animate-pulse opacity-50 -z-10" />
                )}
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10 transition-transform duration-300 group-hover:scale-110">
                    <span className="bg-green-500 text-white text-xs font-semibold px-3 py-1 rounded-full shadow-lg animate-pulse">
                      {plan.badge}
                    </span>
                  </div>
                )}

                <div className="mb-8">
                  {/* Icon and Purpose */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 group-hover:scale-110 ${
                        plan.name === 'Free' ? 'bg-blue-500/20 group-hover:bg-blue-500/30' :
                        plan.name === 'Pro' ? 'bg-green-500/20 group-hover:bg-green-500/30' :
                        'bg-purple-500/20 group-hover:bg-purple-500/30'
                      }`}>
                        {plan.name === 'Free' && <Zap className="w-5 h-5 text-blue-400 transition-transform duration-300 group-hover:rotate-12" />}
                        {plan.name === 'Pro' && <Rocket className="w-5 h-5 text-green-400 transition-transform duration-300 group-hover:rotate-12" />}
                        {plan.name === 'Enterprise' && <Crown className="w-5 h-5 text-purple-400 transition-transform duration-300 group-hover:rotate-12" />}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white">{plan.name}</h3>
                        <p className="text-xs font-semibold ${
                          plan.name === 'Free' ? 'text-blue-400' :
                          plan.name === 'Pro' ? 'text-green-400' :
                          'text-purple-400'
                        }">
                          {plan.name === 'Free' && 'Para Testar'}
                          {plan.name === 'Pro' && 'Para Escalar'}
                          {plan.name === 'Enterprise' && 'Para Dominar'}
                        </p>
                      </div>
                    </div>
                    {plan.name === 'Free' && (
                      <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">1.000 validações</Badge>
                    )}
                    {plan.name === 'Pro' && (
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Ilimitado + API</Badge>
                    )}
                    {plan.name === 'Enterprise' && (
                      <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">Dedicado + SLA</Badge>
                    )}
                  </div>
                  
                  {/* Billing toggle for Pro plan */}
                  {plan.name === 'Pro' && (
                    <div className="flex items-center justify-center space-x-3 mb-4 p-3 bg-gray-800/50 rounded-lg">
                      <span className={`text-xs ${!isAnnual ? 'text-white font-semibold' : 'text-gray-500'}`}>
                        Mensal
                      </span>
                      <Switch
                        checked={isAnnual}
                        onCheckedChange={setIsAnnual}
                        className="data-[state=checked]:bg-green-500 scale-75"
                      />
                      <span className={`text-xs ${isAnnual ? 'text-white font-semibold' : 'text-gray-500'}`}>
                        Anual
                        <span className="ml-1 text-green-400 text-xs">(economize R$120)</span>
                      </span>
                    </div>
                  )}
                  
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
                    <div key={featureIndex} className="flex items-start space-x-3 transition-all duration-200 md:hover:translate-x-1">
                      <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 transition-colors duration-200 ${
                        plan.highlighted ? 'text-green-400' : 'text-gray-400'
                      }`} />
                      <span className={`text-sm ${
                        plan.highlighted ? 'text-gray-300' : 'text-gray-400'
                      }`}>{feature}</span>
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
                  className={`w-full font-semibold py-3 transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500 md:hover:from-green-400 md:hover:to-emerald-400 text-white shadow-lg shadow-green-500/20 md:hover:scale-[1.05] md:hover:shadow-[0_5px_20px_rgba(38,217,157,0.4)]'
                      : 'bg-gray-800 md:hover:bg-gray-700 text-white border border-gray-700 md:hover:border-gray-600'
                  }`}
                >
                  {plan.cta}
                </Button>
              </div>
            ))}
          </div>

          {/* Trust section above cards */}
          <div className="mt-16 text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-3 px-6 py-3 bg-gray-800/50 border border-gray-700 rounded-full">
              <ShieldCheck className="w-5 h-5 text-green-400" />
              <p className="text-sm text-gray-300">
                <span className="font-semibold text-white">Sem risco por 30 dias.</span> Cancele quando quiser.
                <button className="ml-2 text-green-400 hover:text-green-300 underline underline-offset-2 text-xs">
                  Teste agora →
                </button>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mobile sticky mini-bar */}
      {isPricingVisible && (
        <div className="fixed bottom-0 left-0 right-0 z-40 md:hidden bg-gray-900 border-t border-gray-800 p-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs">
              <ShieldCheck className="w-4 h-4 text-green-400 flex-shrink-0" />
              <span className="text-gray-300">
                <span className="text-white font-semibold">Garantia 30 dias</span> • Cancele quando quiser
              </span>
            </div>
            <Button
              onClick={() => {
                if (session) {
                  router.push('/settings/billing?plan=pro')
                } else {
                  setAuthMode('signup')
                  setAuthModalOpen(true)
                }
              }}
              className="px-4 py-2 text-xs bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold"
            >
              Começar Pro
            </Button>
          </div>
        </div>
      )}

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