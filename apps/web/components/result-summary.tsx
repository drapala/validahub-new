"use client";

import { ValidationResult } from "@/lib/api";

export function ResultSummary({ results }: { results: ValidationResult }) {
  // Count total problems, not unique rows
  let totalErrors = 0;
  let totalWarnings = 0;
  
  if (results.validation_items) {
    results.validation_items.forEach(item => {
      item.errors?.forEach(error => {
        if (error.severity === 'ERROR') {
          totalErrors++;
        } else if (error.severity === 'WARNING') {
          totalWarnings++;
        }
      });
    });
  }
  
  const errors = totalErrors || results.summary?.total_errors || results.error_rows || 0;
  const warnings = totalWarnings || results.summary?.total_warnings || results.warnings_count || 0;
  const valids = results.valid_rows || 0;

  return (
    <div className="grid gap-3 md:grid-cols-4">
      <div className="card p-4">
        <div className="text-sm text-zinc-400">Erros</div>
        <div className="text-2xl font-semibold text-red-400">{errors}</div>
      </div>
      <div className="card p-4">
        <div className="text-sm text-zinc-400">Alertas</div>
        <div className="text-2xl font-semibold text-yellow-300">{warnings}</div>
      </div>
      <div className="card p-4">
        <div className="text-sm text-zinc-400">OK</div>
        <div className="text-2xl font-semibold text-emerald-400">{valids}</div>
      </div>
      <div className="card p-4">
        <div className="text-sm text-zinc-400">Total (linhas)</div>
        <div className="text-lg font-medium">{results.total_rows || 0}</div>
        <div className="text-xs text-zinc-500">
          {results.summary?.processing_time_seconds 
            ? `${(results.summary.processing_time_seconds * 1000).toFixed(0)}ms` 
            : `${results.processing_time_ms || 0}ms`}
        </div>
      </div>
    </div>
  );
}