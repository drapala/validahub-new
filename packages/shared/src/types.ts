export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Job {
  id: string;
  status: JobStatus;
  fileName: string;
  marketplace: string;
  category: string;
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  error?: string;
  result?: JobResult;
}

export interface JobResult {
  totalRows: number;
  validRows: number;
  errorRows: number;
  warnings: number;
  downloadUrl?: string;
}

export interface ValidationError {
  row: number;
  column: string;
  error: string;
  value: any;
  suggestion?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}