'use client'

import { useEffect, useState } from 'react'

export default function SmoothScroll({ children }: { children: React.ReactNode }) {
  const [currentSection, setCurrentSection] = useState(0)
  const [isScrolling, setIsScrolling] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)

    // Don't initialize if mobile
    if (window.innerWidth < 768) {
      return () => window.removeEventListener('resize', checkMobile)
    }

    const sections = document.querySelectorAll('.snap-section')
    const totalSections = sections.length
    let lastScrollTime = Date.now()
    const DEBOUNCE_TIME = 1200
    const ANIMATION_DURATION = 800

    // Update hash without scroll
    const updateHash = (index: number) => {
      const section = sections[index]
      const id = section.getAttribute('data-section') || section.id
      if (id) {
        history.replaceState(null, '', `#${id}`)
      }
    }

    // Scroll to section
    const scrollToSection = (index: number) => {
      if (isScrolling || index < 0 || index >= totalSections) return
      
      setIsScrolling(true)
      const targetSection = sections[index] as HTMLElement
      
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setCurrentSection(index)
      updateHash(index)

      setTimeout(() => {
        setIsScrolling(false)
      }, ANIMATION_DURATION)
    }

    // Handle wheel event
    const handleWheel = (e: WheelEvent) => {
      if (isMobile) return

      const now = Date.now()
      if (now - lastScrollTime < DEBOUNCE_TIME) return
      
      e.preventDefault()
      lastScrollTime = now

      const delta = e.deltaY
      const threshold = 50

      if (Math.abs(delta) > threshold) {
        const direction = delta > 0 ? 1 : -1
        const nextSection = currentSection + direction
        scrollToSection(nextSection)
      }
    }

    // Handle keyboard
    const handleKeydown = (e: KeyboardEvent) => {
      if (isMobile) return

      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault()
        const direction = e.key === 'ArrowDown' ? 1 : -1
        const nextSection = currentSection + direction
        scrollToSection(nextSection)
      }
    }

    // Handle touch for mobile swipe
    let touchStart = 0
    const handleTouchStart = (e: TouchEvent) => {
      touchStart = e.touches[0].clientY
    }

    const handleTouchEnd = (e: TouchEvent) => {
      if (isMobile) return // Let mobile scroll normally

      const touchEnd = e.changedTouches[0].clientY
      const diff = touchStart - touchEnd
      const threshold = 50

      if (Math.abs(diff) > threshold) {
        const direction = diff > 0 ? 1 : -1
        const nextSection = currentSection + direction
        scrollToSection(nextSection)
      }
    }

    // Initialize current section from hash
    const initFromHash = () => {
      const hash = window.location.hash.slice(1)
      if (hash) {
        const index = Array.from(sections).findIndex(
          section => section.id === hash || section.getAttribute('data-section') === hash
        )
        if (index !== -1) {
          setCurrentSection(index)
          sections[index].scrollIntoView({ behavior: 'auto', block: 'start' })
        }
      }
    }

    // Set up event listeners
    window.addEventListener('wheel', handleWheel, { passive: false })
    window.addEventListener('keydown', handleKeydown)
    window.addEventListener('touchstart', handleTouchStart)
    window.addEventListener('touchend', handleTouchEnd)
    
    initFromHash()

    return () => {
      window.removeEventListener('wheel', handleWheel)
      window.removeEventListener('keydown', handleKeydown)
      window.removeEventListener('touchstart', handleTouchStart)
      window.removeEventListener('touchend', handleTouchEnd)
      window.removeEventListener('resize', checkMobile)
    }
  }, [currentSection, isScrolling, isMobile])

  // Navigation dots
  const sections = ['hero', 'erp', 'social', 'data', 'visualization', 'features', 'calculator', 'pricing', 'cta']

  return (
    <>
      {/* Navigation Dots */}
      {!isMobile && (
        <div className="fixed right-8 top-1/2 -translate-y-1/2 z-50 flex flex-col gap-3">
          {sections.map((section, index) => (
            <button
              key={section}
              onClick={() => {
                const element = document.querySelector(`[data-section="${section}"]`)
                if (element) {
                  element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  setCurrentSection(index)
                }
              }}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                currentSection === index 
                  ? 'bg-green-400 scale-125' 
                  : 'bg-gray-600 hover:bg-gray-400'
              }`}
              aria-label={`Go to ${section} section`}
            />
          ))}
        </div>
      )}
      {children}
    </>
  )
}