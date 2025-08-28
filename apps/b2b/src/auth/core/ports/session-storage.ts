export interface SessionStorage {
  getSession(key: string): Promise<SessionData | null>;
  setSession(key: string, data: SessionData, ttl?: number): Promise<void>;
  deleteSession(key: string): Promise<void>;
  extendSession(key: string, ttl: number): Promise<void>;
}

export interface SessionData {
  userId: string;
  email: string;
  name: string | null;
  avatar: string | null;
  sessionId: string;
  createdAt: Date;
  expiresAt: Date;
}