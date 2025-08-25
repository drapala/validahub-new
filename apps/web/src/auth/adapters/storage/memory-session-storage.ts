import { SessionStorage, SessionData } from '../../core/ports/session-storage';

export class MemorySessionStorage implements SessionStorage {
  private readonly storage = new Map<string, { data: SessionData; expiresAt: number }>();
  private readonly cleanupInterval: NodeJS.Timeout;

  constructor(cleanupIntervalMs = 5 * 60 * 1000) { // 5 minutes
    // Clean up expired sessions periodically
    this.cleanupInterval = setInterval(() => {
      this.cleanupExpired();
    }, cleanupIntervalMs);
  }

  async getSession(key: string): Promise<SessionData | null> {
    const entry = this.storage.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.storage.delete(key);
      return null;
    }

    return entry.data;
  }

  async setSession(key: string, data: SessionData, ttl = 30 * 24 * 60 * 60 * 1000): Promise<void> {
    const expiresAt = Date.now() + ttl;
    this.storage.set(key, { data, expiresAt });
  }

  async deleteSession(key: string): Promise<void> {
    this.storage.delete(key);
  }

  async extendSession(key: string, ttl: number): Promise<void> {
    const entry = this.storage.get(key);
    if (entry) {
      entry.expiresAt = Date.now() + ttl;
    }
  }

  private cleanupExpired(): void {
    const now = Date.now();
    for (const [key, entry] of this.storage.entries()) {
      if (now > entry.expiresAt) {
        this.storage.delete(key);
      }
    }
  }

  // Cleanup method for graceful shutdown
  cleanup(): void {
    clearInterval(this.cleanupInterval);
    this.storage.clear();
  }
}