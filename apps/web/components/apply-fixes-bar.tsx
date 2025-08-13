"use client";

import { useState } from "react";
import { toast } from "sonner";
import { api, ValidationResult } from "@/lib/api";

interface ApplyFixesBarProps {
  results: ValidationResult;
  file: File | null;
  marketplace: string;
  category: string;
}

export function ApplyFixesBar({ results, file, marketplace, category }: ApplyFixesBarProps) {
  const [isLoading, setIsLoading] = useState(false);
  
  const handlePreview = async () => {
    if (!file || !marketplace || !category) {
      toast.error("Arquivo e configurações necessários");
      return;
    }
    
    setIsLoading(true);
    try {
      const preview = await api.correctionPreview(
        { marketplace, category },
        file
      );
      
      toast.success(
        `Preview: ${preview.summary.total_corrections} correções disponíveis (${preview.summary.success_rate.toFixed(1)}% de sucesso)`
      );
      
      // TODO: Mostrar modal com detalhes do preview
      console.log("Preview details:", preview);
    } catch (error: any) {
      toast.error(error.message || "Erro ao gerar preview");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!file || !marketplace || !category) {
      toast.error("Arquivo e configurações necessários");
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await api.correctCsv(
        { marketplace, category },
        file
      );
      
      // Create download link
      const url = window.URL.createObjectURL(result.blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(
        `CSV corrigido baixado! ${result.corrections} correções aplicadas (${result.successRate} de sucesso)`
      );
    } catch (error: any) {
      toast.error(error.message || "Erro ao corrigir CSV");
    } finally {
      setIsLoading(false);
    }
  };

  const hasErrors = results.error_rows > 0;

  return (
    <div className="sticky bottom-4 bg-card/80 backdrop-blur border border-border rounded-2xl p-4 flex items-center justify-between">
      <div className="text-zinc-400 text-sm">
        {hasErrors 
          ? `${results.error_rows} erros encontrados. Correção automática disponível.`
          : "Nenhum erro encontrado. CSV está válido!"
        }
      </div>
      {hasErrors && (
        <div className="flex gap-3">
          <button 
            className="btn btn-ghost" 
            onClick={handlePreview}
            disabled={isLoading}
          >
            {isLoading ? "Processando..." : "Preview"}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleDownload}
            disabled={isLoading}
          >
            {isLoading ? "Processando..." : "Baixar CSV corrigido"}
          </button>
        </div>
      )}
    </div>
  );
}