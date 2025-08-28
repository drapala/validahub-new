'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  LayoutDashboard,
  Package2,
  Users,
  FileText,
  BarChart3,
  AlertCircle,
  History,
  Settings,
  GitBranch,
  ChevronLeft,
  ChevronRight,
  Briefcase,
  BookOpen,
} from 'lucide-react'

const sidebarItems = [
  {
    title: 'Queue (Jobs)',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Sellers',
    href: '/dashboard/sellers',
    icon: Users,
  },
  {
    title: 'Rules Library',
    href: '/dashboard/rules',
    icon: BookOpen,
  },
  {
    title: 'Integrations',
    href: '/dashboard/integrations',
    icon: GitBranch,
  },
  {
    title: 'Metrics & SLAs',
    href: '/dashboard/metrics',
    icon: BarChart3,
  },
  {
    title: 'Alerts & Incidents',
    href: '/dashboard/alerts',
    icon: AlertCircle,
  },
  {
    title: 'Audit Log',
    href: '/dashboard/audit',
    icon: History,
  },
  {
    title: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
  {
    title: 'Changelog',
    href: '/dashboard/changelog',
    icon: FileText,
  },
]

interface SidebarProps {
  isCollapsed: boolean
  setIsCollapsed: (collapsed: boolean) => void
}

export function Sidebar({ isCollapsed, setIsCollapsed }: SidebarProps) {
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-background border-r transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-4">
        {!isCollapsed && (
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
            <Package2 className="h-6 w-6" />
            <span>ValidaHub B2B</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={cn(isCollapsed && "mx-auto")}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>
      
      <ScrollArea className="h-[calc(100vh-3.5rem)]">
        <nav className="flex flex-col gap-1 p-2">
          {sidebarItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-accent hover:text-accent-foreground",
                pathname === item.href 
                  ? "bg-accent text-accent-foreground" 
                  : "text-muted-foreground",
                isCollapsed && "justify-center"
              )}
              title={isCollapsed ? item.title : undefined}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>{item.title}</span>}
            </Link>
          ))}
        </nav>
      </ScrollArea>
    </div>
  )
}