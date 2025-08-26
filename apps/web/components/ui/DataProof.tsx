'use client'

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { motion, AnimatePresence } from "framer-motion";
import Lottie from "lottie-react";

// Minimal inline Lottie (checkmark burst)
const CHECK_BURST = {
  v: "5.7.6",
  fr: 60,
  ip: 0,
  op: 44,
  w: 120,
  h: 120,
  nm: "check",
  ddd: 0,
  assets: [],
  layers: [
    {
      ddd: 0,
      ind: 1,
      ty: 4,
      nm: "check",
      sr: 1,
      ks: { o: { a: 0, k: 100 }, r: { a: 0, k: 0 }, p: { a: 0, k: [60, 60, 0] }, a: { a: 0, k: [0, 0, 0] }, s: { a: 1, k: [{ i: { x: [0.2, 0.2, 0.2], y: [1, 1, 1] }, o: { x: [0.4, 0.4, 0.4], y: [0, 0, 0] }, t: 0, s: [0, 0, 100] }, { t: 18, s: [100, 100, 100] }] } },
      shapes: [
        {
          ty: "sh",
          ks: {
            a: 0,
            k: { i: [], o: [], v: [[-20, 0], [-5, 15], [25, -15]], c: false }
          },
          nm: "check path"
        },
        { ty: "st", c: { a: 0, k: [0.23, 0.87, 0.53, 1] }, o: { a: 0, k: 100 }, w: { a: 0, k: 14 }, lc: 2, lj: 2, ml: 10, nm: "stroke" }
      ],
      ip: 0,
      op: 44,
      st: 0,
      bm: 0
    },
    {
      ddd: 0,
      ind: 2,
      ty: 4,
      nm: "burst",
      sr: 1,
      ks: { o: { a: 1, k: [{ t: 6, s: 100 }, { t: 24, s: 0 }] }, r: { a: 0, k: 0 }, p: { a: 0, k: [60, 60, 0] }, a: { a: 0, k: [0, 0, 0] }, s: { a: 0, k: [100, 100, 100] } },
      shapes: [
        { ty: "el", p: { a: 0, k: [0, 0] }, s: { a: 0, k: [110, 110] }, nm: "circle" },
        { ty: "st", c: { a: 0, k: [0.23, 0.87, 0.53, 1] }, o: { a: 0, k: 100 }, w: { a: 0, k: 4 }, lc: 1, lj: 1, ml: 10, nm: "stroke" }
      ],
      ip: 0,
      op: 30,
      st: 0,
      bm: 0
    }
  ]
};

// Demo rows (error -> fix)
const RAW_ROWS = [
  {
    field: "title",
    bad: "Produto Incrível Compre Agora!!!",
    badHint: "Excesso de caracteres especiais",
    good: "Produto incrível – pronto para envio",
    goodHint: "Título limpo e elegível",
    type: "error"
  },
  {
    field: "price",
    bad: "R$ 15,999.99",
    badHint: "Formato inválido",
    good: "R$ 15.999,99",
    goodHint: "Padrão aceito pelo marketplace",
    type: "error"
  },
  {
    field: "category_id",
    bad: "MLB1234",
    badHint: "Categoria inexistente",
    good: "MLB1055",
    goodHint: "Categoria válida (Celulares e Telefones)",
    type: "error"
  },
  {
    field: "brand",
    bad: "(vazio)",
    badHint: "Campo vazio",
    good: "Acme",
    goodHint: "Marca informada",
    type: "error"
  },
  {
    field: "ean",
    bad: "789012345678",
    badHint: "EAN inválido",
    good: "7890123456789",
    goodHint: "EAN válido (13 dígitos)",
    type: "error"
  },
  {
    field: "description",
    bad: "Produto ótimo",
    badHint: "Descrição muito curta (pode impactar conversão)",
    good: "Produto ótimo com garantia de 1 ano e frete grátis",
    goodHint: "Descrição otimizada para atrair mais cliques",
    type: "warning"
  }
] as const;

type RowState = {
  hovered: boolean;
  fixed: boolean;
};

export default function DataProof() {
  // Keep internal state for each row; start with all false
  const [states, setStates] = React.useState<RowState[]>(() => RAW_ROWS.map(() => ({ hovered: false, fixed: false })));

  const handleScrollToPricing = () => {
    const pricingSection = document.querySelector('[data-section="pricing"]');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Build a safe view over state to avoid undefined indices during hot reloads or transient renders
  const safeStates = React.useMemo<RowState[]>(
    () => Array.from({ length: RAW_ROWS.length }, (_, i) => states[i] ?? { hovered: false, fixed: false }),
    [states]
  );

  const fixedCount = safeStates.reduce((acc, s) => acc + (s.fixed ? 1 : 0), 0);
  const allFixed = fixedCount === RAW_ROWS.length;

  const patchToLength = (arr: RowState[]): RowState[] =>
    Array.from({ length: RAW_ROWS.length }, (_, i) => arr[i] ?? { hovered: false, fixed: false });

  const onEnter = (idx: number) => {
    setStates(prev => {
      const next = [...prev];
      next[idx] = { hovered: true, fixed: true };
      return patchToLength(next);
    });
  };

  const onLeave = (idx: number) => {
    setStates(prev => {
      const next = [...prev];
      const curr = next[idx] ?? { hovered: false, fixed: true };
      next[idx] = { ...curr, hovered: false };
      return patchToLength(next);
    });
  };

  return (
    <div className="min-h-[600px] w-full bg-gradient-to-b from-neutral-900 to-black text-neutral-100 p-6 md:p-10">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-8 md:mb-12">
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tight">
            De <span className="text-red-400">stress</span> para <span className="text-emerald-400">confiança</span>
          </h2>
          <p className="mt-3 text-neutral-300">Passe o mouse sobre as linhas problemáticas e veja a correção acontecer.</p>
        </div>

        <Card className="bg-neutral-900/60 border-neutral-800 shadow-2xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xl flex items-center gap-2">
              <span className="text-lg">
                {allFixed ? "🟢" : "🔴"}
              </span>
              {allFixed ? "Apto para publicar" : "CSV com Erros"}
            </CardTitle>
          </CardHeader>

          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-neutral-300">Campo</TableHead>
                  <TableHead className="text-neutral-300">Valor</TableHead>
                  <TableHead className="text-neutral-300">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {RAW_ROWS.map((r, idx) => {
                  const st = safeStates[idx];
                  const isWarning = r.type === "warning";
                  return (
                    <motion.tr
                      key={r.field}
                      onMouseEnter={() => onEnter(idx)}
                      onMouseLeave={() => onLeave(idx)}
                      initial={false}
                      animate={{ backgroundColor: st.fixed ? "#052e1a" : isWarning ? "#2e2305" : "#2a0b0b" }}
                      transition={{ duration: 0.4 }}
                      className="cursor-pointer"
                    >
                      <TableCell className="font-mono text-neutral-300">{r.field}</TableCell>
                      <TableCell>
                        <div className="relative">
                          <AnimatePresence mode="popLayout" initial={false}>
                            {!st.fixed ? (
                              <motion.div
                                key="bad"
                                initial={{ opacity: 0.6, y: 2 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -2 }}
                                className={`px-3 py-2 rounded-md border ${isWarning ? "bg-amber-900/30 border-amber-700/50" : "bg-red-900/40 border-red-900/50"}`}
                              >
                                <div className={isWarning ? "text-amber-200" : "text-red-200"}>{r.bad}</div>
                                <div className={`text-xs mt-1 ${isWarning ? "text-amber-300/80" : "text-red-300/80"}`}>{r.badHint}</div>
                              </motion.div>
                            ) : (
                              <motion.div
                                key="good"
                                initial={{ opacity: 0, y: 2 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -2 }}
                                className="px-3 py-2 rounded-md bg-emerald-900/30 border border-emerald-800"
                              >
                                <div className="text-emerald-200">{r.good}</div>
                                <div className="text-xs text-emerald-300/80 mt-1">{r.goodHint}</div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </TableCell>
                      <TableCell className="w-[120px]">
                        <div className="flex items-center gap-2">
                          <div className="h-8 w-8">
                            <AnimatePresence mode="wait" initial={false}>
                              {st.fixed ? (
                                <motion.div key="ok" initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }}>
                                  <Lottie animationData={CHECK_BURST} loop={false} />
                                </motion.div>
                              ) : (
                                <motion.div key="x" initial={{ opacity: 0.5 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className={isWarning ? "text-amber-400" : "text-red-400"}>
                                  {isWarning ? "⚠️" : "❌"}
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                          <Badge className={st.fixed ? "bg-emerald-600 hover:bg-emerald-600" : isWarning ? "bg-amber-600 hover:bg-amber-600" : "bg-red-600 hover:bg-red-600"}>
                            {st.fixed ? "Corrigido" : isWarning ? "Sugestão" : "Erro"}
                          </Badge>
                        </div>
                      </TableCell>
                    </motion.tr>
                  );
                })}
              </TableBody>
            </Table>

            {/* Progress summary */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-neutral-300">Correções concluídas</span>
                <span className="text-sm text-neutral-400">{fixedCount}/{RAW_ROWS.length}</span>
              </div>
              <Progress value={(fixedCount / RAW_ROWS.length) * 100} className="h-2" />
              <AnimatePresence>
                {allFixed && (
                  <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }} className="mt-4 flex items-center justify-between rounded-xl border border-emerald-700/40 bg-emerald-900/20 p-4">
                    <div>
                      <p className="font-medium text-emerald-300">Pronto para publicar</p>
                      <p className="text-sm text-emerald-200/80">Todos os erros foram corrigidos automaticamente.</p>
                    </div>
                    <Button 
                      variant="default" 
                      className="bg-emerald-600 hover:bg-emerald-500"
                      onClick={handleScrollToPricing}
                    >
                      Corrigir meu CSV agora
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}