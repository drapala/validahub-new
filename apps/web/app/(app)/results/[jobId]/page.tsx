"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { JobProgress } from "@/components/job-progress";

export default function ResultsJobPage() {
  const params = useParams<{ jobId: string }>();
  const jobId = params.jobId;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.getJob(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // 2->3->5s simples
      if (status === "done" || status === "failed") return false;
      const c = query.state.fetchFailureCount;
      return c >= 2 ? 5000 : c === 1 ? 3000 : 2000;
    }
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Resultados — Job {jobId}</h1>
      <div className="card p-6">
        {isLoading && <div className="skeleton h-6 w-48" />}
        {isError && <div className="text-red-400">Erro ao consultar job.</div>}
        {data && (
          <>
            <JobProgress status={data.status} eta={data.eta} logs={data.logs} />
            {data.status === "done" && (
              <div className="mt-4 flex flex-wrap gap-3">
                {data.links?.corrected && (
                  <a className="btn btn-primary" href={data.links.corrected} target="_blank" rel="noreferrer">
                    Baixar corrected.csv
                  </a>
                )}
                {data.links?.rejected && (
                  <a className="btn btn-ghost" href={data.links.rejected} target="_blank" rel="noreferrer">
                    rejected.csv
                  </a>
                )}
                {data.links?.report && (
                  <a className="btn btn-ghost" href={data.links.report} target="_blank" rel="noreferrer">
                    report.json
                  </a>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}