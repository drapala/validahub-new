import { z } from 'zod';
import { MARKETPLACES, CATEGORIES } from './constants';

export const validateCsvSchema = z.object({
  file: z.instanceof(File),
  marketplace: z.enum(MARKETPLACES),
  category: z.enum(CATEGORIES),
});

export const uploadInitSchema = z.object({
  fileName: z.string(),
  fileSize: z.number(),
  marketplace: z.enum(MARKETPLACES),
  category: z.enum(CATEGORIES),
});

export const uploadCompleteSchema = z.object({
  uploadId: z.string(),
  parts: z.array(z.object({
    partNumber: z.number(),
    etag: z.string(),
  })),
});

export type ValidateCsvInput = z.infer<typeof validateCsvSchema>;
export type UploadInitInput = z.infer<typeof uploadInitSchema>;
export type UploadCompleteInput = z.infer<typeof uploadCompleteSchema>;