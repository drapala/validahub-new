import { User } from '../entities/user';
import { Session } from '../entities/session';
import { UserRepository } from '../ports/user-repository';
import { CredentialRepository } from '../ports/credential-repository';
import { SessionRepository } from '../ports/session-repository';
import { PasswordService } from '../ports/password-service';
import { TokenService } from '../ports/token-service';
import { InvalidCredentialsError, UserNotFoundError, EmailVerificationRequiredError } from '../errors/auth-errors';

export interface LoginWithEmailInput {
  readonly email: string;
  readonly password: string;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}

export interface LoginWithEmailOutput {
  readonly user: User;
  readonly session: Session;
  readonly token: string;
}

export class LoginWithEmailUseCase {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly credentialRepository: CredentialRepository,
    private readonly sessionRepository: SessionRepository,
    private readonly passwordService: PasswordService,
    private readonly tokenService: TokenService
  ) {}

  async execute(input: LoginWithEmailInput): Promise<LoginWithEmailOutput> {
    // Find user by email
    const user = await this.userRepository.findByEmail(input.email);
    if (!user) {
      throw new UserNotFoundError(input.email);
    }

    // Check email verification
    if (!user.emailVerified) {
      throw new EmailVerificationRequiredError();
    }

    // Find email credential
    const credential = await this.credentialRepository.findEmailCredentialByEmail(input.email);
    if (!credential) {
      throw new InvalidCredentialsError();
    }

    // Verify password
    const isPasswordValid = await this.passwordService.verify(input.password, credential.hashedPassword);
    if (!isPasswordValid) {
      throw new InvalidCredentialsError();
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
      token: jwtToken
    };
  }
}