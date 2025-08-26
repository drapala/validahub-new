/**
 * Login Use Case
 * Orchestrates the login flow
 * UI components call this use case, which uses the AuthPort
 */

import { AuthPort, LoginCredentials, Session } from "@/core/ports/auth.port"

export interface LoginUseCaseInput {
  email: string
  password: string
  rememberMe?: boolean
}

export interface LoginUseCaseOutput {
  success: boolean
  session?: Session
  error?: string
}

export class LoginUseCase {
  constructor(private authPort: AuthPort) {}

  async execute(input: LoginUseCaseInput): Promise<LoginUseCaseOutput> {
    try {
      // Validate input
      if (!this.validateEmail(input.email)) {
        return {
          success: false,
          error: "Email inválido"
        }
      }

      if (!this.validatePassword(input.password)) {
        return {
          success: false,
          error: "Senha deve ter pelo menos 8 caracteres"
        }
      }

      // Attempt login
      const credentials: LoginCredentials = {
        email: input.email.toLowerCase().trim(),
        password: input.password
      }

      const session = await this.authPort.login(credentials)

      // Handle remember me
      if (input.rememberMe) {
        // This could set a longer-lasting session or cookie
        // Implementation depends on the auth adapter
      }

      return {
        success: true,
        session
      }
    } catch (error) {
      // Map technical errors to user-friendly messages
      const message = this.mapErrorMessage(error)
      
      return {
        success: false,
        error: message
      }
    }
  }

  private validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  private validatePassword(password: string): boolean {
    return password.length >= 8
  }

  private mapErrorMessage(error: any): string {
    // Map known error codes to user-friendly messages
    if (error?.code === 'INVALID_CREDENTIALS') {
      return "Email ou senha incorretos"
    }
    
    if (error?.code === 'USER_NOT_FOUND') {
      return "Usuário não encontrado"
    }
    
    if (error?.code === 'ACCOUNT_LOCKED') {
      return "Conta temporariamente bloqueada. Tente novamente mais tarde"
    }
    
    if (error?.code === 'EMAIL_NOT_VERIFIED') {
      return "Por favor, verifique seu email antes de fazer login"
    }
    
    // Network errors
    if (error?.message?.includes('network')) {
      return "Erro de conexão. Verifique sua internet"
    }
    
    // Default message
    return "Erro ao fazer login. Tente novamente"
  }
}