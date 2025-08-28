import type { NextAuthConfig, Session as NextAuthSession, User as NextAuthUser } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import CredentialsProvider from 'next-auth/providers/credentials';
import { JWT } from 'next-auth/jwt';
import { LoginWithEmailUseCase } from '../../core/usecases/login-with-email';
import { LoginWithOAuthUseCase } from '../../core/usecases/login-with-oauth';
import { User } from '../../core/entities/user';

// Extend NextAuth types
declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      email: string;
      name: string | null;
      avatar: string | null;
      emailVerified: boolean;
    };
    sessionId: string;
  }

  interface User {
    id: string;
    email: string;
    name: string | null;
    avatar: string | null;
    emailVerified: boolean;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    userId: string;
    sessionId: string;
    emailVerified: boolean;
  }
}

export interface NextAuthAdapterDeps {
  loginWithEmailUseCase: LoginWithEmailUseCase;
  loginWithOAuthUseCase: LoginWithOAuthUseCase;
}

export function createNextAuthConfig(deps: NextAuthAdapterDeps): NextAuthConfig {
  return {
    providers: [
      GoogleProvider({
        clientId: process.env.GOOGLE_CLIENT_ID!,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        authorization: {
          params: {
            prompt: "consent",
            access_type: "offline",
            response_type: "code"
          }
        }
      }),
      
      CredentialsProvider({
        name: 'credentials',
        credentials: {
          email: { label: 'Email', type: 'email' },
          password: { label: 'Password', type: 'password' }
        },
        async authorize(credentials, req) {
          if (!credentials?.email || !credentials?.password) {
            return null;
          }

          try {
            const result = await deps.loginWithEmailUseCase.execute({
              email: credentials.email as string,
              password: credentials.password as string,
              ipAddress: req.headers?.['x-forwarded-for'] as string || req.ip,
              userAgent: req.headers?.['user-agent'] as string
            });

            return {
              id: result.user.id,
              email: result.user.email,
              name: result.user.name,
              avatar: result.user.avatar,
              emailVerified: result.user.emailVerified,
              sessionId: result.session.id,
              token: result.token
            };
          } catch (error) {
            console.error('Authentication failed:', error);
            return null;
          }
        }
      })
    ],

    callbacks: {
      async signIn({ user, account, profile, credentials }) {
        // Handle OAuth sign in
        if (account?.provider === 'google' && profile) {
          try {
            const result = await deps.loginWithOAuthUseCase.execute({
              provider: 'google',
              providerId: account.providerAccountId,
              email: profile.email!,
              name: profile.name,
              avatar: (profile as any).picture
            });

            // Store session info for JWT callback
            user.id = result.user.id;
            user.emailVerified = result.user.emailVerified;
            (user as any).sessionId = result.session.id;
            (user as any).token = result.token;

            return true;
          } catch (error) {
            console.error('OAuth sign in failed:', error);
            return false;
          }
        }

        // For credentials provider, user object is already populated from authorize
        return true;
      },

      async jwt({ token, user, account }) {
        // Initial sign in
        if (user) {
          token.userId = user.id;
          token.sessionId = (user as any).sessionId;
          token.emailVerified = user.emailVerified;
          token.picture = user.avatar;
        }

        return token;
      },

      async session({ session, token }) {
        if (token) {
          session.user.id = token.userId;
          session.user.emailVerified = token.emailVerified;
          session.user.avatar = token.picture as string | null;
          session.sessionId = token.sessionId;
        }

        return session;
      }
    },

    pages: {
      signIn: '/auth/login',
      signUp: '/auth/signup',
      error: '/auth/error'
    },

    session: {
      strategy: 'jwt',
      maxAge: 30 * 24 * 60 * 60, // 30 days
      updateAge: 24 * 60 * 60 // 24 hours
    },

    cookies: {
      sessionToken: {
        name: 'next-auth.session-token',
        options: {
          httpOnly: true,
          sameSite: 'lax',
          path: '/',
          secure: process.env.NODE_ENV === 'production'
        }
      }
    },

    secret: process.env.NEXTAUTH_SECRET,
    debug: process.env.NODE_ENV === 'development'
  };
}