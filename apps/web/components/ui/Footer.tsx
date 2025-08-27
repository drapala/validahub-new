import Link from 'next/link'
import { Github, Linkedin, Twitter } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    produto: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'API Docs', href: '/docs/api' },
      { label: 'Status', href: '/status' },
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
      { label: 'LGPD', href: '/lgpd' },
    ],
    suporte: [
      { label: 'FAQ', href: '/faq' },
      { label: 'Integrações', href: '/integrations' },
      { label: 'Changelog', href: '/changelog' },
      { label: 'Suporte', href: 'mailto:suporte@validahub.com' },
    ],
  }

  return (
    <footer className="border-t border-zinc-200/80 dark:border-zinc-800 bg-white/60 dark:bg-zinc-950/80 backdrop-blur-sm">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8 md:py-10">
        {/* Links Grid - mais compacto */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-3 text-sm">
          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-3 text-sm">
              Produto
            </h3>
            <ul className="space-y-2">
              {footerLinks.produto.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors leading-tight"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-3 text-sm">
              Empresa
            </h3>
            <ul className="space-y-2">
              {footerLinks.empresa.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors leading-tight"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-3 text-sm">
              Legal
            </h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors leading-tight"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-zinc-900 dark:text-white font-semibold mb-3 text-sm">
              Suporte
            </h3>
            <ul className="space-y-2">
              {footerLinks.suporte.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors leading-tight"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section - mais compacto */}
        <div className="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2
                        border-t border-zinc-200/70 dark:border-zinc-800 pt-4 text-sm text-zinc-500 dark:text-zinc-400">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            {/* Logo compacto */}
            <Link href="/" className="flex items-center gap-2 text-zinc-900 dark:text-white font-bold">
              <svg className="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
              </svg>
              <span>ValidaHub</span>
            </Link>
            <span className="hidden sm:inline text-zinc-400 dark:text-zinc-600">•</span>
            <p>© {currentYear} Todos os direitos reservados</p>
          </div>
          
          {/* Social icons */}
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/validahub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-4 h-4" />
            </a>
            <a
              href="https://linkedin.com/company/validahub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-4 h-4" />
            </a>
            <a
              href="https://twitter.com/validahub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition-colors"
              aria-label="Twitter"
            >
              <Twitter className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}