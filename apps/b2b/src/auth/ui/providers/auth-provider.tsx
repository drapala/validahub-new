"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '../../core/entities/user';
import { getAuthContainer } from '../../infrastructure/auth-container';
import { InvalidTokenError, SessionExpiredError } from '../../core/errors/auth-errors';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const TOKEN_STORAGE_KEY = 'auth-token';

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  const authContainer = getAuthContainer();
  const isAuthenticated = user !== null;

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (storedToken) {
          setToken(storedToken);
          await verifyAndSetUser(storedToken);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        // Clear invalid token
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const verifyAndSetUser = async (authToken: string) => {
    try {
      const result = await authContainer.verifySessionUseCase.execute({
        token: authToken
      });
      setUser(result.user);
    } catch (error) {
      if (error instanceof InvalidTokenError || error instanceof SessionExpiredError) {
        // Token is invalid or expired, clear it
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
        setUser(null);
      }
      throw error;
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const result = await authContainer.loginWithEmailUseCase.execute({
        email,
        password,
        ipAddress: undefined, // Will be handled by the server
        userAgent: navigator.userAgent
      });

      localStorage.setItem(TOKEN_STORAGE_KEY, result.token);
      setToken(result.token);
      setUser(result.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    setIsLoading(true);
    try {
      const result = await authContainer.registerWithEmailUseCase.execute({
        email,
        password,
        name,
        ipAddress: undefined, // Will be handled by the server
        userAgent: navigator.userAgent
      });

      localStorage.setItem(TOKEN_STORAGE_KEY, result.token);
      setToken(result.token);
      setUser(result.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      if (token) {
        await authContainer.logoutUseCase.execute({ token });
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with logout even if server call fails
    } finally {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }
  };

  const refreshSession = async () => {
    if (!token) return;
    
    try {
      await verifyAndSetUser(token);
    } catch (error) {
      console.error('Session refresh failed:', error);
      await logout();
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshSession
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Hook for protected routes
export function useRequireAuth() {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      // Redirect to login page or show login modal
      window.location.href = '/auth/login';
    }
  }, [auth.isLoading, auth.isAuthenticated]);

  return auth;
}