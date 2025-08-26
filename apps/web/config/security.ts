/**
 * Security Configuration
 * 
 * This file contains security headers and configurations for the application.
 * CSP and other security headers are configured here.
 */

export const securityHeaders = {
  // Content Security Policy
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: [
        "'self'",
        "'unsafe-inline'", // TODO: Remove unsafe-inline and use nonces
        "'unsafe-eval'", // TODO: Remove unsafe-eval after reviewing code
        "https://accounts.google.com", // Google OAuth
        "https://apis.google.com",
      ],
      styleSrc: [
        "'self'",
        "'unsafe-inline'", // TODO: Move to external stylesheets
        "https://fonts.googleapis.com",
      ],
      imgSrc: [
        "'self'",
        "data:",
        "https:",
        "blob:",
        "https://lh3.googleusercontent.com", // Google profile images
      ],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      connectSrc: [
        "'self'",
        "https://accounts.google.com",
        "https://apis.google.com",
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001",
      ],
      frameSrc: [
        "'self'",
        "https://accounts.google.com", // Google OAuth iframe
      ],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      manifestSrc: ["'self'"],
      workerSrc: ["'self'", "blob:"],
      childSrc: ["'self'", "blob:"],
      formAction: ["'self'"],
      frameAncestors: ["'none'"],
      baseUri: ["'self'"],
      upgradeInsecureRequests: process.env.NODE_ENV === "production" ? [] : undefined,
    },
  },

  // Other security headers
  headers: {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-XSS-Protection": "1; mode=block",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  },
}

// Allowed callback URLs for authentication
export const allowedCallbackUrls = [
  "/upload",
  "/jobs",
  "/connectors",
  "/mappings",
  "/settings",
  "/settings/billing",
]

// Rate limiting configuration
export const rateLimits = {
  auth: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 requests per window
  },
  api: {
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 60, // 60 requests per minute
  },
  upload: {
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 10, // 10 uploads per minute
  },
}

// Session configuration
export const sessionConfig = {
  maxAge: 30 * 24 * 60 * 60, // 30 days
  updateAge: 24 * 60 * 60, // 24 hours
}

// TODO: Implement rate limiting middleware
// TODO: Add CORS configuration for API routes
// TODO: Implement request signing for sensitive operations
// TODO: Add audit logging for security events
// TODO: Implement IP allowlisting for admin routes
// TODO: Add honeypot fields to forms
// TODO: Implement CAPTCHA for public forms