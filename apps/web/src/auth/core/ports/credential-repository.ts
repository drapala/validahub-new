import { EmailCredential, OAuthCredential, CreateEmailCredentialInput, CreateOAuthCredentialInput } from '../entities/credential';

export interface CredentialRepository {
  findEmailCredentialByEmail(email: string): Promise<EmailCredential | null>;
  findOAuthCredential(provider: string, providerId: string): Promise<OAuthCredential | null>;
  findOAuthCredentialsByUserId(userId: string): Promise<OAuthCredential[]>;
  
  createEmailCredential(userId: string, input: CreateEmailCredentialInput): Promise<EmailCredential>;
  createOAuthCredential(userId: string, input: CreateOAuthCredentialInput): Promise<OAuthCredential>;
  
  updateEmailCredential(userId: string, hashedPassword: string): Promise<EmailCredential>;
  
  deleteEmailCredential(userId: string): Promise<void>;
  deleteOAuthCredential(userId: string, provider: string): Promise<void>;
  deleteAllCredentials(userId: string): Promise<void>;
}