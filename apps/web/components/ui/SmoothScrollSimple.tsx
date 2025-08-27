'use client'

import { useEffect, useState } from 'react'
import ProgressRail from './ProgressRail'
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

  const sections = [
    { id: 'inicio', label: 'Início', targetId: '#hero' },
    { id: 'calc', label: 'Calculadora', targetId: '#calculator' },
    { id: 'depoimentos', label: 'Depoimentos', targetId: '#social' },
    { id: 'demo', label: 'Demonstração', targetId: '#data' },
    { id: 'recursos', label: 'Recursos', targetId: '#features' },
    { id: 'planos', label: 'Planos', targetId: '#pricing' },
    { id: 'contato', label: 'Contato', targetId: '#footer' }
  ]

  return (
    <>
      {/* Progress Rail with Scrollspy */}
      {mounted && (
        <ProgressRail 
          sections={sections}
          whatsapp="5511999999999"
        />
      )}
      {children}
    </>
  )
}