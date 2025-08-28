import { render, screen, fireEvent } from '@testing-library/react'
import { SessionProvider } from 'next-auth/react'
import Pricing from '@/components/ui/Pricing'
import { useRouter } from 'next/navigation'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock next-auth
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
  SessionProvider: ({ children }: { children: React.ReactNode }) => children,
}))

describe('Pricing Component', () => {
  const mockPush = jest.fn()
  
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders all three pricing tiers', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Pro')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('displays correct prices for monthly billing', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    expect(screen.getByText('Grátis')).toBeInTheDocument()
    expect(screen.getByText('R$ 199')).toBeInTheDocument()
    expect(screen.getByText('Personalizado')).toBeInTheDocument()
  })

  it('toggles between monthly and annual pricing', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    // Initially shows monthly price
    expect(screen.getByText('R$ 199')).toBeInTheDocument()
    
    // Find and click the switch
    const switchElement = screen.getByRole('switch')
    fireEvent.click(switchElement)
    
    // Should show annual price (10% discount)
    expect(screen.getByText('R$ 179')).toBeInTheDocument()
  })

  it('highlights the Pro plan as most popular', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    // Check for the "Mais popular" badge
    expect(screen.getByText('Mais popular')).toBeInTheDocument()
  })

  it('shows auth modal when clicking CTA without session', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    // Click on "Criar conta grátis" button
    const ctaButton = screen.getByText('Criar conta grátis')
    fireEvent.click(ctaButton)
    
    // Should open auth modal
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('navigates to upload when clicking CTA with session', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({
      data: { user: { email: 'test@example.com' } },
      status: 'authenticated',
    })
    
    render(<Pricing />)
    
    // Click on "Criar conta grátis" button
    const ctaButton = screen.getByText('Criar conta grátis')
    fireEvent.click(ctaButton)
    
    // Should navigate to upload page
    expect(mockPush).toHaveBeenCalledWith('/upload')
  })

  it('opens email for Enterprise plan', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    // Mock window.location.href
    delete (window as any).location
    window.location = { href: '' } as any
    
    render(<Pricing />)
    
    // Click on "Falar com vendas" button
    const enterpriseButton = screen.getByText('Falar com vendas')
    fireEvent.click(enterpriseButton)
    
    // Should set mailto link
    expect(window.location.href).toContain('mailto:vendas@validahub.com')
  })

  it('displays all features for each plan', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
    
    render(<Pricing />)
    
    // Starter features
    expect(screen.getByText('100 validações/mês')).toBeInTheDocument()
    expect(screen.getByText('Upload até 1k linhas')).toBeInTheDocument()
    
    // Pro features
    expect(screen.getByText('Validações ilimitadas')).toBeInTheDocument()
    expect(screen.getByText('Jobs assíncronos')).toBeInTheDocument()
    
    // Enterprise features
    expect(screen.getByText('SSO/SAML')).toBeInTheDocument()
    expect(screen.getByText('Ambientes dedicados')).toBeInTheDocument()
  })

  it('navigates to billing page for Pro plan when authenticated', () => {
    const { useSession } = require('next-auth/react')
    useSession.mockReturnValue({
      data: { user: { email: 'test@example.com' } },
      status: 'authenticated',
    })
    
    render(<Pricing />)
    
    // Click on "Assinar Pro" button
    const proButton = screen.getByText('Assinar Pro')
    fireEvent.click(proButton)
    
    // Should navigate to billing page with plan parameter
    expect(mockPush).toHaveBeenCalledWith('/settings/billing?plan=pro')
  })
})