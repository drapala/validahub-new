'use client'

import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

export default function HeroSplit() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden">
      {/* Background gradient subtle */}
      <div className="absolute inset-0 dark:bg-zinc-950 bg-white">
        <div className="absolute inset-0 bg-gradient-to-br dark:from-emerald-500/5 dark:via-transparent dark:to-teal-500/5 from-violet-500/5 via-transparent to-purple-500/5" />
      </div>

      <div className="container mx-auto px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Text content - Left side */}
          <div className="max-w-xl">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-3 py-1 
                dark:bg-emerald-500/10 dark:border-emerald-500/20
                bg-violet-500/10 border-violet-500/20
                border rounded-full mb-6"
            >
              <CheckCircle className="w-3.5 h-3.5 dark:text-emerald-400 text-violet-600" />
              <span className="text-xs font-medium dark:text-emerald-400 text-violet-600">
                Redução de 92% em rejeições
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.05, ease: "easeOut" }}
              className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight leading-[0.95] dark:text-zinc-50 text-gray-900"
            >
              Publique produtos
              <span className="block dark:text-emerald-400 text-violet-600">
                sem rejeições.
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
              className="mt-6 text-lg dark:text-zinc-400 text-gray-600"
            >
              ValidaHub detecta e corrige automaticamente os 47 erros mais comuns 
              antes do marketplace rejeitar. Economize 16h/mês e aumente suas vendas.
            </motion.p>

            {/* Feature list */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
              className="mt-8 space-y-3"
            >
              {[
                'Validação em tempo real com regras do MELI',
                'Correção automática de títulos e preços',
                'API pronta para seu ERP em 15 minutos'
              ].map((feature, i) => (
                <div key={i} className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 dark:text-emerald-500 text-violet-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm dark:text-zinc-300 text-gray-700">{feature}</span>
                </div>
              ))}
            </motion.div>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
              className="mt-10 flex flex-col sm:flex-row gap-4"
            >
              {/* Primary CTA */}
              <button className="group inline-flex items-center justify-center gap-2 px-6 py-3.5 
                dark:bg-gradient-to-r dark:from-emerald-500 dark:to-teal-500
                bg-gradient-to-r from-violet-500 to-purple-500
                text-white font-semibold rounded-full
                shadow-lg dark:shadow-emerald-500/25 shadow-violet-500/25
                hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5"
              >
                Testar grátis agora
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </button>

              {/* Secondary CTA */}
              <Link
                href="#pricing"
                className="inline-flex items-center gap-2 px-6 py-3.5 
                  dark:text-zinc-400 dark:hover:text-zinc-200
                  text-gray-600 hover:text-gray-900
                  font-medium transition-colors group"
              >
                Ver planos
                <span className="text-sm group-hover:translate-x-0.5 transition-transform">→</span>
              </Link>
            </motion.div>
          </div>

          {/* Image/Screenshot - Right side */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
            className="relative lg:ml-auto"
          >
            <div className="relative rounded-2xl overflow-hidden 
              dark:border-white/10 border-gray-200/60 border
              dark:bg-zinc-900/50 bg-white/50
              backdrop-blur-xl shadow-2xl"
            >
              {/* Glass effect overlay */}
              <div className="absolute inset-0 dark:bg-gradient-to-tr dark:from-emerald-500/5 dark:to-transparent 
                bg-gradient-to-tr from-violet-500/5 to-transparent pointer-events-none" />
              
              {/* Placeholder for actual screenshot */}
              <div className="aspect-[4/3] bg-gradient-to-br dark:from-zinc-800 dark:to-zinc-900 from-gray-50 to-gray-100 p-8">
                <div className="h-full w-full rounded-lg dark:bg-zinc-950/50 bg-white/80 backdrop-blur 
                  flex items-center justify-center dark:border-zinc-800 border-gray-200 border">
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-xl 
                      dark:bg-emerald-500/10 bg-violet-500/10 
                      flex items-center justify-center">
                      <CheckCircle className="w-8 h-8 dark:text-emerald-500 text-violet-500" />
                    </div>
                    <p className="text-sm dark:text-zinc-500 text-gray-500">Dashboard Preview</p>
                  </div>
                </div>
              </div>

              {/* Floating stats badges */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5, ease: "easeOut" }}
                className="absolute top-4 left-4 px-3 py-1.5 rounded-full 
                  dark:bg-zinc-900/90 bg-white/90 backdrop-blur-xl 
                  dark:border-zinc-800 border-gray-200 border
                  flex items-center gap-2"
              >
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs font-medium dark:text-zinc-300 text-gray-700">
                  2.8% taxa de rejeição
                </span>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6, ease: "easeOut" }}
                className="absolute bottom-4 right-4 px-3 py-1.5 rounded-full 
                  dark:bg-zinc-900/90 bg-white/90 backdrop-blur-xl 
                  dark:border-zinc-800 border-gray-200 border
                  flex items-center gap-2"
              >
                <span className="text-xs font-medium dark:text-zinc-300 text-gray-700">
                  +18% vendas em 2 meses
                </span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}