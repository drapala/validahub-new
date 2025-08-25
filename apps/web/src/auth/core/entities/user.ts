export interface User {
  readonly id: string;
  readonly email: string;
  readonly name: string | null;
  readonly avatar: string | null;
  readonly emailVerified: boolean;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface CreateUserInput {
  readonly email: string;
  readonly name?: string;
  readonly avatar?: string;
}