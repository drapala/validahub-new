'use client'

import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'

interface Section {
  id: string
  label: string
  targetId: string
}

interface ProgressRailProps {
  sections: Section[]
  whatsapp?: string
}

export default function ProgressRail({ sections, whatsapp = '5511999999999' }: ProgressRailProps) {
  const [activeSection, setActiveSection] = useState(0)
  const [hoveredDot, setHoveredDot] = useState<number | null>(null)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [showWhatsApp, setShowWhatsApp] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const { scrollYProgress } = useScroll()
  
  // Check mobile
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024) // Changed to lg breakpoint
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Track scroll progress and auto-hide logic
  useEffect(() => {
    const updateProgress = () => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = Math.min(100, Math.max(0, (window.scrollY / scrollHeight) * 100))
      const ratio = progress / 100
      
      setScrollProgress(Math.round(progress))
      setShowWhatsApp(progress > 80)
      // Auto-hide: only show between 10% and 90% of scroll
      setIsVisible(ratio > 0.1 && ratio < 0.9)
    }
    
    updateProgress()
    window.addEventListener('scroll', updateProgress, { passive: true })
    return () => window.removeEventListener('scroll', updateProgress)
  }, [])

  // Intersection Observer for active section
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = sections.findIndex(s => s.targetId === `#${entry.target.id}`)
            if (index !== -1) setActiveSection(index)
          }
        })
      },
      { threshold: 0.3, rootMargin: '-20% 0px -60% 0px' }
    )

    sections.forEach((section) => {
      const element = document.querySelector(section.targetId)
      if (element) observer.observe(element)
    })

    return () => observer.disconnect()
  }, [sections])

  const scrollToSection = (targetId: string, index: number) => {
    const element = document.querySelector(targetId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setActiveSection(index)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowUp' && index > 0) {
      scrollToSection(sections[index - 1].targetId, index - 1)
    } else if (e.key === 'ArrowDown' && index < sections.length - 1) {
      scrollToSection(sections[index + 1].targetId, index + 1)
    }
  }

  // Mobile progress bar
  if (isMobile) {
    return (
      <motion.div
        className="fixed top-0 left-0 right-0 h-[2px] z-50"
        style={{
          background: 'linear-gradient(to right, #10b981, #14b8a6, #06b6d4)',
          scaleX: scrollYProgress,
          transformOrigin: 'left'
        }}
      />
    )
  }

  // Desktop rail - only visible in dark mode and ≥lg screens
  return (
    <motion.div 
      className="fixed right-4 top-1/2 -translate-y-1/2 z-50 hidden dark:lg:flex flex-col items-center group/rail"
      aria-label="Navegação por seções"
      animate={{ 
        opacity: isVisible ? 1 : 0
      }}
      style={{
        pointerEvents: isVisible ? 'auto' : 'none'
      }}
      transition={{ duration: 0.3 }}
    >
      {/* Trilho vertical - only dark theme colors needed now */}
      <div className="absolute top-0 bottom-0 w-[2px] rounded-full
                      bg-gradient-to-b from-emerald-500/30 via-teal-400/30 to-cyan-400/30
                      opacity-30 group-hover/rail:opacity-80 transition-opacity duration-300" />
      
      {/* Progress pill */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: scrollProgress > 5 ? 1 : 0 }}
        className="absolute top-1/2 -translate-y-1/2 -left-8
                   px-2 py-1 rounded-full bg-zinc-900/60 backdrop-blur-xl
                   border border-white/10 pointer-events-none"
      >
        <span className="text-[10px] font-mono text-zinc-400">{scrollProgress}%</span>
      </motion.div>

      {/* Section dots */}
      <div className="relative flex flex-col gap-8 py-4">
        {sections.map((section, index) => {
          const isActive = activeSection === index
          const isHovered = hoveredDot === index
          
          return (
            <div key={section.id} className="relative flex items-center">
              {/* Tooltip */}
              <AnimatePresence>
                {isHovered && (
                  <motion.div
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.25 }}
                    className="absolute right-full mr-3 pointer-events-none"
                  >
                    <div className="px-3 py-1.5 rounded-lg bg-zinc-900/80 backdrop-blur-xl
                                    border border-white/10 whitespace-nowrap">
                      <span className="text-xs font-medium text-zinc-200">{section.label}</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Dot */}
              <motion.button
                onClick={() => scrollToSection(section.targetId, index)}
                onMouseEnter={() => setHoveredDot(index)}
                onMouseLeave={() => setHoveredDot(null)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                aria-label={`Ir para ${section.label}`}
                aria-current={isActive ? 'true' : 'false'}
                className="relative p-2 focus:outline-none focus-visible:ring-2 
                           focus-visible:ring-emerald-500/50 rounded-full"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              >
                <motion.div
                  animate={{
                    width: isActive ? 8 : 6,
                    height: isActive ? 8 : 6,
                    opacity: isActive ? 1 : 0.4
                  }}
                  transition={{ duration: 0.35, ease: 'easeOut' }}
                  className={`rounded-full ${
                    isActive 
                      ? 'bg-gradient-to-br from-emerald-400 to-teal-400 shadow-lg shadow-emerald-400/30' 
                      : 'bg-zinc-500'
                  }`}
                />
              </motion.button>
            </div>
          )
        })}

        {/* WhatsApp button - aparece ao final */}
        <AnimatePresence>
          {showWhatsApp && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="relative flex items-center mt-4"
            >
              {/* Tooltip WhatsApp */}
              <AnimatePresence>
                {hoveredDot === -1 && (
                  <motion.div
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.25 }}
                    className="absolute right-full mr-3 pointer-events-none"
                  >
                    <div className="px-3 py-1.5 rounded-lg bg-zinc-900/80 backdrop-blur-xl
                                    border border-white/10 whitespace-nowrap">
                      <span className="text-xs font-medium text-zinc-200">
                        Fale com a gente no WhatsApp
                      </span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.a
                href={`https://wa.me/${whatsapp}`}
                target="_blank"
                rel="noopener noreferrer"
                onMouseEnter={() => setHoveredDot(-1)}
                onMouseLeave={() => setHoveredDot(null)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative w-10 h-10 rounded-full overflow-hidden
                           bg-zinc-900/60 backdrop-blur-xl border border-white/10
                           flex items-center justify-center group
                           focus:outline-none focus-visible:ring-2 
                           focus-visible:ring-emerald-500/50"
                aria-label="Conversar no WhatsApp"
              >
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-400/10 to-teal-400/10 
                                opacity-0 group-hover:opacity-100 transition-opacity" />
                
                {/* WhatsApp icon */}
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-zinc-300 relative z-10">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.149-.67.149-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414-.074-.123-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
              </motion.a>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}