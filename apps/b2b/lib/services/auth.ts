const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

interface LoginCredentials {
  email: string
  password: string
  tenant_slug?: string
}

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    name: string
    role: string
    is_verified: boolean
    avatar_url: string | null
  }
  tenant: {
    id: string
    name: string
    slug: string
    plan: string
    features: Record<string, boolean>
  }
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    return response.json()
  },

  async refresh(refreshToken: string): Promise<LoginResponse> {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) {
      throw new Error('Failed to refresh token')
    }

    return response.json()
  },

  async logout(): Promise<void> {
    if (typeof window === 'undefined') return
    
    const accessToken = localStorage.getItem('access_token')
    
    if (accessToken) {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      })
    }

    // Clear local storage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('tenant')
  },

  async getCurrentUser() {
    const accessToken = localStorage.getItem('access_token')
    
    if (!accessToken) {
      throw new Error('Not authenticated')
    }

    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to get current user')
    }

    return response.json()
  },

  getStoredUser() {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  getStoredTenant() {
    if (typeof window === 'undefined') return null
    const tenantStr = localStorage.getItem('tenant')
    return tenantStr ? JSON.parse(tenantStr) : null
  },

  getAccessToken() {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  },

  isAuthenticated() {
    if (typeof window === 'undefined') return false
    return !!localStorage.getItem('access_token')
  },
}