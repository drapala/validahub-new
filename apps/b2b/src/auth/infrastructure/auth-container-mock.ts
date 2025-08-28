/**
 * Mock authentication container for development.
 * This provides working authentication without a backend server.
 */

import type { User } from '../core/entities/user';
import type { Session } from '../core/entities/session';
import type { Credential } from '../core/entities/credential';
import { InvalidCredentialsError } from '../core/errors/auth-errors';

// Mock storage
const mockUsers = new Map<string, { user: User; password: string }>();
const mockSessions = new Map<string, Session>();
const mockTokens = new Map<string, { userId: string; sessionId: string }>();

// Mock use case implementations
class MockLoginWithEmailUseCase {
  async execute({ email, password }: { email: string; password: string }) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const userRecord = mockUsers.get(email);
    
    if (!userRecord) {
      throw new InvalidCredentialsError('Invalid email or password');
    }

    if (userRecord.password !== password) {
      throw new InvalidCredentialsError('Invalid email or password');
    }

    // Create session
    const sessionId = `session_${Date.now()}`;
    const session: Session = {
      id: sessionId,
      userId: userRecord.user.id,
      token: `token_${Date.now()}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    mockSessions.set(sessionId, session);

    // Create token
    const token = `mock_token_${Date.now()}`;
    mockTokens.set(token, { userId: userRecord.user.id, sessionId });

    return {
      user: userRecord.user,
      session,
      token
    };
  }
}

class MockRegisterWithEmailUseCase {
  async execute({ email, password, name }: { email: string; password: string; name?: string }) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (mockUsers.has(email)) {
      throw new InvalidCredentialsError('Email already registered');
    }

    // Create new user
    const userId = `user_${Date.now()}`;
    const user: User = {
      id: userId,
      email,
      name: name || email.split('@')[0],
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(name || email)}`,
      emailVerified: true, // verified for mock
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Store user with password
    mockUsers.set(email, { user, password });

    // Auto-login after registration
    const sessionId = `session_${Date.now()}`;
    const session: Session = {
      id: sessionId,
      userId: userId,
      token: `token_${Date.now()}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    mockSessions.set(sessionId, session);

    const token = `mock_token_${Date.now()}`;
    mockTokens.set(token, { userId, sessionId });

    return {
      user,
      session,
      token
    };
  }
}

class MockLogoutUseCase {
  async execute({ sessionId }: { sessionId: string }) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));

    // Remove session
    mockSessions.delete(sessionId);

    // Remove associated tokens
    for (const [token, data] of mockTokens.entries()) {
      if (data.sessionId === sessionId) {
        mockTokens.delete(token);
      }
    }
  }
}

class MockVerifySessionUseCase {
  async execute({ token }: { token: string }) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));

    const tokenData = mockTokens.get(token);
    if (!tokenData) {
      throw new InvalidCredentialsError('Invalid token');
    }

    const session = mockSessions.get(tokenData.sessionId);
    if (!session) {
      throw new InvalidCredentialsError('Session expired');
    }

    // Check if session expired
    if (new Date() > session.expiresAt) {
      mockSessions.delete(tokenData.sessionId);
      mockTokens.delete(token);
      throw new InvalidCredentialsError('Session expired');
    }

    // Find user
    for (const [email, record] of mockUsers.entries()) {
      if (record.user.id === tokenData.userId) {
        return {
          user: record.user,
          session
        };
      }
    }

    throw new InvalidCredentialsError('User not found');
  }
}

// Add some demo users
const demoUser: User = {
  id: 'demo_user_1',
  email: 'demo@validahub.com',
  name: 'Demo User',
  avatar: 'https://ui-avatars.com/api/?name=Demo+User',
  emailVerified: true,
  createdAt: new Date(),
  updatedAt: new Date()
};

mockUsers.set('demo@validahub.com', {
  user: demoUser,
  password: 'demo123'
});

const testUser: User = {
  id: 'test_user_1',
  email: 'test@example.com',
  name: 'Test User',
  avatar: 'https://ui-avatars.com/api/?name=Test+User',
  emailVerified: true,
  createdAt: new Date(),
  updatedAt: new Date()
};

mockUsers.set('test@example.com', {
  user: testUser,
  password: 'test123'
});

// Add a simple admin user for testing
const adminUser: User = {
  id: 'admin_user_1',
  email: 'admin@validahub.com',
  name: 'Admin User',
  avatar: 'https://ui-avatars.com/api/?name=Admin+User',
  emailVerified: true,
  createdAt: new Date(),
  updatedAt: new Date()
};

mockUsers.set('admin@validahub.com', {
  user: adminUser,
  password: 'admin123'
});

export const mockAuthContainer = {
  loginWithEmailUseCase: new MockLoginWithEmailUseCase(),
  registerWithEmailUseCase: new MockRegisterWithEmailUseCase(),
  logoutUseCase: new MockLogoutUseCase(),
  verifySessionUseCase: new MockVerifySessionUseCase(),
};

export function getMockAuthContainer() {
  console.log('Using mock authentication container');
  console.log('Demo users:');
  console.log('  - demo@validahub.com / demo123');
  console.log('  - test@example.com / test123');
  console.log('  - admin@validahub.com / admin123');
  return mockAuthContainer;
}