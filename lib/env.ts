// Valida a existência da URL da API e exporta a flag de mock.
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
if (!apiBaseUrl) {
  throw new Error("A variável de ambiente NEXT_PUBLIC_API_BASE_URL não está definida.");
}

export const API_BASE = apiBaseUrl;
export const MOCK = process.env.NEXT_PUBLIC_MOCK === "1";