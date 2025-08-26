import { Upload, CheckCircle, Download } from 'lucide-react'

export default function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: 'Faça upload do CSV',
      description: 'Envie seu arquivo CSV com os produtos do marketplace. Suportamos arquivos de até 100MB com milhões de linhas.',
      number: '01'
    },
    {
      icon: CheckCircle,
      title: 'Valide e corrija com regras do marketplace',
      description: 'Nossa engine valida cada campo usando regras específicas do marketplace e sugere correções automáticas.',
      number: '02'
    },
    {
      icon: Download,
      title: 'Exporte e publique',
      description: 'Baixe o arquivo corrigido pronto para publicação ou envie diretamente via API para o marketplace.',
      number: '03'
    }
  ]

  return (
    <section id="how-it-works" className="py-20 bg-gray-800/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Como funciona
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Três passos simples para validar e corrigir seus catálogos de produtos
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connection line for desktop */}
          <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-green-500/20 via-green-500/40 to-green-500/20" />
          
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <div key={index} className="relative">
                <div className="bg-gray-900 rounded-xl p-8 border border-gray-700 hover:border-green-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/10">
                  {/* Step number */}
                  <div className="absolute -top-4 -right-4 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {step.number}
                  </div>
                  
                  {/* Icon */}
                  <div className="w-16 h-16 bg-green-500/10 rounded-lg flex items-center justify-center mb-6">
                    <Icon className="w-8 h-8 text-green-400" />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}