import { Session, CreateSessionInput } from '../entities/session';

export interface SessionRepository {
  findById(id: string): Promise<Session | null>;
  findByToken(token: string): Promise<Session | null>;
  findByUserId(userId: string): Promise<Session[]>;
  create(input: CreateSessionInput): Promise<Session>;
  update(id: string, updates: Partial<Omit<Session, 'id' | 'createdAt'>>): Promise<Session>;
  delete(id: string): Promise<void>;
  deleteByUserId(userId: string): Promise<void>;
  deleteExpired(): Promise<number>;
}