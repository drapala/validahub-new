import { authService } from './auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

export interface Job {
  id: string
  seller: string
  channel: string
  created_at: string
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'needs_review'
  errors_count: number
  warnings_count: number
  rows_processed: number
  duration_ms: number
  type: 'upload_csv' | 'api' | 'delta' | 'full'
  marketplace_account?: string
  severity?: 'blocking' | 'warning' | 'info'
}

export interface JobFilters {
  status?: string[]
  channel?: string[]
  seller?: string
  period?: string
  severity?: string
  type?: string[]
  page?: number
  limit?: number
}

export interface JobStats {
  total: number
  succeeded: number
  failed: number
  running: number
  queued: number
  needs_review: number
  avg_latency_ms: number
  p95_latency_ms: number
}

export const jobsService = {
  async getJobs(filters: JobFilters): Promise<{ jobs: Job[]; total: number }> {
    const params = new URLSearchParams()
    
    if (filters.status?.length) {
      filters.status.forEach(s => params.append('status', s))
    }
    if (filters.channel?.length) {
      filters.channel.forEach(c => params.append('channel', c))
    }
    if (filters.seller) params.append('seller', filters.seller)
    if (filters.period) params.append('period', filters.period)
    if (filters.severity) params.append('severity', filters.severity)
    if (filters.type?.length) {
      filters.type.forEach(t => params.append('type', t))
    }
    if (filters.page) params.append('page', String(filters.page))
    if (filters.limit) params.append('limit', String(filters.limit))

    const response = await fetch(`${API_URL}/api/jobs?${params}`, {
      headers: {
        'Authorization': `Bearer ${authService.getAccessToken()}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch jobs')
    }

    return response.json()
  },

  async getJobById(id: string): Promise<Job> {
    const response = await fetch(`${API_URL}/api/jobs/${id}`, {
      headers: {
        'Authorization': `Bearer ${authService.getAccessToken()}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch job')
    }

    return response.json()
  },

  async retryJob(id: string): Promise<Job> {
    const response = await fetch(`${API_URL}/api/jobs/${id}/retry`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authService.getAccessToken()}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to retry job')
    }

    return response.json()
  },

  async applyFixes(id: string, fixes: any): Promise<Job> {
    const response = await fetch(`${API_URL}/api/jobs/${id}/apply-fixes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authService.getAccessToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(fixes),
    })

    if (!response.ok) {
      throw new Error('Failed to apply fixes')
    }

    return response.json()
  },

  async getStats(filters: JobFilters): Promise<JobStats> {
    const params = new URLSearchParams()
    
    if (filters.period) params.append('period', filters.period)
    if (filters.channel?.length) {
      filters.channel.forEach(c => params.append('channel', c))
    }

    const response = await fetch(`${API_URL}/api/jobs/stats?${params}`, {
      headers: {
        'Authorization': `Bearer ${authService.getAccessToken()}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch job stats')
    }

    return response.json()
  },
}