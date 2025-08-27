'use client'

import dynamic from 'next/dynamic'
import { useInView } from 'react-intersection-observer'

const ROICalculator = dynamic(() => import('@/components/ui/ROICalculator'), {
  loading: () => <div className="min-h-screen" />
})

const SocialProofCondensed = dynamic(() => import('@/components/ui/SocialProofCondensed'), {
  loading: () => <div className="min-h-[80vh]" />
})

const DataProof = dynamic(() => import('@/components/ui/DataProof'), {
  loading: () => <div className="min-h-screen" />
})

const FeaturesAccordion = dynamic(() => import('@/components/ui/FeaturesAccordion'), {
  loading: () => <div className="min-h-screen" />
})

const Pricing = dynamic(() => import('@/components/ui/Pricing'), {
  loading: () => <div className="min-h-screen" />
})

const Footer = dynamic(() => import('@/components/ui/Footer'), {
  loading: () => <div className="min-h-[50vh]" />
})

const StickyPromoBar = dynamic(() => import('@/components/ui/StickyPromoBar'))
const CookieConsent = dynamic(() => import('@/components/ui/CookieConsent'))

function LazySection({ children, className, dataSection }: any) {
  const { ref, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
    rootMargin: '100px'
  })
  
  return (
    <section ref={ref} className={className} data-section={dataSection}>
      {inView ? children : <div className={className.includes('min-h-') ? className : 'min-h-screen'} />}
    </section>
  )
}

export default function LazyComponentsPerformance() {
  return (
    <>
      <LazySection className="min-h-[80vh] md:min-h-screen scroll-mt-24" dataSection="calculator">
        <ROICalculator />
      </LazySection>
      
      <LazySection className="min-h-[60vh] md:min-h-[80vh] scroll-mt-20" dataSection="social">
        <SocialProofCondensed />
      </LazySection>
      
      <LazySection className="min-h-[80vh] md:min-h-screen scroll-mt-20" dataSection="data">
        <DataProof />
      </LazySection>
      
      <LazySection className="min-h-[80vh] md:min-h-screen scroll-mt-20" dataSection="features">
        <FeaturesAccordion />
      </LazySection>
      
      <LazySection className="min-h-[90vh] md:min-h-screen scroll-mt-20" dataSection="pricing">
        <Pricing />
      </LazySection>
      
      <LazySection className="min-h-[40vh] md:min-h-[50vh] scroll-mt-20" dataSection="footer">
        <Footer />
      </LazySection>
      
      <StickyPromoBar />
      <CookieConsent />
    </>
  )
}