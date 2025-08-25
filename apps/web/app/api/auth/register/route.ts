import { NextRequest, NextResponse } from 'next/server';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';
import { UserAlreadyExistsError } from '@/src/auth/core/errors/auth-errors';
import { z } from 'zod';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/\d/, 'Password must contain at least one number')
    .regex(/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/, 'Password must contain at least one special character'),
  name: z.string().min(2).optional()
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, name } = registerSchema.parse(body);

    const authContainer = getAuthContainer();
    
    const result = await authContainer.registerWithEmailUseCase.execute({
      email,
      password,
      name,
      ipAddress: request.ip || request.headers.get('x-forwarded-for') || undefined,
      userAgent: request.headers.get('user-agent') || undefined
    });

    return NextResponse.json({
      user: result.user,
      session: result.session,
      token: result.token
    });
  } catch (error) {
    console.error('Registration error:', error);

    if (error instanceof UserAlreadyExistsError) {
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

    if (error instanceof Error && error.message.includes('Password validation failed')) {
      return NextResponse.json(
        { message: error.message },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}