'use client'

import { useState, useEffect, useCallback } from 'react'
import { Calculator, TrendingUp, AlertTriangle, DollarSign, Lock, ArrowRight, Mail, Phone, CheckCircle2, X } from 'lucide-react'
import { navigateToSection } from '@/lib/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"

export default function ROICalculatorWithLead() {
  const [productsPerMonth, setProductsPerMonth] = useState(100)
  const [rejectionRate, setRejectionRate] = useState(20)
  const [averageTicket, setAverageTicket] = useState(150)
  
  // Calculated values
  const [rejectedProducts, setRejectedProducts] = useState(0)
  const [lostSalesWithout, setLostSalesWithout] = useState(0)
  const [lostSalesWith, setLostSalesWith] = useState(0)
  const [monthlySavings, setMonthlySavings] = useState(0)
  const [roi, setROI] = useState(0)
  const [paybackDays, setPaybackDays] = useState(0)

  // Lead capture states
  const [hasAccess, setHasAccess] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  
  const closeDialog = useCallback(() => {
    console.log('closeDialog called, forcing close')
    setDialogOpen(false)
    // Force update
    setTimeout(() => {
      console.log('Dialog should be closed after timeout')
    }, 0)
  }, [])
  const [email, setEmail] = useState("")
  const [whatsapp, setWhatsapp] = useState("")
  const [consent, setConsent] = useState(false)
  const [emailError, setEmailError] = useState("")
  const [whatsappError, setWhatsappError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const VALIDAHUB_PRICE = 47 // Plano Pro
  const REDUCED_REJECTION_RATE = 2.8
  const DAYS_PER_MONTH = 30

  // Check localStorage on mount
  useEffect(() => {
    // Debug: Para testar, descomente a linha abaixo para limpar o acesso
    localStorage.removeItem("vh_roi_access")
    
    const stored = localStorage.getItem("vh_roi_access")
    if (stored) {
      try {
        const { ok, exp } = JSON.parse(stored)
        if (ok && exp > Date.now()) {
          setHasAccess(true)
          console.log("Acesso já liberado até:", new Date(exp).toLocaleString())
        } else {
          localStorage.removeItem("vh_roi_access")
          console.log("Acesso expirado, removido do localStorage")
        }
      } catch (e) {
        localStorage.removeItem("vh_roi_access")
      }
    } else {
      console.log("Sem acesso prévio - blur ativo")
    }
  }, [])

  useEffect(() => {
    // Calculate rejected products
    const rejected = Math.round(productsPerMonth * (rejectionRate / 100))
    const rejectedWithValidaHub = Math.round(productsPerMonth * (REDUCED_REJECTION_RATE / 100))
    
    // Calculate REAL monthly losses (without the inflated 30x multiplier)
    // Formula: Rejected products * Average ticket value
    const monthlyLossWithout = rejected * averageTicket
    const monthlyLossWith = rejectedWithValidaHub * averageTicket
    
    // Calculate savings (economia bruta - investimento ValidaHub)
    const grossSavings = monthlyLossWithout - monthlyLossWith
    const netSavings = grossSavings - VALIDAHUB_PRICE
    
    // Calculate ROI (return on investment)
    const roiPercent = VALIDAHUB_PRICE > 0 ? ((netSavings / VALIDAHUB_PRICE) * 100) : 0
    
    // Calculate payback in days
    // If net savings is positive, calculate how many days to recover investment
    const dailySavings = netSavings / DAYS_PER_MONTH
    const payback = netSavings > 0 ? Math.ceil(VALIDAHUB_PRICE / (grossSavings / DAYS_PER_MONTH)) : 999
    
    setRejectedProducts(rejected)
    setLostSalesWithout(monthlyLossWithout)
    setLostSalesWith(monthlyLossWith)
    setMonthlySavings(netSavings)
    setROI(roiPercent)
    setPaybackDays(payback)
    
    // Save calculation to sessionStorage for Pricing component
    sessionStorage.setItem('roiCalculation', JSON.stringify({
      monthlyLoss: monthlyLossWithout,
      monthlySavings: netSavings,
      productsPerMonth,
      rejectionRate,
      averageTicket
    }))
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent('roiCalculationUpdated', {
      detail: { monthlyLoss: monthlyLossWithout }
    }))
  }, [productsPerMonth, rejectionRate, averageTicket])

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const handleViewResult = () => {
    setDialogOpen(true)
  }

  const validateEmail = (email: string): boolean => {
    const KNOWN_EMAIL_REGEX = /^[A-Za-z0-9._%+-]+@(?:gmail\.com|hotmail\.com|outlook\.com|live\.com|icloud\.com|yahoo\.com|proton\.me|protonmail\.com|zoho\.com|bol\.com\.br|uol\.com\.br|terra\.com\.br)$/i
    
    if (!KNOWN_EMAIL_REGEX.test(email)) {
      setEmailError("Use um e-mail de domínio conhecido (Gmail, Outlook, etc)")
      return false
    }
    
    return true
  }

  const validateWhatsApp = (phone: string): boolean => {
    // Remove all non-numeric characters
    const cleaned = phone.replace(/\D/g, '')
    
    // Check if it's a valid Brazilian phone number (11 digits)
    if (cleaned.length !== 11) {
      setWhatsappError("Digite um número válido com DDD (11 dígitos)")
      return false
    }
    
    // Check if it starts with a valid area code (11-99)
    const areaCode = parseInt(cleaned.substring(0, 2))
    if (areaCode < 11 || areaCode > 99) {
      setWhatsappError("DDD inválido")
      return false
    }
    
    // Check if it's a mobile number (starts with 9)
    if (cleaned[2] !== '9') {
      setWhatsappError("Digite um número de celular válido")
      return false
    }
    
    return true
  }

  const formatWhatsApp = (value: string): string => {
    const cleaned = value.replace(/\D/g, '')
    
    if (cleaned.length <= 2) {
      return cleaned
    } else if (cleaned.length <= 7) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`
    } else if (cleaned.length <= 11) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`
    }
    
    return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7, 11)}`
  }

  const handleEmailSubmit = async () => {
    console.log('handleEmailSubmit called')
    let hasError = false
    
    if (!validateEmail(email)) {
      hasError = true
    }
    
    if (!validateWhatsApp(whatsapp)) {
      hasError = true
    }
    
    if (!consent) {
      setEmailError("Você precisa concordar com os termos")
      hasError = true
    }
    
    if (hasError) {
      console.log('Validation error, returning')
      return
    }
    
    setIsSubmitting(true)
    setEmailError("")
    setWhatsappError("")
    
    try {
      console.log('Processing submission...')
      // Mock API call - would send email and whatsapp to backend
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Save to localStorage for 30 days
      const expiry = Date.now() + (30 * 24 * 60 * 60 * 1000)
      localStorage.setItem("vh_roi_access", JSON.stringify({ 
        ok: true, 
        exp: expiry,
        email,
        whatsapp: whatsapp.replace(/\D/g, '')
      }))
      
      setHasAccess(true)
      console.log('Closing dialog...')
      closeDialog()
      
      // Dispatch event to update Pricing component after lead capture
      window.dispatchEvent(new CustomEvent('roiCalculationUpdated', {
        detail: { 
          monthlyLoss: lostSalesWithout,
          hasAccess: true 
        }
      }))
      
    } catch (error) {
      console.error('Error:', error)
      setEmailError("Erro ao processar. Tente novamente.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section 
      className="py-20 relative overflow-hidden"
      id="roi-calculator"
      data-section="calculator"
      aria-label="Calculadora de ROI"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-white/[0.01] bg-[size:80px_80px]" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-6">
            <Calculator className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">
              Calculadora de ROI interativa
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 outline-none" data-heading>
            Ainda não se convenceu?
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">Veja os números reais</span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Ajuste com seus dados e descubra quanto está deixando na mesa todo mês.
            <span className="text-white font-semibold"> Spoiler: é mais que R$97.</span>
          </p>
        </div>

        {/* Calculator Container */}
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Input Controls */}
            <div>
              <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8">
                <h3 className="text-xl font-bold text-white mb-6">Seus números atuais</h3>
                
                {/* Products per month */}
                <div className="mb-8">
                  <label className="flex justify-between text-gray-300 mb-3">
                    <span>Produtos cadastrados/mês</span>
                    <span className="text-white font-bold">{productsPerMonth}</span>
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="1000"
                    step="10"
                    value={productsPerMonth}
                    onChange={(e) => setProductsPerMonth(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                    style={{
                      background: `linear-gradient(to right, #10b981 0%, #10b981 ${(productsPerMonth - 10) / 9.9}%, #374151 ${(productsPerMonth - 10) / 9.9}%, #374151 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>10</span>
                    <span>1.000</span>
                  </div>
                </div>

                {/* Rejection rate */}
                <div className="mb-8">
                  <label className="flex justify-between text-gray-300 mb-3">
                    <span>Taxa de rejeição atual</span>
                    <span className="text-red-400 font-bold">{rejectionRate}%</span>
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="1"
                    value={rejectionRate}
                    onChange={(e) => setRejectionRate(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #ef4444 0%, #ef4444 ${(rejectionRate - 5) / 0.45}%, #374151 ${(rejectionRate - 5) / 0.45}%, #374151 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>5%</span>
                    <span>50%</span>
                  </div>
                </div>

                {/* Average ticket */}
                <div className="mb-8">
                  <label className="flex justify-between text-gray-300 mb-3">
                    <span>Ticket médio do produto</span>
                    <span className="text-white font-bold">{formatCurrency(averageTicket)}</span>
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="10"
                    value={averageTicket}
                    onChange={(e) => setAverageTicket(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(averageTicket - 50) / 9.5}%, #374151 ${(averageTicket - 50) / 9.5}%, #374151 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>R$ 50</span>
                    <span>R$ 1.000</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Results Display */}
            <div className="space-y-4">
              {/* Current Loss */}
              <div className="bg-gradient-to-b from-red-950/30 to-red-950/20 border border-red-500/20 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  <h4 className="text-sm font-bold text-white">Seu prejuízo atual</h4>
                </div>
                <div className="space-y-1 relative">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-400">Produtos rejeitados/mês:</span>
                    <div className="relative">
                      <span className={`font-semibold text-sm text-red-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {rejectedProducts}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-400">Potencial perdido/mês:</span>
                    <div className="relative">
                      <span className={`font-bold text-base text-red-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {formatCurrency(lostSalesWithout)}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* With ValidaHub */}
              <div className="bg-gradient-to-b from-green-950/30 to-green-950/20 border border-green-500/20 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-green-400" />
                  <h4 className="text-sm font-bold text-white">Com ValidaHub</h4>
                </div>
                <div className="space-y-1 relative">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-400">Taxa de rejeição:</span>
                    <div className="relative">
                      <span className={`font-semibold text-sm text-green-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        2.8%
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-400">Potencial perdido/mês:</span>
                    <div className="relative">
                      <span className={`font-semibold text-sm text-green-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {formatCurrency(lostSalesWith)}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-400">Investimento ValidaHub:</span>
                    <span className="text-gray-300 font-semibold text-sm">R$ 47/mês</span>
                  </div>
                </div>
              </div>

              {/* ROI Summary */}
              <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-xl p-4 relative overflow-hidden">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-green-400" />
                  <h4 className="text-sm font-bold text-white">Seu retorno</h4>
                </div>
                <div className="space-y-2">
                  <div className="text-center py-2 border-b border-gray-700">
                    <div className={`text-2xl font-bold text-green-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                      {formatCurrency(monthlySavings)}
                    </div>
                    <div className="text-xs text-gray-400">Economia mensal líquida</div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <div className="text-center">
                      <div className={`text-lg font-bold text-white ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {roi > 0 ? `${roi.toFixed(0)}%` : '—'}
                      </div>
                      <div className="text-xs text-gray-400">ROI</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-lg font-bold text-white ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {paybackDays < 999 ? `${paybackDays} dias` : '—'}
                      </div>
                      <div className="text-xs text-gray-400">Payback</div>
                    </div>
                  </div>

                  {monthlySavings > 0 && (
                    <div className="pt-2 border-t border-gray-700">
                      <p className="text-center text-xs text-gray-400">
                        Em 1 ano você economiza
                        <span className={`block text-lg font-bold text-green-400 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                          {formatCurrency(monthlySavings * 12)}
                        </span>
                      </p>
                    </div>
                  )}
                </div>

                {!hasAccess && (
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-t from-gray-900/95 via-gray-900/80 to-transparent flex items-center justify-center">
                    <Button size="lg" onClick={handleViewResult} className="bg-green-500 hover:bg-green-600 z-10">
                      <Lock className="mr-2 h-4 w-4" />
                      Ver resultado completo
                    </Button>
                  </div>
                )}
              </div>

              {/* CTA */}
              {hasAccess && (
                <button 
                  onClick={() => navigateToSection('pricing')}
                  className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold rounded-lg shadow-lg shadow-green-500/20 transition-all duration-200 hover:shadow-xl hover:shadow-green-500/30">
                  Começar a economizar agora
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Email Capture Dialog */}
      {console.log('Dialog render, dialogOpen:', dialogOpen)}
      {dialogOpen && (
        <Dialog 
          open={true} 
          onOpenChange={(open) => {
            console.log('onOpenChange called with:', open)
            if (!open) {
              setDialogOpen(false)
            }
          }}>
          <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Veja seu resultado completo</DialogTitle>
            <DialogDescription>
              Insira seus dados para desbloquear a análise detalhada do ROI
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-mail corporativo</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="seu@empresa.com"
                  className="pl-9"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    setEmailError("")
                  }}
                  disabled={isSubmitting}
                />
              </div>
              {emailError && (
                <p className="text-sm text-red-500">{emailError}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="whatsapp">WhatsApp</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="whatsapp"
                  type="tel"
                  placeholder="(11) 98765-4321"
                  className="pl-9"
                  value={whatsapp}
                  onChange={(e) => {
                    const formatted = formatWhatsApp(e.target.value)
                    setWhatsapp(formatted)
                    setWhatsappError("")
                  }}
                  maxLength={15}
                  disabled={isSubmitting}
                />
              </div>
              {whatsappError && (
                <p className="text-sm text-red-500">{whatsappError}</p>
              )}
            </div>
            
            <div className="flex items-start space-x-2">
              <Checkbox
                id="consent"
                checked={consent}
                onCheckedChange={(checked) => setConsent(checked as boolean)}
                disabled={isSubmitting}
              />
              <label
                htmlFor="consent"
                className="text-sm text-muted-foreground leading-tight cursor-pointer"
              >
                Usaremos seus dados para enviar materiais exclusivos do ValidaHub. 
                Você pode cancelar quando quiser.
              </label>
            </div>
          </div>

          <DialogFooter>
            <Button 
              type="button"
              variant="outline" 
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                console.log('Cancelar clicked, current state:', dialogOpen)
                closeDialog()
                console.log('Dialog should be closed now')
              }}
              disabled={isSubmitting}
              className="sm:mr-2"
            >
              Cancelar
            </Button>
            <Button 
              type="button"
              onClick={async () => {
                console.log('Submit clicked')
                await handleEmailSubmit()
              }}
              disabled={isSubmitting || !email || !whatsapp || !consent}
              className="flex-1"
            >
              {isSubmitting ? (
                <>Processando...</>
              ) : (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Ver resultado completo
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
        </Dialog>
      )}
    </section>
  )
}