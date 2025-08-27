'use client'

import dynamic from 'next/dynamic'
import HeroOptimized from '@/components/ui/HeroOptimized'
import SmoothScrollSimple from '@/components/ui/SmoothScrollSimple'

// Lazy load componentes pesados
const ROICalculator = dynamic(() => import('@/components/ui/ROICalculator'), {
  loading: () => <div className="min-h-screen flex items-center justify-center"><div className="text-gray-400">Carregando calculadora...</div></div>,
  ssr: false
})

const SocialProofCondensed = dynamic(() => import('@/components/ui/SocialProofCondensed'), {
  loading: () => <div className="min-h-[60vh] flex items-center justify-center"><div className="text-gray-400">Carregando...</div></div>,
  ssr: true
})

const DataProof = dynamic(() => import('@/components/ui/DataProof'), {
  loading: () => <div className="min-h-screen flex items-center justify-center"><div className="text-gray-400">Carregando demonstração...</div></div>,
  ssr: false
})

const FeaturesAccordion = dynamic(() => import('@/components/ui/FeaturesAccordion'), {
  loading: () => <div className="min-h-screen flex items-center justify-center"><div className="text-gray-400">Carregando features...</div></div>,
  ssr: true
})

const Pricing = dynamic(() => import('@/components/ui/Pricing'), {
  loading: () => <div className="min-h-screen flex items-center justify-center"><div className="text-gray-400">Carregando planos...</div></div>,
  ssr: true
})

const Footer = dynamic(() => import('@/components/ui/Footer'), {
  loading: () => <div className="min-h-[40vh]"></div>,
  ssr: true
})

const StickyPromoBar = dynamic(() => import('@/components/ui/StickyPromoBar'), {
  ssr: false
})

const CookieConsent = dynamic(() => import('@/components/ui/CookieConsent'), {
  ssr: false
})

const WhatsAppFloat = dynamic(() => import('@/components/ui/WhatsAppFloat'), {
  ssr: false
})

export default function LandingPageOptimized() {
  return (
    <>
      <SmoothScrollSimple>
        <main id="snap-container" className="bg-gradient-to-b from-gray-900 via-gray-900 to-black md:h-screen md:overflow-y-scroll">
          {/* Hero: Server Component otimizado */}
          <section className="snap-section min-h-screen scroll-mt-20" data-section="hero">
            <HeroOptimized />
          </section>
          
          {/* Componentes lazy-loaded */}
          <section className="snap-section min-h-[80vh] md:min-h-screen scroll-mt-24" data-section="calculator">
            <ROICalculator />
          </section>
          
          <section className="snap-section min-h-[60vh] md:min-h-[80vh] scroll-mt-20" data-section="social">
            <SocialProofCondensed />
          </section>
          
          <section className="snap-section min-h-[80vh] md:min-h-screen scroll-mt-20" data-section="data">
            <DataProof />
          </section>
          
          <section className="snap-section min-h-[80vh] md:min-h-screen scroll-mt-20" data-section="features">
            <FeaturesAccordion />
          </section>
          
          <section className="snap-section min-h-[90vh] md:min-h-screen scroll-mt-20" data-section="pricing">
            <Pricing />
          </section>
          
          <section className="snap-section min-h-[40vh] md:min-h-[50vh] scroll-mt-20" data-section="footer">
            <Footer />
          </section>
        </main>
      </SmoothScrollSimple>
      
      {/* Componentes não-críticos */}
      <StickyPromoBar />
      <CookieConsent />
      <WhatsAppFloat />
    </>
  )
}