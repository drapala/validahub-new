import { ArrowRight, Check, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

// Server Component - sem client-side JS pesado
export default function HeroOptimized() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background com CSS puro */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900 via-gray-900 to-black">
        <div className="absolute inset-0 bg-grid-white/[0.01] bg-[size:80px_80px]" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-5xl mx-auto">
          {/* Título com animação CSS */}
          <h1 className="hero-title text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold text-white mb-4">
            <span className="text-red-400">R$127/dia</span> jogados fora
          </h1>
          
          <h2 className="hero-subtitle text-4xl sm:text-5xl md:text-6xl font-bold text-gray-400 mb-8">
            com rejeições de produtos nos marketplaces
          </h2>

          <p className="hero-description text-lg sm:text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
            <span className="text-white font-semibold">3 milhões de sellers</span> perdem vendas todo dia
            por erros bestas no cadastro. <span className="text-green-400 font-semibold">ValidaHub corrige tudo em 1 clique.</span>
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button
              size="lg"
              className="hero-cta-primary group relative px-8 py-6 text-lg font-bold bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white shadow-2xl transition-all duration-200 hover:scale-105"
            >
              Validar CSV agora (grátis)
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>

            <Button
              size="lg"
              variant="outline"
              className="hero-cta-secondary px-8 py-6 text-lg border-2 border-gray-600 hover:border-gray-500 text-gray-300 hover:text-white transition-all duration-200"
            >
              Calcular meu ROI
            </Button>
          </div>

          {/* Trust badges - sem animação complexa */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <div className="flex items-center gap-2 text-gray-400">
              <Check className="w-5 h-5 text-green-400" />
              <span>1.247 sellers ativos</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <Check className="w-5 h-5 text-green-400" />
              <span>{'<'}3% de rejeição garantida</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <Check className="w-5 h-5 text-green-400" />
              <span>Setup em 15 minutos</span>
            </div>
          </div>

          {/* Erro ticker simplificado */}
          <div className="mt-12 inline-flex items-center gap-3 px-6 py-3 bg-red-900/20 border border-red-500/30 rounded-full">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300">
              Título &gt; 60 caracteres • 
              <span className="text-white font-semibold ml-2">Corrigido automaticamente</span>
            </span>
          </div>
        </div>
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .hero-title {
          animation: fadeInUp 0.6s ease-out;
        }

        .hero-subtitle {
          animation: fadeInUp 0.6s ease-out 0.3s backwards;
        }

        .hero-description {
          animation: fadeInUp 0.6s ease-out 0.6s backwards;
        }

        .hero-cta-primary {
          animation: fadeInUp 0.6s ease-out 0.9s backwards;
        }

        .hero-cta-secondary {
          animation: fadeInUp 0.6s ease-out 1s backwards;
        }
      `}</style>
    </section>
  )
}