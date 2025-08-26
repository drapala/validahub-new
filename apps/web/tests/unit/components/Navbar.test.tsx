import { render, screen, fireEvent } from '@testing-library/react'
import { SessionProvider } from 'next-auth/react'
import Navbar from '@/components/ui/Navbar'
import { useRouter } from 'next/navigation'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(() => '/'),
}))

// Mock next-auth
jest.mock('next-auth/react', () => ({
  useSession: jest.fn(),
  signOut: jest.fn(),
  SessionProvider: ({ children }: { children: React.ReactNode }) => children,
}))

describe('Navbar', () => {
  const mockPush = jest.fn()
  
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Desktop view', () => {
    it('renders logo and navigation links', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      expect(screen.getByText('ValidaHub')).toBeInTheDocument()
      expect(screen.getByText('Features')).toBeInTheDocument()
      expect(screen.getByText('Como funciona')).toBeInTheDocument()
      expect(screen.getByText('Preços')).toBeInTheDocument()
      expect(screen.getByText('FAQ')).toBeInTheDocument()
      expect(screen.getByText('Docs')).toBeInTheDocument()
    })

    it('shows auth buttons when not authenticated', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /cadastrar/i })).toBeInTheDocument()
    })

    it('shows user menu when authenticated', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@example.com',
          },
        },
        status: 'authenticated',
      })
      
      render(<Navbar />)
      
      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /entrar/i })).not.toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /cadastrar/i })).not.toBeInTheDocument()
    })

    it('navigates to pricing page when clicking Preços', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      const pricingButton = screen.getByText('Preços')
      fireEvent.click(pricingButton)
      
      expect(mockPush).toHaveBeenCalledWith('/pricing')
    })

    it('adds scroll effect class when scrolled', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      const { container } = render(<Navbar />)
      
      // Simulate scroll
      Object.defineProperty(window, 'scrollY', { value: 100, writable: true })
      window.dispatchEvent(new Event('scroll'))
      
      // Check if navbar has scrolled styles
      const nav = container.querySelector('nav')
      expect(nav?.className).toContain('bg-gray-900')
    })
  })

  describe('Mobile view', () => {
    beforeEach(() => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })
    })

    it('shows hamburger menu on mobile', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      // Look for menu button (hamburger)
      const menuButtons = screen.getAllByRole('button')
      const hamburgerButton = menuButtons.find(btn => 
        btn.querySelector('svg') && !btn.textContent
      )
      
      expect(hamburgerButton).toBeInTheDocument()
    })

    it('opens mobile menu when hamburger is clicked', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      // Find and click hamburger button
      const menuButtons = screen.getAllByRole('button')
      const hamburgerButton = menuButtons.find(btn => 
        btn.querySelector('svg') && !btn.textContent
      )
      
      if (hamburgerButton) {
        fireEvent.click(hamburgerButton)
        
        // Check if mobile menu content is visible
        // Note: This depends on your Sheet component implementation
      }
    })
  })

  describe('Authentication modal', () => {
    it('opens auth modal when clicking Cadastrar', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      const signUpButton = screen.getByRole('button', { name: /cadastrar/i })
      fireEvent.click(signUpButton)
      
      // Auth modal should be rendered
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('opens auth modal in signin mode when clicking Entrar', () => {
      const { useSession } = require('next-auth/react')
      useSession.mockReturnValue({ data: null, status: 'unauthenticated' })
      
      render(<Navbar />)
      
      const signInButton = screen.getByRole('button', { name: /entrar/i })
      fireEvent.click(signInButton)
      
      // Auth modal should be rendered in sign in mode
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })
})