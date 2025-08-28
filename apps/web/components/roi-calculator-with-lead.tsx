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
  
  // Check if we're in dark mode
  const [isDark, setIsDark] = useState(false)
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDark(document.documentElement.classList.contains('dark'))
    }
    checkDarkMode()
    // Listen for theme changes
    const observer = new MutationObserver(checkDarkMode)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])
  
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

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(Math.round(value))
  }

  const formatROI = (roiPercent: number) => {
    return roiPercent >= 1000 
      ? `${(roiPercent/100).toFixed(1)}×` 
      : `${formatNumber(roiPercent)}%`
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
          <div className="inline-flex items-center gap-2 px-4 py-2 
            dark:bg-green-500/10 dark:border-green-500/20 
            bg-purple-500/10 border-purple-500/20 
            rounded-full mb-6">
            <Calculator className="w-4 h-4 dark:text-green-400 text-purple-600" />
            <span className="text-sm dark:text-green-400 text-purple-600 font-medium">
              Calculadora de ROI interativa
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight dark:text-white text-gray-900 mb-6 outline-none" data-heading>
            Ainda não se convenceu?
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-violet-600 dark:from-emerald-500 dark:to-emerald-600">Veja os números reais</span>
          </h2>
          
          <p className="text-xl text-zinc-600 dark:text-zinc-300 max-w-3xl mx-auto">
            Ajuste seus dados e veja o impacto <span className="font-semibold text-zinc-900 dark:text-zinc-100">agora</span>.
            <span className="text-zinc-900 dark:text-zinc-100 font-semibold"> Spoiler: é mais que R$97.</span>
          </p>
        </div>

        {/* Calculator Container - Premium spacing */}
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1.1fr_1fr] gap-y-6 gap-x-8">
            {/* Input Controls - Premium card with light surface */}
            <div>
              <div className="rounded-2xl border border-zinc-200/80 dark:border-white/10
                bg-white/90 dark:bg-white/[0.06]
                backdrop-blur-md
                shadow-[0_2px_0_rgba(2,6,23,.04),0_24px_48px_-12px_rgba(2,6,23,.12)] 
                dark:shadow-[0_24px_40px_-16px_rgba(0,0,0,.65)]
                p-5 md:p-6">
                <h3 className="text-xl font-bold dark:text-white text-zinc-900 mb-6">Seus números atuais</h3>
                
                {/* Products per month */}
                <div className="mb-8">
                  <label className="flex justify-between items-center mb-3">
                    <span className="text-zinc-600 dark:text-zinc-400 text-sm">Produtos cadastrados/mês</span>
                    <span className="ml-auto rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-white px-2.5 py-0.5 text-sm font-medium tabular-nums">
                      {formatNumber(productsPerMonth)}
                    </span>
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="1000"
                    step="10"
                    value={productsPerMonth}
                    onChange={(e) => setProductsPerMonth(Number(e.target.value))}
                    aria-valuetext={`${productsPerMonth} produtos por mês`}
                    className="vh-slider"
                    style={{
                      background: `linear-gradient(to right, ${isDark ? '#10b981' : '#7c3aed'} 0%, ${isDark ? '#10b981' : '#7c3aed'} ${((productsPerMonth - 10) / (1000 - 10)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} ${((productsPerMonth - 10) / (1000 - 10)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs dark:text-zinc-600 text-zinc-400 mt-2">
                    <span>10</span>
                    <span>1.000</span>
                  </div>
                </div>

                {/* Rejection rate */}
                <div className="mb-8">
                  <label className="flex justify-between items-center mb-3">
                    <span className="text-zinc-600 dark:text-zinc-400 text-sm">Taxa de rejeição atual</span>
                    <span className={`ml-auto rounded-lg px-2.5 py-0.5 text-sm font-semibold tabular-nums ${
                      rejectionRate < 8 
                        ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:ring-emerald-900/30'
                        : rejectionRate < 20
                        ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:ring-amber-900/30'
                        : 'bg-rose-100 text-rose-700 ring-1 ring-rose-200 dark:bg-red-950/30 dark:text-red-400 dark:ring-red-900/30'
                    }`}>
                      {rejectionRate}%
                    </span>
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="1"
                    value={rejectionRate}
                    onChange={(e) => setRejectionRate(Number(e.target.value))}
                    aria-valuetext={`Taxa de rejeição: ${rejectionRate}%`}
                    className="vh-slider"
                    style={{
                      background: `linear-gradient(to right, ${isDark ? '#10b981' : '#7c3aed'} 0%, ${isDark ? '#10b981' : '#7c3aed'} ${((rejectionRate - 5) / (50 - 5)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} ${((rejectionRate - 5) / (50 - 5)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs dark:text-zinc-600 text-zinc-400 mt-2">
                    <span>5%</span>
                    <span>50%</span>
                  </div>
                </div>

                {/* Average ticket */}
                <div className="mb-8">
                  <label className="flex justify-between items-center mb-3">
                    <span className="text-zinc-600 dark:text-zinc-400 text-sm">Ticket médio do produto</span>
                    <span className="ml-auto rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-white px-2.5 py-0.5 text-sm font-medium tabular-nums">
                      {formatCurrency(averageTicket)}
                    </span>
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="10"
                    value={averageTicket}
                    onChange={(e) => setAverageTicket(Number(e.target.value))}
                    aria-valuetext={`Ticket médio: ${formatCurrency(averageTicket)}`}
                    className="vh-slider"
                    style={{
                      background: `linear-gradient(to right, ${isDark ? '#10b981' : '#7c3aed'} 0%, ${isDark ? '#10b981' : '#7c3aed'} ${((averageTicket - 50) / (1000 - 50)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} ${((averageTicket - 50) / (1000 - 50)) * 100}%, ${isDark ? '#3f3f46' : '#e4e4e7'} 100%)`
                    }}
                  />
                  <div className="flex justify-between text-xs dark:text-zinc-600 text-zinc-400 mt-2">
                    <span>R$ 50</span>
                    <span>R$ 1.000</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Results Display - Premium cards with equal heights */}
            <div className="flex flex-col gap-4">
              {/* Current Loss - Rose theme with premium tint */}
              <div className="rounded-2xl bg-rose-50 border-rose-200 border 
                dark:bg-rose-500/10 dark:border-rose-300/20
                shadow-[0_2px_0_rgba(2,6,23,.04),0_24px_48px_-12px_rgba(2,6,23,.12)]
                dark:shadow-[0_24px_40px_-16px_rgba(0,0,0,.65)]
                p-5 md:p-6 min-h-[140px]">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 opacity-70" />
                  <h4 className="text-sm font-semibold text-rose-800 dark:text-rose-200">Seu prejuízo atual</h4>
                </div>
                <div className="space-y-3 relative">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-600 dark:text-zinc-300">Produtos rejeitados/mês:</span>
                    <div className="relative">
                      <span className={`font-medium text-sm tabular-nums text-rose-800 dark:text-white/90 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {formatNumber(rejectedProducts)}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-600 dark:text-zinc-300">Potencial perdido/mês:</span>
                    <div className="relative">
                      <span className={`font-bold text-base tabular-nums text-rose-800 dark:text-white/90 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {formatCurrency(lostSalesWithout)}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* With ValidaHub - Emerald theme with premium tint */}
              <div className="rounded-2xl bg-emerald-50 border-emerald-200 border 
                dark:bg-emerald-500/10 dark:border-emerald-300/20
                shadow-[0_2px_0_rgba(2,6,23,.04),0_24px_48px_-12px_rgba(2,6,23,.12)]
                dark:shadow-[0_24px_40px_-16px_rgba(0,0,0,.65)]
                p-5 md:p-6 min-h-[140px]">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400 opacity-70" />
                  <h4 className="text-sm font-semibold text-emerald-800 dark:text-emerald-200">Com ValidaHub</h4>
                </div>
                <div className="space-y-3 relative">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-600 dark:text-zinc-300">Taxa de rejeição:</span>
                    <div className="relative">
                      <span className={`font-medium text-sm tabular-nums text-emerald-700 dark:text-white/90 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        2.8%
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-600 dark:text-zinc-300">Potencial perdido/mês:</span>
                    <div className="relative">
                      <span className={`font-medium text-sm tabular-nums text-emerald-700 dark:text-white/90 ${!hasAccess ? 'filter blur-md select-none' : ''}`}>
                        {formatCurrency(lostSalesWith)}
                      </span>
                      {!hasAccess && (
                        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/[0.005] to-transparent" />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-600 dark:text-zinc-300">Investimento ValidaHub:</span>
                    <span className="font-medium text-sm tabular-nums text-zinc-700 dark:text-white/90">R$ 47/mês</span>
                  </div>
                </div>
              </div>

              {/* ROI Summary - Premium with selective blur */}
              <div className={`relative group ${!hasAccess ? '' : 'unlocked'}`}>
                <div className="rounded-2xl border border-zinc-200/80 dark:border-white/10
                  bg-white/90 dark:bg-white/[0.06]
                  backdrop-blur-md
                  shadow-[0_2px_0_rgba(2,6,23,.04),0_24px_48px_-12px_rgba(2,6,23,.12)]
                  dark:shadow-[0_24px_40px_-16px_rgba(0,0,0,.65)]
                  p-5 md:p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <DollarSign className="w-4 h-4 dark:text-emerald-400 text-emerald-600" />
                    <h4 className="text-sm font-semibold dark:text-zinc-300 text-zinc-700">Seu retorno</h4>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="text-center pb-3 border-b border-zinc-200/70 dark:border-zinc-700/70">
                      <div className="relative">
                        <div className={`text-2xl font-bold tabular-nums text-emerald-700 dark:text-emerald-400 ${!hasAccess ? 'blur-sm select-none' : ''}`}>
                          {formatCurrency(monthlySavings)}
                        </div>
                        {!hasAccess && (
                          <div className="absolute inset-0 rounded-lg backdrop-blur-[2px] bg-white/55 dark:bg-black/35" />
                        )}
                      </div>
                      <div className="text-xs dark:text-zinc-400 text-zinc-600 mt-1">Economia mensal líquida</div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center">
                        <div className="relative">
                          <div className={`text-lg font-bold tabular-nums text-zinc-900 dark:text-white ${!hasAccess ? 'blur-sm select-none' : ''}`}>
                            {roi > 0 ? formatROI(roi) : '—'}
                          </div>
                          {!hasAccess && (
                            <div className="absolute inset-0 rounded backdrop-blur-[2px] bg-white/55 dark:bg-black/35" />
                          )}
                        </div>
                        <div className="text-xs dark:text-zinc-400 text-zinc-600 mt-1">ROI</div>
                      </div>
                      <div className="text-center">
                        <div className="relative">
                          <div className={`text-lg font-bold tabular-nums text-zinc-900 dark:text-white ${!hasAccess ? 'blur-sm select-none' : ''}`}>
                            {paybackDays < 999 ? `${paybackDays} dias` : '—'}
                          </div>
                          {!hasAccess && (
                            <div className="absolute inset-0 rounded backdrop-blur-[2px] bg-white/55 dark:bg-black/35" />
                          )}
                        </div>
                        <div className="text-xs dark:text-zinc-400 text-zinc-600 mt-1">Payback</div>
                      </div>
                    </div>

                    {monthlySavings > 0 && (
                      <div className="pt-3 mt-3 border-t border-zinc-200/70 dark:border-zinc-700/70">
                        <p className="text-center text-xs dark:text-zinc-400 text-zinc-600">
                          Em 1 ano você economiza
                        </p>
                        <div className="relative mt-1">
                          <span className={`block text-lg text-center font-bold tabular-nums text-emerald-700 dark:text-emerald-400 ${!hasAccess ? 'blur-sm select-none' : ''}`}>
                            {formatCurrency(monthlySavings * 12)}
                          </span>
                          {!hasAccess && (
                            <div className="absolute inset-0 rounded backdrop-blur-[2px] bg-white/55 dark:bg-black/35" />
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* CTA button outside the card */}
                {!hasAccess && (
                  <button
                    onClick={handleViewResult}
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2
                      rounded-2xl bg-violet-600 dark:bg-emerald-600 text-white px-5 py-2.5 
                      font-semibold shadow-lg
                      ring-2 ring-violet-400/30 dark:ring-emerald-400/30 hover:ring-violet-400/50 dark:hover:ring-emerald-400/50
                      focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70
                      hover:scale-105 transition-all duration-200"
                  >
                    <Lock className="inline-block mr-2 h-4 w-4" />
                    Desbloquear resultado
                  </button>
                )}
              </div>

              {/* Premium CTA with elevation */}
              {hasAccess && (
                <button 
                  onClick={() => navigateToSection('pricing')}
                  className="w-full rounded-2xl bg-violet-600 dark:bg-emerald-500 text-white py-3.5 font-semibold
                    shadow-lg ring-2 ring-violet-300/40 hover:ring-violet-400/60
                    dark:ring-emerald-400/40 dark:hover:ring-emerald-300/60
                    focus:outline-none focus-visible:ring-4 focus-visible:ring-violet-400/70 dark:focus-visible:ring-emerald-400/70
                    hover:scale-[1.02] transition-all duration-200">
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