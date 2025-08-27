import Hero from '@/components/ui/HeroPerformance'
import dynamic from 'next/dynamic'

const LazyComponents = dynamic(() => import('./LazyComponentsPerformance'), {
  ssr: false,
  loading: () => null
})

export default function LandingPage() {
  return (
    <>
      <main className="bg-gradient-to-b from-gray-900 via-gray-900 to-black">
        <section className="min-h-screen scroll-mt-20" data-section="hero">
          <Hero />
        </section>
        
        <LazyComponents />
      </main>
    </>
  )
}