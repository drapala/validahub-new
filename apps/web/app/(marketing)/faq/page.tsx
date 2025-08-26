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
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Perguntas Frequentes
          </h1>
          <p className="text-gray-400 text-lg max-w-3xl mx-auto">
            Encontre respostas para as dúvidas mais comuns sobre o ValidaHub
          </p>
        </div>
      </div>
      <FAQ />
      <Footer />
    </main>
  )
}