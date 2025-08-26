"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { SignupForm } from '@/src/auth/ui/components/signup-form';
import { OAuthButton } from '@/src/auth/ui/components/oauth-button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function SignupPage() {
  const router = useRouter();

  const handleSignupSuccess = () => {
    router.push('/upload'); // Redirect to main app after signup
  };

  const handleOAuthSignup = (provider: 'google' | 'github' | 'microsoft') => {
    // In a real implementation, this would redirect to NextAuth OAuth flow
    console.log(`Initiating ${provider} OAuth flow`);
    // window.location.href = `/api/auth/signin/${provider}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-2xl font-bold">Create your account</CardTitle>
          <CardDescription>
            Get started with ValidaHub today
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <OAuthButton
              provider="google"
              onClick={() => handleOAuthSignup('google')}
            >
              Sign up with Google
            </OAuthButton>
          </div>
          
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or create account with email
              </span>
            </div>
          </div>

          <SignupForm onSuccess={handleSignupSuccess} />

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link 
                href="/auth/login" 
                className="text-primary underline-offset-4 hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>

          <div className="text-xs text-muted-foreground text-center space-y-1">
            <p>
              By creating an account, you agree to our{' '}
              <Link href="/terms" className="underline-offset-4 hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="underline-offset-4 hover:underline">
                Privacy Policy
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}