import FAQ from '@/components/ui/FAQ'
import Footer from '@/components/ui/Footer'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Perguntas Frequentes - ValidaHub',
  description: 'Tire suas dúvidas sobre a plataforma ValidaHub. Como funciona, segurança, integrações e muito mais.',
}

export default function FAQPage() {
  return (
    <main className="min-h-screen bg-gray-900 pt-20">
      <FAQ />
      <Footer />
    </main>
  )
}