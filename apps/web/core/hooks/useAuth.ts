/**
 * useAuth Hook
 * Unified authentication hook following Clean Architecture
 * Provides all auth-related functionality in one place
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getAuthAdapter } from '@/core/adapters/auth/nextauth.adapter'
import { User, Session } from '@/core/ports/auth.port'
import { LoginUseCase } from '@/core/usecases/auth/login.usecase'
import { RegisterUseCase } from '@/core/usecases/auth/register.usecase'
import { LogoutUseCase } from '@/core/usecases/auth/logout.usecase'
import { GoogleLoginUseCase } from '@/core/usecases/auth/google-login.usecase'

interface AuthState {
  user: User | null
  session: Session | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string, rememberMe?: boolean) => Promise<boolean>
  register: (email: string, password: string, name?: string, acceptTerms?: boolean) => Promise<boolean>
  loginWithGoogle: () => Promise<boolean>
  logout: () => Promise<void>
  refreshSession: () => Promise<void>
  clearError: () => void
}

export interface UseAuthReturn extends AuthState, AuthActions {}

export function useAuth(): UseAuthReturn {
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  })

  const router = useRouter()
  const authAdapter = getAuthAdapter()

  // Use cases
  const loginUseCase = new LoginUseCase(authAdapter)
  const registerUseCase = new RegisterUseCase(authAdapter)
  const logoutUseCase = new LogoutUseCase(authAdapter)
  const googleLoginUseCase = new GoogleLoginUseCase(authAdapter)

  // Fetch current session on mount and when auth state changes
  const fetchSession = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const session = await authAdapter.getSession()
      
      if (session) {
        setState({
          user: session.user,
          session,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
      } else {
        setState({
          user: null,
          session: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        })
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to fetch session',
      }))
    }
  }, [authAdapter])

  useEffect(() => {
    fetchSession()

    // Listen for auth state changes
    const handleFocus = () => fetchSession()
    window.addEventListener('focus', handleFocus)

    // Check session periodically
    const interval = setInterval(fetchSession, 5 * 60 * 1000) // Every 5 minutes

    return () => {
      window.removeEventListener('focus', handleFocus)
      clearInterval(interval)
    }
  }, [fetchSession])

  const login = useCallback(async (
    email: string,
    password: string,
    rememberMe = false
  ): Promise<boolean> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const result = await loginUseCase.execute({
        email,
        password,
        rememberMe,
      })

      if (result.success && result.session) {
        setState({
          user: result.session.user,
          session: result.session,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        return true
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Login failed',
        }))
        return false
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'An unexpected error occurred',
      }))
      return false
    }
  }, [loginUseCase])

  const register = useCallback(async (
    email: string,
    password: string,
    name?: string,
    acceptTerms = true
  ): Promise<boolean> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const result = await registerUseCase.execute({
        email,
        password,
        name,
        acceptTerms,
      })

      if (result.success && result.session) {
        setState({
          user: result.session.user,
          session: result.session,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        return true
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Registration failed',
        }))
        return false
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'An unexpected error occurred',
      }))
      return false
    }
  }, [registerUseCase])

  const loginWithGoogle = useCallback(async (): Promise<boolean> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const result = await googleLoginUseCase.execute()

      if (result.success && result.session) {
        setState({
          user: result.session.user,
          session: result.session,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
        return true
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Google login failed',
        }))
        return false
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'An unexpected error occurred',
      }))
      return false
    }
  }, [googleLoginUseCase])

  const logout = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      await logoutUseCase.execute()
      
      setState({
        user: null,
        session: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
      
      router.push('/')
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to logout',
      }))
    }
  }, [logoutUseCase, router])

  const refreshSession = useCallback(async () => {
    await fetchSession()
  }, [fetchSession])

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  return {
    ...state,
    login,
    register,
    loginWithGoogle,
    logout,
    refreshSession,
    clearError,
  }
}

// Export a provider for easier usage
export { useAuth as default }