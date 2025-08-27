import NextAuth from 'next-auth';
import { createNextAuthConfig } from '@/src/auth/adapters/nextauth/nextauth-adapter';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';

const authContainer = getAuthContainer();

const authOptions = createNextAuthConfig({
  loginWithEmailUseCase: authContainer.loginWithEmailUseCase,
  loginWithOAuthUseCase: authContainer.loginWithOAuthUseCase
});

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };