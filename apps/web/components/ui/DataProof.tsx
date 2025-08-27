'use client'

import React from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, AlertCircle, AlertTriangle, ChevronRight, ChevronDown, ArrowRight } from "lucide-react";

// Real marketplace validation rules with severity levels
const RAW_ROWS = [
  {
    field: "EAN/GTIN",
    bad: "789012345678",
    good: "7890123456789",
    type: "fatal",
    rule: "Dígito verificador inválido",
    impact: "Bloqueio garantido"
  },
  {
    field: "Categoria",
    bad: "Eletrônicos > Sem categoria",
    good: "MLB1002 - Celulares",
    type: "fatal",
    rule: "Categoria não mapeada no marketplace",
    impact: "Rejeição automática"
  },
  {
    field: "Título",
    bad: "CELULAR SAMSUNG COMPRE JÁ!!! PROMOÇÃO!!!",
    good: "Samsung Galaxy A54 5G 128GB",
    type: "critical",
    rule: "Termos promocionais proibidos",
    impact: "35% de rejeição"
  },
  {
    field: "Preço",
    bad: "R$ 2,499.00",
    good: "R$ 2.499,00",
    type: "critical",
    rule: "Formato USD incompatível",
    impact: "28% de falha"
  },
  {
    field: "Estoque",
    bad: "1 unidade",
    good: "25 unidades",
    type: "warning",
    rule: "Quantidade abaixo do ideal",
    impact: "-40% ranking"
  },
  {
    field: "Descrição",
    bad: "Celular novo na caixa.",
    good: "Smartphone 6.4\", 50MP, 6GB RAM",
    type: "warning",
    rule: "Descrição muito curta",
    impact: "-25% conversão"
  }
] as const;

type TabType = 'all' | 'fatal' | 'critical' | 'warning' | 'fixed';

export default function DataProof() {
  const [states, setStates] = React.useState<boolean[]>(() => RAW_ROWS.map(() => false));
  const [activeTab, setActiveTab] = React.useState<TabType>('all');
  const [expandedRow, setExpandedRow] = React.useState<number | null>(null);
  const [showFixed, setShowFixed] = React.useState(true);
  const [hoveredRow, setHoveredRow] = React.useState<number | null>(null);

  const handleScrollToPricing = () => {
    const pricingSection = document.querySelector('[data-section="pricing"]');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const fixedCount = states.filter(s => s).length;
  const allFixed = fixedCount === RAW_ROWS.length;
  
  // Count by type
  const counts = {
    fatal: RAW_ROWS.filter(r => r.type === 'fatal' && !states[RAW_ROWS.indexOf(r)]).length,
    critical: RAW_ROWS.filter(r => r.type === 'critical' && !states[RAW_ROWS.indexOf(r)]).length,
    warning: RAW_ROWS.filter(r => r.type === 'warning' && !states[RAW_ROWS.indexOf(r)]).length,
    fixed: fixedCount
  };

  const onToggle = (idx: number) => {
    setStates(prev => {
      const next = [...prev];
      next[idx] = !next[idx];
      return next;
    });
  };

  // Filter rows based on active tab
  const getFilteredRows = () => {
    if (activeTab === 'all') return RAW_ROWS;
    if (activeTab === 'fixed') return RAW_ROWS.filter((_, i) => states[i]);
    return RAW_ROWS.filter(r => r.type === activeTab && !states[RAW_ROWS.indexOf(r)]);
  };

  const visibleRows = showFixed ? getFilteredRows() : getFilteredRows().filter((_, i) => !states[i]);

  const getIcon = (type: string, fixed: boolean) => {
    if (fixed) return <CheckCircle2 className="w-4 h-4 text-green-500" />;
    if (type === 'fatal') return <XCircle className="w-4 h-4 text-red-500" />;
    if (type === 'critical') return <AlertCircle className="w-4 h-4 text-orange-400" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
  };

  const getStatusText = (type: string, fixed: boolean) => {
    if (fixed) return "OK";
    if (type === 'fatal') return "Fatal";
    if (type === 'critical') return "Crítico";
    return "Alerta";
  };

  const tabs = [
    { id: 'all', label: 'Todos', count: RAW_ROWS.length },
    { id: 'fatal', label: 'Fatais', count: counts.fatal, color: 'text-red-400' },
    { id: 'critical', label: 'Críticos', count: counts.critical, color: 'text-orange-400' },
    { id: 'warning', label: 'Alertas', count: counts.warning, color: 'text-yellow-400' },
    { id: 'fixed', label: 'Corrigidos', count: counts.fixed, color: 'text-green-400' }
  ];

  return (
    <>
      <div className="min-h-[500px] w-full text-neutral-100 p-6 md:p-10" data-section="data">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-4 relative">
            <h2 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-wide">
              Validação em <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">tempo real</span>
            </h2>
            <p className="mt-3 text-base text-neutral-400 font-medium">
              Clique para simular correções
            </p>
            {/* Linha de conexão visual */}
            <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-24 h-0.5 bg-gradient-to-r from-transparent via-green-500/50 to-transparent" />
          </div>

          <Card className="bg-neutral-900/30 border-neutral-800/40 shadow-xl overflow-hidden relative mt-6">
            {/* Gradiente superior conectando ao título */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-green-500/30 to-transparent" />
            {/* Header with tabs */}
            <CardHeader className="pb-0 pt-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-sm">
                  {allFixed ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                      <span className="font-medium text-green-400">Apto para publicar</span>
                    </>
                  ) : (
                    <>
                      <div className="flex gap-4">
                        {counts.fatal > 0 && (
                          <span className="text-red-400">{counts.fatal} Fatais</span>
                        )}
                        {counts.critical > 0 && (
                          <span className="text-orange-400">{counts.critical} Críticos</span>
                        )}
                        {counts.warning > 0 && (
                          <span className="text-yellow-400">{counts.warning} Alertas</span>
                        )}
                      </div>
                    </>
                  )}
                </div>
                {counts.fixed > 0 && !allFixed && (
                  <button
                    onClick={() => setShowFixed(!showFixed)}
                    className="text-xs text-neutral-500 hover:text-neutral-300 flex items-center gap-1"
                  >
                    {showFixed ? 'Esconder' : 'Mostrar'} corrigidos ({counts.fixed})
                    {showFixed ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                  </button>
                )}
              </div>

              {/* Tabs */}
              <div className="flex gap-1 border-b border-neutral-800/40 mt-2">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as TabType)}
                    className={`px-3 py-2 text-xs font-medium transition-colors relative ${
                      activeTab === tab.id 
                        ? 'text-neutral-200' 
                        : 'text-neutral-500 hover:text-neutral-300'
                    }`}
                  >
                    <span className={tab.color}>{tab.label}</span>
                    {tab.count > 0 && (
                      <span className="ml-1.5 text-neutral-600">({tab.count})</span>
                    )}
                    {activeTab === tab.id && (
                      <motion.div 
                        layoutId="activeTab"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-green-500"
                        transition={{ duration: 0.2 }}
                      />
                    )}
                  </button>
                ))}
              </div>
            </CardHeader>

            <CardContent className="p-0">
              {/* Compact table */}
              <div className="divide-y divide-neutral-800/20">
                <div className="grid grid-cols-12 gap-2 px-4 py-2 text-xs text-neutral-500 font-medium uppercase tracking-wider">
                  <div className="col-span-3">Campo</div>
                  <div className="col-span-5">Valor</div>
                  <div className="col-span-2">Status</div>
                  <div className="col-span-1"></div>
                  <div className="col-span-1"></div>
                </div>

                <AnimatePresence mode="popLayout">
                  {visibleRows.length > 0 ? (
                    visibleRows.map((r, i) => {
                      const idx = RAW_ROWS.indexOf(r);
                      const isFixed = states[idx];
                      const isExpanded = expandedRow === idx;
                      
                      return (
                        <motion.div
                          key={r.field}
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          transition={{ duration: 0.2 }}
                        >
                          <div 
                            className={`grid grid-cols-12 gap-2 px-4 py-2 cursor-pointer transition-all duration-200 relative group ${
                              isFixed 
                                ? 'opacity-60 border-l-4 border-green-500' 
                                : 'hover:shadow-[0_0_12px_rgba(34,197,94,0.3)] hover:bg-green-500/5 border-l-4 border-transparent hover:border-green-500/50'
                            }`}
                            onClick={() => onToggle(idx)}
                            onMouseEnter={() => setHoveredRow(idx)}
                            onMouseLeave={() => setHoveredRow(null)}
                          >
                            <div className="col-span-3 text-sm font-medium text-neutral-300">
                              {r.field}
                            </div>
                            <div className="col-span-5 text-sm text-neutral-400 truncate">
                              {isFixed ? r.good : r.bad}
                            </div>
                            <div className="col-span-2 flex items-center gap-1.5">
                              {getIcon(r.type, isFixed)}
                              <span className={`text-xs ${
                                isFixed ? 'text-green-500' : 
                                r.type === 'fatal' ? 'text-red-500' :
                                r.type === 'critical' ? 'text-orange-400' :
                                'text-yellow-400'
                              }`}>
                                {getStatusText(r.type, isFixed)}
                              </span>
                            </div>
                            {/* Hover action indicator */}
                            <div className="col-span-1 flex items-center justify-end gap-1">
                              {hoveredRow === idx && !isFixed && (
                                <motion.div
                                  initial={{ opacity: 0, scale: 0.8 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  exit={{ opacity: 0, scale: 0.8 }}
                                  className="flex items-center gap-1 md:inline-flex text-xs text-green-400 font-medium whitespace-nowrap mr-2"
                                >
                                  <span>✓</span>
                                  <span className="hidden md:inline">Corrigir</span>
                                </motion.div>
                              )}
                            </div>
                            <div className="col-span-1 flex justify-end">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setExpandedRow(isExpanded ? null : idx);
                                }}
                                className="p-1 hover:bg-neutral-700/50 rounded transition-all duration-200"
                                aria-label={isExpanded ? "Fechar detalhes" : "Expandir detalhes"}
                              >
                                <ChevronRight className={`w-4 h-4 transition-all duration-200 ${
                                  isExpanded ? 'rotate-90 text-green-400' : 'text-neutral-400 hover:text-neutral-200'
                                }`} />
                              </button>
                            </div>
                          </div>
                          
                          {/* Expanded detail row */}
                          <AnimatePresence>
                            {isExpanded && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.2 }}
                                className="overflow-hidden"
                              >
                                <div className="px-4 py-3 bg-neutral-800/20 border-l-2 border-green-500/30 ml-4">
                                  <div className="grid grid-cols-2 gap-4 text-xs">
                                    <div>
                                      <p className="text-neutral-500 mb-1 font-medium">Antes</p>
                                      <p className="text-red-400/80 line-through">{r.bad}</p>
                                    </div>
                                    <div>
                                      <p className="text-neutral-500 mb-1 font-medium">Depois</p>
                                      <p className="text-green-400 font-medium">{r.good}</p>
                                    </div>
                                  </div>
                                  <div className="mt-3 pt-3 border-t border-neutral-800/50 space-y-1">
                                    <p className="text-xs">
                                      <span className="text-neutral-500">Regra:</span>
                                      <span className="text-neutral-300 ml-1">{r.rule}</span>
                                    </p>
                                    <p className="text-xs">
                                      <span className="text-neutral-500">Impacto:</span>
                                      <span className={`ml-1 font-medium ${
                                        r.type === 'fatal' ? 'text-red-400' : 
                                        r.type === 'critical' ? 'text-orange-400' : 
                                        'text-yellow-400'
                                      }`}>{r.impact}</span>
                                    </p>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </motion.div>
                      );
                    })
                  ) : (
                    <div className="py-8 text-center text-neutral-500 text-sm">
                      Nenhum item nesta categoria
                    </div>
                  )}
                </AnimatePresence>
              </div>

              {/* Footer with progress */}
              <div className="px-4 py-3 border-t border-neutral-800/40">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-1 w-24 bg-neutral-800 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                        initial={{ width: 0 }}
                        animate={{ width: `${(fixedCount / RAW_ROWS.length) * 100}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <span className="text-xs text-neutral-500">
                      {fixedCount}/{RAW_ROWS.length} corrigidos
                    </span>
                  </div>
                  
                  {allFixed ? (
                    <Button 
                      size="sm"
                      className="bg-green-600 hover:bg-green-500 text-white border-0 text-xs h-7 px-3"
                      onClick={handleScrollToPricing}
                    >
                      Validar meu CSV
                    </Button>
                  ) : (
                    <button
                      onClick={() => {
                        setStates(RAW_ROWS.map(() => true));
                      }}
                      className="text-xs text-green-400 hover:text-green-300"
                    >
                      Corrigir tudo →
                    </button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}