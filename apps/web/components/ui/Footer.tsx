import Link from 'next/link'
import { Github, Linkedin, Twitter } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    produto: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '/pricing' },
      { label: 'FAQ', href: '/faq' },
      { label: 'Docs', href: '/docs' },
    ],
    empresa: [
      { label: 'Sobre', href: '/about' },
      { label: 'Blog', href: '/blog' },
      { label: 'Carreiras', href: '/careers' },
      { label: 'Contato', href: 'mailto:contato@validahub.com' },
    ],
    legal: [
      { label: 'Privacidade', href: '/privacy' },
      { label: 'Termos', href: '/terms' },
      { label: 'SLA', href: '/sla' },
      { label: 'Status', href: '/status' },
    ],
    recursos: [
      { label: 'API Docs', href: '/docs/api' },
      { label: 'Integrações', href: '/integrations' },
      { label: 'Changelog', href: '/changelog' },
      { label: 'Suporte', href: 'mailto:suporte@validahub.com' },
    ],
  }

  return (
    <footer className="border-t border-gray-800">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          {/* Logo and description */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center space-x-2 text-white font-bold text-xl mb-4">
              <svg className="w-8 h-8 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
              </svg>
              <span>ValidaHub</span>
            </Link>
            <p className="text-gray-400 text-sm mb-4">
              Validação inteligente de catálogos para marketplaces brasileiros.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com/validahub"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/validahub"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/validahub"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links sections */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Produto
            </h3>
            <ul className="space-y-2">
              {footerLinks.produto.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Empresa
            </h3>
            <ul className="space-y-2">
              {footerLinks.empresa.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Legal
            </h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">
              Recursos
            </h3>
            <ul className="space-y-2">
              {footerLinks.recursos.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="text-center space-y-2">
            <p className="text-gray-400 text-sm">
              © {currentYear} ValidaHub. Todos os direitos reservados.
            </p>
            <p className="text-gray-500 text-xs">
              Drapala Technology Solutions Ltda | CNPJ: 57.508.298/0001-62
            </p>
            <p className="text-gray-500 text-sm">
              Feito com 💚 no Brasil
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}