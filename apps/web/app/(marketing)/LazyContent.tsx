'use client'

import { useInViewport } from '@/hooks/useInViewport'
import dynamic from 'next/dynamic'

// Componentes lazy com loading skeleton mínimo
const ROICalculator = dynamic(() => import('@/components/ui/ROICalculator'))
const DataProofLite = dynamic(() => import('@/components/ui/DataProofLite'))
const Pricing = dynamic(() => import('@/components/ui/Pricing'))
const Footer = dynamic(() => import('@/components/ui/Footer'))

// Componentes menores
const SocialProofCondensed = dynamic(() => import('@/components/ui/SocialProofCondensed'))
const FeaturesAccordion = dynamic(() => import('@/components/ui/FeaturesAccordion'))
const StickyPromoBar = dynamic(() => import('@/components/ui/StickyPromoBar'))
const CookieConsent = dynamic(() => import('@/components/ui/CookieConsent'))
const WhatsAppFloat = dynamic(() => import('@/components/ui/WhatsAppFloat'))

function LazySection({ id, children, minHeight = "min-h-screen" }: any) {
  const [ref, isInView] = useInViewport<HTMLDivElement>({ 
    rootMargin: '100px',
    triggerOnce: true 
  })

  return (
    <section 
      ref={ref}
      id={id}
      data-section={id}
      className={`${minHeight} scroll-mt-20`}
    >
      {isInView ? children : (
        <div className={`${minHeight} flex items-center justify-center`}>
          <div className="w-8 h-8 border-2 border-gray-600 border-t-green-400 rounded-full animate-spin" />
        </div>
      )}
    </section>
  )
}

export default function LazyContent() {
  return (
    <>
      <LazySection id="calculator" minHeight="min-h-[80vh] md:min-h-screen">
        <ROICalculator />
      </LazySection>

      <LazySection id="social" minHeight="min-h-[60vh] md:min-h-[80vh]">
        <SocialProofCondensed />
      </LazySection>

      <LazySection id="data" minHeight="min-h-[80vh] md:min-h-screen">
        <DataProofLite />
      </LazySection>

      <LazySection id="features" minHeight="min-h-[80vh] md:min-h-screen">
        <FeaturesAccordion />
      </LazySection>

      <LazySection id="pricing" minHeight="min-h-[90vh] md:min-h-screen">
        <Pricing />
      </LazySection>

      <LazySection id="footer" minHeight="min-h-[40vh] md:min-h-[50vh]">
        <Footer />
      </LazySection>

      {/* Componentes flutuantes */}
      <StickyPromoBar />
      <CookieConsent />
      <WhatsAppFloat />
    </>
  )
}