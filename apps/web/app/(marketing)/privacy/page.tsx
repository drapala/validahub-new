import Footer from '@/components/ui/Footer'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Política de Privacidade - ValidaHub',
  description: 'Política de Privacidade do ValidaHub. Entenda como coletamos, usamos e protegemos seus dados.',
}

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-gray-900 pt-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold text-white mb-8">Política de Privacidade</h1>
        
        <div className="prose prose-invert prose-gray max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Informações que Coletamos</h2>
            <p className="text-gray-400 mb-4">
              O ValidaHub coleta informações necessárias para fornecer nossos serviços de validação de catálogos:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Dados de conta: nome, email, empresa</li>
              <li>Arquivos CSV enviados para validação</li>
              <li>Logs de uso e métricas de desempenho</li>
              <li>Informações de pagamento (processadas via parceiros seguros)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Como Usamos suas Informações</h2>
            <p className="text-gray-400 mb-4">
              Utilizamos suas informações exclusivamente para:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Processar e validar seus arquivos CSV</li>
              <li>Melhorar nossos algoritmos de validação</li>
              <li>Fornecer suporte técnico</li>
              <li>Enviar notificações sobre o status dos processamentos</li>
              <li>Cumprir obrigações legais</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Segurança dos Dados</h2>
            <p className="text-gray-400 mb-4">
              Implementamos medidas rigorosas de segurança:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Criptografia AES-256 para dados em repouso</li>
              <li>TLS 1.3 para dados em trânsito</li>
              <li>Ambientes isolados para processamento</li>
              <li>Exclusão automática de arquivos após 30 dias</li>
              <li>Conformidade com LGPD</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Compartilhamento de Dados</h2>
            <p className="text-gray-400 mb-4">
              Não vendemos, alugamos ou compartilhamos seus dados com terceiros, exceto:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Com seu consentimento explícito</li>
              <li>Para cumprir obrigações legais</li>
              <li>Com processadores de pagamento certificados</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Seus Direitos</h2>
            <p className="text-gray-400 mb-4">
              Conforme a LGPD, você tem direito a:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Acessar seus dados pessoais</li>
              <li>Corrigir dados incorretos</li>
              <li>Solicitar exclusão de dados</li>
              <li>Portabilidade dos dados</li>
              <li>Revogar consentimento</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Contato</h2>
            <p className="text-gray-400">
              Para questões sobre privacidade, entre em contato: <br />
              Email: privacidade@validahub.com <br />
              DPO: João Silva - dpo@validahub.com
            </p>
          </section>

          <section className="mb-8">
            <p className="text-gray-500 text-sm">
              Última atualização: Janeiro de 2025
            </p>
          </section>
        </div>
      </div>
      <Footer />
    </main>
  )
}