import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/app/api/auth/[...nextauth]/route'
import { redirect } from 'next/navigation'

export async function getSession() {
  const session = await getServerSession(authOptions)
  return session
}

export async function getCurrentUser() {
  const session = await getSession()
  return session?.user
}

export async function requireAuth() {
  const session = await getSession()
  
  if (!session) {
    redirect('/')
  }
  
  return session
}

export async function requireNoAuth() {
  const session = await getSession()
  
  if (session) {
    redirect('/upload')
  }
  
  return null
}