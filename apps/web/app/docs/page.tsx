'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowRight, Book, Code, Webhook, FileJson, Shield, Zap } from 'lucide-react'
import Link from 'next/link'

export default function DocsPage() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <div className="pb-8">
        <h1 className="text-4xl font-bold tracking-tight">
          Documentação ValidaHub
        </h1>
        <p className="text-muted-foreground mt-4 text-lg">
          Tudo que você precisa saber para integrar e usar o ValidaHub em seus projetos.
        </p>
      </div>

      {/* Quick Start */}
      <div className="mb-8">
        <Card className="bg-primary/5 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Início Rápido
            </CardTitle>
            <CardDescription>
              Comece a validar seus catálogos em minutos
            </CardDescription>
          </CardHeader>
          <CardContent className="flex gap-4">
            <Button asChild>
              <Link href="/docs/quickstart">
                Começar Agora <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/docs/api">
                Ver API Reference
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Main Sections */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Book className="h-5 w-5 text-primary" />
              Guias
            </CardTitle>
            <CardDescription>
              Aprenda os conceitos fundamentais e melhores práticas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/docs/guides/csv-format" className="hover:text-primary transition-colors">
                  • Formato e estrutura do CSV
                </Link>
              </li>
              <li>
                <Link href="/docs/guides/marketplace-rules" className="hover:text-primary transition-colors">
                  • Regras por marketplace
                </Link>
              </li>
              <li>
                <Link href="/docs/guides/error-handling" className="hover:text-primary transition-colors">
                  • Tratamento de erros
                </Link>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5 text-primary" />
              API Reference
            </CardTitle>
            <CardDescription>
              Documentação completa dos endpoints da API
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/docs/api/authentication" className="hover:text-primary transition-colors">
                  • Autenticação e tokens
                </Link>
              </li>
              <li>
                <Link href="/docs/api/validation" className="hover:text-primary transition-colors">
                  • Endpoints de validação
                </Link>
              </li>
              <li>
                <Link href="/docs/api/errors" className="hover:text-primary transition-colors">
                  • Códigos de erro
                </Link>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Webhook className="h-5 w-5 text-primary" />
              Webhooks
            </CardTitle>
            <CardDescription>
              Receba notificações em tempo real
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/docs/webhooks/setup" className="hover:text-primary transition-colors">
                  • Configuração inicial
                </Link>
              </li>
              <li>
                <Link href="/docs/webhooks/events" className="hover:text-primary transition-colors">
                  • Tipos de eventos
                </Link>
              </li>
              <li>
                <Link href="/docs/webhooks/security" className="hover:text-primary transition-colors">
                  • Validação de assinatura
                </Link>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Code Examples */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Exemplos de Código</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Python</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code className="text-sm">{`import requests

# Autenticação
headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}

# Validar CSV
files = {'file': open('catalog.csv', 'rb')}
response = requests.post(
    'https://api.validahub.com/validate',
    headers=headers,
    files=files
)

print(response.json())`}</code>
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">JavaScript</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code className="text-sm">{`const FormData = require('form-data');
const fs = require('fs');

// Preparar arquivo
const form = new FormData();
form.append('file', fs.createReadStream('catalog.csv'));

// Enviar para validação
const response = await fetch('https://api.validahub.com/validate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: form
});

const result = await response.json();`}</code>
              </pre>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Additional Resources */}
      <div className="border-t pt-8">
        <h2 className="text-2xl font-semibold mb-4">Recursos Adicionais</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <FileJson className="h-5 w-5 text-primary" />
                Postman Collection
              </CardTitle>
              <CardDescription>
                Coleção completa com todos os endpoints da API
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" size="sm" asChild>
                <Link href="/docs/postman">
                  Download Collection
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Shield className="h-5 w-5 text-primary" />
                Segurança
              </CardTitle>
              <CardDescription>
                Melhores práticas de segurança e compliance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" size="sm" asChild>
                <Link href="/docs/security">
                  Ver Guia de Segurança
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}