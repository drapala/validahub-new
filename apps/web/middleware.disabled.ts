import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

// Rotas públicas que não precisam de autenticação
const publicPaths = [
  '/',
  '/pricing',
  '/faq',
  '/privacy',
  '/terms',
  '/docs',
  '/status',
  '/api/auth',
  '/_next',
  '/favicon.ico',
]

// Rotas que requerem autenticação
const protectedPaths = [
  '/upload',
  '/jobs',
  '/connectors',
  '/mappings',
  '/billing',
  '/results',
  '/settings',
  '/webhooks',
  '/validate-row'
]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Permitir sempre requisições para assets e API de auth
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/favicon') ||
    pathname.includes('.')
  ) {
    return NextResponse.next()
  }

  // Verificar se a rota está protegida
  const isProtectedRoute = protectedPaths.some(path => pathname.startsWith(path))
  
  if (isProtectedRoute) {
    try {
      // Verificar se o usuário está autenticado
      const token = await getToken({ 
        req: request,
        secret: process.env.NEXTAUTH_SECRET 
      })

      if (!token) {
        // Redirecionar para a landing page se não autenticado
        const url = new URL('/', request.url)
        url.searchParams.set('callbackUrl', pathname)
        return NextResponse.redirect(url)
      }

      // Adicionar headers de segurança para rotas protegidas
      const response = NextResponse.next()
      response.headers.set('X-Frame-Options', 'DENY')
      response.headers.set('X-Content-Type-Options', 'nosniff')
      response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
      
      return response
    } catch (error) {
      console.error('Middleware auth error:', error)
      return NextResponse.redirect(new URL('/', request.url))
    }
  }

  // Headers de segurança para todas as rotas
  const response = NextResponse.next()
  response.headers.set('X-Frame-Options', 'SAMEORIGIN')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  
  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/webhooks (webhook endpoints)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api/webhooks|_next/static|_next/image|favicon.ico).*)',
  ],
}