export interface Session {
  readonly id: string;
  readonly userId: string;
  readonly token: string;
  readonly expiresAt: Date;
  readonly createdAt: Date;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}

export interface CreateSessionInput {
  readonly userId: string;
  readonly expiresAt: Date;
  readonly ipAddress?: string;
  readonly userAgent?: string;
}