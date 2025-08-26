import { NextRequest, NextResponse } from 'next/server';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';
import { InvalidCredentialsError, UserNotFoundError, EmailVerificationRequiredError } from '@/src/auth/core/errors/auth-errors';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = loginSchema.parse(body);

    const authContainer = getAuthContainer();
    
    const result = await authContainer.loginWithEmailUseCase.execute({
      email,
      password,
      ipAddress: request.ip || request.headers.get('x-forwarded-for') || undefined,
      userAgent: request.headers.get('user-agent') || undefined
    });

    return NextResponse.json({
      user: result.user,
      session: result.session,
      token: result.token
    });
  } catch (error) {
    console.error('Login error:', error);

    if (error instanceof InvalidCredentialsError || 
        error instanceof UserNotFoundError || 
        error instanceof EmailVerificationRequiredError) {
      return NextResponse.json(
        { message: error.message, code: error.code },
        { status: error.statusCode }
      );
    }

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { message: 'Invalid input', errors: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}