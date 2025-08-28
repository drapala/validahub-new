'use client'

import { motion } from 'framer-motion'
import { Trophy, TrendingUp, Shield, Star, Quote, ArrowRight } from 'lucide-react'
import { Button } from './button'

export default function SocialProofCondensed() {
  
  const stats = [
    { value: '1.247', label: 'Sellers ativos', icon: TrendingUp, color: 'text-green-400' },
    { value: '2.9%', label: 'Taxa de rejeição', icon: Shield, color: 'text-blue-400' },
    { value: '4.9/5', label: 'Nota média', icon: Star, color: 'text-yellow-400' },
  ]
  
  const testimonials = [
    {
      name: 'Carlos Eduardo',
      company: 'Magazine Luiza',
      quote: 'Redução de 92% no tempo de correção. Vendas subiram 18% em 2 meses.',
      metric: '+R$ 47k/mês',
    },
    {
      name: 'Ana Silva',
      company: 'Netshoes',
      quote: 'Antes 3 dias corrigindo CSVs. Agora 30 segundos com ValidaHub.',
      metric: 'ROI em 7 dias',
    }
  ]

  return (
    <section className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-green-950/5 to-transparent" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Main headline */}
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-6">
            <Trophy className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Resultados comprovados
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4">
            7 das 10 maiores agências
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
              já migraram para ValidaHub
            </span>
          </h2>
        </motion.div>

        {/* Stats Grid */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {stats.map((stat, idx) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={idx}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 + idx * 0.1 }}
                className="bg-gray-900/50 border border-gray-700 rounded-2xl p-6 text-center hover:border-green-500/30 transition-all"
              >
                <Icon className={`w-10 h-10 ${stat.color} mx-auto mb-3`} />
                <div className="text-4xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Testimonials Row */}
        <motion.div 
          className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {testimonials.map((testimonial, idx) => (
            <motion.div
              key={idx}
              initial={{ x: idx === 0 ? -20 : 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.6 + idx * 0.1 }}
              className="bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-700 rounded-2xl p-6 relative hover:border-green-500/30 transition-all"
            >
              <Quote className="absolute top-4 right-4 w-8 h-8 text-green-400/20" />
              <p className="text-gray-300 mb-4 italic">
                "{testimonial.quote}"
              </p>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">{testimonial.name}</div>
                  <div className="text-sm text-gray-400">{testimonial.company}</div>
                </div>
                <div className="text-2xl font-bold text-green-400">
                  {testimonial.metric}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <p className="text-xl text-gray-400 mb-6">
            Enquanto você lê isso, seus concorrentes já validaram 
            <span className="text-white font-semibold"> 47 CSVs sem erros.</span>
          </p>
          <Button
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20 group"
          >
            Ver demonstração ao vivo
            <ArrowRight className="inline ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </motion.div>
      </div>
    </section>
  )
}