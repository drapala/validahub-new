import NextAuth from 'next-auth';
import { createNextAuthConfig } from '@/src/auth/adapters/nextauth/nextauth-adapter';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';

const authContainer = getAuthContainer();

const authConfig = createNextAuthConfig({
  loginWithEmailUseCase: authContainer.loginWithEmailUseCase,
  loginWithOAuthUseCase: authContainer.loginWithOAuthUseCase
});

const handler = NextAuth(authConfig);

export { handler as GET, handler as POST };