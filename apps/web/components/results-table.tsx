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
    <div className="w-1/6 truncate text-sm font-semibold">SKU</div>
    <div className="w-1/6 truncate text-sm font-semibold">Campo</div>
    <div className="w-1/6 truncate text-sm font-semibold">Código</div>
    <div className="w-2/6 truncate text-sm font-semibold">Mensagem</div>
    <div className="w-1/6 truncate text-sm font-semibold">Sugestão</div>
  </div>
);

export function ResultsTable({ results }: ResultsTableProps) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: results.items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 38,
    overscan: 5,
    // Adiciona uma key única para cada item
    getItemKey: (index) => `${results.items[index].sku}-${results.items[index].field}-${index}`,
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto border border-border rounded-2xl relative">
      <TableHeader />
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, width: "100%", position: "relative" }}>
        {rowVirtualizer.getVirtualItems().map((virtualItem) => {
          const item = results.items[virtualItem.index];
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
              <div className="w-1/6 truncate text-sm font-mono">{item.sku}</div>
              <div className="w-1/6 truncate text-sm">{item.field}</div>
              <div className="w-1/6 truncate text-sm">
                <Badge variant={severityMap[item.severity]}>{item.code}</Badge>
              </div>
              <div className="w-2/6 truncate text-sm text-zinc-400">{item.message}</div>
              <div className="w-1/6 truncate text-sm text-emerald-400">{item.suggestion}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}