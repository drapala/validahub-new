'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

export default function FAQ() {
  const [openItems, setOpenItems] = useState<number[]>([])

  const toggleItem = (index: number) => {
    setOpenItems(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  const faqs = [
    {
      question: 'Como vocês validam cada marketplace?',
      answer: 'Mantemos um banco de dados atualizado com as regras de cada marketplace brasileiro. Nossa equipe monitora constantemente mudanças nas políticas e atualiza as regras automaticamente. Cada marketplace tem validações específicas para categorias, atributos obrigatórios, formatos de dados e limites de caracteres.'
    },
    {
      question: 'Meus dados ficam seguros na plataforma?',
      answer: 'Sim! Utilizamos criptografia AES-256 para dados em repouso e TLS 1.3 para dados em trânsito. Todos os arquivos são processados em ambientes isolados e deletados automaticamente após 30 dias. Somos certificados ISO 27001 e seguimos as diretrizes da LGPD.'
    },
    {
      question: 'Posso integrar com meu sistema ERP?',
      answer: 'Sim, oferecemos uma API REST completa e webhooks para integração com qualquer sistema. Temos integrações nativas com os principais ERPs do mercado como SAP, TOTVS, e Bling. Para o plano Enterprise, podemos desenvolver conectores customizados.'
    },
    {
      question: 'Quanto tempo leva para validar um arquivo?',
      answer: 'Arquivos de até 10.000 linhas são processados instantaneamente. Para arquivos maiores, o processamento é assíncrono e leva em média 1 minuto para cada 100.000 linhas. Você recebe uma notificação por email quando o processamento termina.'
    },
    {
      question: 'Vocês corrigem os erros automaticamente?',
      answer: 'Sim! Nossa IA identifica e corrige automaticamente erros comuns como: formatação de preços, padronização de medidas, correção de categorias, ajuste de caracteres especiais e normalização de descrições. Você sempre pode revisar e aprovar as correções antes de exportar.'
    },
    {
      question: 'Qual a diferença entre os planos?',
      answer: 'O plano Starter é ideal para pequenos vendedores com até 100 validações mensais. O Pro atende empresas médias com validações ilimitadas e recursos avançados como API e webhooks. O Enterprise é personalizado para grandes operações com SLA garantido, ambientes dedicados e suporte 24/7.'
    }
  ]

  return (
    <section id="faq" className="py-20 bg-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Perguntas frequentes
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Tire suas dúvidas sobre o ValidaHub
          </p>
        </div>

        <div className="max-w-3xl mx-auto">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden transition-all duration-200 hover:border-gray-600"
              >
                <button
                  onClick={() => toggleItem(index)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-800/50 transition-colors"
                >
                  <span className="text-white font-medium pr-4">{faq.question}</span>
                  {openItems.includes(index) ? (
                    <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  )}
                </button>
                
                <div
                  className={`px-6 transition-all duration-300 ${
                    openItems.includes(index) ? 'py-4' : 'max-h-0 overflow-hidden'
                  }`}
                >
                  <p className="text-gray-400 leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-400 mb-4">
              Ainda tem dúvidas?
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/docs"
                className="inline-flex items-center justify-center px-6 py-3 border border-gray-600 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors"
              >
                Consultar documentação
              </a>
              <a
                href="mailto:suporte@validahub.com"
                className="inline-flex items-center justify-center px-6 py-3 bg-green-500 hover:bg-green-600 rounded-lg text-white font-semibold transition-colors"
              >
                Falar com suporte
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}