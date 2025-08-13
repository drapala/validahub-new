"use client";

export function JobProgress({
  status,
  eta,
  logs
}: {
  status: "queued" | "processing" | "done" | "failed";
  eta?: string;
  logs?: string[];
}) {
  const pct = status === "queued" ? 10 : status === "processing" ? 60 : status === "done" ? 100 : 100;
  const color = status === "failed" ? "bg-red-500" : "bg-emerald-500";
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm text-zinc-400">
        <span>Status: {status}</span>
        {eta && <span>ETA: {eta}</span>}
      </div>
      <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      {logs && logs.length > 0 && (
        <div className="mt-2 bg-zinc-900 rounded-xl p-3 text-xs text-zinc-400 max-h-48 overflow-auto">
          {logs.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      )}
    </div>
  );
}