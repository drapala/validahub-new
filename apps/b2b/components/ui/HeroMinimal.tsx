'use client'

import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function HeroMinimal() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden">
      {/* Background gradient subtle */}
      <div className="absolute inset-0 dark:bg-zinc-950 bg-white">
        <div className="absolute inset-0 bg-gradient-to-br dark:from-emerald-500/5 dark:via-transparent dark:to-teal-500/5 from-violet-500/5 via-transparent to-purple-500/5" />
      </div>

      <div className="container mx-auto px-6 lg:px-8 relative z-10">
        <div className="max-w-[60%] lg:max-w-[55%]">
          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-bold tracking-tight leading-[0.95] dark:text-zinc-50 text-gray-900"
          >
            Valide catálogos.
            <span className="block dark:text-emerald-400 text-violet-600">
              Venda mais.
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="mt-6 text-lg sm:text-xl dark:text-zinc-400 text-gray-600 max-w-2xl"
          >
            Reduza rejeições de 30% para menos de 3%. 
            Validação automática com regras específicas de cada marketplace.
          </motion.p>

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
              Começar grátis
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </button>

            {/* Secondary CTA */}
            <Link
              href="#demo"
              className="inline-flex items-center gap-2 px-6 py-3.5 
                dark:text-zinc-400 dark:hover:text-zinc-200
                text-gray-600 hover:text-gray-900
                font-medium transition-colors group"
            >
              Ver demonstração
              <span className="text-sm group-hover:translate-x-0.5 transition-transform">→</span>
            </Link>
          </motion.div>

          {/* Trust indicators */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
            className="mt-16 flex items-center gap-8"
          >
            <div className="flex -space-x-2">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-8 h-8 rounded-full dark:bg-zinc-800 bg-gray-200 dark:border-zinc-950 border-white border-2"
                />
              ))}
            </div>
            <p className="text-sm dark:text-zinc-500 text-gray-500">
              <span className="dark:text-zinc-300 text-gray-700 font-semibold">1,247+</span> empresas confiam no ValidaHub
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  )
}