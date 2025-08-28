'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { Menu, X } from 'lucide-react'
import { ThemeToggle } from './ThemeToggle'

const sections = [
  { id: 'hero', label: 'Início' },
  { id: 'calculator', label: 'Calculadora' },
  { id: 'social', label: 'Depoimentos' },
  { id: 'data', label: 'Demo' },
  { id: 'features', label: 'Recursos' },
  { id: 'pricing', label: 'Planos' },
]

export default function NavbarRefined() {
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState<string>('hero')
  const { scrollY } = useScroll()
  
  // Transições mais sutis
  const bgOpacity = useTransform(scrollY, [0, 100], [0.3, 0.5])
  const blur = useTransform(scrollY, [0, 100], ['blur(12px) saturate(140%)', 'blur(16px) saturate(160%)'])
  const height = useTransform(scrollY, [0, 100], [64, 56])
  const logoScale = useTransform(scrollY, [0, 100], [1, 0.95])

  // Scrollspy
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActive(entry.target.id)
          }
        })
      },
      { rootMargin: '-30% 0px -60% 0px', threshold: 0.1 }
    )

    sections.forEach(({ id }) => {
      const element = document.getElementById(id)
      if (element) observer.observe(element)
    })

    return () => observer.disconnect()
  }, [])

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setOpen(false)
  }

  return (
    <motion.nav
      style={{ 
        height,
        top: 'var(--promo-h, 0px)'
      }}
      className="fixed inset-x-0 z-50 transition-[top] duration-300 ease-out"
      aria-label="Navegação principal"
    >
      {/* Background com glass adaptativo ao tema */}
      <motion.div
        style={{ 
          backdropFilter: blur,
          WebkitBackdropFilter: blur,
        }}
        className="absolute inset-0 
          dark:bg-zinc-950/20
          bg-white/30
          border-b dark:border-zinc-800/20 border-gray-200/30
          transition-all duration-300"
      />
      
      {/* Container */}
      <div className="relative h-full mx-auto max-w-7xl px-6">
        <div className="flex h-full items-center justify-between">
          
          {/* Logo - mais peso visual */}
          <motion.div style={{ scale: logoScale }}>
            <Link href="/" className="flex items-center gap-3 group">
              {/* Icon adaptativo ao tema */}
              <div className="relative">
                <div className="absolute inset-0 rounded-lg blur-xl transition-colors
                  dark:bg-emerald-500/20 dark:group-hover:bg-emerald-500/30
                  bg-violet-500/20 group-hover:bg-violet-500/30" />
                <div className="relative h-9 w-9 rounded-lg flex items-center justify-center
                  dark:bg-zinc-900 dark:border-emerald-500/30
                  bg-white border-violet-500/30 border">
                  <div className="h-2.5 w-2.5 rounded-full 
                    dark:bg-gradient-to-br dark:from-emerald-400 dark:to-teal-400
                    bg-gradient-to-br from-violet-500 to-purple-500" />
                </div>
              </div>
              {/* Nome adaptativo */}
              <span className="text-lg font-bold tracking-tight
                dark:text-white text-gray-900">
                ValidaHub
              </span>
            </Link>
          </motion.div>

          {/* Desktop Navigation - espaçamento uniforme */}
          <div className="hidden md:flex items-center gap-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`
                  relative px-4 py-2 text-[13px] font-medium transition-all duration-200
                  ${active === section.id 
                    ? 'dark:text-white text-gray-900' 
                    : 'dark:text-zinc-400 dark:hover:text-zinc-200 text-gray-600 hover:text-gray-900'
                  }
                `}
                aria-current={active === section.id ? 'page' : undefined}
              >
                <span className="relative z-10">{section.label}</span>
                
                {/* Indicador único e sutil */}
                {active === section.id && (
                  <motion.div
                    layoutId="nav-active"
                    className="absolute inset-0 dark:bg-gradient-to-r dark:from-emerald-500/10 dark:to-teal-500/10 bg-gradient-to-r from-purple-500/10 to-violet-500/10 rounded-lg"
                    transition={{ type: 'spring', duration: 0.5, bounce: 0.2 }}
                  />
                )}
              </button>
            ))}
          </div>

          {/* Actions - mais equilibrado */}
          <div className="hidden md:flex items-center gap-3">
            <ThemeToggle />
            <Link
              href="http://localhost:3002/auth/login"
              className="px-4 py-2 text-[13px] font-medium dark:text-zinc-300 dark:hover:text-white text-gray-700 hover:text-gray-900 transition-colors"
            >
              Entrar
            </Link>
            <Link
              href="/signup"
              className="px-5 py-2 rounded-lg text-[13px] font-semibold transition-all
                dark:bg-emerald-500/10 dark:hover:bg-emerald-500/20 dark:border dark:border-emerald-500/30 dark:text-emerald-400 dark:hover:shadow-lg dark:hover:shadow-emerald-500/10
                bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-600 hover:shadow-lg hover:shadow-purple-500/10"
            >
              Testar Grátis
            </Link>
          </div>

          {/* Mobile menu */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden p-2 text-zinc-400 hover:text-white transition-colors"
            aria-label={open ? 'Fechar menu' : 'Abrir menu'}
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Sheet - mais clean */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden absolute inset-x-0 top-full overflow-hidden"
          >
            <div className="bg-zinc-950/95 backdrop-blur-xl border-t border-zinc-800/50 px-6 py-4">
              <div className="space-y-1">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={`
                      w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-all
                      ${active === section.id
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
                      }
                    `}
                  >
                    {section.label}
                  </button>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-zinc-800/50 flex gap-3">
                <Link
                  href="http://localhost:3002/auth/login"
                  className="flex-1 py-2.5 text-center text-sm font-medium text-zinc-400 hover:text-white transition-colors"
                  onClick={() => setOpen(false)}
                >
                  Entrar
                </Link>
                <Link
                  href="/signup"
                  className="flex-1 py-2.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm font-semibold text-center hover:bg-emerald-500/20 transition-all"
                  onClick={() => setOpen(false)}
                >
                  Testar Grátis
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}