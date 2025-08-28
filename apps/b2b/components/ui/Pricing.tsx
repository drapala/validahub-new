'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { navigateToSection } from '@/lib/navigation'
import { Check, X, Zap, Rocket, Crown, ShieldCheck, Calendar, MessageCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'

export default function Pricing() {
  const [cycle, setCycle] = useState<'monthly' | 'yearly'>('monthly')
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
      monthlyPrice: 0,
      yearlyPrice: 0,
      description: '1.000 validações grátis • sem cartão • baixe o CSV corrigido',
      features: [
        'Detecta os 47 erros fatais',
        'Corrige títulos e preços básicos',
        'Valida EAN/GTIN',
        'Regras MELI + Amazon principais',
        'Download do CSV corrigido',
      ],
      notIncluded: [
        'API & Webhooks',
        'Histórico de validações',
        'Suporte prioritário',
        'Todos os marketplaces',
      ],
      cta: 'Testar grátis agora',
      highlighted: false,
      action: () => router.push('/upload')
    },
    {
      name: 'Pro',
      monthlyPrice: 97,
      yearlyPrice: 87,
      badge: 'Mais popular',
      description: 'Cancelamento a qualquer momento • nota fiscal • suporte em até 2h',
      features: [
        'Validações ilimitadas',
        'Detecta e corrige 47+ tipos de erro',
        'Corrige automaticamente títulos, preços, atributos',
        'API & Webhooks enterprise',
        'Histórico completo de 90 dias',
        'Todos os marketplaces (MELI, Amazon, Magalu, etc)',
        'Suporte prioritário em até 2h',
        'Taxa de rejeição < 3% garantida*',
      ],
      notIncluded: [
        'Ambiente dedicado',
        'SLA personalizado',
      ],
      cta: 'Começar Pro agora',
      highlighted: true,
      action: () => {
        if (session) {
          router.push('/settings/billing?plan=pro')
        } else {
          router.push('/auth/signup?plan=pro')
        }
      }
    },
    {
      name: 'Enterprise',
      monthlyPrice: null,
      yearlyPrice: null,
      customPrice: 'Consulte-nos',
      description: 'SLA 99,9% • regras custom • WhatsApp direto • SSO (Google/SAML)',
      features: [
        'Tudo do Pro, mais:',
        'Ambiente dedicado isolado',
        'SLA 99.9% monitorado 24/7',
        'Regras de validação 100% customizadas',
        'API sem limite de requests/min',
        'Treinamento completo da equipe',
        'Suporte via WhatsApp direto',
        'Compliance LGPD certificado',
      ],
      notIncluded: [],
      primaryCta: 'Agendar conversa',
      secondaryCta: 'Falar no WhatsApp',
      highlighted: false,
      primaryAction: () => window.open('https://calendly.com/validahub/enterprise', '_blank'),
      secondaryAction: () => window.open('https://wa.me/5511999999999?text=Olá! Gostaria de saber mais sobre o plano Enterprise do ValidaHub', '_blank')
    }
  ]

  return (
    <>
      <section 
        className="py-20 relative overflow-hidden bg-white dark:bg-zinc-950"
        id="pricing"
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-7xl mx-auto">
            
            {/* Header */}
            <div className="text-center mb-12">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
              >
                <p className="text-sm font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-4">
                  Preços transparentes
                </p>
              </motion.div>
              
              <motion.h2 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-4xl sm:text-5xl lg:text-6xl font-bold text-zinc-900 dark:text-white"
              >
                Custa menos que <span className="text-violet-600 dark:text-emerald-400">1 produto rejeitado</span>
              </motion.h2>
              
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="mt-4 text-lg text-zinc-600 dark:text-zinc-300 max-w-2xl mx-auto mb-8"
              >
                R$ 97/mês vs{' '}
                {calculatedLoss && hasROIAccess ? (
                  <>
                    <span className="text-red-600 dark:text-red-400 font-semibold">
                      R$ {calculatedLoss.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}/mês
                    </span>{' '}
                    em vendas perdidas.
                    <span className="text-zinc-900 dark:text-white font-semibold"> Seu cálculo real.</span>
                  </>
                ) : (
                  <>
                    <span className="inline-flex items-center gap-2">
                      <span className="text-red-600 dark:text-red-400 font-semibold blur-sm select-none">
                        R$ ???/mês
                      </span>
                      <button
                        onClick={() => navigateToSection('calculator')}
                        className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 underline underline-offset-2 text-sm font-medium transition-colors duration-200"
                      >
                        Descubra sua perda →
                      </button>
                    </span>{' '}
                    em vendas perdidas.
                  </>
                )}
              </motion.p>
            </div>
            
            {/* Toggle mensal/anual */}
            <div className="flex flex-col items-center mb-12">
              <div className="flex items-center gap-4 p-1 bg-zinc-100 dark:bg-zinc-800 rounded-2xl">
                <button
                  className={`px-6 py-2 rounded-xl font-medium text-sm transition-all duration-200 ${
                    cycle === 'monthly'
                      ? 'bg-purple-600 dark:bg-emerald-600 text-white shadow-sm'
                      : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
                  }`}
                  onClick={() => setCycle('monthly')}
                >
                  Mensal
                </button>
                <button
                  className={`px-6 py-2 rounded-xl font-medium text-sm transition-all duration-200 ${
                    cycle === 'yearly'
                      ? 'bg-purple-600 dark:bg-emerald-600 text-white shadow-sm'
                      : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
                  }`}
                  onClick={() => setCycle('yearly')}
                >
                  Anual
                </button>
              </div>
              {cycle === 'yearly' && (
                <div className="mt-3 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                  2 meses grátis no anual
                </div>
              )}
            </div>

            {/* Plans Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
              {plans.map((plan, index) => {
                const price = plan.customPrice || (cycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice)
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className={`relative rounded-3xl p-6 transition-all duration-200 ${
                      plan.highlighted
                        ? 'border border-violet-300/40 dark:border-emerald-300/40 bg-white/90 dark:bg-white/[0.06] backdrop-blur-md shadow-lg ring-2 ring-violet-400/30 dark:ring-emerald-400/30 before:absolute before:-inset-2 before:-z-10 before:rounded-[28px] before:bg-violet-500/15 dark:before:bg-emerald-500/15 before:blur-xl'
                        : 'border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 backdrop-blur-md hover:shadow-lg dark:hover:shadow-zinc-950/50'
                    }`}
                  >
                    {/* Badge */}
                    {plan.badge && (
                      <div className="flex items-center justify-between mb-6">
                        <span className="text-lg font-semibold text-zinc-900 dark:text-white">{plan.name}</span>
                        <span className="rounded-xl bg-violet-500/10 dark:bg-emerald-500/10 text-violet-700 dark:text-emerald-300 ring-1 ring-violet-400/30 dark:ring-emerald-400/30 px-3 py-1 text-xs font-semibold">
                          {plan.badge}
                        </span>
                      </div>
                    )}
                    
                    {!plan.badge && (
                      <div className="mb-6">
                        <span className="text-lg font-semibold text-zinc-900 dark:text-white">{plan.name}</span>
                      </div>
                    )}

                    {/* Price */}
                    <div className="mb-6">
                      <div className="flex items-baseline gap-2">
                        <div className="text-5xl font-extrabold tabular-nums text-zinc-900 dark:text-zinc-50">
                          {typeof price === 'number' ? `R$ ${price}` : price}
                        </div>
                        {typeof price === 'number' && (
                          <span className="text-zinc-500 dark:text-zinc-400">/mês</span>
                        )}
                      </div>
                      <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">{plan.description}</p>
                    </div>

                    {/* Features */}
                    <ul className="space-y-3 mb-8">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-start gap-3">
                          <Check className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-zinc-700 dark:text-zinc-200">{feature}</span>
                        </li>
                      ))}
                      
                      {plan.notIncluded.length > 0 && (
                        <>
                          <li className="border-t border-zinc-200/70 dark:border-zinc-700 mt-3 pt-3"></li>
                          {plan.notIncluded.map((feature, featureIndex) => (
                            <li key={featureIndex} className="flex items-start gap-3 opacity-60">
                              <X className="w-4 h-4 text-zinc-400 flex-shrink-0 mt-0.5" />
                              <span className="text-sm text-zinc-500 dark:text-zinc-400 line-through">{feature}</span>
                            </li>
                          ))}
                        </>
                      )}
                    </ul>

                    {/* CTA(s) */}
                    {plan.name === 'Enterprise' ? (
                      <div className="flex flex-col gap-2">
                        <button
                          onClick={plan.primaryAction}
                          className="w-full rounded-2xl bg-violet-600 dark:bg-emerald-600 text-white px-6 py-3 font-semibold shadow-lg ring-2 ring-violet-400/30 dark:ring-emerald-400/30 hover:ring-violet-400/50 dark:hover:ring-emerald-400/50 focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70 hover:shadow-xl hover:scale-[1.02] transition-all duration-200"
                        >
                          <Calendar className="inline-block mr-2 w-4 h-4" />
                          {plan.primaryCta}
                        </button>
                        <button
                          onClick={plan.secondaryAction}
                          className="w-full rounded-2xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-transparent px-6 py-3 text-zinc-800 dark:text-white font-medium hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-all duration-200"
                        >
                          <MessageCircle className="inline-block mr-2 w-4 h-4" />
                          {plan.secondaryCta}
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={plan.action}
                        className="w-full rounded-2xl bg-violet-600 dark:bg-emerald-600 text-white px-6 py-3 font-semibold shadow-lg ring-2 ring-violet-400/30 dark:ring-emerald-400/30 hover:ring-violet-400/50 dark:hover:ring-emerald-400/50 focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70 hover:shadow-xl hover:scale-[1.02] transition-all duration-200"
                      >
                        {plan.cta}
                      </button>
                    )}
                    
                    {/* Pill abaixo do preço para Pro */}
                    {plan.highlighted && (
                      <div className="mt-3 flex justify-center">
                        <span className="inline-flex items-center gap-2 px-3 py-1 bg-violet-50 dark:bg-emerald-950/30 border border-violet-200/50 dark:border-emerald-800/50 rounded-full text-xs font-medium text-violet-600 dark:text-emerald-400">
                          <div className="w-2 h-2 bg-violet-500 dark:bg-emerald-500 rounded-full" />
                          Lucro garantido*
                        </span>
                      </div>
                    )}
                    
                    {plan.highlighted && (
                      <p className="mt-2 text-[11px] text-zinc-500 dark:text-zinc-400 text-center">*Garantia sujeita a termos de uso.</p>
                    )}
                  </motion.div>
                )
              })}
            </div>

            {/* Trust section */}
            <div className="mt-16 text-center max-w-2xl mx-auto">
              <div className="inline-flex items-center gap-3 px-6 py-3 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-full">
                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                <p className="text-sm text-zinc-700 dark:text-zinc-300">
                  <span className="font-semibold text-zinc-900 dark:text-white">Sem risco por 30 dias.</span> Cancele quando quiser.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}