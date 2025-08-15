"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Upload, ListChecks, ServerCog, Webhook, Code2, Settings, FileText, CheckSquare } from "lucide-react";

const NAV = [
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/validate-row", label: "Validar Linha", icon: CheckSquare },
  { href: "/jobs", label: "Jobs", icon: ListChecks },
  { href: "/connectors", label: "Conectores", icon: ServerCog },
  { href: "/webhooks", label: "Webhooks", icon: Webhook },
  { href: "/mappings", label: "Mappings", icon: Code2 },
  { href: "/settings/billing", label: "Billing", icon: Settings },
  { href: "/docs", label: "Docs", icon: FileText }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen grid grid-cols-12">
      <aside className="col-span-12 md:col-span-3 lg:col-span-2 border-r border-border px-4 py-6">
        <div className="mb-6">
          <Link href="/" className="font-semibold text-xl">ValidaHub</Link>
        </div>
        <nav className="space-y-1">
          {NAV.map((item) => {
            const active = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-muted",
                  active && "bg-muted"
                )}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="col-span-12 md:col-span-9 lg:col-span-10 px-6 py-8">
        {children}
      </main>
    </div>
  );
}