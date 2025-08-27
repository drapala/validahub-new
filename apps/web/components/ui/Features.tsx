'use client'

import { useState } from 'react'
import { 
  Shield, 
  Zap, 
  AlertTriangle, 
  GitBranch, 
  Link, 
  History,
  Globe,
  Cpu,
  Lock,
  DollarSign,
  ArrowRight,
  Info
} from 'lucide-react'
import { Button } from './button'
import { useRouter } from 'next/navigation'

export default function Features() {
  const router = useRouter()
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null)
  
  const errorExamples = [
    'Título com mais de 60 caracteres',
    'Preço sem casas decimais corretas',
    'GTIN/EAN com dígito verificador inválido',
    'Categoria não mapeada para o marketplace',
    'Imagem com resolução menor que 500x500px',
    'SKU duplicado no catálogo',
    'Atributos obrigatórios vazios',
    'Unidade de medida incorreta',
    'Descrição com HTML não permitido',
    'Estoque negativo ou inválido'
  ]
  
  const features = [
    {
      icon: AlertTriangle,
      title: 'Detecta os 47 erros fatais do MELI',
      description: 'Para de perder vendas por "título muito longo", "categoria errada", "EAN inválido" e outros 44 erros bestas que você nem sabia que existiam.',
      benefit: 'De 30% → menos de 3% de rejeição',
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      hasExamples: true
    },
    {
      icon: Zap,
      title: 'Corrige antes da rejeição',
      description: 'Não espera o marketplace rejeitar. Corrige títulos, formata preços, valida atributos e ajusta tudo ANTES de você enviar.',
      benefit: 'Zero retrabalho',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10'
    },
    {
      icon: Shield,
      title: 'Regras específicas por marketplace',
      description: 'MELI tem uma regra, Amazon tem outra, Magalu tem a dela. ValidaHub conhece TODAS e aplica a certa pro lugar certo.',
      benefit: 'Publicação garantida',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10'
    },
    {
      icon: Link,
      title: 'API pronta pro seu ERP',
      description: 'Integra em 15 minutos com Bling, Tiny, Linx ou qualquer sistema. Webhooks prontos, documentação clara, suporte real.',
      benefit: 'Setup em 15 minutos',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'
    },
    {
      icon: History,
      title: 'Histórico pra auditoria LGPD',
      description: 'Cada validação fica gravada. Quem validou, quando, o que mudou. Seu jurídico dorme tranquilo, você também.',
      benefit: 'Compliance garantido',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    {
      icon: DollarSign,
      title: 'ROI desde o primeiro mês',
      description: 'Custa menos que 1 produto rejeitado. Economiza 16h/mês. Faz a conta: você ganha dinheiro usando ValidaHub.',
      benefit: 'Lucro de R$2.034+/mês',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10'
    }
  ]

  return (
    <section 
      id="features" 
      className="scroll-mt-20 py-24 pb-20 relative"
      data-section="features"
      aria-label="Benefícios que importam">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500/8 to-emerald-500/8 border border-green-500/20 rounded-full mb-6">
            <Zap className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Benefícios que importam
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
            Não vendemos features.
            <span className="block text-green-400">Vendemos vendas.</span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Cada feature do ValidaHub existe por um único motivo: 
            <span className="text-white font-semibold"> fazer você vender mais, perder menos.</span>
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
                  <div 
                    className="relative"
                    onMouseEnter={() => feature.hasExamples && setHoveredFeature(index)}
                    onMouseLeave={() => setHoveredFeature(null)}
                  >
                    <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                      {feature.title}
                      {feature.hasExamples && (
                        <Info className="w-4 h-4 text-gray-500 cursor-help" />
                      )}
                    </h3>
                    
                    {/* Tooltip with error examples */}
                    {feature.hasExamples && hoveredFeature === index && (
                      <div className="absolute z-50 top-full left-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-xl">
                        <p className="text-sm font-semibold text-white mb-3">Exemplos dos 47 erros detectados:</p>
                        <ul className="space-y-2">
                          {errorExamples.slice(0, 5).map((error, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-xs text-gray-300">
                              <span className="text-red-400 mt-0.5">•</span>
                              {error}
                            </li>
                          ))}
                        </ul>
                        <p className="text-xs text-gray-500 mt-3">...e mais 42 erros validados automaticamente</p>
                      </div>
                    )}
                  </div>
                  
                  <p className="text-gray-400 leading-relaxed mb-4">
                    {feature.description}
                  </p>
                  
                  {/* Benefit Badge */}
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-semibold text-green-400">
                      {feature.benefit}
                    </span>
                  </div>
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
        
        {/* CTA Intermediário */}
        <div className="mt-16 text-center">
          <p className="text-2xl font-bold text-white mb-4">
            Para de vender features. Comece a vender mais.
          </p>
          <Button
            onClick={() => router.push('/upload')}
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30 group"
          >
            Validar grátis agora
            <ArrowRight className="inline ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </div>
    </section>
  )
}