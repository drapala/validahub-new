import { NextRequest, NextResponse } from 'next/server';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';
import { InvalidTokenError, SessionExpiredError, UserNotFoundError } from '@/src/auth/core/errors/auth-errors';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { message: 'Missing or invalid authorization header' },
        { status: 401 }
      );
    }

    const token = authHeader.substring(7); // Remove "Bearer " prefix
    const authContainer = getAuthContainer();
    
    const result = await authContainer.verifySessionUseCase.execute({ token });

    return NextResponse.json({
      user: result.user,
      session: result.session,
      isValid: result.isValid
    });
  } catch (error) {
    console.error('Session verification error:', error);

    if (error instanceof InvalidTokenError || 
        error instanceof SessionExpiredError || 
        error instanceof UserNotFoundError) {
      return NextResponse.json(
        { message: error.message, code: error.code },
        { status: error.statusCode }
      );
    }

    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}