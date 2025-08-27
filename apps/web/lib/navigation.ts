/**
 * Centralized navigation utility for scroll handling
 * This ensures consistent scroll behavior across the app
 */

export function navigateToSection(sectionId: string) {
  // Remove # if present
  const cleanId = sectionId.replace('#', '')
  
  // Find the section
  const section = document.querySelector(`[data-section="${cleanId}"]`) || 
                  document.getElementById(cleanId)
  
  if (!section) {
    console.warn(`Section not found: ${cleanId}`)
    return
  }
  
  // Use native CSS scroll-behavior from globals.css
  // The snap container handles the smooth scrolling
  section.scrollIntoView({ 
    behavior: 'smooth', 
    block: 'start'
  })
  
  // Update URL without triggering navigation
  if (window.history.replaceState) {
    window.history.replaceState(null, '', `#${cleanId}`)
  }
}

// Helper to get current section
export function getCurrentSection(): string | null {
  const sections = document.querySelectorAll('[data-section]')
  const viewportMiddle = window.innerHeight / 2
  
  for (const section of sections) {
    const rect = section.getBoundingClientRect()
    if (rect.top <= viewportMiddle && rect.bottom >= viewportMiddle) {
      return section.getAttribute('data-section')
    }
  }
  
  return null
}