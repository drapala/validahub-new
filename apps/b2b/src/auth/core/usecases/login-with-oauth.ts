import { User } from '../entities/user';
import { Session } from '../entities/session';
import { UserRepository } from '../ports/user-repository';
import { CredentialRepository } from '../ports/credential-repository';
import { SessionRepository } from '../ports/session-repository';
import { TokenService } from '../ports/token-service';

export interface LoginWithOAuthInput {
  readonly provider: 'google' | 'github' | 'microsoft';
  readonly providerId: string;
  readonly email: string;
  readonly name?: string;
  readonly avatar?: string;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}

export interface LoginWithOAuthOutput {
  readonly user: User;
  readonly session: Session;
  readonly token: string;
  readonly isNewUser: boolean;
}

export class LoginWithOAuthUseCase {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly credentialRepository: CredentialRepository,
    private readonly sessionRepository: SessionRepository,
    private readonly tokenService: TokenService
  ) {}

  async execute(input: LoginWithOAuthInput): Promise<LoginWithOAuthOutput> {
    let user: User;
    let isNewUser = false;

    // Try to find existing OAuth credential
    const existingCredential = await this.credentialRepository.findOAuthCredential(input.provider, input.providerId);
    
    if (existingCredential) {
      // User exists, get their profile
      user = await this.userRepository.findById(existingCredential.userId);
      if (!user) {
        throw new Error('User not found for existing OAuth credential');
      }
      
      // Update user info if needed
      if (input.name !== user.name || input.avatar !== user.avatar) {
        user = await this.userRepository.update(user.id, {
          name: input.name || user.name,
          avatar: input.avatar || user.avatar,
          updatedAt: new Date()
        });
      }
    } else {
      // Check if user exists by email
      const existingUser = await this.userRepository.findByEmail(input.email);
      
      if (existingUser) {
        // Link OAuth credential to existing user
        user = existingUser;
        await this.credentialRepository.createOAuthCredential(user.id, {
          provider: input.provider,
          providerId: input.providerId,
          email: input.email,
          name: input.name,
          avatar: input.avatar
        });
      } else {
        // Create new user
        isNewUser = true;
        user = await this.userRepository.create({
          email: input.email,
          name: input.name || null,
          avatar: input.avatar || null
        });

        // Create OAuth credential
        await this.credentialRepository.createOAuthCredential(user.id, {
          provider: input.provider,
          providerId: input.providerId,
          email: input.email,
          name: input.name,
          avatar: input.avatar
        });
      }
    }

    // Create session
    const sessionToken = await this.tokenService.generateSessionToken();
    const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days
    
    const session = await this.sessionRepository.create({
      userId: user.id,
      expiresAt,
      ipAddress: input.ipAddress,
      userAgent: input.userAgent
    });

    // Generate JWT
    const jwtToken = await this.tokenService.generateJWT({
      userId: user.id,
      email: user.email,
      sessionId: session.id
    }, '30d');

    return {
      user,
      session,
      token: jwtToken,
      isNewUser
    };
  }
}