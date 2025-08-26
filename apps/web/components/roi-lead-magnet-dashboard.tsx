"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Checkbox } from "@/components/ui/checkbox";
import {
  ArrowRight,
  Lock,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Mail,
} from "lucide-react";

// Default allowed domains regex
const KNOWN_EMAIL_REGEX = /^[A-Za-z0-9._%+-]+@(?:gmail\.com|hotmail\.com|outlook\.com|live\.com|icloud\.com|yahoo\.com|proton\.me|protonmail\.com|zoho\.com|bol\.com\.br|uol\.com\.br|terra\.com\.br)$/i;

// Utility to build regex from domain list
function buildAllowlistRegex(domains: string[]): RegExp {
  if (!domains || domains.length === 0) return KNOWN_EMAIL_REGEX;
  
  const escapedDomains = domains.map(d => d.replace(/\./g, '\\.'));
  const pattern = `^[A-Za-z0-9._%+-]+@(?:${escapedDomains.join('|')})$`;
  return new RegExp(pattern, 'i');
}

// Blacklisted temporary email domains
const TEMP_EMAIL_DOMAINS = [
  'mailinator.com',
  'tempmail.',
  'guerrillamail.com',
  '10minutemail.com',
  'throwaway.email',
];

interface SimulationData {
  monthlyProducts: number;
  rejectionRate: number;
  hoursSpent: number;
  avgProductValue: number;
}

interface RoiResults {
  currentLosses: number;
  potentialSavings: number;
  timeSaved: number;
  newRejectionRate: number;
  roi7Days: number;
  roi30Days: number;
}

export default function RoiLeadMagnetDashboard() {
  const [simulationData, setSimulationData] = useState<SimulationData>({
    monthlyProducts: 1000,
    rejectionRate: 27,
    hoursSpent: 16,
    avgProductValue: 127,
  });
  
  const [roiResults, setRoiResults] = useState<RoiResults | null>(null);
  const [hasAccess, setHasAccess] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitCount, setSubmitCount] = useState(0);
  const [lastSubmitTime, setLastSubmitTime] = useState(0);

  // Check localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("vh_roi_access");
    if (stored) {
      try {
        const { ok, exp } = JSON.parse(stored);
        if (ok && exp > Date.now()) {
          setHasAccess(true);
        } else {
          localStorage.removeItem("vh_roi_access");
        }
      } catch (e) {
        localStorage.removeItem("vh_roi_access");
      }
    }
  }, []);

  // Calculate ROI
  const handleSimulate = () => {
    console.log("roi.simulate_clicked");
    
    const { monthlyProducts, rejectionRate, hoursSpent, avgProductValue } = simulationData;
    
    // Mock calculations
    const rejectedProducts = monthlyProducts * (rejectionRate / 100);
    const currentLosses = rejectedProducts * avgProductValue;
    const newRejectionRate = 2.8; // ValidaHub average
    const newRejectedProducts = monthlyProducts * (newRejectionRate / 100);
    const potentialSavings = currentLosses - (newRejectedProducts * avgProductValue);
    const timeSaved = hoursSpent * 0.85; // 85% time reduction
    const roi7Days = potentialSavings * 0.25; // 7 days = ~25% of month
    const roi30Days = potentialSavings;

    setRoiResults({
      currentLosses,
      potentialSavings,
      timeSaved,
      newRejectionRate,
      roi7Days,
      roi30Days,
    });
  };

  // Handle view result click
  const handleViewResult = () => {
    console.log("roi.view_result_clicked");
    console.log("lead.capture_opened");
    setDialogOpen(true);
  };

  // Validate email with regex
  const validateEmail = (email: string): boolean => {
    // Check format
    const basicRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!basicRegex.test(email)) return false;
    
    // Check against temp domains
    const domain = email.split('@')[1];
    if (TEMP_EMAIL_DOMAINS.some(temp => domain.includes(temp))) {
      setEmailError("Por favor, use um e-mail pessoal ou corporativo.");
      return false;
    }
    
    // Check against allowed domains
    if (!KNOWN_EMAIL_REGEX.test(email)) {
      setEmailError("Use um e-mail de domínio suportado (Gmail, Outlook, Yahoo, etc).");
      return false;
    }
    
    return true;
  };

  // Handle email submission
  const handleEmailSubmit = async () => {
    // Rate limiting
    const now = Date.now();
    if (now - lastSubmitTime < 60000 && submitCount >= 3) {
      setEmailError("Muitas tentativas. Aguarde 1 minuto.");
      return;
    }
    
    if (!validateEmail(email)) {
      return;
    }
    
    if (!consent) {
      setEmailError("Você precisa concordar com os termos.");
      return;
    }
    
    console.log("lead.submitted");
    setIsSubmitting(true);
    setEmailError("");
    
    // Update rate limit tracking
    if (now - lastSubmitTime > 60000) {
      setSubmitCount(1);
    } else {
      setSubmitCount(submitCount + 1);
    }
    setLastSubmitTime(now);
    
    try {
      // Mock API call
      // TODO: plug real endpoint
      await new Promise((resolve, reject) => {
        setTimeout(() => {
          if (Math.random() > 0.1) {
            resolve({ ok: true });
          } else {
            reject(new Error("Network error"));
          }
        }, 1000);
      });
      
      console.log("lead.captured_success");
      
      // Save to localStorage for 30 days
      const expiry = Date.now() + (30 * 24 * 60 * 60 * 1000);
      localStorage.setItem("vh_roi_access", JSON.stringify({ ok: true, exp: expiry }));
      
      setHasAccess(true);
      setDialogOpen(false);
      console.log("roi.unblurred");
      
    } catch (error) {
      console.log("lead.captured_error", error);
      setEmailError("Erro ao processar. Tente novamente.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Reset simulation
  const handleReset = () => {
    setRoiResults(null);
    setSimulationData({
      monthlyProducts: 1000,
      rejectionRate: 27,
      hoursSpent: 16,
      avgProductValue: 127,
    });
  };

  return (
    <TooltipProvider>
      <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Calculadora de ROI ValidaHub</h1>
          <p className="text-muted-foreground">
            Descubra quanto você está perdendo com produtos rejeitados nos marketplaces
          </p>
        </div>

        <Separator />

        {/* Simulation Form */}
        {!roiResults ? (
          <Card>
            <CardHeader>
              <CardTitle>Configure sua operação</CardTitle>
              <CardDescription>
                Insira os dados da sua operação atual para calcular o potencial de economia
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="products">Produtos enviados/mês</Label>
                  <Input
                    id="products"
                    type="number"
                    value={simulationData.monthlyProducts}
                    onChange={(e) => setSimulationData({
                      ...simulationData,
                      monthlyProducts: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rejection">Taxa de rejeição atual (%)</Label>
                  <Input
                    id="rejection"
                    type="number"
                    value={simulationData.rejectionRate}
                    onChange={(e) => setSimulationData({
                      ...simulationData,
                      rejectionRate: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hours">Horas gastas/mês com correções</Label>
                  <Input
                    id="hours"
                    type="number"
                    value={simulationData.hoursSpent}
                    onChange={(e) => setSimulationData({
                      ...simulationData,
                      hoursSpent: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="value">Valor médio do produto (R$)</Label>
                  <Input
                    id="value"
                    type="number"
                    value={simulationData.avgProductValue}
                    onChange={(e) => setSimulationData({
                      ...simulationData,
                      avgProductValue: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
              </div>
              <Button onClick={handleSimulate} size="lg" className="w-full">
                Simular economia
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Results Dashboard */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {/* Current Losses */}
              <Card className="relative overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Perdas Atuais/mês
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <div className={!hasAccess ? "filter blur-md" : ""}>
                    <div className="text-2xl font-bold text-red-500">
                      R$ {roiResults.currentLosses.toLocaleString('pt-BR')}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      com produtos rejeitados
                    </p>
                  </div>
                  {!hasAccess && (
                    <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-background/50 flex items-center justify-center">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Potential Savings */}
              <Card className="relative overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Economia Potencial
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <div className={!hasAccess ? "filter blur-md" : ""}>
                    <div className="text-2xl font-bold text-green-500">
                      R$ {roiResults.potentialSavings.toLocaleString('pt-BR')}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      por mês com ValidaHub
                    </p>
                  </div>
                  {!hasAccess && (
                    <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-background/50 flex items-center justify-center">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Time Saved */}
              <Card className="relative overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Tempo Economizado
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <div className={!hasAccess ? "filter blur-md" : ""}>
                    <div className="text-2xl font-bold text-blue-500">
                      {roiResults.timeSaved.toFixed(1)}h
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      por mês (-85%)
                    </p>
                  </div>
                  {!hasAccess && (
                    <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-background/50 flex items-center justify-center">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* New Rejection Rate */}
              <Card className="relative overflow-hidden">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Nova Taxa de Rejeição
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <div className={!hasAccess ? "filter blur-md" : ""}>
                    <div className="text-2xl font-bold text-emerald-500">
                      {roiResults.newRejectionRate}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      média ValidaHub
                    </p>
                  </div>
                  {!hasAccess && (
                    <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-background/50 flex items-center justify-center">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* ROI Projection */}
            <Card className="relative">
              <CardHeader>
                <CardTitle>Projeção de ROI</CardTitle>
                <CardDescription>
                  Retorno sobre investimento estimado com ValidaHub
                </CardDescription>
              </CardHeader>
              <CardContent className="relative space-y-4">
                <div className={!hasAccess ? "filter blur-md" : ""}>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">ROI em 7 dias</span>
                        <span className="text-sm font-bold">
                          R$ {roiResults.roi7Days.toLocaleString('pt-BR')}
                        </span>
                      </div>
                      <Progress value={25} className="h-2" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">ROI em 30 dias</span>
                        <span className="text-sm font-bold">
                          R$ {roiResults.roi30Days.toLocaleString('pt-BR')}
                        </span>
                      </div>
                      <Progress value={100} className="h-2" />
                    </div>
                  </div>
                  <div className="mt-6 p-4 bg-emerald-500/10 rounded-lg">
                    <div className="flex items-center gap-2 text-emerald-600">
                      <TrendingUp className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        O ValidaHub se paga em menos de 7 dias
                      </span>
                    </div>
                  </div>
                </div>
                
                {!hasAccess && (
                  <div className="absolute inset-0 bg-gradient-to-t from-background to-background/50 flex items-center justify-center">
                    <Button size="lg" onClick={handleViewResult}>
                      <Lock className="mr-2 h-4 w-4" />
                      Ver resultado completo
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Action Buttons */}
            {hasAccess && (
              <div className="flex gap-4">
                <Button onClick={handleReset} variant="outline">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refazer simulação
                </Button>
                <Button className="flex-1">
                  Começar teste grátis
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            )}
          </>
        )}

        {/* Email Capture Dialog */}
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          if (!hasAccess) setDialogOpen(open);
        }}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Veja seu resultado completo</DialogTitle>
              <DialogDescription>
                Insira seu e-mail para desbloquear a análise detalhada do ROI
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
                      setEmail(e.target.value);
                      setEmailError("");
                    }}
                    disabled={isSubmitting}
                  />
                </div>
                {emailError && (
                  <div className="flex items-center gap-2 text-sm text-red-500">
                    <AlertCircle className="h-3 w-3" />
                    {emailError}
                  </div>
                )}
                <Tooltip>
                  <TooltipTrigger asChild>
                    <p className="text-xs text-muted-foreground cursor-help">
                      Aceitos: Gmail, Outlook, Yahoo, iCloud e principais provedores
                    </p>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Gmail, Hotmail, Outlook, Live, iCloud, Yahoo,</p>
                    <p>ProtonMail, Zoho, BOL, UOL, Terra</p>
                  </TooltipContent>
                </Tooltip>
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
                  Usaremos seu e-mail para enviar materiais do ValidaHub. 
                  Você pode cancelar quando quiser.{" "}
                  <a href="/privacy" className="underline" target="_blank">
                    Política de Privacidade
                  </a>
                </label>
              </div>
            </div>

            <DialogFooter>
              <Button 
                onClick={handleEmailSubmit} 
                disabled={isSubmitting || !email || !consent}
                className="w-full"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Processando...
                  </>
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
      </div>
    </TooltipProvider>
  );
}