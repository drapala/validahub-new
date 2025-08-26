import Footer from '@/components/ui/Footer'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Termos de Serviço - ValidaHub',
  description: 'Termos de Serviço do ValidaHub. Entenda as condições de uso da plataforma.',
}

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-gray-900 pt-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold text-white mb-8">Termos de Serviço</h1>
        
        <div className="prose prose-invert prose-gray max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Aceitação dos Termos</h2>
            <p className="text-gray-400 mb-4">
              Ao usar o ValidaHub, você concorda com estes Termos de Serviço. Se não concordar, 
              não utilize nossos serviços.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Descrição do Serviço</h2>
            <p className="text-gray-400 mb-4">
              O ValidaHub oferece serviços de validação e correção de catálogos CSV para marketplaces, incluindo:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Validação com regras específicas por marketplace</li>
              <li>Correção automática de erros comuns</li>
              <li>Exportação de arquivos corrigidos</li>
              <li>APIs e webhooks para integração</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Uso Aceitável</h2>
            <p className="text-gray-400 mb-4">
              Você concorda em:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Fornecer informações precisas e atualizadas</li>
              <li>Manter a confidencialidade de suas credenciais</li>
              <li>Não usar o serviço para atividades ilegais</li>
              <li>Não tentar comprometer a segurança do sistema</li>
              <li>Respeitar os limites de uso do seu plano</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Pagamento e Cobrança</h2>
            <p className="text-gray-400 mb-4">
              Para planos pagos:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Cobrança mensal ou anual conforme escolhido</li>
              <li>Renovação automática até cancelamento</li>
              <li>Sem reembolso parcial por cancelamento</li>
              <li>Preços sujeitos a alteração com 30 dias de aviso</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Propriedade Intelectual</h2>
            <p className="text-gray-400 mb-4">
              Você mantém todos os direitos sobre seus dados. O ValidaHub mantém direitos sobre:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Software e algoritmos da plataforma</li>
              <li>Regras de validação proprietárias</li>
              <li>Marca e identidade visual</li>
              <li>Documentação e conteúdo do site</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Garantias e Limitações</h2>
            <p className="text-gray-400 mb-4">
              O ValidaHub é fornecido "como está". Não garantimos:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Disponibilidade ininterrupta do serviço</li>
              <li>Ausência total de erros</li>
              <li>Adequação para fins específicos</li>
            </ul>
            <p className="text-gray-400 mt-4">
              Nossa responsabilidade é limitada ao valor pago nos últimos 12 meses.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">7. Cancelamento</h2>
            <p className="text-gray-400 mb-4">
              Você pode cancelar sua assinatura a qualquer momento. Após cancelamento:
            </p>
            <ul className="list-disc list-inside text-gray-400 space-y-2 ml-4">
              <li>Acesso continua até o fim do período pago</li>
              <li>Dados são mantidos por 30 dias</li>
              <li>Exclusão permanente após período de retenção</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">8. Alterações nos Termos</h2>
            <p className="text-gray-400">
              Podemos atualizar estes termos. Alterações significativas serão notificadas com 
              30 dias de antecedência. O uso continuado após alterações implica aceitação.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">9. Foro</h2>
            <p className="text-gray-400">
              Estes termos são regidos pelas leis brasileiras. Fica eleito o foro da 
              comarca de São Paulo/SP para dirimir questões.
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