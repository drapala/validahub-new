'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  const isDark = theme === 'dark'

  return (
    <motion.button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={`
        relative p-2 rounded-lg transition-all duration-300
        ${isDark 
          ? 'bg-zinc-900/50 hover:bg-zinc-800/50 border border-zinc-800/50' 
          : 'bg-purple-50/50 hover:bg-purple-100/50 border border-purple-200/30'
        }
      `}
      whileTap={{ scale: 0.95 }}
      aria-label={`Mudar para tema ${isDark ? 'claro' : 'escuro'}`}
    >
      <AnimatePresence mode="wait">
        {isDark ? (
          <motion.div
            key="moon"
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          >
            <Moon className="h-4 w-4 text-zinc-400" strokeWidth={1.5} />
          </motion.div>
        ) : (
          <motion.div
            key="sun"
            initial={{ rotate: 90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: -90, opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          >
            <Sun className="h-4 w-4 text-purple-600" strokeWidth={1.5} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Glow sutil no hover */}
      <AnimatePresence>
        {isDark ? (
          <motion.div
            className="absolute inset-0 rounded-lg bg-emerald-500/10 blur-xl pointer-events-none"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        ) : (
          <motion.div
            className="absolute inset-0 rounded-lg bg-purple-500/10 blur-xl pointer-events-none"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </AnimatePresence>
    </motion.button>
  )
}