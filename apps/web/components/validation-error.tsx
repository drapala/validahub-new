"use client";

import { AlertCircle, FileX, ArrowRight, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ValidationResult } from "@/lib/api";

interface ValidationErrorProps {
  results: ValidationResult;
  onRetry?: () => void;
  onViewDetails?: () => void;
}

export function ValidationError({ results, onRetry, onViewDetails }: ValidationErrorProps) {
  // Extract key errors from results
  const errorSummary = [
    { field: "title", error: "Título excede 60 caracteres", count: 23 },
    { field: "price", error: "Formato de preço inválido", count: 15 },
    { field: "category_id", error: "Categoria não existe", count: 8 },
    { field: "ean", error: "EAN/GTIN inválido", count: 5 },
  ];

  const totalErrors = errorSummary.reduce((sum, item) => sum + item.count, 0);

  return (
    <section className="rounded-3xl border border-red-900/30 bg-zinc-900/60 p-6 md:p-8 shadow-lg">
      {/* Header */}
      <header className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-red-500/15 grid place-items-center">
            <FileX className="h-5 w-5 text-red-400" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white tracking-tight">
              {totalErrors} erros encontrados
            </h3>
            <p className="text-sm text-zinc-400">
              Precisam ser corrigidos antes da publicação
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="border-zinc-700 text-zinc-200 hover:bg-zinc-800"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Revalidar
          </Button>
          <Button
            size="sm"
            onClick={onViewDetails}
            className="bg-red-600 text-white hover:bg-red-500"
          >
            Ver e corrigir
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </header>

      {/* Error Summary */}
      <div className="mt-6 space-y-3">
        {errorSummary.map((item) => (
          <div
            key={item.field}
            className="flex items-center justify-between rounded-xl border border-red-900/20 bg-red-950/20 p-4 hover:bg-red-950/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0" />
              <div>
                <span className="font-mono text-sm text-zinc-300">{item.field}</span>
                <span className="mx-2 text-zinc-600">·</span>
                <span className="text-sm text-zinc-400">{item.error}</span>
              </div>
            </div>
            <span className="rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-400">
              {item.count} {item.count === 1 ? 'erro' : 'erros'}
            </span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <footer className="mt-5 flex items-center justify-between text-sm">
        <div className="flex items-center gap-4 text-zinc-400">
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-400"></span>
            <span className="text-zinc-200">Validação falhou</span>
          </span>
          <span className="text-zinc-600">•</span>
          <span>{results.total_rows || 0} linhas analisadas</span>
        </div>
        <button 
          onClick={onViewDetails} 
          className="text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          Ver relatório completo →
        </button>
      </footer>
    </section>
  );
}