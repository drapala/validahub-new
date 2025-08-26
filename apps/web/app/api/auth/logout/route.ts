import { NextRequest, NextResponse } from 'next/server';
import { getAuthContainer } from '@/src/auth/infrastructure/auth-container';
import { InvalidTokenError, SessionExpiredError } from '@/src/auth/core/errors/auth-errors';

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
    
    const result = await authContainer.logoutUseCase.execute({ token });

    return NextResponse.json({ success: result.success });
  } catch (error) {
    console.error('Logout error:', error);

    if (error instanceof InvalidTokenError || error instanceof SessionExpiredError) {
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