import { User, CreateUserInput } from '../../core/entities/user';
import { Session, CreateSessionInput } from '../../core/entities/session';
import { EmailCredential, OAuthCredential, CreateEmailCredentialInput, CreateOAuthCredentialInput } from '../../core/entities/credential';
import { UserRepository } from '../../core/ports/user-repository';
import { SessionRepository } from '../../core/ports/session-repository';
import { CredentialRepository } from '../../core/ports/credential-repository';
import { PasswordService } from '../../core/ports/password-service';
import { TokenService } from '../../core/ports/token-service';

export class MemoryUserRepository implements UserRepository {
  private readonly users = new Map<string, User>();
  private readonly emailIndex = new Map<string, string>(); // email -> id

  constructor(private readonly tokenService: TokenService) {}

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const id = this.emailIndex.get(email.toLowerCase());
    return id ? this.users.get(id) || null : null;
  }

  async create(input: CreateUserInput): Promise<User> {
    const id = this.tokenService.generateSecureId();
    const now = new Date();
    
    const user: User = {
      id,
      email: input.email.toLowerCase(),
      name: input.name || null,
      avatar: input.avatar || null,
      emailVerified: false, // Will be set to true after email verification
      createdAt: now,
      updatedAt: now
    };

    this.users.set(id, user);
    this.emailIndex.set(user.email, id);
    
    return user;
  }

  async update(id: string, updates: Partial<Omit<User, 'id' | 'createdAt'>>): Promise<User> {
    const user = this.users.get(id);
    if (!user) {
      throw new Error(`User not found: ${id}`);
    }

    // Update email index if email changed
    if (updates.email && updates.email !== user.email) {
      this.emailIndex.delete(user.email);
      this.emailIndex.set(updates.email.toLowerCase(), id);
    }

    const updatedUser: User = {
      ...user,
      ...updates,
      email: updates.email?.toLowerCase() || user.email,
      updatedAt: new Date()
    };

    this.users.set(id, updatedUser);
    return updatedUser;
  }

  async delete(id: string): Promise<void> {
    const user = this.users.get(id);
    if (user) {
      this.emailIndex.delete(user.email);
      this.users.delete(id);
    }
  }
}

export class MemorySessionRepository implements SessionRepository {
  private readonly sessions = new Map<string, Session>();
  private readonly tokenIndex = new Map<string, string>(); // token -> id
  private readonly userIndex = new Map<string, string[]>(); // userId -> sessionIds[]

  constructor(private readonly tokenService: TokenService) {}

  async findById(id: string): Promise<Session | null> {
    return this.sessions.get(id) || null;
  }

  async findByToken(token: string): Promise<Session | null> {
    const id = this.tokenIndex.get(token);
    return id ? this.sessions.get(id) || null : null;
  }

  async findByUserId(userId: string): Promise<Session[]> {
    const sessionIds = this.userIndex.get(userId) || [];
    return sessionIds.map(id => this.sessions.get(id)).filter(Boolean) as Session[];
  }

  async create(input: CreateSessionInput): Promise<Session> {
    const id = this.tokenService.generateSecureId();
    const token = await this.tokenService.generateSessionToken();
    const now = new Date();

    const session: Session = {
      id,
      userId: input.userId,
      token,
      expiresAt: input.expiresAt,
      createdAt: now,
      ipAddress: input.ipAddress,
      userAgent: input.userAgent
    };

    this.sessions.set(id, session);
    this.tokenIndex.set(token, id);
    
    // Update user index
    const userSessions = this.userIndex.get(input.userId) || [];
    userSessions.push(id);
    this.userIndex.set(input.userId, userSessions);

    return session;
  }

  async update(id: string, updates: Partial<Omit<Session, 'id' | 'createdAt'>>): Promise<Session> {
    const session = this.sessions.get(id);
    if (!session) {
      throw new Error(`Session not found: ${id}`);
    }

    const updatedSession: Session = {
      ...session,
      ...updates
    };

    this.sessions.set(id, updatedSession);
    return updatedSession;
  }

  async delete(id: string): Promise<void> {
    const session = this.sessions.get(id);
    if (session) {
      this.tokenIndex.delete(session.token);
      
      // Update user index
      const userSessions = this.userIndex.get(session.userId) || [];
      const index = userSessions.indexOf(id);
      if (index > -1) {
        userSessions.splice(index, 1);
        if (userSessions.length === 0) {
          this.userIndex.delete(session.userId);
        } else {
          this.userIndex.set(session.userId, userSessions);
        }
      }
      
      this.sessions.delete(id);
    }
  }

  async deleteByUserId(userId: string): Promise<void> {
    const sessionIds = this.userIndex.get(userId) || [];
    for (const id of sessionIds) {
      await this.delete(id);
    }
  }

  async deleteExpired(): Promise<number> {
    const now = new Date();
    let deletedCount = 0;
    
    for (const [id, session] of this.sessions.entries()) {
      if (session.expiresAt < now) {
        await this.delete(id);
        deletedCount++;
      }
    }
    
    return deletedCount;
  }
}

export class MemoryCredentialRepository implements CredentialRepository {
  private readonly emailCredentials = new Map<string, EmailCredential>(); // userId -> credential
  private readonly oauthCredentials = new Map<string, OAuthCredential[]>(); // userId -> credentials[]
  private readonly emailIndex = new Map<string, string>(); // email -> userId
  private readonly oauthIndex = new Map<string, string>(); // provider:providerId -> userId

  constructor(private readonly passwordService: PasswordService) {}

  async findEmailCredentialByEmail(email: string): Promise<EmailCredential | null> {
    const userId = this.emailIndex.get(email.toLowerCase());
    return userId ? this.emailCredentials.get(userId) || null : null;
  }

  async findOAuthCredential(provider: string, providerId: string): Promise<OAuthCredential | null> {
    const key = `${provider}:${providerId}`;
    const userId = this.oauthIndex.get(key);
    if (!userId) return null;

    const credentials = this.oauthCredentials.get(userId) || [];
    return credentials.find(c => c.provider === provider && c.providerId === providerId) || null;
  }

  async findOAuthCredentialsByUserId(userId: string): Promise<OAuthCredential[]> {
    return this.oauthCredentials.get(userId) || [];
  }

  async createEmailCredential(userId: string, input: CreateEmailCredentialInput): Promise<EmailCredential> {
    const hashedPassword = await this.passwordService.hash(input.password);
    const now = new Date();

    const credential: EmailCredential = {
      userId,
      email: input.email.toLowerCase(),
      hashedPassword,
      createdAt: now,
      updatedAt: now
    };

    this.emailCredentials.set(userId, credential);
    this.emailIndex.set(credential.email, userId);
    
    return credential;
  }

  async createOAuthCredential(userId: string, input: CreateOAuthCredentialInput): Promise<OAuthCredential> {
    const now = new Date();
    const key = `${input.provider}:${input.providerId}`;

    const credential: OAuthCredential = {
      userId,
      provider: input.provider,
      providerId: input.providerId,
      email: input.email.toLowerCase(),
      name: input.name,
      avatar: input.avatar,
      createdAt: now,
      updatedAt: now
    };

    const userCredentials = this.oauthCredentials.get(userId) || [];
    userCredentials.push(credential);
    this.oauthCredentials.set(userId, userCredentials);
    this.oauthIndex.set(key, userId);
    
    return credential;
  }

  async updateEmailCredential(userId: string, hashedPassword: string): Promise<EmailCredential> {
    const credential = this.emailCredentials.get(userId);
    if (!credential) {
      throw new Error(`Email credential not found for user: ${userId}`);
    }

    const updatedCredential: EmailCredential = {
      ...credential,
      hashedPassword,
      updatedAt: new Date()
    };

    this.emailCredentials.set(userId, updatedCredential);
    return updatedCredential;
  }

  async deleteEmailCredential(userId: string): Promise<void> {
    const credential = this.emailCredentials.get(userId);
    if (credential) {
      this.emailIndex.delete(credential.email);
      this.emailCredentials.delete(userId);
    }
  }

  async deleteOAuthCredential(userId: string, provider: string): Promise<void> {
    const credentials = this.oauthCredentials.get(userId) || [];
    const filtered = credentials.filter(c => c.provider !== provider);
    
    if (filtered.length === 0) {
      this.oauthCredentials.delete(userId);
    } else {
      this.oauthCredentials.set(userId, filtered);
    }

    // Update index
    const toDelete = credentials.find(c => c.provider === provider);
    if (toDelete) {
      const key = `${toDelete.provider}:${toDelete.providerId}`;
      this.oauthIndex.delete(key);
    }
  }

  async deleteAllCredentials(userId: string): Promise<void> {
    await this.deleteEmailCredential(userId);
    
    const oauthCredentials = this.oauthCredentials.get(userId) || [];
    for (const credential of oauthCredentials) {
      const key = `${credential.provider}:${credential.providerId}`;
      this.oauthIndex.delete(key);
    }
    
    this.oauthCredentials.delete(userId);
  }
}