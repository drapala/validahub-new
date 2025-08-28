import { NextResponse, NextRequest } from 'next/server'

function toBase64(bytes: Uint8Array) {
  let str = ''
  for (let i = 0; i < bytes.length; i++) str += String.fromCharCode(bytes[i])
  // btoa é suportado no Edge Runtime
  return btoa(str)
}

export function middleware(req: NextRequest) {
  const res = NextResponse.next()
  
  // Gera nonce (Edge-safe)
  const nonce = toBase64(crypto.getRandomValues(new Uint8Array(16)))
  
  // Detectar ambiente (localhost = desenvolvimento)
  const isDev = req.nextUrl.hostname === 'localhost' || req.nextUrl.hostname === '127.0.0.1'

  // Domínios externos necessários
  const LOTTIE_HOSTS = [
    'https://assets.lottiefiles.com',
    'https://lottie.host',
    'https://cdn.jsdelivr.net', // Para animações Lottie via CDN
  ]

  const GOOGLE_HOSTS = [
    'https://accounts.google.com',
    'https://apis.google.com',
    'https://www.googleapis.com',
    'https://securetoken.googleapis.com',
  ]
  
  // CSP diferente para dev e prod
  let csp: string
  
  if (isDev) {
    // Desenvolvimento: mais permissivo para hot reload e debug
    csp = [
      `default-src 'self'`,
      // Scripts: permite eval e inline para hot reload
      `script-src 'self' 'unsafe-inline' 'unsafe-eval' ${GOOGLE_HOSTS.join(' ')}`,
      // Conexões: permite websocket para hot reload
      `connect-src 'self' ws://localhost:* http://localhost:* ${GOOGLE_HOSTS.join(' ')} ${LOTTIE_HOSTS.join(' ')} https://api.github.com`,
      // Imagens
      `img-src 'self' data: https: blob:`,
      // Estilos
      `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`,
      // Fonts
      `font-src 'self' data: https://fonts.gstatic.com`,
      // Workers
      `worker-src 'self' blob:`,
      // Frames
      `frame-src ${GOOGLE_HOSTS.join(' ')}`,
      // Media
      `media-src 'self' blob: data:`,
      // Base e form
      `base-uri 'self'`,
      `form-action 'self'`,
      // Object
      `object-src 'none'`,
    ].join('; ')
  } else {
    // Produção: restritivo com nonce
    csp = [
      `default-src 'self'`,
      // Scripts: apenas com nonce
      `script-src 'self' 'nonce-${nonce}' ${GOOGLE_HOSTS.join(' ')}`,
        // Conexões: apenas HTTPS
      `connect-src 'self' ${GOOGLE_HOSTS.join(' ')} ${LOTTIE_HOSTS.join(' ')} https://api.github.com`,
      // Imagens
      `img-src 'self' data: https: blob:`,
      // Estilos
      `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`,
      // Fonts
      `font-src 'self' data: https://fonts.gstatic.com`,
      // Workers
      `worker-src 'self' blob:`,
      // Frames
      `frame-src ${GOOGLE_HOSTS.join(' ')}`,
      // Media
      `media-src 'self' blob: data:`,
      // Base e form
      `base-uri 'self'`,
      `form-action 'self'`,
      // Object
      `object-src 'none'`,
    ].join('; ')
  }

  // Sempre adicionar o nonce no header para o Next.js usar
  res.headers.set('x-nonce', nonce)
  res.headers.set('Content-Security-Policy', csp)

  return res
}

export const config = {
  // Evita aplicar CSP em assets estáticos
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png|.*\\.jpg|.*\\.jpeg|.*\\.svg|.*\\.gif|.*\\.webp).*)'],
}