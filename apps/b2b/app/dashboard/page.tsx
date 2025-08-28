'use client'

import { useState } from 'react'
import { JobsTable } from '@/components/dashboard/jobs-table'
import { JobsFilters } from '@/components/dashboard/jobs-filters'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, Download, AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { jobsService } from '@/lib/services/jobs'

// Mock data for now - will be replaced with API call
const mockStats = {
  total: 1245,
  succeeded: 1089,
  failed: 43,
  running: 23,
  queued: 90,
  needsReview: 12,
  avgLatencyMs: 245,
  p95LatencyMs: 890,
}

export default function QueuePage() {
  const [filters, setFilters] = useState({
    status: [],
    channel: [],
    seller: '',
    period: 'last24h',
    severity: 'all',
    type: [],
  })

  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ['jobStats', filters],
    queryFn: () => Promise.resolve(mockStats),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Queue (Jobs)</h1>
          <p className="text-muted-foreground">
            Monitor and manage validation jobs across all marketplaces
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetchStats()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats ? ((stats.succeeded / stats.total) * 100).toFixed(1) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {stats?.succeeded.toLocaleString()} succeeded
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Jobs</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.failed}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.needsReview} need review
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <AlertCircle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.avgLatencyMs}ms</div>
            <p className="text-xs text-muted-foreground">
              P95: {stats?.p95LatencyMs}ms
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <JobsFilters filters={filters} onFiltersChange={setFilters} />

      {/* Jobs Table */}
      <JobsTable filters={filters} />
    </div>
  )
}