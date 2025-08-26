/** @type {import('next').NextConfig} */

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3001';
const isDev = process.env.NODE_ENV === 'development';

// Enhanced CSP for authentication security
const cspHeader = `
    default-src 'self';
    connect-src 'self' ${apiBaseUrl} https://accounts.google.com https://oauth2.googleapis.com https://www.googleapis.com;
    script-src 'self' ${isDev ? "'unsafe-eval' 'unsafe-inline'" : "'nonce-{NONCE}'"} https://accounts.google.com https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://accounts.google.com https://fonts.googleapis.com;
    img-src 'self' blob: data: https://*.googleusercontent.com https://accounts.google.com;
    font-src 'self' https://fonts.gstatic.com;
    frame-src 'self' https://accounts.google.com https://content.googleapis.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self' https://accounts.google.com;
    frame-ancestors 'none';
    block-all-mixed-content;
    ${!isDev ? 'upgrade-insecure-requests;' : ''}
`;

const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: cspHeader.replace(/\s{2,}/g, ' ').trim(),
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'false',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains; preload',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), accelerometer=(), gyroscope=()',
  },
];

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ['bcryptjs'],
  },
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL || `http://localhost:3000`,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET || 'your-super-secret-nextauth-key-change-in-production',
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
      // Additional security headers for auth endpoints
      {
        source: "/api/auth/:path*",
        headers: [
          ...securityHeaders,
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
          {
            key: 'Pragma',
            value: 'no-cache',
          },
          {
            key: 'Expires',
            value: '0',
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      // Redirect old auth routes to new ones
      {
        source: '/login',
        destination: '/auth/login',
        permanent: true,
      },
      {
        source: '/register',
        destination: '/auth/signup',
        permanent: true,
      },
      {
        source: '/signup',
        destination: '/auth/signup',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;