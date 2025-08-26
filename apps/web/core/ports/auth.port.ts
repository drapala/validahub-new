/**
 * Authentication Port
 * Defines the contract for authentication operations
 * UI components should depend on this interface, not on concrete implementations
 */

export interface User {
  id: string
  email: string
  name?: string
  image?: string
  role?: string
  createdAt?: Date
  updatedAt?: Date
}

export interface Session {
  user: User
  accessToken?: string
  refreshToken?: string
  expiresAt: Date
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  name?: string
}

export interface AuthPort {
  // Authentication methods
  login(credentials: LoginCredentials): Promise<Session>
  loginWithGoogle(): Promise<Session>
  register(data: RegisterData): Promise<Session>
  logout(): Promise<void>
  
  // Session management
  getSession(): Promise<Session | null>
  refreshSession(): Promise<Session | null>
  
  // User operations
  getCurrentUser(): Promise<User | null>
  updateUser(data: Partial<User>): Promise<User>
  
  // Password operations
  requestPasswordReset(email: string): Promise<void>
  resetPassword(token: string, newPassword: string): Promise<void>
  
  // Token validation
  validateToken(token: string): Promise<boolean>
}

// Events that can be emitted by the auth system
export type AuthEvent = 
  | { type: 'LOGIN_SUCCESS'; session: Session }
  | { type: 'LOGIN_FAILURE'; error: string }
  | { type: 'LOGOUT' }
  | { type: 'SESSION_EXPIRED' }
  | { type: 'SESSION_REFRESHED'; session: Session }

export interface AuthEventListener {
  (event: AuthEvent): void
}

export interface AuthEventEmitter {
  on(listener: AuthEventListener): void
  off(listener: AuthEventListener): void
  emit(event: AuthEvent): void
}