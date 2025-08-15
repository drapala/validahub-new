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
  
  const handleReport = async () => {
    if (!results) {
      toast.error("Nenhum resultado para gerar relatório");
      return;
    }
    
    setIsLoading(true);
    try {
      // Create report data
      const report = {
        timestamp: new Date().toISOString(),
        marketplace,
        category,
        summary: {
          total_rows: results.total_rows,
          errors: errorCount,
          warnings: warningCount,
          total_issues: errorCount + warningCount,
          processing_time: results.summary?.processing_time_seconds || results.processing_time_ms
        },
        issues: [] as any[]
      };
      
      // Extract all issues from validation_items
      if (results.validation_items) {
        results.validation_items.forEach(item => {
          item.errors?.forEach(error => {
            report.issues.push({
              row: item.row_number,
              severity: error.severity,
              field: error.field,
              message: error.message,
              current_value: error.value,
              expected: error.expected
            });
          });
        });
      }
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `validation-report-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success("Relatório baixado com sucesso!");
    } catch (error: any) {
      toast.error(error.message || "Erro ao gerar relatório");
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

  // Count total problems from validation_items
  let errorCount = 0;
  let warningCount = 0;
  
  if (results.validation_items) {
    results.validation_items.forEach(item => {
      item.errors?.forEach(error => {
        if (error.severity === 'ERROR') {
          errorCount++;
        } else if (error.severity === 'WARNING') {
          warningCount++;
        }
      });
    });
  } else {
    errorCount = results.summary?.total_errors || results.error_rows || 0;
    warningCount = results.summary?.total_warnings || results.warnings_count || 0;
  }
  
  const totalIssues = errorCount + warningCount;
  const hasIssues = totalIssues > 0;

  return (
    <div className="sticky bottom-4 bg-card/80 backdrop-blur border border-border rounded-2xl p-4 flex items-center justify-between">
      <div className="text-zinc-400 text-sm">
        {hasIssues 
          ? `${totalIssues} problemas encontrados (${errorCount} erros, ${warningCount} alertas). Correção automática disponível.`
          : "Nenhum problema encontrado. CSV está válido!"
        }
      </div>
      {hasIssues && (
        <div className="flex gap-3">
          <button 
            className="btn btn-ghost" 
            onClick={handleReport}
            disabled={isLoading}
          >
            {isLoading ? "Processando..." : "Baixar Relatório"}
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