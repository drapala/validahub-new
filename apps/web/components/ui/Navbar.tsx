'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { useSession, signOut } from 'next-auth/react'
import { Button } from './button'
// AuthModal is temporarily commented out
// import AuthModal from './AuthModal'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from './sheet'
import { Menu, X, User, LogOut, Settings, FileText, CreditCard } from 'lucide-react'
import { cn } from '@/lib/utils'

const navLinks = [
  { href: '#features', label: 'Features' },
  { href: '#how-it-works', label: 'Como funciona' },
  { href: '/pricing', label: 'Preços' },
  { href: '/faq', label: 'FAQ' },
]

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin')
  
  const { data: session, status } = useSession()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleSignOut = async () => {
    await signOut({ redirect: false })
    router.push('/')
  }

  const handleAuthClick = (mode: 'signin' | 'signup') => {
    setAuthMode(mode)
    setAuthModalOpen(true)
    setMobileMenuOpen(false)
  }

  const scrollToSection = (href: string) => {
    if (href.startsWith('#')) {
      const element = document.querySelector(href)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  const isHomePage = pathname === '/'

  return (
    <>
      <nav
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
          isScrolled
            ? 'bg-gray-900/95 backdrop-blur-md border-b border-gray-800 shadow-lg'
            : 'bg-transparent'
        )}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center space-x-2 text-white font-bold text-xl hover:text-green-400 transition-colors"
            >
              <svg
                className="w-8 h-8 text-green-400"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
              </svg>
              <span>ValidaHub</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => {
                    if (link.href.startsWith('#') && isHomePage) {
                      scrollToSection(link.href)
                    } else if (link.href.startsWith('#')) {
                      router.push('/' + link.href)
                    } else {
                      router.push(link.href)
                    }
                  }}
                  className="text-gray-300 hover:text-white transition-colors text-sm font-medium"
                >
                  {link.label}
                </button>
              ))}
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              {status === 'loading' ? (
                <div className="w-32 h-10 bg-gray-800 animate-pulse rounded-lg" />
              ) : session ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="flex items-center space-x-2 text-white hover:bg-gray-800"
                    >
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-sm">{session.user?.name || session.user?.email}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56 bg-gray-900 border-gray-800">
                    <DropdownMenuLabel className="text-gray-400">Minha Conta</DropdownMenuLabel>
                    <DropdownMenuSeparator className="bg-gray-800" />
                    <DropdownMenuItem onClick={() => router.push('/upload')} className="text-gray-300 hover:bg-gray-800">
                      <FileText className="mr-2 h-4 w-4" />
                      Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => router.push('/settings')} className="text-gray-300 hover:bg-gray-800">
                      <Settings className="mr-2 h-4 w-4" />
                      Configurações
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => router.push('/settings/billing')} className="text-gray-300 hover:bg-gray-800">
                      <CreditCard className="mr-2 h-4 w-4" />
                      Billing
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-gray-800" />
                    <DropdownMenuItem onClick={handleSignOut} className="text-red-400 hover:bg-gray-800">
                      <LogOut className="mr-2 h-4 w-4" />
                      Sair
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    onClick={() => handleAuthClick('signin')}
                    className="text-gray-300 hover:text-white hover:bg-gray-800"
                  >
                    Entrar
                  </Button>
                  <Button
                    onClick={() => handleAuthClick('signup')}
                    className="bg-green-500 hover:bg-green-600 text-white font-semibold"
                  >
                    Cadastrar
                  </Button>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon" className="text-white">
                  {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[300px] bg-gray-900 border-gray-800">
                <div className="flex flex-col space-y-6 mt-8">
                  {/* Mobile Navigation Links */}
                  {navLinks.map((link) => (
                    <button
                      key={link.href}
                      onClick={() => {
                        if (link.href.startsWith('#') && isHomePage) {
                          scrollToSection(link.href)
                        } else if (link.href.startsWith('#')) {
                          router.push('/' + link.href)
                        } else {
                          router.push(link.href)
                        }
                        setMobileMenuOpen(false)
                      }}
                      className="text-gray-300 hover:text-white transition-colors text-lg font-medium text-left"
                    >
                      {link.label}
                    </button>
                  ))}

                  <div className="border-t border-gray-800 pt-6">
                    {session ? (
                      <div className="space-y-4">
                        <div className="flex items-center space-x-3 px-2">
                          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <p className="text-white font-medium">{session.user?.name}</p>
                            <p className="text-gray-400 text-sm">{session.user?.email}</p>
                          </div>
                        </div>
                        <Button
                          onClick={() => {
                            router.push('/upload')
                            setMobileMenuOpen(false)
                          }}
                          className="w-full bg-gray-800 hover:bg-gray-700 text-white"
                        >
                          Dashboard
                        </Button>
                        <Button
                          onClick={handleSignOut}
                          variant="outline"
                          className="w-full border-red-500 text-red-400 hover:bg-red-500/10"
                        >
                          Sair
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <Button
                          onClick={() => handleAuthClick('signin')}
                          variant="outline"
                          className="w-full border-gray-600 text-gray-300 hover:bg-gray-800"
                        >
                          Entrar
                        </Button>
                        <Button
                          onClick={() => handleAuthClick('signup')}
                          className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold"
                        >
                          Cadastrar
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </nav>

      {/* AuthModal temporarily disabled
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      /> */}
    </>
  )
}