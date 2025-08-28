export interface EmailCredential {
  readonly userId: string;
  readonly email: string;
  readonly hashedPassword: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface OAuthCredential {
  readonly userId: string;
  readonly provider: 'google' | 'github' | 'microsoft';
  readonly providerId: string;
  readonly email: string;
  readonly name?: string;
  readonly avatar?: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateEmailCredentialInput {
  readonly email: string;
  readonly password: string;
}

export interface CreateOAuthCredentialInput {
  readonly provider: 'google' | 'github' | 'microsoft';
  readonly providerId: string;
  readonly email: string;
  readonly name?: string;
  readonly avatar?: string;
}