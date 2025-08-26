import { 
  Shield, 
  Zap, 
  Code, 
  GitBranch, 
  Link, 
  History,
  Globe,
  Cpu,
  Lock
} from 'lucide-react'

export default function Features() {
  const features = [
    {
      icon: Shield,
      title: 'Regras por categoria',
      description: 'Validação específica para MELI, Amazon, B2W, Magazine Luiza e outros marketplaces brasileiros.',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'
    },
    {
      icon: Zap,
      title: 'Correções automáticas',
      description: 'Sistema inteligente que corrige automaticamente erros comuns e padroniza formatos.',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10'
    },
    {
      icon: Code,
      title: 'Validações avançadas',
      description: 'Suporte a enum, regex, decimal-BR, datas, CPF/CNPJ e validações customizadas.',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    {
      icon: GitBranch,
      title: 'Engine YAML versionada',
      description: 'Políticas de validação versionadas em YAML com histórico completo de mudanças.',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10'
    },
    {
      icon: History,
      title: 'Job History',
      description: 'Histórico completo de processamentos com links assinados para download dos resultados.',
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10'
    },
    {
      icon: Link,
      title: 'Webhooks & Connectors',
      description: 'Integração via webhooks e conectores nativos para automação completa do fluxo.',
      color: 'text-pink-400',
      bgColor: 'bg-pink-500/10'
    }
  ]

  return (
    <section id="features" className="py-20 bg-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Features poderosas para seu negócio
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Tudo que você precisa para validar e publicar seus produtos nos marketplaces
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="group relative bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300 hover:shadow-xl hover:shadow-black/20"
              >
                {/* Gradient effect on hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-green-500/0 via-green-500/5 to-green-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
                
                <div className="relative">
                  {/* Icon */}
                  <div className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4`}>
                    <Icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        {/* Additional features grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: Globe, label: 'Multi-marketplace' },
            { icon: Cpu, label: 'Processamento rápido' },
            { icon: Lock, label: 'Dados seguros' },
            { icon: History, label: 'Auditoria completa' },
          ].map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-center space-x-2 bg-gray-800/30 rounded-lg py-3 px-4 border border-gray-700/50"
            >
              <item.icon className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-300">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}