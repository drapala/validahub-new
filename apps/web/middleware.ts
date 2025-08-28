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

  const csp = [
    `default-src 'self'`,
    // Scripts: Next.js + inline com nonce + Google
    `script-src 'self' 'nonce-${nonce}' ${GOOGLE_HOSTS.join(' ')}`,
    // Conexões: APIs próprias, Google Auth, Lottie hosts
    `connect-src 'self' ${GOOGLE_HOSTS.join(' ')} ${LOTTIE_HOSTS.join(' ')} https://api.github.com`,
    // Imagens: self, data URLs, HTTPS
    `img-src 'self' data: https: blob:`,
    // Estilos: permitir inline (necessário para styled components/emotion)
    `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`,
    // Fonts
    `font-src 'self' data: https://fonts.gstatic.com`,
    // Workers e blob URLs (Lottie pode usar)
    `worker-src 'self' blob:`,
    // Frames (Google OAuth)
    `frame-src ${GOOGLE_HOSTS.join(' ')}`,
    // Media
    `media-src 'self' blob: data:`,
    // Base e form
    `base-uri 'self'`,
    `form-action 'self'`,
    // Object
    `object-src 'none'`,
  ].join('; ')

  res.headers.set('x-nonce', nonce)
  res.headers.set('Content-Security-Policy', csp)

  return res
}

export const config = {
  // Evita aplicar CSP em assets estáticos
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png|.*\\.jpg|.*\\.jpeg|.*\\.svg|.*\\.gif|.*\\.webp).*)'],
}