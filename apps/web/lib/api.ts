// const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:3001";

import { API_BASE, MOCK } from "./env";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    // Omitir credenciais no modo mock para evitar avisos do navegador
    credentials: MOCK ? "omit" : "include",
    ...init,
  });

  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const j = await res.json();
      msg = j?.message || j?.detail || msg;
    } catch {}
    throw new Error(msg);
  }

  if (res.headers.get("content-type")?.includes("application/json")) {
    return res.json() as Promise<T>;
  }
  // Return can be empty or text
  return (await res.text()) as T;
}

export type UploadInitResponse = { 
  url: string; 
  headers: Record<string, string>; 
  upload_ref: string 
};

export type CreateJobRequest = { 
  upload_ref?: string;
  marketplace: string; 
  category: string;
  file?: File; // Para o fallback multipart
};

export type CreateJobResponse = { job_id: string };

export type JobResponse = {
  id: string;
  status: "queued" | "processing" | "done" | "failed";
  eta?: string;
  logs?: string[];
  links?: { corrected?: string; rejected?: string; report?: string };
};

// Tipo ValidationResult - matching backend response
export type ValidationResult = {
  total_rows: number;
  valid_rows: number;
  error_rows: number;
  errors: Array<{
    row: number;
    column: string;
    error: string;
    value?: string | null;
    suggestion?: string;
    severity: "error" | "warning" | "info";
  }>;
  warnings_count: number;
  processing_time_ms: number;
};


export const api = {
  login: async (email: string, password: string) => {
    if (MOCK) {
      console.log("Login mockado com sucesso");
      return Promise.resolve({ token: "mock-token" });
    }
    return http<{ token: string }>("/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  },

  getStatus: async () => {
    if (MOCK) return Promise.resolve({ status: "ok" });
    return http<{ status: string }>("/status");
  },

  validateCsv: async (params: { marketplace: string; category: string }, file: File) => {
    if (MOCK) {
      console.log("Retornando validação mockada para", params);
      // Simula um pequeno delay de rede
      await new Promise(resolve => setTimeout(resolve, 500));
      return Promise.resolve<ValidationResult>({
        ruleset_version: "2025-01-15.1.0",
        source_url: "https://example.com/rules",
        items: [
          { sku: "SKU-1001", field: "title", code: "TITLE_TOO_LONG", message: "Título com mais de 200 caracteres", severity: "error", suggestion: "Cortar para 200" },
          { sku: "SKU-1002", field: "description", code: "MISSING_FIELD", message: "Descrição está faltando", severity: "error", suggestion: "Adicionar descrição" },
          { sku: "SKU-1003", field: "price", code: "INVALID_PRICE", message: "Preço parece baixo demais", severity: "warning", suggestion: "Verificar preço" },
        ],
      });
    }
    const qs = new URLSearchParams({ 
      marketplace: params.marketplace, 
      category: params.category 
    });
    const form = new FormData();
    form.append("file", file);
    return http<ValidationResult>(`/api/v1/validate_csv?${qs.toString()}`, {
      method: "POST",
      body: form,
    });
  },

  uploadInit: async (): Promise<UploadInitResponse> => {
    return http<UploadInitResponse>("/upload/init", { method: "POST" });
  },

  putPresigned: async (url: string, headers: Record<string, string>, file: File) => {
    const res = await fetch(url, {
      method: "PUT",
      body: file,
      headers
    });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return true;
  },

  createJob: async (req: CreateJobRequest) => {
    if (MOCK) {
      console.log("Criando job mockado");
      const jobId = `mock-job-${Date.now()}`;
      return Promise.resolve({ job_id: jobId });
    }
    // Fallback: se tem upload_ref usa JSON, senão multipart
    if (req.upload_ref) {
      return http<CreateJobResponse>("/jobs", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          upload_ref: req.upload_ref,
          marketplace: req.marketplace,
          category: req.category
        }),
      });
    } else if (req.file) {
      // Fallback com multipart/form-data
      const form = new FormData();
      form.append("file", req.file);
      form.append("marketplace", req.marketplace);
      form.append("category", req.category);
      return http<CreateJobResponse>("/jobs", {
        method: "POST",
        body: form,
      });
    } else {
      throw new Error("É necessário 'upload_ref' ou 'file' para criar um job");
    }
  },

  getJob: async (jobId: string): Promise<JobResponse> => {
    if (MOCK) {
      console.log(`Buscando job mockado: ${jobId}`);
      return Promise.resolve({
        id: jobId,
        status: "done",
        eta: "2 minutos",
        logs: ["Iniciando processamento...", "Validando arquivo...", "Concluído!"],
        links: {
          corrected: "/mock-corrected.csv",
          rejected: "/mock-rejected.csv",
          report: "/mock-report.json"
        }
      });
    }
    return http<JobResponse>(`/jobs/${jobId}`);
  },

  getRuleset: (_marketplace: string, _category: string) => {
    return http<any>("/rulesets", { method: "GET" });
  },

  getDiff: async (from: string, to: string) => {
    const qs = new URLSearchParams({ from, to });
    return http<any>(`/diff?${qs.toString()}`, { method: "GET" });
  },
};