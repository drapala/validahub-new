"use client";

import { toast } from "sonner";

export function ApplyFixesBar({ results }: { results: any }) {
  const handlePreview = () => {
    toast.info("Preview de correções (em breve)");
  };

  const handleDownload = () => {
    // Fallback simples: back-end deverá retornar signed URL; por ora apenas placeholder
    toast.info("Download via signed URL (em breve)");
  };

  return (
    <div className="sticky bottom-4 bg-card/80 backdrop-blur border border-border rounded-2xl p-4 flex items-center justify-between">
      <div className="text-zinc-400 text-sm">
        Aplicar correções seguras com preview antes do download.
      </div>
      <div className="flex gap-3">
        <button className="btn btn-ghost" onClick={handlePreview}>Preview</button>
        <button className="btn btn-primary" onClick={handleDownload}>Baixar CSV corrigido</button>
      </div>
    </div>
  );
}