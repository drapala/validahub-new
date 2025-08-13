"use client";

import { useState } from "react";
import { DropzoneCard } from "@/components/dropzone-card";
import { CategoryPicker } from "@/components/category-picker";
import { ResultSummary } from "@/components/result-summary";
import { ApplyFixesBar } from "@/components/apply-fixes-bar";
import { api, ValidationResult } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { ResultsTable } from "@/components/results-table"; // Importar a nova tabela

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [marketplace, setMarketplace] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [results, setResults] = useState<ValidationResult | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isAsyncing, setIsAsyncing] = useState(false);
  const router = useRouter();

  const isLarge = (f: File | null) => (f ? f.size > 1024 * 1024 * 2 : false);

  const handleValidateSync = async () => {
    if (!file || !marketplace || !category) {
      toast.error("Selecione arquivo, marketplace e categoria");
      return;
    }
    setIsSyncing(true);
    try {
      const res = await api.validateCsv({ marketplace, category }, file);
      setResults(res);
      toast.success("Validação concluída");
    } catch (e: any) {
      toast.error(e?.message ?? "Falha na validação");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleUploadAsync = async () => {
    if (!file || !marketplace || !category) {
      toast.error("Selecione arquivo, marketplace e categoria");
      return;
    }
    setIsAsyncing(true);
    try {
      // Fallback: se /upload/init falhar, tenta /jobs com multipart
      try {
        const init = await api.uploadInit();
        await api.putPresigned(init.url, init.headers, file);
        const job = await api.createJob({ upload_ref: init.upload_ref, marketplace, category });
        toast.success(`Job ${job.job_id} criado`);
        router.push(`/results/${job.job_id}`);
      } catch (initError) {
        console.warn("Presigned URL falhou, tentando fallback multipart:", initError);
        const job = await api.createJob({ marketplace, category, file });
        toast.success(`Job ${job.job_id} criado (fallback)`);
        router.push(`/results/${job.job_id}`);
      }
    } catch (e: any) {
      toast.error(e?.message ?? "Falha no upload");
    } finally {
      setIsAsyncing(false);
    }
  };

  const isLoading = isSyncing || isAsyncing;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Upload</h1>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6 space-y-4">
          <DropzoneCard
            onFileAccepted={(f) => setFile(f)}
            currentFile={file}
          />
          <CategoryPicker
            marketplace={marketplace}
            category={category}
            onChange={(mp, cat) => { setMarketplace(mp); setCategory(cat); }}
          />
          <div className="flex gap-3">
            <button 
              className="btn btn-primary" 
              onClick={isLarge(file) ? handleUploadAsync : handleValidateSync}
              disabled={isLoading}
            >
              {isLoading ? "Processando..." : (isLarge(file) ? "Enviar (Assíncrono)" : "Validar (Síncrono)")}
            </button>
            <button className="btn btn-ghost" onClick={() => { setFile(null); setResults(null); }}>
              Limpar
            </button>
          </div>
        </div>
        <div className="card p-6">
          {!results ? (
            <div className="text-zinc-400 flex items-center justify-center h-full">
              Solte um CSV e inicie a validação para ver o resumo e a tabela de resultados.
            </div>
          ) : (
            <div className="space-y-4">
              <ResultSummary results={results} />
              <ResultsTable results={results} />
              <ApplyFixesBar results={results} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}