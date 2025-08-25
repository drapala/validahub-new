import * as jose from 'jose';
import { TokenService, JWTPayload } from '../../core/ports/token-service';
import { randomBytes } from 'crypto';

export class JoseTokenService implements TokenService {
  private readonly secret: Uint8Array;
  private readonly issuer: string;
  private readonly audience: string;

  constructor(
    secret: string = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
    issuer = 'validahub',
    audience = 'validahub-web'
  ) {
    this.secret = new TextEncoder().encode(secret);
    this.issuer = issuer;
    this.audience = audience;
  }

  async generateSessionToken(): Promise<string> {
    // Generate a cryptographically secure random token
    return randomBytes(32).toString('hex');
  }

  async generateJWT(payload: Record<string, any>, expiresIn = '30d'): Promise<string> {
    const jwt = await new jose.SignJWT(payload)
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setIssuer(this.issuer)
      .setAudience(this.audience)
      .setExpirationTime(expiresIn)
      .sign(this.secret);

    return jwt;
  }

  async verifyJWT(token: string): Promise<Record<string, any>> {
    try {
      const { payload } = await jose.jwtVerify(token, this.secret, {
        issuer: this.issuer,
        audience: this.audience
      });

      return payload as Record<string, any>;
    } catch (error) {
      if (error instanceof jose.errors.JWTExpired) {
        throw new Error('Token has expired');
      } else if (error instanceof jose.errors.JWTClaimValidationFailed) {
        throw new Error('Token validation failed');
      } else if (error instanceof jose.errors.JWSInvalid) {
        throw new Error('Invalid token signature');
      } else {
        throw new Error('Invalid token');
      }
    }
  }

  generateSecureId(): string {
    // Generate a URL-safe base64 encoded random ID
    return randomBytes(16).toString('base64url');
  }
}