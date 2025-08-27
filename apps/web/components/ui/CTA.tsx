'use client'

import { useState } from 'react'
import { Button } from './button'
import { ArrowRight } from 'lucide-react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
// AuthModal is temporarily commented out
// import { AuthModal } from '@/components/blocks/AuthModal'

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
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
              A escolha é simples:
            </h2>
            <p className="text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              <span className="text-red-400 font-semibold">Continuar perdendo R$3.810/mês</span> em vendas
              <br />ou <span className="text-green-400 font-semibold">investir R$97/mês</span> e lucrar.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={handleStartNow}
                className="min-w-[300px] bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold px-10 py-7 text-xl rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
              >
                Validar CSV mais problemático agora
                <ArrowRight className="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>

            <div className="mt-12 flex flex-wrap justify-center gap-8 text-base">
              <div className="flex items-center gap-2 text-white font-semibold">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>1.000 validações grátis</span>
              </div>
              <div className="flex items-center gap-2 text-white font-semibold">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>30 dias de garantia</span>
              </div>
              <div className="flex items-center gap-2 text-white font-semibold">
                <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Resultado em 30 segundos</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AuthModal temporarily disabled
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode="signup"
        onModeChange={() => {}}
      /> */}
    </>
  )
}