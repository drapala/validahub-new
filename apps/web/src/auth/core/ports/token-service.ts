export interface TokenService {
  generateSessionToken(): Promise<string>;
  generateJWT(payload: Record<string, any>, expiresIn?: string): Promise<string>;
  verifyJWT(token: string): Promise<Record<string, any>>;
  generateSecureId(): string;
}

export interface JWTPayload {
  userId: string;
  email: string;
  sessionId: string;
  iat: number;
  exp: number;
}