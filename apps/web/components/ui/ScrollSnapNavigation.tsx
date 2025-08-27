'use client'

import { useEffect, useRef, useState } from 'react'

export default function ScrollSnapNavigation({ children }: { children: React.ReactNode }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const sectionsRef = useRef<HTMLElement[]>([])
  const currentIndexRef = useRef(0) // Use ref to avoid stale closure
  const isScrollingRef = useRef(false) // Use ref for scrolling state
  const keyLockRef = useRef(false) // Use ref for key lock

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Force scroll to top on mount (handles hard refresh)
    window.scrollTo(0, 0)
    if (container.scrollTo) {
      container.scrollTo(0, 0)
    }

    // Collect all snap sections (excluding footer)
    const sections = Array.from(container.querySelectorAll('.snap-section')) as HTMLElement[]
    sectionsRef.current = sections

    // Scroll options
    const SCROLL_OPTS: ScrollIntoViewOptions = { 
      behavior: 'smooth', 
      block: 'start' 
    }

    // Navigate to specific section
    const goToSection = (index: number) => {
      if (index < 0 || index >= sections.length) return
      if (isScrollingRef.current) return // Prevent overlapping animations
      
      isScrollingRef.current = true
      const targetSection = sections[index]
      
      // Disable CSS snap temporarily
      if (container) {
        container.classList.add('navigating')
      }
      
      targetSection.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      })
      
      // Update URL hash
      const sectionId = targetSection.getAttribute('data-section')
      if (sectionId) {
        history.replaceState(null, '', `#${sectionId}`)
      }
      
      setCurrentIndex(index)
      currentIndexRef.current = index
      
      // Re-enable CSS snap after animation
      setTimeout(() => {
        isScrollingRef.current = false
        if (container) {
          container.classList.remove('navigating')
        }
      }, 1000) // Increased timeout for smoother navigation
    }

    // Update current index based on viewport
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.5
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const index = sections.indexOf(entry.target as HTMLElement)
          if (index !== -1) {
            setCurrentIndex(index)
      currentIndexRef.current = index
            // Update URL hash
            const sectionId = entry.target.getAttribute('data-section')
            if (sectionId) {
              history.replaceState(null, '', `#${sectionId}`)
            }
          }
        }
      })
    }, observerOptions)

    sections.forEach(section => observer.observe(section))

    // Keyboard navigation with debounce
    const handleKeydown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input
      const target = e.target as HTMLElement
      const tagName = target.tagName?.toLowerCase()
      if (['input', 'textarea', 'select'].includes(tagName) || e.metaKey || e.ctrlKey) {
        return
      }

      // Prevent rapid key presses
      if (keyLockRef.current) return
      
      let shouldNavigate = false
      let targetIndex = currentIndexRef.current

      switch (e.key) {
        case 'ArrowDown':
        case 'PageDown':
        case ' ':
          e.preventDefault()
          targetIndex = currentIndexRef.current + 1
          shouldNavigate = true
          break
        case 'ArrowUp':
        case 'PageUp':
          e.preventDefault()
          targetIndex = currentIndexRef.current - 1
          shouldNavigate = true
          break
        case 'Home':
          e.preventDefault()
          targetIndex = 0
          shouldNavigate = true
          break
        case 'End':
          e.preventDefault()
          targetIndex = sections.length - 1
          shouldNavigate = true
          break
      }
      
      if (shouldNavigate) {
        console.log('Navigating from', currentIndexRef.current, 'to', targetIndex)
        keyLockRef.current = true
        goToSection(targetIndex)
        // Reset lock after navigation completes
        setTimeout(() => {
          keyLockRef.current = false
          console.log('Navigation unlocked')
        }, 1200)
      }
    }

    // Wheel navigation with throttle - DISABLED for now to avoid conflicts
    // let wheelLock = false
    // const handleWheel = (e: WheelEvent) => {
    //   // Only apply snap navigation on desktop
    //   if (window.innerWidth < 768) return
      
    //   if (wheelLock) return
    //   wheelLock = true
    //   setTimeout(() => { wheelLock = false }, 400)

    //   if (Math.abs(e.deltaY) > 10) {
    //     if (e.deltaY > 0) {
    //       goToSection(currentIndex + 1)
    //     } else {
    //       goToSection(currentIndex - 1)
    //     }
    //   }
    // }

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (!prefersReducedMotion) {
      window.addEventListener('keydown', handleKeydown)
      // Temporarily disable wheel navigation for better UX
      // window.addEventListener('wheel', handleWheel, { passive: true })
    }

    // Navigate to hash on load
    const hash = window.location.hash.slice(1)
    if (hash) {
      const targetSection = sections.find(s => s.getAttribute('data-section') === hash)
      if (targetSection) {
        const index = sections.indexOf(targetSection)
        setTimeout(() => goToSection(index), 100)
      }
    }

    return () => {
      window.removeEventListener('keydown', handleKeydown)
      // window.removeEventListener('wheel', handleWheel)
      observer.disconnect()
    }
  }, []) // No dependencies - setup once on mount

  return (
    <div 
      ref={containerRef}
      className="snap-container"
      style={{ height: 'auto', minHeight: '100svh' }}
    >
      {children}
      
      {/* Navigation dots indicator */}
      <div className="fixed right-6 top-1/2 -translate-y-1/2 z-40 hidden md:flex flex-col gap-3">
        {Array.from({ length: sectionsRef.current.length }).map((_, i) => (
          <button
            key={i}
            onClick={() => {
              const section = sectionsRef.current[i]
              if (section) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' })
              }
            }}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              i === currentIndex 
                ? 'bg-green-400 w-8' 
                : 'bg-gray-600 hover:bg-gray-400'
            }`}
            aria-label={`Go to section ${i + 1}`}
          />
        ))}
      </div>
    </div>
  )
}