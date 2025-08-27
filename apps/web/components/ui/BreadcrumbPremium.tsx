'use client'

import { motion, useInView } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { useRef, useState, useEffect } from 'react'

interface BreadcrumbItem {
  label: string
  onClick?: () => void
  isActive?: boolean
}

interface BreadcrumbPremiumProps {
  items: BreadcrumbItem[]
  currentSection: number
}

export default function BreadcrumbPremium({ items, currentSection }: BreadcrumbPremiumProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: false, margin: "-100px" })
  const [isMobile, setIsMobile] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const activeItem = items[currentSection] || items[0]

  // Mobile dropdown version
  if (isMobile) {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ duration: 0.5 }}
        className="fixed top-20 right-4 z-50"
      >
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="px-4 py-2 bg-zinc-900/80 backdrop-blur-xl rounded-lg border border-zinc-800/50 text-sm font-semibold text-neutral-300 flex items-center gap-2"
        >
          <span className="bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
            {activeItem.label}
          </span>
          <ChevronRight className={`w-4 h-4 transition-transform ${showDropdown ? 'rotate-90' : ''}`} />
        </button>
        
        {showDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-full right-0 mt-2 py-2 bg-zinc-900/90 backdrop-blur-xl rounded-lg border border-zinc-800/50 shadow-xl"
          >
            {items.map((item, index) => (
              <button
                key={index}
                onClick={() => {
                  item.onClick?.()
                  setShowDropdown(false)
                }}
                className={`block w-full px-4 py-2 text-left text-sm font-medium transition-colors whitespace-nowrap ${
                  index === currentSection
                    ? 'text-green-400'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-zinc-800/50'
                }`}
              >
                {item.label}
              </button>
            ))}
          </motion.div>
        )}
      </motion.div>
    )
  }

  // Desktop horizontal version
  return (
    <motion.nav
      ref={ref}
      initial={{ opacity: 0, y: -20 }}
      animate={{ 
        opacity: isInView ? 1 : 0,
        y: isInView ? 0 : -20
      }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="fixed top-24 left-1/2 -translate-x-1/2 z-40 hidden md:block"
    >
      <div className="flex items-center gap-2 px-6 py-3 bg-zinc-900/60 backdrop-blur-xl rounded-full border border-zinc-800/30">
        {items.map((item, index) => (
          <div key={index} className="flex items-center">
            <motion.button
              onClick={item.onClick}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`
                px-3 py-1.5 text-sm font-semibold tracking-wide transition-all duration-300
                ${index === currentSection
                  ? 'text-transparent bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text'
                  : 'text-neutral-400 hover:text-neutral-100'
                }
              `}
            >
              {item.label}
            </motion.button>
            
            {/* Separator */}
            {index < items.length - 1 && (
              <div className="mx-2 relative">
                <div className="w-1 h-1 rounded-full bg-gradient-to-r from-green-400/50 to-blue-400/50" />
                {/* Animated glow when passing */}
                {(index === currentSection || index === currentSection - 1) && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 2, opacity: 1 }}
                    transition={{ duration: 0.5 }}
                    className="absolute inset-0 w-1 h-1 rounded-full bg-gradient-to-r from-green-400 to-blue-400 blur-sm"
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </motion.nav>
  )
}