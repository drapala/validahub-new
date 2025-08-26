import Pricing from '@/components/ui/Pricing'
import Footer from '@/components/ui/Footer'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Planos e Preços - ValidaHub',
  description: 'Escolha o plano ideal para validar seus catálogos. Planos flexíveis para pequenos vendedores e grandes empresas.',
}

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-gray-900 pt-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Planos e Preços
          </h1>
          <p className="text-gray-400 text-lg max-w-3xl mx-auto">
            Escolha o plano que melhor se adapta ao seu negócio. 
            Todos os planos incluem acesso completo à plataforma e suporte em português.
          </p>
        </div>
      </div>
      <Pricing />
      <Footer />
    </main>
  )
}