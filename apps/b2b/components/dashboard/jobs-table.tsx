'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
} from '@tanstack/react-table'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { MoreHorizontal, Eye, RotateCcw, X, UserCheck, AlertCircle } from 'lucide-react'
import { jobsService, Job } from '@/lib/services/jobs'
import { toast } from 'sonner'

// Mock data for development
const mockJobs: Job[] = [
  {
    id: 'JOB-8742',
    seller: 'Loja ACME',
    channel: 'Magalu',
    created_at: '2025-08-28T11:04:00Z',
    status: 'failed',
    errors_count: 12,
    warnings_count: 5,
    rows_processed: 1500,
    duration_ms: 2140,
    type: 'upload_csv',
    marketplace_account: 'acme_magalu',
    severity: 'blocking',
  },
  {
    id: 'JOB-8741',
    seller: 'PetTop',
    channel: 'Mercado Livre',
    created_at: '2025-08-28T10:58:00Z',
    status: 'needs_review',
    errors_count: 4,
    warnings_count: 8,
    rows_processed: 850,
    duration_ms: 1230,
    type: 'api',
    marketplace_account: 'pettop_meli',
    severity: 'warning',
  },
  {
    id: 'JOB-8740',
    seller: 'MegaHouse',
    channel: 'Shopee',
    created_at: '2025-08-28T10:52:00Z',
    status: 'succeeded',
    errors_count: 0,
    warnings_count: 2,
    rows_processed: 2100,
    duration_ms: 3456,
    type: 'delta',
    marketplace_account: 'mega_shopee',
  },
]

interface JobsTableProps {
  filters: any
}

export function JobsTable({ filters }: JobsTableProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [sorting, setSorting] = useState<SortingState>([])
  const [rowSelection, setRowSelection] = useState({})
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 50,
  })

  // Fetch jobs
  const { data, isLoading } = useQuery({
    queryKey: ['jobs', filters, pagination],
    queryFn: async () => {
      // For now, return mock data
      return { jobs: mockJobs, total: mockJobs.length }
    },
    // queryFn: () => jobsService.getJobs({
    //   ...filters,
    //   page: pagination.pageIndex + 1,
    //   limit: pagination.pageSize,
    // }),
  })

  // Retry job mutation
  const retryMutation = useMutation({
    mutationFn: (jobId: string) => jobsService.retryJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Job reprocessado com sucesso')
    },
    onError: () => {
      toast.error('Erro ao reprocessar job')
    },
  })

  const getStatusBadge = (status: Job['status']) => {
    const variants: Record<Job['status'], { variant: any; label: string; icon?: any }> = {
      queued: { variant: 'secondary', label: 'Na fila' },
      running: { variant: 'default', label: 'Processando' },
      succeeded: { variant: 'success', label: 'Sucesso' },
      failed: { variant: 'destructive', label: 'Falhou' },
      needs_review: { variant: 'warning', label: 'Revisão', icon: AlertCircle },
    }

    const config = variants[status]
    return (
      <Badge variant={config.variant} className="gap-1">
        {config.icon && <config.icon className="h-3 w-3" />}
        {config.label}
      </Badge>
    )
  }

  const getChannelBadge = (channel: string) => {
    const colors: Record<string, string> = {
      'Magalu': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'Mercado Livre': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Shopee': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      'Amazon': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    }
    return (
      <Badge variant="outline" className={colors[channel] || ''}>
        {channel}
      </Badge>
    )
  }

  const columns: ColumnDef<Job>[] = [
    {
      id: 'select',
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: 'id',
      header: 'ID',
      cell: ({ row }) => (
        <div className="font-mono text-xs">{row.getValue('id')}</div>
      ),
    },
    {
      accessorKey: 'seller',
      header: 'Seller',
      cell: ({ row }) => (
        <div>
          <div className="font-medium">{row.getValue('seller')}</div>
          {row.original.marketplace_account && (
            <div className="text-xs text-muted-foreground">
              {row.original.marketplace_account}
            </div>
          )}
        </div>
      ),
    },
    {
      accessorKey: 'channel',
      header: 'Canal',
      cell: ({ row }) => getChannelBadge(row.getValue('channel')),
    },
    {
      accessorKey: 'created_at',
      header: 'Criado em',
      cell: ({ row }) => (
        <div className="text-sm">
          {format(new Date(row.getValue('created_at')), 'dd/MM HH:mm', { locale: ptBR })}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => getStatusBadge(row.getValue('status')),
    },
    {
      accessorKey: 'errors_count',
      header: 'Erros',
      cell: ({ row }) => {
        const errors = row.getValue('errors_count') as number
        const warnings = row.original.warnings_count
        return (
          <div className="flex gap-2">
            {errors > 0 && (
              <Badge variant="destructive" className="text-xs">
                {errors} erros
              </Badge>
            )}
            {warnings > 0 && (
              <Badge variant="outline" className="text-xs">
                {warnings} avisos
              </Badge>
            )}
            {errors === 0 && warnings === 0 && (
              <span className="text-xs text-muted-foreground">—</span>
            )}
          </div>
        )
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const job = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => router.push(`/dashboard/jobs/${job.id}`)}>
                <Eye className="mr-2 h-4 w-4" />
                View details
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => retryMutation.mutate(job.id)}
                disabled={job.status === 'running' || job.status === 'queued'}
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Retry
              </DropdownMenuItem>
              <DropdownMenuItem disabled={job.status !== 'running'}>
                <X className="mr-2 h-4 w-4" />
                Cancel
              </DropdownMenuItem>
              <DropdownMenuItem>
                <UserCheck className="mr-2 h-4 w-4" />
                Assign to me
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  const table = useReactTable({
    data: data?.jobs || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      rowSelection,
      pagination,
    },
    onPaginationChange: setPagination,
    pageCount: data ? Math.ceil(data.total / pagination.pageSize) : -1,
    manualPagination: true,
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {Object.keys(rowSelection).length > 0 && (
        <div className="flex items-center gap-2 rounded-lg bg-muted p-2">
          <span className="text-sm text-muted-foreground">
            {Object.keys(rowSelection).length} selected
          </span>
          <Button variant="outline" size="sm">
            Retry selected
          </Button>
          <Button variant="outline" size="sm">
            Mark as needs review
          </Button>
          <Button variant="outline" size="sm">
            Export errors CSV
          </Button>
        </div>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {data?.jobs.length || 0} of {data?.total || 0} jobs
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}