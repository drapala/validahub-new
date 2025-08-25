import * as bcrypt from 'bcryptjs';
import { PasswordService, ValidationResult, PasswordRequirements } from '../../core/ports/password-service';

export class BcryptPasswordService implements PasswordService {
  private readonly saltRounds: number;
  private readonly requirements: PasswordRequirements;

  constructor(
    saltRounds = 12,
    requirements: PasswordRequirements = {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true
    }
  ) {
    this.saltRounds = saltRounds;
    this.requirements = requirements;
  }

  async hash(password: string): Promise<string> {
    return bcrypt.hash(password, this.saltRounds);
  }

  async verify(password: string, hashedPassword: string): Promise<boolean> {
    return bcrypt.compare(password, hashedPassword);
  }

  async validate(password: string): Promise<ValidationResult> {
    const errors: string[] = [];

    // Check minimum length
    if (password.length < this.requirements.minLength) {
      errors.push(`Password must be at least ${this.requirements.minLength} characters long`);
    }

    // Check for uppercase letter
    if (this.requirements.requireUppercase && !/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    // Check for lowercase letter
    if (this.requirements.requireLowercase && !/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    // Check for numbers
    if (this.requirements.requireNumbers && !/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    // Check for special characters
    if (this.requirements.requireSpecialChars && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    // Check for common weak passwords
    const commonPasswords = [
      'password', '123456', '123456789', '12345678', '12345',
      '1234567', '1234567890', 'qwerty', 'abc123', 'password123'
    ];
    
    if (commonPasswords.includes(password.toLowerCase())) {
      errors.push('Password is too common and easily guessable');
    }

    // Check for repeated characters
    if (/(.)\1{3,}/.test(password)) {
      errors.push('Password cannot contain more than 3 consecutive identical characters');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}