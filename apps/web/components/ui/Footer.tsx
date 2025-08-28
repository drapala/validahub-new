import Link from 'next/link'
import { 
  Github, 
  Linkedin, 
  Twitter, 
  Mail, 
  Phone, 
  MapPin, 
  Building2,
  Shield,
  Award,
  CheckCircle2,
  Globe
} from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    produto: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'API Docs', href: '/docs/api' },
      { label: 'Status', href: '/status' },
      { label: 'Roadmap', href: '/roadmap' },
    ],
    empresa: [
      { label: 'Sobre', href: '/about' },
      { label: 'Blog', href: '/blog' },
      { label: 'Carreiras', href: '/careers' },
      { label: 'Parceiros', href: '/partners' },
      { label: 'Imprensa', href: '/press' },
    ],
    legal: [
      { label: 'Privacidade', href: '/privacy' },
      { label: 'Termos de Uso', href: '/terms' },
      { label: 'SLA', href: '/sla' },
      { label: 'LGPD', href: '/lgpd' },
      { label: 'Compliance', href: '/compliance' },
    ],
    suporte: [
      { label: 'Central de Ajuda', href: '/help' },
      { label: 'FAQ', href: '/faq' },
      { label: 'Integrações', href: '/integrations' },
      { label: 'Changelog', href: '/changelog' },
      { label: 'Status API', href: 'https://status.validahub.com' },
    ],
  }

  return (
    <footer className="border-t border-zinc-200/80 dark:border-zinc-800 bg-gradient-to-b from-white to-zinc-50 dark:from-zinc-950 dark:to-black">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        
        {/* Company Info Section */}
        <div className="mb-10 pb-8 border-b border-zinc-200/60 dark:border-zinc-800">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            {/* Brand & Description */}
            <div className="lg:col-span-1">
              <Link href="/" className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/20">
                  <CheckCircle2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-zinc-900 dark:text-white">ValidaHub</span>
              </Link>
              <p className="text-zinc-600 dark:text-zinc-400 mb-4 leading-relaxed">
                Plataforma líder em validação e correção inteligente de catálogos para marketplaces. 
                Reduza rejeições de 30% para menos de 3% com nossa tecnologia proprietária.
              </p>
              
              {/* Trust Badges */}
              <div className="flex flex-wrap gap-3">
                <div className="flex items-center gap-1 text-xs text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded-full">
                  <Shield className="w-3 h-3" />
                  <span>ISO 27001</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded-full">
                  <Award className="w-3 h-3" />
                  <span>LGPD Compliant</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-1 rounded-full">
                  <Globe className="w-3 h-3" />
                  <span>SOC 2 Type II</span>
                </div>
              </div>
            </div>

            {/* Company Legal Info */}
            <div className="lg:col-span-1">
              <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 flex items-center gap-2">
                <Building2 className="w-4 h-4 text-emerald-500" />
                Informações Legais
              </h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-zinc-500 dark:text-zinc-500 text-xs mb-1">Razão Social</p>
                  <p className="text-zinc-700 dark:text-zinc-300 font-medium">
                    Drapala Technology Solutions Ltda
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500 dark:text-zinc-500 text-xs mb-1">CNPJ</p>
                  <p className="text-zinc-700 dark:text-zinc-300 font-mono">
                    57.508.298/0001-62
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500 dark:text-zinc-500 text-xs mb-1">Endereço</p>
                  <p className="text-zinc-700 dark:text-zinc-300">
                    São Paulo, SP - Brasil
                  </p>
                </div>
              </div>
            </div>

            {/* Contact Info */}
            <div className="lg:col-span-1">
              <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 flex items-center gap-2">
                <Phone className="w-4 h-4 text-emerald-500" />
                Contato Direto
              </h3>
              <div className="space-y-3">
                <a 
                  href="mailto:contato@validahub.com" 
                  className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                >
                  <Mail className="w-4 h-4" />
                  <span>contato@validahub.com</span>
                </a>
                <a 
                  href="mailto:suporte@validahub.com" 
                  className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                >
                  <Mail className="w-4 h-4" />
                  <span>suporte@validahub.com</span>
                </a>
                <a 
                  href="https://wa.me/5511999999999" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  <span>WhatsApp Business</span>
                </a>
              </div>
              
              {/* Social Links */}
              <div className="flex items-center gap-3 mt-6">
                <a
                  href="https://github.com/drapala"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-400 hover:bg-emerald-500 hover:text-white dark:hover:bg-emerald-500 transition-all"
                  aria-label="GitHub"
                >
                  <Github className="w-4 h-4" />
                </a>
                <a
                  href="https://linkedin.com/company/validahub"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-400 hover:bg-emerald-500 hover:text-white dark:hover:bg-emerald-500 transition-all"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="w-4 h-4" />
                </a>
                <a
                  href="https://twitter.com/validahub"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-400 hover:bg-emerald-500 hover:text-white dark:hover:bg-emerald-500 transition-all"
                  aria-label="Twitter"
                >
                  <Twitter className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 mb-10">
          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Produto
            </h3>
            <ul className="space-y-3">
              {footerLinks.produto.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Empresa
            </h3>
            <ul className="space-y-3">
              {footerLinks.empresa.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Legal
            </h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Suporte
            </h3>
            <ul className="space-y-3">
              {footerLinks.suporte.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="pt-8 border-t border-zinc-200/60 dark:border-zinc-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-col md:flex-row items-center gap-2 md:gap-4 text-sm text-zinc-500 dark:text-zinc-400">
              <p className="font-medium">
                © {currentYear} Drapala Technology Solutions Ltda
              </p>
              <span className="hidden md:inline">•</span>
              <p>CNPJ: 57.508.298/0001-62</p>
              <span className="hidden md:inline">•</span>
              <p>Todos os direitos reservados</p>
            </div>
            
            {/* Compliance & Security */}
            <div className="flex items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
              <span className="flex items-center gap-1">
                <Shield className="w-3 h-3 text-green-500" />
                SSL Secured
              </span>
              <span className="flex items-center gap-1">
                <Award className="w-3 h-3 text-blue-500" />
                PCI DSS
              </span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                99.9% SLA
              </span>
            </div>
          </div>
          
          {/* Final disclaimer */}
          <div className="mt-6 text-center text-xs text-zinc-400 dark:text-zinc-500">
            <p>
              ValidaHub® é uma marca registrada da Drapala Technology Solutions Ltda. 
              Mercado Livre®, Amazon®, Shopee® são marcas registradas de suas respectivas empresas.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}