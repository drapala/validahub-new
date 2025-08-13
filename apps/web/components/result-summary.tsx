"use client";

import { ValidationResult } from "@/lib/api";

export function ResultSummary({ results }: { results: ValidationResult }) {
  const errors = results.items.filter(item => item.severity === "error").length;
  const warnings = results.items.filter(item => item.severity === "warning").length;
  const valids = results.items.length - errors - warnings;

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
        <div className="text-sm text-zinc-400">Ruleset</div>
        <div className="text-lg font-medium">{results.ruleset_version ?? "-"}</div>
        {results.source_url && (
          <a 
            className="text-sm text-emerald-400 underline" 
            href={results.source_url} 
            target="_blank" 
            rel="noreferrer"
          >
            Fonte
          </a>
        )}
      </div>
    </div>
  );
}