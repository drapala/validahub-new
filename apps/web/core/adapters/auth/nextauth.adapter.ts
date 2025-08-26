/**
 * NextAuth Adapter
 * Implements the AuthPort interface using NextAuth
 * This is the concrete implementation that the use cases will use
 */

import { AuthPort, User, Session, LoginCredentials, RegisterData } from "@/core/ports/auth.port"
import { signIn, signOut, getSession as getNextAuthSession } from "next-auth/react"

export class NextAuthAdapter implements AuthPort {
  async login(credentials: LoginCredentials): Promise<Session> {
    const result = await signIn("credentials", {
      email: credentials.email,
      password: credentials.password,
      redirect: false,
    })

    if (!result?.ok) {
      throw new Error(result?.error || "Login failed")
    }

    const session = await this.getSession()
    if (!session) {
      throw new Error("Failed to get session after login")
    }

    return session
  }

  async loginWithGoogle(): Promise<Session> {
    await signIn("google", { redirect: false })
    
    const session = await this.getSession()
    if (!session) {
      throw new Error("Failed to get session after Google login")
    }

    return session
  }

  async register(data: RegisterData): Promise<Session> {
    // Call your registration API endpoint
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || "Registration failed")
    }

    // Auto-login after registration
    return this.login({
      email: data.email,
      password: data.password,
    })
  }

  async logout(): Promise<void> {
    await signOut({ redirect: false })
  }

  async getSession(): Promise<Session | null> {
    const nextAuthSession = await getNextAuthSession()
    
    if (!nextAuthSession?.user) {
      return null
    }

    return {
      user: {
        id: nextAuthSession.user.id || "",
        email: nextAuthSession.user.email || "",
        name: nextAuthSession.user.name || undefined,
        image: nextAuthSession.user.image || undefined,
      },
      accessToken: nextAuthSession.accessToken,
      expiresAt: new Date(nextAuthSession.expires),
    }
  }

  async refreshSession(): Promise<Session | null> {
    // NextAuth handles session refresh automatically
    // This method can trigger a manual refresh if needed
    const event = new Event("visibilitychange")
    document.dispatchEvent(event)
    
    return this.getSession()
  }

  async getCurrentUser(): Promise<User | null> {
    const session = await this.getSession()
    return session?.user || null
  }

  async updateUser(data: Partial<User>): Promise<User> {
    const response = await fetch("/api/user/profile", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error("Failed to update user")
    }

    return response.json()
  }

  async requestPasswordReset(email: string): Promise<void> {
    const response = await fetch("/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    })

    if (!response.ok) {
      throw new Error("Failed to request password reset")
    }
  }

  async resetPassword(token: string, newPassword: string): Promise<void> {
    const response = await fetch("/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password: newPassword }),
    })

    if (!response.ok) {
      throw new Error("Failed to reset password")
    }
  }

  async validateToken(token: string): Promise<boolean> {
    const response = await fetch("/api/auth/validate-token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })

    return response.ok
  }
}

// Singleton instance
let authAdapterInstance: NextAuthAdapter | null = null

export function getAuthAdapter(): NextAuthAdapter {
  if (!authAdapterInstance) {
    authAdapterInstance = new NextAuthAdapter()
  }
  return authAdapterInstance
}