export abstract class AuthError extends Error {
  abstract readonly code: string;
  abstract readonly statusCode: number;
  
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class InvalidCredentialsError extends AuthError {
  readonly code = 'INVALID_CREDENTIALS';
  readonly statusCode = 401;
  
  constructor(message = 'Invalid email or password') {
    super(message);
  }
}

export class UserAlreadyExistsError extends AuthError {
  readonly code = 'USER_ALREADY_EXISTS';
  readonly statusCode = 409;
  
  constructor(email: string) {
    super(`User with email ${email} already exists`);
  }
}

export class UserNotFoundError extends AuthError {
  readonly code = 'USER_NOT_FOUND';
  readonly statusCode = 404;
  
  constructor(identifier: string) {
    super(`User not found: ${identifier}`);
  }
}

export class InvalidTokenError extends AuthError {
  readonly code = 'INVALID_TOKEN';
  readonly statusCode = 401;
  
  constructor(message = 'Invalid or expired token') {
    super(message);
  }
}

export class SessionExpiredError extends AuthError {
  readonly code = 'SESSION_EXPIRED';
  readonly statusCode = 401;
  
  constructor(message = 'Session has expired') {
    super(message);
  }
}

export class InsufficientPrivilegesError extends AuthError {
  readonly code = 'INSUFFICIENT_PRIVILEGES';
  readonly statusCode = 403;
  
  constructor(message = 'Insufficient privileges to perform this action') {
    super(message);
  }
}

export class EmailVerificationRequiredError extends AuthError {
  readonly code = 'EMAIL_VERIFICATION_REQUIRED';
  readonly statusCode = 401;
  
  constructor(message = 'Email verification is required') {
    super(message);
  }
}

export class RateLimitExceededError extends AuthError {
  readonly code = 'RATE_LIMIT_EXCEEDED';
  readonly statusCode = 429;
  
  constructor(retryAfter: number) {
    super(`Too many attempts. Retry after ${retryAfter} seconds`);
  }
}