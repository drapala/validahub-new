"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../providers/auth-provider';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { LoginForm } from './login-form';
import { SignupForm } from './signup-form';
import { OAuthButton } from './oauth-button';
import { User, LogOut, Settings, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AuthNavbarProps {
  className?: string;
}

type AuthModal = 'login' | 'signup' | null;

export function AuthNavbar({ className }: AuthNavbarProps) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [authModal, setAuthModal] = useState<AuthModal>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleAuthSuccess = () => {
    setAuthModal(null);
  };

  const handleOAuthLogin = (provider: 'google' | 'github' | 'microsoft') => {
    // In a real implementation, this would redirect to NextAuth OAuth flow
    // For now, we'll show a placeholder
    console.log(`Initiating ${provider} OAuth flow`);
    // window.location.href = `/api/auth/signin/${provider}`;
  };

  if (isLoading) {
    return (
      <nav className={cn("flex items-center justify-end space-x-4", className)}>
        <Loader2 className="h-4 w-4 animate-spin" />
      </nav>
    );
  }

  return (
    <>
      <nav className={cn("flex items-center justify-end space-x-4", className)}>
        {isAuthenticated && user ? (
          <>
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span className="text-sm font-medium">
                {user.name || user.email}
              </span>
            </div>
            
            <Button variant="ghost" size="sm" asChild>
              <Link href="/settings">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Link>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <LogOut className="h-4 w-4 mr-2" />
              )}
              Sign Out
            </Button>
          </>
        ) : (
          <>
            <Button 
              variant="ghost" 
              onClick={() => setAuthModal('login')}
            >
              Sign In
            </Button>
            <Button onClick={() => setAuthModal('signup')}>
              Sign Up
            </Button>
          </>
        )}
      </nav>

      {/* Auth Modals */}
      <Dialog open={authModal === 'login'} onOpenChange={(open) => !open && setAuthModal(null)}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Sign In to ValidaHub</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <OAuthButton
                provider="google"
                onClick={() => handleOAuthLogin('google')}
              />
            </div>
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with email
                </span>
              </div>
            </div>

            <LoginForm onSuccess={handleAuthSuccess} />

            <div className="text-center">
              <button
                className="text-sm text-muted-foreground hover:text-primary underline-offset-4 hover:underline"
                onClick={() => setAuthModal('signup')}
              >
                Don't have an account? Sign up
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={authModal === 'signup'} onOpenChange={(open) => !open && setAuthModal(null)}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create Your Account</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <OAuthButton
                provider="google"
                onClick={() => handleOAuthLogin('google')}
              />
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

            <SignupForm onSuccess={handleAuthSuccess} />

            <div className="text-center">
              <button
                className="text-sm text-muted-foreground hover:text-primary underline-offset-4 hover:underline"
                onClick={() => setAuthModal('login')}
              >
                Already have an account? Sign in
              </button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}