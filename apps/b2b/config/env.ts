/**
 * Environment Variables Configuration
 * 
 * This file validates and exports environment variables
 * required for the application to run properly.
 */

const requiredEnvVars = {
  // NextAuth
  NEXTAUTH_URL: process.env.NEXTAUTH_URL,
  NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
  
  // Google OAuth (optional but recommended)
  GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
  
  // API
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001',
  
  // Database
  DATABASE_URL: process.env.DATABASE_URL,
  
  // Redis (optional)
  REDIS_URL: process.env.REDIS_URL,
  
  // AWS S3 (optional)
  AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
  AWS_REGION: process.env.AWS_REGION || 'us-east-1',
  AWS_S3_BUCKET: process.env.AWS_S3_BUCKET,
}

// Validate required environment variables in production
if (process.env.NODE_ENV === 'production') {
  const missingVars = []
  
  const criticalVars = [
    'NEXTAUTH_URL',
    'NEXTAUTH_SECRET',
    'DATABASE_URL',
  ]
  
  for (const varName of criticalVars) {
    if (!process.env[varName]) {
      missingVars.push(varName)
    }
  }
  
  if (missingVars.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missingVars.join(', ')}\n` +
      'Please check your .env file or environment configuration.'
    )
  }
}

// Export validated environment variables
export const env = {
  // App
  nodeEnv: process.env.NODE_ENV || 'development',
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development',
  
  // NextAuth
  nextAuthUrl: requiredEnvVars.NEXTAUTH_URL || 'http://localhost:3000',
  nextAuthSecret: requiredEnvVars.NEXTAUTH_SECRET || 'development-secret-change-in-production',
  
  // Google OAuth
  googleClientId: requiredEnvVars.GOOGLE_CLIENT_ID || '',
  googleClientSecret: requiredEnvVars.GOOGLE_CLIENT_SECRET || '',
  
  // API
  apiUrl: requiredEnvVars.NEXT_PUBLIC_API_URL,
  
  // Database
  databaseUrl: requiredEnvVars.DATABASE_URL || '',
  
  // Redis
  redisUrl: requiredEnvVars.REDIS_URL || '',
  
  // AWS
  aws: {
    accessKeyId: requiredEnvVars.AWS_ACCESS_KEY_ID || '',
    secretAccessKey: requiredEnvVars.AWS_SECRET_ACCESS_KEY || '',
    region: requiredEnvVars.AWS_REGION,
    s3Bucket: requiredEnvVars.AWS_S3_BUCKET || '',
  },
}

// Helper function to check if a feature is enabled
export const isFeatureEnabled = (feature: string): boolean => {
  const envVar = `FEATURE_${feature.toUpperCase()}_ENABLED`
  return process.env[envVar] === 'true'
}

// Export helper to get public runtime config
export const getPublicConfig = () => ({
  apiUrl: env.apiUrl,
  isProduction: env.isProduction,
})