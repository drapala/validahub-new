'use client'

import { motion } from 'framer-motion'
import { 
  Shield, 
  Zap, 
  AlertTriangle, 
  Link, 
  History,
  DollarSign,
  ArrowRight,
  Activity,
  Lock,
  Database,
  PlayCircle
} from 'lucide-react'

// BenefitCard component with proper hierarchy
function BenefitCard({ 
  icon: Icon, 
  title, 
  value, 
  pill, 
  delay = 0 
}: {
  icon: any
  title: string
  value: string
  pill: string
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="group rounded-2xl border border-zinc-200/80 dark:border-zinc-800 
        bg-white dark:bg-zinc-900/50 backdrop-blur-md p-6
        hover:shadow-lg dark:hover:shadow-zinc-950/50 
        hover:border-zinc-300 dark:hover:border-zinc-700
        transition-all duration-200"
    >
      <div className="flex flex-col h-full">
        {/* Icon */}
        <div className="w-12 h-12 rounded-xl bg-zinc-100 dark:bg-zinc-800 
          text-zinc-600 dark:text-zinc-400 flex items-center justify-center mb-4">
          <Icon className="w-6 h-6" />
        </div>
        
        {/* Title */}
        <h3 className="font-semibold text-lg text-zinc-900 dark:text-white mb-2">
          {title}
        </h3>
        
        {/* Value */}
        <div className="text-2xl font-bold text-zinc-900 dark:text-white mb-4 flex-1">
          {value}
        </div>
        
        {/* Pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1 
          bg-emerald-50 dark:bg-emerald-950/30 
          border border-emerald-200/50 dark:border-emerald-800/50 
          rounded-full text-sm font-medium text-emerald-600 dark:text-emerald-400 w-fit">
          <div className="w-2 h-2 bg-emerald-500 rounded-full" />
          {pill}
        </div>
      </div>
    </motion.div>
  )
}

export default function Features() {
  const benefits = [
    {
      icon: AlertTriangle,
      title: "Diagnóstico (o que está matando)",
      value: "47 tipos de erro fatal detectados",
      pill: "Zero perda por erro bobo"
    },
    {
      icon: Zap,
      title: "Correção (arrumamos pra você)",
      value: "Corrige automaticamente",
      pill: "90% dos erros auto-fix"
    },
    {
      icon: Shield,
      title: "Publicação (confiança 100%)",
      value: "Taxa de rejeição ≤ 3%",
      pill: "vs 28% sem ValidaHub"
    },
    {
      icon: Link,
      title: "Integração (plug & play)",
      value: "APIs enterprise-ready",
      pill: "Setup em 15 minutos"
    },
    {
      icon: History,
      title: "Auditoria (compliance LGPD)",
      value: "Histórico completo gravado",
      pill: "Jurídico aprovado"
    },
    {
      icon: DollarSign,
      title: "ROI (resultado comprovado)",
      value: "R$ 2.034+ economia/mês",
      pill: "Paga sozinho"
    }
  ]

  return (
    <section 
      className="py-20 relative overflow-hidden bg-white dark:bg-zinc-950"
      id="features"
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
                O que o ValidaHub resolve
              </p>
            </motion.div>
            
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-zinc-900 dark:text-white"
            >
              Diagnóstico → Correção → Publicação
            </motion.h2>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mt-4 text-lg text-zinc-600 dark:text-zinc-300 max-w-2xl mx-auto"
            >
              Enquanto outros mostram dashboards bonitos, nós eliminamos erros e rejeições
            </motion.p>
          </div>

          {/* Benefits Grid - 3x2 equal height */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16 max-w-6xl mx-auto">
            {benefits.map((benefit, i) => (
              <BenefitCard
                key={i}
                icon={benefit.icon}
                title={benefit.title}
                value={benefit.value}
                pill={benefit.pill}
                delay={i * 0.1}
              />
            ))}
          </div>

          {/* Enterprise Guarantees */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mb-16"
          >
            <h3 className="text-center text-sm font-medium uppercase tracking-wider 
              text-zinc-500 dark:text-zinc-400 mb-8">
              Garantias enterprise
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl mx-auto">
              {[
                { icon: Activity, title: 'SLA 99.9%', desc: 'monitorado 24/7' },
                { icon: Lock, title: 'LGPD/SOC2', desc: 'compliance total' },
                { icon: Database, title: 'API REST', desc: '100k req/min' },
              ].map(({ icon: Icon, title, desc }, i) => (
                <motion.div
                  key={i}
                  whileHover={{ y: -2 }}
                  className="flex items-center gap-3 p-4 rounded-xl 
                    border border-zinc-200/80 dark:border-zinc-800
                    bg-white dark:bg-zinc-900/50 backdrop-blur-sm
                    hover:shadow-md transition-all duration-200"
                  aria-label={`${title}: ${desc}`}
                >
                  <Icon className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-sm text-zinc-900 dark:text-white">
                      {title}
                    </div>
                    <div className="text-xs text-zinc-500 dark:text-zinc-400">{desc}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Dual CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="flex flex-col sm:flex-row gap-3 justify-center"
          >
            <button
              className="rounded-2xl bg-violet-600 dark:bg-emerald-600 text-white px-8 py-4 font-semibold 
                shadow-lg ring-2 ring-violet-400/30 dark:ring-emerald-400/30 hover:ring-violet-400/50 dark:hover:ring-emerald-400/50 
                focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70
                hover:shadow-xl hover:scale-[1.02] 
                transition-all duration-200"
              data-analytics-id="features-trial-click"
              onClick={() => window.dispatchEvent(new CustomEvent('features_trial_click'))}
              aria-label="Começar validação gratuita"
            >
              Validar grátis agora
              <ArrowRight className="inline-block ml-2 w-4 h-4" />
            </button>
            
            <button
              className="rounded-2xl border border-zinc-300 dark:border-zinc-700
                bg-white dark:bg-transparent px-8 py-4 
                text-zinc-800 dark:text-white font-medium
                hover:bg-zinc-50 dark:hover:bg-zinc-900
                transition-all duration-200"
              data-analytics-id="features-demo-click"
              onClick={() => window.dispatchEvent(new CustomEvent('features_demo_open'))}
              aria-label="Assistir demonstração de 90 segundos"
            >
              <PlayCircle className="inline-block mr-2 w-4 h-4" />
              Ver demo de 90s
            </button>
          </motion.div>
        </div>
      </div>
    </section>
  )
}