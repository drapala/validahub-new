import { SessionRepository } from '../ports/session-repository';
import { SessionStorage } from '../ports/session-storage';
import { TokenService } from '../ports/token-service';
import { InvalidTokenError, SessionExpiredError } from '../errors/auth-errors';

export interface LogoutInput {
  readonly token: string;
}

export interface LogoutOutput {
  readonly success: boolean;
}

export class LogoutUseCase {
  constructor(
    private readonly sessionRepository: SessionRepository,
    private readonly sessionStorage: SessionStorage,
    private readonly tokenService: TokenService
  ) {}

  async execute(input: LogoutInput): Promise<LogoutOutput> {
    try {
      // Verify and decode JWT
      const payload = await this.tokenService.verifyJWT(input.token);
      const sessionId = payload.sessionId as string;

      if (!sessionId) {
        throw new InvalidTokenError('Session ID not found in token');
      }

      // Find session
      const session = await this.sessionRepository.findById(sessionId);
      if (!session) {
        throw new InvalidTokenError('Session not found');
      }

      // Check if session is expired
      if (session.expiresAt < new Date()) {
        throw new SessionExpiredError();
      }

      // Delete session from database
      await this.sessionRepository.delete(sessionId);

      // Delete from session storage
      await this.sessionStorage.deleteSession(`session:${sessionId}`);
      await this.sessionStorage.deleteSession(`user:${session.userId}`);

      return { success: true };
    } catch (error) {
      if (error instanceof InvalidTokenError || error instanceof SessionExpiredError) {
        throw error;
      }
      
      // For any other error, treat as invalid token
      throw new InvalidTokenError('Failed to logout: invalid token');
    }
  }
}