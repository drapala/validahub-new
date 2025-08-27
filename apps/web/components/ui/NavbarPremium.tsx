'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import Link from 'next/link'

const sections = [
  { id: 'hero', label: 'Início' },
  { id: 'calculator', label: 'Calculadora' },
  { id: 'social', label: 'Depoimentos' },
  { id: 'data', label: 'Demonstração' },
  { id: 'features', label: 'Recursos' },
  { id: 'pricing', label: 'Planos' },
  { id: 'footer', label: 'Contato' },
]

export default function NavbarPremium() {
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState<string>('hero')
  const { scrollY } = useScroll()
  const bgOpacity = useTransform(scrollY, [0, 32, 120], [0.35, 0.65, 1])
  const blur = useTransform(scrollY, [0, 120], ['blur(8px)', 'blur(12px)'])
  const height = useTransform(scrollY, [0, 120], [72, 60])

  // Scrollspy
  const obs = useRef<IntersectionObserver | null>(null)
  useEffect(() => {
    const opts = { rootMargin: '-40% 0px -55% 0px', threshold: 0.01 }
    obs.current = new IntersectionObserver((entries) => {
      const inView = entries
        .filter((e) => e.isIntersecting)
        .map((e) => e.target.getAttribute('id') || '')
      if (inView[0]) setActive(inView[0])
    }, opts)
    sections.forEach(({ id }) => {
      const el = document.getElementById(id)
      if (el) obs.current?.observe(el)
    })
    return () => obs.current?.disconnect()
  }, [])

  const go = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })

  return (
    <motion.nav
      style={{ height }}
      className="fixed inset-x-0 top-10 z-50"
      aria-label="Navegação principal"
    >
      {/* camada de fundo glass → sólido */}
      <motion.div
        style={{ 
          backdropFilter: blur,
          // @ts-ignore - Framer Motion types issue
          backgroundColor: useTransform(scrollY, [0, 32, 120], [
            'rgba(9,11,12, 0.35)',
            'rgba(9,11,12, 0.65)', 
            'rgba(9,11,12, 1)'
          ])
        }}
        className="absolute inset-0 border-b border-white/10"
      />
      <div className="relative mx-auto max-w-7xl px-4">
        <div className="flex h-full items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative">
              <span className="absolute inset-0 h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400/20 to-teal-400/20 blur-xl group-hover:from-emerald-400/30 group-hover:to-teal-400/30 transition-all" />
              <span className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900/80 border border-white/10">
                <span className="h-2 w-2 rounded-full bg-gradient-to-br from-emerald-400 to-teal-400" />
              </span>
            </div>
            <span className="font-semibold tracking-tight text-white">ValidaHub</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center rounded-full bg-white/5 border border-white/10 px-2 py-1.5">
              {sections.map((s, i) => (
                <button
                  key={s.id}
                  onClick={() => go(s.id)}
                  aria-current={active === s.id ? 'page' : undefined}
                  className="relative px-3 py-1 text-sm group"
                >
                  <span
                    className={`transition-all duration-200 ${
                      active === s.id
                        ? 'bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-300 font-medium'
                        : 'text-zinc-400 hover:text-white'
                    }`}
                  >
                    {s.label}
                  </span>
                  {active === s.id && (
                    <motion.span 
                      layoutId="navbar-indicator"
                      className="absolute -bottom-1 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-gradient-to-r from-emerald-400 to-teal-400 shadow-sm shadow-emerald-400/50" 
                    />
                  )}
                  {i !== sections.length - 1 && (
                    <span className="ml-3 text-zinc-700">•</span>
                  )}
                </button>
              ))}
            </div>

            <Link
              href="/login"
              className="px-4 py-1.5 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Entrar
            </Link>
            <Link
              href="/signup"
              className="relative group overflow-hidden rounded-full bg-gradient-to-r from-emerald-400 to-teal-400 px-5 py-1.5 text-sm font-semibold text-black transition-all hover:shadow-lg hover:shadow-emerald-400/25"
            >
              <span className="relative z-10">Testar Grátis</span>
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setOpen((v) => !v)}
            className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors"
            aria-label="Abrir menu"
          >
            <svg 
              viewBox="0 0 24 24" 
              className="h-5 w-5 text-white/90"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
            >
              {open ? (
                <>
                  <path d="M6 18L18 6" />
                  <path d="M6 6l12 12" />
                </>
              ) : (
                <>
                  <path d="M4 7h16" />
                  <path d="M4 12h16" />
                  <path d="M4 17h16" />
                </>
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Sheet */}
      {open && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute inset-x-2 top-14 rounded-2xl border border-white/10 bg-zinc-950/95 backdrop-blur-xl p-3 shadow-2xl"
        >
          <div className="space-y-1">
            {sections.map((s) => (
              <button
                key={s.id}
                onClick={() => {
                  setOpen(false)
                  go(s.id)
                }}
                className={`w-full text-left px-4 py-2.5 rounded-xl transition-all ${
                  active === s.id 
                    ? 'bg-gradient-to-r from-emerald-400/10 to-teal-400/10 text-white font-medium' 
                    : 'text-zinc-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
          <div className="my-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          <div className="flex gap-2">
            <Link 
              href="/login" 
              className="flex-1 rounded-xl border border-white/10 px-4 py-2.5 text-center text-zinc-300 hover:bg-white/5 transition-colors"
              onClick={() => setOpen(false)}
            >
              Entrar
            </Link>
            <Link
              href="/signup"
              className="flex-1 rounded-xl bg-gradient-to-r from-emerald-400 to-teal-400 px-4 py-2.5 text-black text-center font-semibold hover:shadow-lg hover:shadow-emerald-400/25 transition-all"
              onClick={() => setOpen(false)}
            >
              Testar Grátis
            </Link>
          </div>
        </motion.div>
      )}
    </motion.nav>
  )
}