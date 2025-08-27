import { Metadata } from 'next'
import Link from 'next/link'
import { Book, Home, ChevronLeft } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Documentação - ValidaHub',
  description: 'Documentação completa da API e guias de integração do ValidaHub',
}

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background">
      {/* Header Simples para Docs */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center px-4 sm:px-8">
          {/* Logo e Título */}
          <div className="mr-8 flex items-center space-x-2">
            <Book className="h-6 w-6 text-primary" />
            <span className="hidden font-bold sm:inline-block">
              ValidaHub Docs
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-6 text-sm">
            <Link
              href="/"
              className="flex items-center gap-2 text-foreground/60 transition-colors hover:text-foreground"
            >
              <Home className="h-4 w-4" />
              Home
            </Link>
            <Link
              href="/docs"
              className="text-foreground/60 transition-colors hover:text-foreground"
            >
              Guias
            </Link>
            <Link
              href="/docs/api"
              className="text-foreground/60 transition-colors hover:text-foreground"
            >
              API Reference
            </Link>
            <Link
              href="/docs/examples"
              className="text-foreground/60 transition-colors hover:text-foreground"
            >
              Exemplos
            </Link>
          </nav>

          {/* Spacer */}
          <div className="flex flex-1 items-center justify-end space-x-2">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Acessar App
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container flex-1 items-start md:grid md:grid-cols-[220px_minmax(0,1fr)] md:gap-6 lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-10">
        {/* Sidebar */}
        <aside className="fixed top-14 z-30 -ml-2 hidden h-[calc(100vh-3.5rem)] w-full shrink-0 md:sticky md:block">
          <div className="relative overflow-hidden h-full py-6 pr-6 lg:py-8">
            <div className="h-full w-full overflow-y-auto">
              <div className="w-full">
                <div className="pb-4">
                  <h4 className="mb-1 rounded-md px-2 py-1 text-sm font-semibold">
                    Início
                  </h4>
                  <div className="grid grid-flow-row auto-rows-max text-sm">
                    <Link
                      href="/docs"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Introdução
                    </Link>
                    <Link
                      href="/docs/quickstart"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Início Rápido
                    </Link>
                  </div>
                </div>

                <div className="pb-4">
                  <h4 className="mb-1 rounded-md px-2 py-1 text-sm font-semibold">
                    API Reference
                  </h4>
                  <div className="grid grid-flow-row auto-rows-max text-sm">
                    <Link
                      href="/docs/api/authentication"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Autenticação
                    </Link>
                    <Link
                      href="/docs/api/validation"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Validação
                    </Link>
                    <Link
                      href="/docs/api/webhooks"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Webhooks
                    </Link>
                  </div>
                </div>

                <div className="pb-4">
                  <h4 className="mb-1 rounded-md px-2 py-1 text-sm font-semibold">
                    Guias
                  </h4>
                  <div className="grid grid-flow-row auto-rows-max text-sm">
                    <Link
                      href="/docs/guides/csv-format"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Formato CSV
                    </Link>
                    <Link
                      href="/docs/guides/marketplace-rules"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Regras por Marketplace
                    </Link>
                    <Link
                      href="/docs/guides/error-handling"
                      className="group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:underline text-muted-foreground"
                    >
                      Tratamento de Erros
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Content */}
        <main className="relative py-6 lg:gap-10 lg:py-8 xl:grid xl:grid-cols-[1fr_300px]">
          <div className="mx-auto w-full min-w-0">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}