'use client'

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './dialog'
import { Button } from './button'
import { Input } from './input'
import { Label } from './label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs'
import { Checkbox } from './checkbox'
import { AlertCircle, Loader2 } from 'lucide-react'
import { Alert, AlertDescription } from './alert'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  mode: 'signin' | 'signup'
  onModeChange: (mode: 'signin' | 'signup') => void
}

export default function AuthModal({ isOpen, onClose, mode, onModeChange }: AuthModalProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)
  
  // Form fields
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')

  const handleGoogleSignIn = async () => {
    setLoading(true)
    setError('')
    try {
      const result = await signIn('google', { 
        callbackUrl: '/upload',
        redirect: false 
      })
      
      if (result?.error) {
        setError('Erro ao fazer login com Google. Tente novamente.')
      } else if (result?.url) {
        router.push(result.url)
        onClose()
      }
    } catch (err) {
      setError('Erro inesperado. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (mode === 'signup' && !acceptTerms) {
      setError('Você precisa aceitar os termos e condições')
      setLoading(false)
      return
    }

    try {
      if (mode === 'signin') {
        const result = await signIn('credentials', {
          email,
          password,
          redirect: false,
          callbackUrl: '/upload'
        })

        if (result?.error) {
          setError('Email ou senha inválidos')
        } else if (result?.ok) {
          router.push('/upload')
          onClose()
        }
      } else {
        // Sign up logic
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        })

        if (response.ok) {
          // Auto sign in after registration
          const result = await signIn('credentials', {
            email,
            password,
            redirect: false,
            callbackUrl: '/upload'
          })

          if (result?.ok) {
            router.push('/upload')
            onClose()
          }
        } else {
          const data = await response.json()
          setError(data.message || 'Erro ao criar conta')
        }
      }
    } catch (err) {
      setError('Erro inesperado. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmail('')
    setPassword('')
    setName('')
    setAcceptTerms(false)
    setError('')
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => {
      if (!open) {
        resetForm()
        onClose()
      }
    }}>
      <DialogContent className="sm:max-w-[425px] bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white text-center">
            {mode === 'signin' ? 'Entrar na sua conta' : 'Criar nova conta'}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <Alert variant="destructive" className="bg-red-500/10 border-red-500/50">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value="google" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-gray-800">
            <TabsTrigger value="google" className="data-[state=active]:bg-gray-700">
              Google
            </TabsTrigger>
            <TabsTrigger value="email" className="data-[state=active]:bg-gray-700">
              Email
            </TabsTrigger>
          </TabsList>

          <TabsContent value="google" className="space-y-4">
            <Button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="w-full bg-white hover:bg-gray-100 text-gray-900 font-medium"
            >
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
              )}
              {mode === 'signin' ? 'Entrar com Google' : 'Cadastrar com Google'}
            </Button>
          </TabsContent>

          <TabsContent value="email">
            <form onSubmit={handleEmailAuth} className="space-y-4">
              {mode === 'signup' && (
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-gray-200">
                    Nome completo
                  </Label>
                  <Input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="João Silva"
                    required
                    className="bg-gray-800 border-gray-700 text-white placeholder-gray-500"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-200">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                  className="bg-gray-800 border-gray-700 text-white placeholder-gray-500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-200">
                  Senha
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={8}
                  className="bg-gray-800 border-gray-700 text-white placeholder-gray-500"
                />
              </div>

              {mode === 'signup' && (
                <div className="flex items-start space-x-2">
                  <Checkbox
                    id="terms"
                    checked={acceptTerms}
                    onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                    className="mt-1"
                  />
                  <Label htmlFor="terms" className="text-sm text-gray-400 cursor-pointer">
                    Aceito os{' '}
                    <a href="/terms" className="text-green-400 hover:underline">
                      Termos de Serviço
                    </a>{' '}
                    e a{' '}
                    <a href="/privacy" className="text-green-400 hover:underline">
                      Política de Privacidade
                    </a>
                  </Label>
                </div>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {mode === 'signin' ? 'Entrar' : 'Criar conta'}
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        <div className="text-center text-sm text-gray-400">
          {mode === 'signin' ? (
            <>
              Não tem uma conta?{' '}
              <button
                onClick={() => {
                  onModeChange('signup')
                  resetForm()
                }}
                className="text-green-400 hover:underline font-medium"
              >
                Cadastre-se
              </button>
            </>
          ) : (
            <>
              Já tem uma conta?{' '}
              <button
                onClick={() => {
                  onModeChange('signin')
                  resetForm()
                }}
                className="text-green-400 hover:underline font-medium"
              >
                Fazer login
              </button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}