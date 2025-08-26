import Hero from '@/components/ui/Hero'
import SocialProof from '@/components/ui/SocialProof'
import HowItWorks from '@/components/ui/HowItWorks'
import Features from '@/components/ui/Features'
import Pricing from '@/components/ui/Pricing'
import FAQ from '@/components/ui/FAQ'
import CTA from '@/components/ui/CTA'
import Footer from '@/components/ui/Footer'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-900">
      <Hero />
      <SocialProof />
      <HowItWorks />
      <Features />
      <Pricing />
      <FAQ />
      <CTA />
      <Footer />
    </main>
  )
}