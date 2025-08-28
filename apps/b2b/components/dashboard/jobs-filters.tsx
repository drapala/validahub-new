'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { X } from 'lucide-react'

interface JobsFiltersProps {
  filters: {
    status: string[]
    channel: string[]
    seller: string
    period: string
    severity: string
    type: string[]
  }
  onFiltersChange: (filters: any) => void
}

const statusOptions = [
  { value: 'queued', label: 'Queued' },
  { value: 'running', label: 'Running' },
  { value: 'succeeded', label: 'Succeeded' },
  { value: 'failed', label: 'Failed' },
  { value: 'needs_review', label: 'Needs Review' },
]

const channelOptions = [
  { value: 'magalu', label: 'Magalu' },
  { value: 'meli', label: 'Mercado Livre' },
  { value: 'shopee', label: 'Shopee' },
  { value: 'amazon', label: 'Amazon' },
]

const typeOptions = [
  { value: 'upload_csv', label: 'Upload CSV' },
  { value: 'api', label: 'API' },
  { value: 'delta', label: 'Delta' },
  { value: 'full', label: 'Full' },
]

export function JobsFilters({ filters, onFiltersChange }: JobsFiltersProps) {
  const handleStatusChange = (status: string, checked: boolean) => {
    const newStatus = checked
      ? [...filters.status, status]
      : filters.status.filter((s) => s !== status)
    onFiltersChange({ ...filters, status: newStatus })
  }

  const handleChannelChange = (channel: string, checked: boolean) => {
    const newChannels = checked
      ? [...filters.channel, channel]
      : filters.channel.filter((c) => c !== channel)
    onFiltersChange({ ...filters, channel: newChannels })
  }

  const handleTypeChange = (type: string, checked: boolean) => {
    const newTypes = checked
      ? [...filters.type, type]
      : filters.type.filter((t) => t !== type)
    onFiltersChange({ ...filters, type: newTypes })
  }

  const clearFilters = () => {
    onFiltersChange({
      status: [],
      channel: [],
      seller: '',
      period: 'last24h',
      severity: 'all',
      type: [],
    })
  }

  const hasActiveFilters = 
    filters.status.length > 0 ||
    filters.channel.length > 0 ||
    filters.seller ||
    filters.type.length > 0 ||
    filters.severity !== 'all'

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Status Filters */}
          <div>
            <Label className="text-sm font-medium mb-2 block">Status</Label>
            <div className="flex flex-wrap gap-3">
              {statusOptions.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`status-${option.value}`}
                    checked={filters.status.includes(option.value)}
                    onCheckedChange={(checked) =>
                      handleStatusChange(option.value, checked as boolean)
                    }
                  />
                  <Label
                    htmlFor={`status-${option.value}`}
                    className="text-sm font-normal cursor-pointer"
                  >
                    {option.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Channel Filters */}
          <div>
            <Label className="text-sm font-medium mb-2 block">Canal</Label>
            <div className="flex flex-wrap gap-3">
              {channelOptions.map((option) => (
                <Badge
                  key={option.value}
                  variant={filters.channel.includes(option.value) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() =>
                    handleChannelChange(
                      option.value,
                      !filters.channel.includes(option.value)
                    )
                  }
                >
                  {option.label}
                </Badge>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Seller */}
            <div>
              <Label htmlFor="seller" className="text-sm font-medium mb-1 block">
                Seller
              </Label>
              <Input
                id="seller"
                placeholder="Search seller..."
                value={filters.seller}
                onChange={(e) =>
                  onFiltersChange({ ...filters, seller: e.target.value })
                }
              />
            </div>

            {/* Period */}
            <div>
              <Label htmlFor="period" className="text-sm font-medium mb-1 block">
                Período
              </Label>
              <Select
                value={filters.period}
                onValueChange={(value) =>
                  onFiltersChange({ ...filters, period: value })
                }
              >
                <SelectTrigger id="period">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last1h">Last hour</SelectItem>
                  <SelectItem value="last6h">Last 6 hours</SelectItem>
                  <SelectItem value="last24h">Last 24 hours</SelectItem>
                  <SelectItem value="last7d">Last 7 days</SelectItem>
                  <SelectItem value="last30d">Last 30 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Severity */}
            <div>
              <Label htmlFor="severity" className="text-sm font-medium mb-1 block">
                Severidade
              </Label>
              <Select
                value={filters.severity}
                onValueChange={(value) =>
                  onFiltersChange({ ...filters, severity: value })
                }
              >
                <SelectTrigger id="severity">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="blocking">Blocking</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Type */}
            <div>
              <Label className="text-sm font-medium mb-1 block">Tipo</Label>
              <Select
                value={filters.type[0] || 'all'}
                onValueChange={(value) =>
                  onFiltersChange({
                    ...filters,
                    type: value === 'all' ? [] : [value],
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All types</SelectItem>
                  {typeOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <div className="flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="h-8"
              >
                <X className="mr-2 h-3 w-3" />
                Clear filters
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}