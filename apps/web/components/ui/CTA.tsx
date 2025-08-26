'use client'

import { useState } from 'react'
import { Button } from './button'
import { ArrowRight } from 'lucide-react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import AuthModal from './AuthModal'

export default function CTA() {
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const { data: session } = useSession()
  const router = useRouter()

  const handleStartNow = () => {
    if (session) {
      router.push('/upload')
    } else {
      setAuthModalOpen(true)
    }
  }

  return (
    <>
      <section className="py-20 bg-gradient-to-r from-green-500/10 via-gray-900 to-green-500/10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Pronto para validar seus catálogos com excelência?
            </h2>
            <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Junte-se a milhares de vendedores que já economizam horas de trabalho
              e publicam com confiança nos marketplaces.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={handleStartNow}
                className="min-w-[200px] bg-green-500 hover:bg-green-600 text-white font-semibold px-8 py-6 text-lg rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
              >
                Começar agora
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button
                size="lg"
                variant="outline"
                onClick={() => router.push('/pricing')}
                className="min-w-[200px] border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white font-semibold px-8 py-6 text-lg rounded-lg transition-all duration-200"
              >
                Ver planos
              </Button>
            </div>

            <div className="mt-12 flex flex-wrap justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Sem cartão de crédito</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Cancelamento a qualquer momento</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Suporte em português</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode="signup"
        onModeChange={() => {}}
      />
    </>
  )
}