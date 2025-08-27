'use client'

import { useEffect, useState } from 'react'
import './smooth-scroll-simple.css'

export default function SmoothScrollSimple({ children }: { children: React.ReactNode }) {
  const [currentSection, setCurrentSection] = useState(0)
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

  // Removed smooth scroll wheel/keyboard handlers - using native scroll only

  const sections = ['hero', 'calculator', 'social', 'data', 'features', 'pricing', 'footer']

  return (
    <>
      {mounted && window.innerWidth >= 768 && (
        <div className="fixed right-8 top-1/2 -translate-y-1/2 z-50 hidden md:flex flex-col gap-3">
          {sections.map((sectionName, index) => (
            <button
              key={index}
              onClick={() => {
                const container = document.getElementById('snap-container')
                if (!container) return
                
                const sections = container.querySelectorAll('.snap-section')
                if (sections[index]) {
                  // Use native scrollIntoView without smooth behavior
                  sections[index].scrollIntoView({ behavior: 'auto', block: 'start' })
                }
                
                setCurrentSection(index)
              }}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                currentSection === index 
                  ? 'bg-green-400 scale-125' 
                  : 'bg-gray-600 hover:bg-gray-400'
              }`}
              aria-label={`Go to ${sectionName} section`}
            />
          ))}
        </div>
      )}
      {children}
    </>
  )
}