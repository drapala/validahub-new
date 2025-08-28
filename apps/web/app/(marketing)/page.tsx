'use client'

import Hero from '@/components/ui/Hero'
import SectionEnterprise from '@/components/ui/SectionEnterprise'
import DataProof from '@/components/ui/DataProof'
import Features from '@/components/ui/Features'
import ROICalculatorWithLead from '@/components/roi-calculator-with-lead'
import Pricing from '@/components/ui/Pricing'
import Footer from '@/components/ui/Footer'
import WhatsAppFloatPremium from '@/components/ui/WhatsAppFloatPremium'
import CookieBanner from '@/components/ui/CookieBanner'

export default function LandingPage() {
  return (
    <>
      <main className="dark:bg-zinc-950 bg-white">
        
        <section id="hero" className="min-h-screen">
          <Hero />
        </section>
        
        <section id="enterprise" className="min-h-screen">
          <SectionEnterprise />
        </section>
        
        <section id="calculator" className="min-h-[80vh] md:min-h-screen">
          <ROICalculatorWithLead />
        </section>
        
        <section id="data" className="min-h-[80vh] md:min-h-screen">
          <DataProof />
        </section>
        
        <section id="features" className="min-h-[90vh] md:min-h-screen">
          <Features />
        </section>
        
        <section id="pricing" className="min-h-[90vh] md:min-h-screen">
          <Pricing />
        </section>
        
        <section id="footer" className="min-h-[40vh] md:min-h-[50vh]">
          <Footer />
        </section>
      </main>
      
      {/* Componentes flutuantes */}
      <WhatsAppFloatPremium />
      <CookieBanner />
    </>
  )
}