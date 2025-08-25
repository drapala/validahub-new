import { User } from '../entities/user';
import { Session } from '../entities/session';
import { UserRepository } from '../ports/user-repository';
import { CredentialRepository } from '../ports/credential-repository';
import { SessionRepository } from '../ports/session-repository';
import { PasswordService } from '../ports/password-service';
import { TokenService } from '../ports/token-service';
import { UserAlreadyExistsError } from '../errors/auth-errors';

export interface RegisterWithEmailInput {
  readonly email: string;
  readonly password: string;
  readonly name?: string;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}

export interface RegisterWithEmailOutput {
  readonly user: User;
  readonly session: Session;
  readonly token: string;
}

export class RegisterWithEmailUseCase {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly credentialRepository: CredentialRepository,
    private readonly sessionRepository: SessionRepository,
    private readonly passwordService: PasswordService,
    private readonly tokenService: TokenService
  ) {}

  async execute(input: RegisterWithEmailInput): Promise<RegisterWithEmailOutput> {
    // Check if user already exists
    const existingUser = await this.userRepository.findByEmail(input.email);
    if (existingUser) {
      throw new UserAlreadyExistsError(input.email);
    }

    // Validate password
    const passwordValidation = await this.passwordService.validate(input.password);
    if (!passwordValidation.isValid) {
      throw new Error(`Password validation failed: ${passwordValidation.errors.join(', ')}`);
    }

    // Create user
    const user = await this.userRepository.create({
      email: input.email,
      name: input.name || null
    });

    // Create email credential
    await this.credentialRepository.createEmailCredential(user.id, {
      email: input.email,
      password: input.password
    });

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