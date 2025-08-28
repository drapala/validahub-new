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
  // New format with validation_items
  validation_items?: Array<{
    row_number: number;
    status: string;
    errors?: Array<{
      code: string;
      message: string;
      severity: string;
      field?: string;
      value?: any;
      expected?: any;
    }>;
    corrections?: Array<{
      field: string;
      original_value?: any;
      corrected_value: any;
      correction_type: string;
      confidence: number;
    }>;
  }>;
  // Old format for backward compatibility
  errors?: Array<{
    row: number;
    column: string;
    error: string;
    value?: string | null;
    suggestion?: string;
    severity: "error" | "warning" | "info";
  }>;
  summary?: {
    total_errors: number;
    total_warnings: number;
    total_corrections: number;
    error_types: Record<string, number>;
    processing_time_seconds: number;
  };
  warnings_count?: number;
  processing_time_ms?: number;
  auto_fix_applied?: boolean;
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

  validateCsv: async (params: { marketplace: string; category: string; auto_fix?: boolean }, file: File) => {
    if (MOCK) {
      console.log("Retornando validação mockada para", params);
      // Simula um pequeno delay de rede
      await new Promise(resolve => setTimeout(resolve, 500));
      return Promise.resolve<ValidationResult>({
        total_rows: 10,
        valid_rows: 7,
        error_rows: 3,
        errors: [
          { row: 2, column: "title", error: "Título com mais de 200 caracteres", value: "Produto com título muito longo...", suggestion: "Cortar para 200", severity: "error" },
          { row: 5, column: "price", error: "Preço inválido", value: "0", suggestion: "Adicionar preço válido", severity: "error" },
          { row: 8, column: "stock", error: "Estoque negativo", value: "-5", suggestion: "Corrigir estoque", severity: "warning" },
        ],
        warnings_count: 1,
        processing_time_ms: 123
      });
    }
    const qs = new URLSearchParams({ 
      marketplace: params.marketplace, 
      category: params.category,
      auto_fix: String(params.auto_fix ?? false) // By default, do not auto-fix during validation
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

  correctCsv: async (params: { marketplace: string; category: string }, file: File) => {
    const qs = new URLSearchParams({ 
      marketplace: params.marketplace, 
      category: params.category 
    });
    const form = new FormData();
    form.append("file", file);
    
    const res = await fetch(`${API_BASE}/api/v1/correct_csv?${qs.toString()}`, {
      method: "POST",
      body: form,
      credentials: MOCK ? "omit" : "include",
    });
    
    if (!res.ok) {
      throw new Error(`Failed to correct CSV: ${res.status}`);
    }
    
    return {
      blob: await res.blob(),
      filename: res.headers.get("content-disposition")?.split("filename=")[1] || "corrected.csv",
      corrections: res.headers.get("x-corrections-applied") || "0",
      successRate: res.headers.get("x-success-rate") || "0%"
    };
  },

  correctionPreview: async (params: { marketplace: string; category: string }, file: File) => {
    const qs = new URLSearchParams({ 
      marketplace: params.marketplace, 
      category: params.category 
    });
    const form = new FormData();
    form.append("file", file);
    return http<any>(`/api/v1/correction_preview?${qs.toString()}`, {
      method: "POST",
      body: form,
    });
  },
};