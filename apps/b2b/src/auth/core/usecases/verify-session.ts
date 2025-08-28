import { User } from '../entities/user';
import { Session } from '../entities/session';
import { UserRepository } from '../ports/user-repository';
import { SessionRepository } from '../ports/session-repository';
import { SessionStorage } from '../ports/session-storage';
import { TokenService } from '../ports/token-service';
import { InvalidTokenError, SessionExpiredError, UserNotFoundError } from '../errors/auth-errors';

export interface VerifySessionInput {
  readonly token: string;
}

export interface VerifySessionOutput {
  readonly user: User;
  readonly session: Session;
  readonly isValid: boolean;
}

export class VerifySessionUseCase {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly sessionRepository: SessionRepository,
    private readonly sessionStorage: SessionStorage,
    private readonly tokenService: TokenService
  ) {}

  async execute(input: VerifySessionInput): Promise<VerifySessionOutput> {
    try {
      // Verify and decode JWT
      const payload = await this.tokenService.verifyJWT(input.token);
      const userId = payload.userId as string;
      const sessionId = payload.sessionId as string;

      if (!userId || !sessionId) {
        throw new InvalidTokenError('User ID or Session ID not found in token');
      }

      // Try to get from session storage first (faster)
      const cachedSession = await this.sessionStorage.getSession(`session:${sessionId}`);
      
      if (cachedSession && cachedSession.expiresAt > new Date()) {
        // Get user from cache or database
        const user = await this.userRepository.findById(userId);
        if (!user) {
          throw new UserNotFoundError(userId);
        }

        // Convert cached session to Session entity
        const session: Session = {
          id: sessionId,
          userId: cachedSession.userId,
          token: input.token,
          expiresAt: cachedSession.expiresAt,
          createdAt: cachedSession.createdAt,
        };

        return {
          user,
          session,
          isValid: true
        };
      }

      // Fallback to database
      const session = await this.sessionRepository.findById(sessionId);
      if (!session) {
        throw new InvalidTokenError('Session not found');
      }

      // Check if session is expired
      if (session.expiresAt < new Date()) {
        // Clean up expired session
        await this.sessionRepository.delete(sessionId);
        await this.sessionStorage.deleteSession(`session:${sessionId}`);
        throw new SessionExpiredError();
      }

      // Get user
      const user = await this.userRepository.findById(userId);
      if (!user) {
        throw new UserNotFoundError(userId);
      }

      // Update session storage
      await this.sessionStorage.setSession(`session:${sessionId}`, {
        userId: user.id,
        email: user.email,
        name: user.name,
        avatar: user.avatar,
        sessionId: session.id,
        createdAt: session.createdAt,
        expiresAt: session.expiresAt
      });

      return {
        user,
        session,
        isValid: true
      };
    } catch (error) {
      if (error instanceof InvalidTokenError || 
          error instanceof SessionExpiredError || 
          error instanceof UserNotFoundError) {
        throw error;
      }
      
      // For JWT verification errors
      throw new InvalidTokenError('Failed to verify session');
    }
  }
}