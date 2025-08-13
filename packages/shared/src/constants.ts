export const MARKETPLACES = [
  'mercado_livre',
  'shopee',
  'magalu',
  'amazon',
  'americanas',
] as const;

export const CATEGORIES = [
  'eletronicos',
  'moda',
  'casa',
  'esporte',
  'beleza',
  'livros',
  'brinquedos',
  'alimentos',
] as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ALLOWED_FILE_TYPES = ['.csv', '.xlsx', '.xls'];

export const API_ENDPOINTS = {
  STATUS: '/status',
  VALIDATE: '/validate_csv',
  UPLOAD_INIT: '/upload/init',
  UPLOAD_COMPLETE: '/upload/complete',
  JOBS: '/jobs',
  JOB_DETAIL: (id: string) => `/jobs/${id}`,
  JOB_DOWNLOAD: (id: string) => `/jobs/${id}/download`,
} as const;