"use client";

export const dynamic = 'force-dynamic';

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function StatusPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["status"],
    queryFn: api.getStatus
  });

  return (
    <main className="container-app py-12 space-y-4">
      <h1 className="text-3xl font-semibold">Status</h1>
      <div className="card p-6">
        {isLoading && <div className="skeleton h-6 w-40" />}
        {isError && <div className="text-red-400">Erro ao carregar status.</div>}
        {data && (
          <pre className="text-sm text-zinc-400">{JSON.stringify(data, null, 2)}</pre>
        )}
      </div>
    </main>
  );
}