'use client'

import { Shield, AlertTriangle, CheckCircle, X } from 'lucide-react'

export default function ERPComparison() {
  return (
    <section className="py-24 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-6xl mx-auto">
          {/* Section header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/20 rounded-full mb-6">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-yellow-400 font-medium">
                A verdade que ninguém te conta
              </span>
            </div>
            
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
              ERPs <span className="text-red-400">integram</span>, mas 
              <span className="text-red-500"> não protegem</span>
            </h2>
            
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Bling, Tiny, Linx... Todos prometem integração com marketplaces. 
              <span className="text-white font-semibold"> Mas nenhum valida seus produtos antes do envio.</span>
            </p>
          </div>

          {/* Comparison grid */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* ERP Column */}
            <div className="bg-gradient-to-b from-red-950/20 to-red-950/10 border border-red-500/20 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
                  <X className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">ERP Tradicional</h3>
                  <p className="text-sm text-gray-400">O que você tem hoje</p>
                </div>
              </div>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <X className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">Envia direto sem validar</strong> - 
                    Descobre o erro quando já é tarde
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <X className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">Genérico para todos marketplaces</strong> - 
                    Ignora regras específicas de cada um
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <X className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">R$400-2000/mês</strong> - 
                    Para funcionalidades que você não usa
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <X className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">Suporte via ticket</strong> - 
                    48h para responder "não é conosco"
                  </span>
                </li>
              </ul>
            </div>

            {/* ValidaHub Column */}
            <div className="bg-gradient-to-b from-green-950/20 to-green-950/10 border border-green-500/20 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">ValidaHub + ERP</h3>
                  <p className="text-sm text-green-400">A proteção que faltava</p>
                </div>
              </div>
              
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">Valida ANTES do envio</strong> - 
                    Detecta e corrige os 47 erros fatais
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">Regras específicas por marketplace</strong> - 
                    MELI, Amazon, Magalu, cada um com suas regras
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">R$0-297/mês</strong> - 
                    ROI positivo desde o primeiro mês
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                  <span className="text-gray-300">
                    <strong className="text-white">API e Webhooks</strong> - 
                    Integra com qualquer ERP em 15 minutos
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="text-center bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-2xl p-8">
            <p className="text-2xl font-bold text-white mb-2">
              Seu ERP é o carro. ValidaHub é o airbag.
            </p>
            <p className="text-lg text-gray-400">
              Você não para de dirigir porque tem airbag. Você dirige mais tranquilo.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}