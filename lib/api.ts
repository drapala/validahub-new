const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:3001";

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

// Tipo ValidationResult adicionado
export type ValidationResult = {
  items: Array<{
    sku: string;
    field: string;
    code: string;
    message: string;
    suggestion?: string;
    severity: "error" | "warning" | "info";
  }>;
  ruleset_version?: string;
  source_url?: string;
};


export const api = {
  login: async (password: string) => {
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
      marketplace: params.marketplace.toUpperCase(), 
      category: params.category.toUpperCase() 
    });
    const form = new FormData();
    form.append("file", file);
    return http<ValidationResult>(`/validate_csv?${qs.toString()}`, {
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
          marketplace: req.marketplace.toUpperCase(),
          category: req.category.toUpperCase()
        }),
      });
    } else if (req.file) {
      // Fallback com multipart/form-data
      const form = new FormData();
      form.append("file", req.file);
      form.append("marketplace", req.marketplace.toUpperCase());
      form.append("category", req.category.toUpperCase());
      return http<CreateJobResponse>("/jobs", {
        method: "POST",
        body: form,
      });
    } else {
      throw new Error("É necessário 'upload_ref' ou 'file' para criar um job");
    }
  },

  getJob: async (jobId: string) => {
    if (MOCK) {
      console.log(`Buscando job mockado: ${jobId}`);
      return Promise.resolve({
        job_id: jobId,
        status: "completed",
        marketplace: "MOCKPLACE",
        category: "MOCKATEGORY",
        created_at: new Date().toISOString(),
        links: {
          corrected: "/mock-corrected.csv",
          rejected: "/mock-rejected.csv",
          report: "/mock-report.json"
        }
      });
    }
    return http<JobResponse>(`/jobs/${jobId}`);
  },

  getRuleset: (marketplace: string, category: string) => {
    return http<any>("/rulesets", { method: "GET" });
  },

  getDiff: async (from: string, to: string) => {
    const qs = new URLSearchParams({ from, to });
    return http<any>(`/diff?${qs.toString()}`, { method: "GET" });
  },
};