"use client";

import * as React from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ValidationResult } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

type ResultsTableProps = {
  results: ValidationResult;
};

const severityMap = {
  error: "destructive",
  warning: "secondary",
  info: "default",
} as const;

const TableHeader = () => (
  <div className="flex items-center px-4 h-10 sticky top-0 bg-card z-10 border-b border-border">
    <div className="w-1/6 truncate text-sm font-semibold">Linha</div>
    <div className="w-1/6 truncate text-sm font-semibold">Coluna</div>
    <div className="w-1/6 truncate text-sm font-semibold">Severidade</div>
    <div className="w-2/6 truncate text-sm font-semibold">Erro</div>
    <div className="w-1/6 truncate text-sm font-semibold">Sugestão</div>
  </div>
);

export function ResultsTable({ results }: ResultsTableProps) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const errors = results.errors || [];

  const rowVirtualizer = useVirtualizer({
    count: errors.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 38,
    overscan: 5,
    // Adiciona uma key única para cada item
    getItemKey: (index) => `${errors[index].row}-${errors[index].column}-${index}`,
  });

  if (errors.length === 0) {
    return (
      <div className="h-[200px] border border-border rounded-2xl flex items-center justify-center text-zinc-400">
        Nenhum erro encontrado
      </div>
    );
  }

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto border border-border rounded-2xl relative">
      <TableHeader />
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: "100%", position: "relative" }}>
        {rowVirtualizer.getVirtualItems().map((virtualItem) => {
          const item = errors[virtualItem.index];
          if (!item) return null;

          return (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
              className="flex items-center px-4 border-b border-border h-[38px]"
            >
              <div className="w-1/6 truncate text-sm font-mono">{item.row}</div>
              <div className="w-1/6 truncate text-sm">{item.column}</div>
              <div className="w-1/6 truncate text-sm">
                <Badge variant={severityMap[item.severity]}>{item.severity}</Badge>
              </div>
              <div className="w-2/6 truncate text-sm text-zinc-400">{item.error}</div>
              <div className="w-1/6 truncate text-sm text-emerald-400">{item.suggestion || '-'}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}