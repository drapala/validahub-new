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
  const [reportFormat, setReportFormat] = useState<"json" | "excel" | "pdf">("excel");
  const [showFormatMenu, setShowFormatMenu] = useState(false);
  
  const handleReport = async (format: "json" | "excel" | "pdf" = reportFormat) => {
    if (!results) {
      toast.error("Nenhum resultado para gerar relatório");
      return;
    }
    
    setIsLoading(true);
    setShowFormatMenu(false);
    
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
      
      // Call API to generate report in selected format
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'}/api/v1/validation_report?format=${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(report)
      });
      
      if (!response.ok) {
        throw new Error(`Erro ao gerar relatório: ${response.statusText}`);
      }
      
      // Get the blob from response
      const blob = await response.blob();
      
      // Determine file extension based on format
      const extensions: Record<string, string> = {
        json: 'json',
        excel: 'xlsx',
        pdf: 'pdf'
      };
      
      // Download the file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `validation-report-${Date.now()}.${extensions[format]}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      const formatNames: Record<string, string> = {
        json: 'JSON',
        excel: 'Excel',
        pdf: 'PDF'
      };
      
      toast.success(`Relatório ${formatNames[format]} baixado com sucesso!`);
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
          <div className="relative">
            <button 
              className="btn btn-ghost flex items-center gap-2" 
              onClick={() => setShowFormatMenu(!showFormatMenu)}
              disabled={isLoading}
            >
              {isLoading ? "Processando..." : (
                <>
                  Baixar Relatório
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </>
              )}
            </button>
            {showFormatMenu && (
              <div className="absolute bottom-full left-0 mb-2 bg-card border border-border rounded-lg shadow-lg py-1 min-w-[150px]">
                <button
                  className="w-full px-4 py-2 text-left hover:bg-zinc-800 transition-colors flex items-center gap-2"
                  onClick={() => handleReport('excel')}
                >
                  <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M15.8,20H14L12,16.6L10,20H8.2L11.1,15.5L8.2,11H10L12,14.4L14,11H15.8L12.9,15.5L15.8,20M13,9V3.5L18.5,9H13Z"/>
                  </svg>
                  Excel (.xlsx)
                </button>
                <button
                  className="w-full px-4 py-2 text-left hover:bg-zinc-800 transition-colors flex items-center gap-2"
                  onClick={() => handleReport('pdf')}
                >
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M10.5,11.5C10.5,12.33 9.83,13 9,13H7V9H9C9.83,9 10.5,9.67 10.5,10.5V11.5M14.5,13.5C14.5,14.33 13.83,15 13,15H11V9H13C13.83,9 14.5,9.67 14.5,10.5V13.5M18.5,10.5H17V14H18.5V12.5H17V11H18.5V10.5M13,3.5L18.5,9H13V3.5M8,10.5V11.5H9C9.28,11.5 9.5,11.28 9.5,11V10.5C9.5,10.22 9.28,10 9,10H8M12,10.5V13.5H13C13.28,13.5 13.5,13.28 13.5,13V10.5C13.5,10.22 13.28,10 13,10H12Z"/>
                  </svg>
                  PDF
                </button>
                <button
                  className="w-full px-4 py-2 text-left hover:bg-zinc-800 transition-colors flex items-center gap-2"
                  onClick={() => handleReport('json')}
                >
                  <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3H16Z"/>
                  </svg>
                  JSON
                </button>
              </div>
            )}
          </div>
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