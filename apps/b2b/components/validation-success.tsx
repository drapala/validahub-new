"use client";

import { CheckCircle2, Download, Upload, Copy, Check } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ValidationResult } from "@/lib/api";

interface ValidationSuccessProps {
  results: ValidationResult;
  onExport?: () => void;
  onPublish?: () => void;
}

export function ValidationSuccess({ results, onExport, onPublish }: ValidationSuccessProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = async (value: string, field: string) => {
    await navigator.clipboard.writeText(value);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  // Sample validated data - in real app, this would come from results
  const validatedFields = [
    { 
      field: "title", 
      value: "Produto Incrível — Entrega Imediata", 
      status: "Otimizado",
      modified: true 
    },
    { 
      field: "price", 
      value: "15999.99", 
      status: "Formato OK",
      modified: false 
    },
    { 
      field: "category_id", 
      value: "MLB1055", 
      status: "Categoria válida",
      modified: false 
    },
    { 
      field: "brand", 
      value: "Generic", 
      status: "Preenchido",
      modified: true 
    },
    { 
      field: "ean", 
      value: "7890123456789", 
      status: "EAN correto",
      modified: false 
    },
  ];

  return (
    <section className="rounded-3xl border border-zinc-800 bg-zinc-900/60 p-6 md:p-8 shadow-lg">
      {/* Header */}
      <header className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-emerald-500/15 grid place-items-center">
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white tracking-tight">CSV validado</h3>
            <p className="text-sm text-zinc-400">Pronto para publicar no marketplace</p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onExport}
            className="hidden md:inline-flex border-zinc-700 text-zinc-200 hover:bg-zinc-800"
          >
            <Download className="mr-2 h-4 w-4" />
            Exportar CSV
          </Button>
          <Button
            size="sm"
            onClick={onPublish}
            className="bg-emerald-600 text-white hover:bg-emerald-500"
          >
            <Upload className="mr-2 h-4 w-4" />
            Publicar agora
          </Button>
        </div>
      </header>

      {/* Table */}
      <div className="mt-6 overflow-hidden rounded-2xl border border-emerald-900/30">
        <table className="w-full text-sm">
          <thead className="bg-zinc-900/70">
            <tr className="text-zinc-400">
              <th className="text-left font-medium px-5 py-3 w-1/4">Campo</th>
              <th className="text-left font-medium px-5 py-3">Valor</th>
              <th className="text-left font-medium px-5 py-3 w-1/5">Status</th>
            </tr>
          </thead>
          <tbody className="[&_tr:nth-child(even)]:bg-zinc-900/40">
            {validatedFields.map((item) => (
              <tr key={item.field} className="border-t border-zinc-800/60 hover:bg-zinc-800/30 transition-colors">
                <td className="px-5 py-3 text-zinc-300 font-medium">{item.field}</td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2 group">
                    <span className="font-mono text-zinc-100 truncate max-w-md">{item.value}</span>
                    <button
                      onClick={() => handleCopy(item.value, item.field)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-zinc-700 rounded"
                    >
                      {copiedField === item.field ? (
                        <Check className="h-3 w-3 text-emerald-400" />
                      ) : (
                        <Copy className="h-3 w-3 text-zinc-400" />
                      )}
                    </button>
                  </div>
                </td>
                <td className="px-5 py-3">
                  <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2.5 py-1 text-emerald-400">
                    {item.modified && (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    )}
                    <span className="text-xs font-medium">{item.status}</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <footer className="mt-5 flex items-center justify-between text-sm">
        <div className="flex items-center gap-4 text-zinc-400">
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-zinc-200">Anúncio aprovado</span>
          </span>
          <span className="text-zinc-600">•</span>
          <span>{results.total_rows || 0} produtos validados</span>
        </div>
        <button 
          onClick={() => {}} 
          className="text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          Ver detalhes técnicos →
        </button>
      </footer>
    </section>
  );
}