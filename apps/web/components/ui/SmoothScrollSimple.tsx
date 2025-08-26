'use client'

import { useEffect, useState } from 'react'
import './smooth-scroll-simple.css'

export default function SmoothScrollSimple({ children }: { children: React.ReactNode }) {
  const [currentSection, setCurrentSection] = useState(0)
  const [isScrolling, setIsScrolling] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Detect current section based on scroll position
  useEffect(() => {
    if (!mounted || window.innerWidth < 768) return

    const updateCurrentSection = () => {
      const container = document.getElementById('snap-container')
      if (!container) return

      const sections = container.querySelectorAll('.snap-section')
      const scrollPosition = container.scrollTop + window.innerHeight / 2

      sections.forEach((section, index) => {
        const element = section as HTMLElement
        const top = element.offsetTop
        const bottom = top + element.offsetHeight

        if (scrollPosition >= top && scrollPosition < bottom) {
          setCurrentSection(index)
        }
      })
    }

    const container = document.getElementById('snap-container')
    if (container) {
      container.addEventListener('scroll', updateCurrentSection)
      updateCurrentSection() // Initial check
    }

    return () => {
      if (container) {
        container.removeEventListener('scroll', updateCurrentSection)
      }
    }
  }, [mounted])

  useEffect(() => {
    if (!mounted) return
    
    // Mobile check
    if (window.innerWidth < 768) {
      return
    }

    const container = document.getElementById('snap-container')
    if (!container) return

    const sections = container.querySelectorAll('.snap-section')
    let scrollTimeout: NodeJS.Timeout

    const handleScroll = (e: WheelEvent) => {
      if (isScrolling) return
      
      e.preventDefault()
      clearTimeout(scrollTimeout)

      const direction = e.deltaY > 0 ? 1 : -1
      const nextSection = Math.max(0, Math.min(sections.length - 1, currentSection + direction))
      
      if (nextSection !== currentSection) {
        setIsScrolling(true)
        
        sections[nextSection].scrollIntoView({ 
          behavior: 'smooth',
          block: 'start' 
        })

        scrollTimeout = setTimeout(() => {
          setIsScrolling(false)
        }, 1000)
      }
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault()
        const direction = e.key === 'ArrowDown' ? 1 : -1
        const nextSection = Math.max(0, Math.min(sections.length - 1, currentSection + direction))
        
        if (nextSection !== currentSection) {
          sections[nextSection].scrollIntoView({ 
            behavior: 'smooth',
            block: 'start' 
          })
        }
      }
    }

    window.addEventListener('wheel', handleScroll, { passive: false })
    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('wheel', handleScroll)
      window.removeEventListener('keydown', handleKeyDown)
      clearTimeout(scrollTimeout)
    }
  }, [currentSection, isScrolling, mounted])

  const sections = ['hero', 'erp', 'social', 'data', 'visualization', 'features', 'calculator', 'pricing', 'cta', 'footer']

  return (
    <>
      {mounted && window.innerWidth >= 768 && (
        <div className="fixed right-8 top-1/2 -translate-y-1/2 z-50 hidden md:flex flex-col gap-3">
          {sections.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                const container = document.getElementById('snap-container')
                if (!container) return
                const sections = container.querySelectorAll('.snap-section')
                sections[index]?.scrollIntoView({ behavior: 'smooth' })
              }}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                currentSection === index 
                  ? 'bg-green-400 scale-125' 
                  : 'bg-gray-600 hover:bg-gray-400'
              }`}
              aria-label={`Section ${index + 1}`}
            />
          ))}
        </div>
      )}
      {children}
    </>
  )
}