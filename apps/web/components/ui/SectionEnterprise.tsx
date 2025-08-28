'use client'

import { useState, useEffect } from 'react'
import { motion, useAnimation, useInView } from 'framer-motion'
import { useRef } from 'react'
import { 
  Shield,
  Lock,
  Database,
  Users,
  Activity,
  ArrowRight,
  Building2,
  ChevronRight
} from 'lucide-react'

// Counter animation hook
function useCounter(end: number, duration: number = 1000, start: boolean = false, decimals: number = 0) {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    if (!start) return
    let startTime: number | null = null
    let animationFrame: number
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      
      if (decimals > 0) {
        setCount(Number((progress * end).toFixed(decimals)))
      } else {
        setCount(Math.floor(progress * end))
      }
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }
    
    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [end, duration, start, decimals])
  
  return count
}

// Result Row Component
function ResultRow({
  logo, 
  name, 
  quote, 
  stat, 
  unit, 
  href = "#",
  delay = 0
}: {
  logo: string
  name: string
  quote: string
  stat: string
  unit: string
  href?: string
  delay?: number
}) {
  return (
    <motion.a 
      href={href} 
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="group flex items-center gap-4 rounded-2xl border
        border-zinc-200/80 dark:border-zinc-800 bg-white/80 dark:bg-zinc-900/50 
        backdrop-blur-md p-4 hover:bg-white dark:hover:bg-zinc-900
        transition-all duration-200 shadow-sm hover:shadow-md"
      data-analytics-id={`result-row-${name.toLowerCase().replace(/\s+/g, '-')}`}
      aria-label={`Ver caso de sucesso de ${name}`}
    >
      <div className="grid place-items-center size-12 rounded-lg bg-zinc-100 dark:bg-zinc-800 
        text-zinc-600 dark:text-zinc-400 font-bold text-sm">
        {logo}
      </div>
      <div className="min-w-0 flex-1">
        <div className="font-semibold text-zinc-900 dark:text-white">{name}</div>
        <div className="text-zinc-500 dark:text-zinc-400 text-sm truncate">"{quote}"</div>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <span className="block text-2xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
            {stat}
          </span>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">{unit}</span>
        </div>
        <ChevronRight className="w-5 h-5 text-zinc-400 group-hover:text-violet-600 
          dark:group-hover:text-emerald-400 transition-all duration-200 
          group-hover:translate-x-1" />
      </div>
    </motion.a>
  )
}

export default function SectionEnterprise() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })
  
  // Animated counters
  const rejectionRate = useCounter(2, 1000, isInView)
  const timeSaved = useCounter(16, 1000, isInView)
  const roiValue = useCounter(8.5, 1200, isInView, 1)
  const activeUsers = useCounter(1247, 1500, isInView)

  // Logos reais de marketplaces
  const logos = [
    { name: 'MercadoLivre', mono: 'ML' },
    { name: 'Magazine Luiza', mono: 'MGLU' },
    { name: 'B2W', mono: 'B2W' },
    { name: 'Via', mono: 'VIA' },
    { name: 'Netshoes', mono: 'NS' },
    { name: 'Carrefour', mono: 'CF' },
  ]

  const caseStudies = [
    {
      name: "Magazine Luiza",
      logo: "MGLU",
      quote: "Reduzimos rejeições de 28% para 2% em 30 dias",
      stat: "+R$127k",
      unit: "economia/mês",
      href: "#case-magalu"
    },
    {
      name: "MercadoLivre Premium",
      logo: "MLP",
      quote: "16 horas de retrabalho virou 30 segundos de API",
      stat: "8,5×",
      unit: "ROI",
      href: "#case-meli"
    },
    {
      name: "Via Varejo",
      logo: "VIA",
      quote: "Publicamos 10x mais produtos com a mesma equipe",
      stat: "-92%",
      unit: "tempo",
      href: "#case-via"
    }
  ]

  const kpis = [
    { value: `${rejectionRate}%`, label: "taxa de rejeição", footnote: "vs 28% sem ValidaHub" },
    { value: `${timeSaved}h`, label: "horas economizadas/mês", footnote: "por loja (média)" },
    { value: `${roiValue}×`, label: "ROI médio", footnote: "em 30 dias" },
    { value: activeUsers.toLocaleString('pt-BR'), label: "vendedores ativos", footnote: "+23% no mês" },
  ]

  return (
    <section 
      ref={ref}
      className="py-20 relative overflow-hidden bg-white dark:bg-zinc-950"
      id="enterprise"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          
          {/* Header com eyebrow */}
          <div className="text-center mb-12">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              <p className="text-sm font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-400 mb-4">
                Enterprise-ready
              </p>
            </motion.div>
            
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-zinc-900 dark:text-white"
            >
              As principais agências já migraram
            </motion.h2>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mt-4 text-lg text-zinc-600 dark:text-zinc-300 max-w-2xl mx-auto"
            >
              Profissionais publicam em escala porque eliminam rejeição e retrabalho
            </motion.p>
          </div>

          {/* Logo Cloud - monocromático */}
          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 flex justify-center"
          >
            <div className="flex flex-wrap justify-center items-center gap-8 lg:gap-12">
              {logos.map((logo, i) => (
                <motion.div
                  key={i}
                  className="opacity-40 hover:opacity-100 transition-opacity duration-300"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="h-12 px-4 rounded-lg bg-zinc-100 dark:bg-zinc-900 
                    flex items-center justify-center font-bold text-sm
                    text-zinc-600 dark:text-zinc-400 border border-zinc-200/50 dark:border-zinc-800">
                    {logo.mono}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* KPI Strip - limpo e com divisórias */}
          <motion.ul 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mx-auto mb-20 max-w-6xl grid grid-cols-2 md:grid-cols-4
              rounded-2xl border border-zinc-200/80 dark:border-zinc-800 
              bg-white/80 dark:bg-zinc-900/50 backdrop-blur-md
              divide-y md:divide-y-0 md:divide-x divide-zinc-200/70 dark:divide-zinc-800"
          >
            {kpis.map(({value, label, footnote}, i) => (
              <motion.li 
                key={label} 
                className="p-6 text-center"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                data-analytics-id={`kpi-${label.replace(/\s+/g, '-')}`}
              >
                <div className="text-5xl font-extrabold tabular-nums text-zinc-900 dark:text-white">
                  {value}
                </div>
                <div className="mt-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  {label}
                </div>
                <div className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">
                  {footnote}
                </div>
              </motion.li>
            ))}
          </motion.ul>

          {/* Case Studies - Resultados verificados */}
          <div className="mb-20">
            <h3 className="text-center text-sm font-medium uppercase tracking-wider 
              text-zinc-500 dark:text-zinc-400 mb-8">
              Resultados verificados
            </h3>
            
            <div className="space-y-4 max-w-4xl mx-auto">
              {caseStudies.map((study, i) => (
                <ResultRow
                  key={i}
                  logo={study.logo}
                  name={study.name}
                  quote={study.quote}
                  stat={study.stat}
                  unit={study.unit}
                  href={study.href}
                  delay={i * 0.1}
                />
              ))}
            </div>
          </div>

          {/* Enterprise Guarantees - 5 bullets objetivos */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mb-16"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 max-w-6xl mx-auto">
              {[
                { icon: Activity, title: 'SLA 99.9%', desc: 'monitorado 24/7' },
                { icon: Shield, title: 'LGPD/SOC2', desc: 'compliance total' },
                { icon: Lock, title: 'SSO/SAML', desc: 'Google, Azure' },
                { icon: Users, title: 'RBAC', desc: 'multi-tenant' },
                { icon: Database, title: 'API REST', desc: '100k req/min' },
              ].map(({ icon: Icon, title, desc }, i) => (
                <motion.div
                  key={i}
                  whileHover={{ y: -2 }}
                  className="flex items-center gap-3 p-4 rounded-xl 
                    border border-zinc-200/80 dark:border-zinc-800
                    bg-white/80 dark:bg-zinc-900/50 backdrop-blur-sm
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

          {/* CTA Duplo - violeta primário + ghost secundário */}
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
              data-analytics-id="trial-click"
              onClick={() => window.dispatchEvent(new CustomEvent('enterprise_trial_click'))}
              aria-label="Começar teste gratuito com mil validações"
            >
              Testar grátis com 1.000 validações
              <ArrowRight className="inline-block ml-2 w-4 h-4" />
            </button>
            
            <button
              className="rounded-2xl border border-zinc-300 dark:border-zinc-700
                bg-white dark:bg-transparent px-8 py-4 
                text-zinc-800 dark:text-white font-medium
                hover:bg-zinc-50 dark:hover:bg-zinc-900
                transition-all duration-200"
              data-analytics-id="enterprise-click"
              onClick={() => window.dispatchEvent(new CustomEvent('enterprise_contact_open'))}
              aria-label="Abrir formulário de contato enterprise"
            >
              <Building2 className="inline-block mr-2 w-4 h-4" />
              Falar com Enterprise
            </button>
          </motion.div>
        </div>
      </div>
    </section>
  )
}