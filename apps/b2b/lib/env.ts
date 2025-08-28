// Valida a existência da URL da API e exporta a flag de mock.
// Durante o build, essas variáveis podem não estar disponíveis
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '';

// Só valida em runtime, não durante o build
if (typeof window !== 'undefined' && !apiBaseUrl) {
  console.error("A variável de ambiente NEXT_PUBLIC_API_BASE_URL não está definida.");
}

export const API_BASE = apiBaseUrl || 'http://localhost:3001';
export const MOCK = process.env.NEXT_PUBLIC_MOCK === "1";