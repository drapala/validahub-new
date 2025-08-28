'use client'

export default function HeroUltra() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/[0.01] bg-[size:80px_80px]" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-green-500/10 rounded-full blur-3xl" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white tracking-tight mb-6">
            Cada produto rejeitado custa
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400"> R$127/dia </span>
            em vendas perdidas
          </h1>

          <p className="text-lg sm:text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            <span className="text-white font-semibold">3 milhões de sellers no Brasil</span> perdem 
            16h/mês corrigindo planilhas manualmente. Enquanto você lê isso, seus concorrentes 
            já validaram e publicaram com ValidaHub.
          </p>
          
          <div className="mb-16 bg-black/30 border border-gray-700 max-w-2xl mx-auto rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="text-sm text-gray-500">Erro detectado:</p>
                  <p className="text-white font-semibold">Título > 60 caracteres</p>
                </div>
              </div>
              <svg className="w-5 h-5 text-gray-600 mx-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm text-gray-500">ValidaHub:</p>
                  <p className="text-green-400 font-semibold">Corrigido automaticamente</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => document.querySelector('[data-section="data"]')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
              className="relative min-w-[250px] px-8 py-4 font-bold text-white bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 rounded-lg transition-transform duration-200 hover:scale-[1.02] flex items-center justify-center group"
            >
              Validar CSV agora (grátis)
              <svg className="ml-2 w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
            
            <button
              onClick={() => document.querySelector('[data-section="calculator"]')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
              className="min-w-[250px] px-8 py-4 font-medium border border-red-500/50 text-red-300 hover:bg-red-500/10 rounded-lg transition-colors duration-200"
            >
              Calcular meu prejuízo agora
            </button>
          </div>

          <div className="mt-16 flex flex-col sm:flex-row gap-8 justify-center items-center text-gray-500">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-white font-semibold">30 segundos para validar</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-white font-semibold">1.247 sellers já testaram</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-white font-semibold">{'<'}3% de rejeição garantida</span>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>
  )
}