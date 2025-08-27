'use client'

import Hero from '@/components/ui/Hero'
import ERPComparison from '@/components/ui/ERPComparison'
import SocialProof from '@/components/ui/SocialProof'
import DataProof from '@/components/ui/DataProof'
import Features from '@/components/ui/Features'
import ROICalculator from '@/components/ui/ROICalculator'
import Pricing from '@/components/ui/Pricing'
import CTA from '@/components/ui/CTA'
import Footer from '@/components/ui/Footer'
import SmoothScrollSimple from '@/components/ui/SmoothScrollSimple'

export default function LandingPage() {
  return (
    <SmoothScrollSimple>
      <main id="snap-container" className="bg-gray-900 md:h-screen md:overflow-y-scroll">
        <section className="snap-section min-h-screen" data-section="hero">
          <Hero />
        </section>
        
        <section className="snap-section min-h-[70vh] md:min-h-screen" data-section="erp">
          <ERPComparison />
        </section>
        
        <section className="snap-section min-h-[50vh] md:min-h-[60vh]" data-section="social">
          <SocialProof />
        </section>
        
        <section className="snap-section min-h-[80vh] md:min-h-screen" data-section="data">
          <DataProof />
        </section>
        
        <section className="snap-section min-h-[90vh] md:min-h-screen" data-section="features">
          <Features />
        </section>
        
        <section className="snap-section min-h-[80vh] md:min-h-screen" data-section="calculator">
          <ROICalculator />
        </section>
        
        <section className="snap-section min-h-[90vh] md:min-h-screen" data-section="pricing">
          <Pricing />
        </section>
        
        <section className="snap-section min-h-[70vh] md:min-h-[80vh]" data-section="cta">
          <CTA />
        </section>
        
        <section className="snap-section min-h-[40vh] md:min-h-[50vh]" data-section="footer">
          <Footer />
        </section>
      </main>
    </SmoothScrollSimple>
  )
}