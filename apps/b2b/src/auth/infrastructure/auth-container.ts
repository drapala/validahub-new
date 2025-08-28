// Dependency injection container for auth system
import { LoginWithEmailUseCase } from '../core/usecases/login-with-email';
import { RegisterWithEmailUseCase } from '../core/usecases/register-with-email';
import { LoginWithOAuthUseCase } from '../core/usecases/login-with-oauth';
import { LogoutUseCase } from '../core/usecases/logout';
import { VerifySessionUseCase } from '../core/usecases/verify-session';

import { MemoryUserRepository, MemorySessionRepository, MemoryCredentialRepository } from '../adapters/storage/memory-repositories';
import { MemorySessionStorage } from '../adapters/storage/memory-session-storage';
import { BcryptPasswordService } from '../adapters/services/bcrypt-password-service';
import { JoseTokenService } from '../adapters/services/jose-token-service';
import { AuthApiAdapter } from '../adapters/api/auth-api-adapter';

export interface AuthContainer {
  // Use Cases
  loginWithEmailUseCase: LoginWithEmailUseCase;
  registerWithEmailUseCase: RegisterWithEmailUseCase;
  loginWithOAuthUseCase: LoginWithOAuthUseCase;
  logoutUseCase: LogoutUseCase;
  verifySessionUseCase: VerifySessionUseCase;

  // Adapters
  authApiAdapter: AuthApiAdapter;

  // Services
  passwordService: BcryptPasswordService;
  tokenService: JoseTokenService;
  sessionStorage: MemorySessionStorage;

  // Repositories
  userRepository: MemoryUserRepository;
  sessionRepository: MemorySessionRepository;
  credentialRepository: MemoryCredentialRepository;
}

let container: AuthContainer | null = null;

export function createAuthContainer(): AuthContainer {
  if (container) {
    return container;
  }

  // Services (leaf dependencies)
  const passwordService = new BcryptPasswordService();
  const tokenService = new JoseTokenService();
  const sessionStorage = new MemorySessionStorage();

  // Repositories
  const userRepository = new MemoryUserRepository(tokenService);
  const sessionRepository = new MemorySessionRepository(tokenService);
  const credentialRepository = new MemoryCredentialRepository(passwordService);

  // Use Cases
  const loginWithEmailUseCase = new LoginWithEmailUseCase(
    userRepository,
    credentialRepository,
    sessionRepository,
    passwordService,
    tokenService
  );

  const registerWithEmailUseCase = new RegisterWithEmailUseCase(
    userRepository,
    credentialRepository,
    sessionRepository,
    passwordService,
    tokenService
  );

  const loginWithOAuthUseCase = new LoginWithOAuthUseCase(
    userRepository,
    credentialRepository,
    sessionRepository,
    tokenService
  );

  const logoutUseCase = new LogoutUseCase(
    sessionRepository,
    sessionStorage,
    tokenService
  );

  const verifySessionUseCase = new VerifySessionUseCase(
    userRepository,
    sessionRepository,
    sessionStorage,
    tokenService
  );

  // Adapters
  const authApiAdapter = new AuthApiAdapter();

  container = {
    loginWithEmailUseCase,
    registerWithEmailUseCase,
    loginWithOAuthUseCase,
    logoutUseCase,
    verifySessionUseCase,
    authApiAdapter,
    passwordService,
    tokenService,
    sessionStorage,
    userRepository,
    sessionRepository,
    credentialRepository
  };

  return container;
}

export function getAuthContainer(): AuthContainer {
  // Use mock container in development without backend
  const useMock = process.env.NEXT_PUBLIC_USE_MOCK_AUTH === 'true' || 
                  (process.env.NODE_ENV === 'development');
  
  if (useMock) {
    // Dynamic import to avoid bundling in production
    const { getMockAuthContainer } = require('./auth-container-mock');
    return getMockAuthContainer();
  }
  
  if (!container) {
    return createAuthContainer();
  }
  return container;
}

// Cleanup function for graceful shutdown
export function cleanupAuthContainer(): void {
  if (container?.sessionStorage) {
    container.sessionStorage.cleanup();
  }
  container = null;
}