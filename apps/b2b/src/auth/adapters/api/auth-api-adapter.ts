import { LoginWithEmailInput, LoginWithEmailOutput } from '../../core/usecases/login-with-email';
import { RegisterWithEmailInput, RegisterWithEmailOutput } from '../../core/usecases/register-with-email';
import { LogoutInput, LogoutOutput } from '../../core/usecases/logout';
import { VerifySessionInput, VerifySessionOutput } from '../../core/usecases/verify-session';

export interface AuthApiPort {
  loginWithEmail(input: LoginWithEmailInput): Promise<LoginWithEmailOutput>;
  registerWithEmail(input: RegisterWithEmailInput): Promise<RegisterWithEmailOutput>;
  logout(input: LogoutInput): Promise<LogoutOutput>;
  verifySession(input: VerifySessionInput): Promise<VerifySessionOutput>;
}

export class AuthApiAdapter implements AuthApiPort {
  private readonly baseUrl: string;

  constructor(baseUrl: string = '/api/auth') {
    this.baseUrl = baseUrl;
  }

  async loginWithEmail(input: LoginWithEmailInput): Promise<LoginWithEmailOutput> {
    const response = await this.fetchApi('/login', {
      method: 'POST',
      body: JSON.stringify({
        email: input.email,
        password: input.password
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Login failed');
    }

    return response.json();
  }

  async registerWithEmail(input: RegisterWithEmailInput): Promise<RegisterWithEmailOutput> {
    const response = await this.fetchApi('/register', {
      method: 'POST',
      body: JSON.stringify({
        email: input.email,
        password: input.password,
        name: input.name
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Registration failed');
    }

    return response.json();
  }

  async logout(input: LogoutInput): Promise<LogoutOutput> {
    const response = await this.fetchApi('/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${input.token}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Logout failed');
    }

    return response.json();
  }

  async verifySession(input: VerifySessionInput): Promise<VerifySessionOutput> {
    const response = await this.fetchApi('/verify', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${input.token}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Session verification failed');
    }

    return response.json();
  }

  private async fetchApi(path: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseUrl}${path}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers
      },
      credentials: 'include' // Include cookies for CSRF protection
    };

    return fetch(url, { ...defaultOptions, ...options });
  }
}