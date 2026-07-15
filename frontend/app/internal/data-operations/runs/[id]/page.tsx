"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Clock, Database, FileWarning } from "lucide-react";
import { AppShell } from "@/components/layout";
import { internalOperationsService, handleApiError } from "@/services/api";

function badgeClass(value: string): string {
  const normalized = value.toLowerCase();
  if (["completed", "healthy", "fresh"].includes(normalized)) return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
  if (["rejected", "failed", "error"].includes(normalized)) return "border-red-400/30 bg-red-400/10 text-red-300";
  if (["warning", "degraded"].includes(normalized)) return "border-amber-400/30 bg-amber-400/10 text-amber-300";
  return "border-slate-400/30 bg-slate-400/10 text-slate-300";
}

function StatusBadge({ value }: { value: string }) {
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${badgeClass(value)}`}>{value}</span>;
}

function InfoCard({ title, value, helper }: { title: string; value: string | number | null | undefined; helper: string }) {
  return <div className="rounded-lg border border-border p-4"><p className="text-xs uppercase text-muted-foreground">{title}</p><p className="mt-2 text-lg font-semibold">{value ?? "-"}</p><p className="mt-1 text-xs text-muted-foreground">{helper}</p></div>;
}

export default function IngestionRunDetailPage() {
  const params = useParams<{ id: string }>();
  const runId = Number(params?.id);
  const detailQuery = useQuery({ queryKey: ["internal-run-detail", runId], queryFn: () => internalOperationsService.getRunDetail(runId), enabled: Number.isFinite(runId), retry: 1 });
  const issuesQuery = useQuery({ queryKey: ["internal-run-detail-issues", runId], queryFn: () => internalOperationsService.getRunIssues(runId, { limit: 100 }), enabled: Number.isFinite(runId), retry: 1 });

  const detail = detailQuery.data?.data;
  const run = detail?.run;
  const issues = issuesQuery.data?.data ?? [];
  const error = detailQuery.error || issuesQuery.error;

  return (
    <AppShell>
      <div className="space-y-6">
        <Link href="/internal/data-operations" className="inline-flex items-center gap-2 text-sm text-primary hover:underline"><ArrowLeft className="h-4 w-4" /> Back to data operations</Link>
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-primary">Ingestion Run</p>
            <h1 className="mt-2 text-3xl font-semibold">Run #{runId}</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">Safe run metadata, issue-code distribution, and retry guidance. Raw source documents are not displayed.</p>
          </div>
          {run ? <StatusBadge value={run.status} /> : null}
        </header>

        {error ? <div className="warning-panel">{handleApiError(error)}</div> : null}
        {detailQuery.isLoading ? <div className="skeleton-card h-72" /> : null}

        {run ? (
          <>
            <section className="premium-card p-5">
              <div className="mb-4 flex items-center gap-2"><Database className="h-5 w-5 text-primary" /><h2 className="text-xl font-semibold">Run Metadata</h2></div>
              <div className="grid gap-4 md:grid-cols-4">
                <InfoCard title="Source" value={run.source_name} helper={run.source_type} />
                <InfoCard title="Entity" value={run.entity} helper={`mode ${run.mode}`} />
                <InfoCard title="Checksum" value={run.checksum} helper="Source checksum when available" />
                <InfoCard title="Dataset" value={run.dataset_version} helper="Version supplied by source adapter" />
              </div>
            </section>

            <section className="grid gap-4 md:grid-cols-4">
              <InfoCard title="Received" value={run.received_count} helper="Source records loaded" />
              <InfoCard title="Valid" value={run.valid_count} helper="Records accepted by validation" />
              <InfoCard title="Rejected" value={run.rejected_count} helper="Rejected or skipped due to validation" />
              <InfoCard title="Duration" value={run.duration_ms ? `${run.duration_ms} ms` : null} helper="Run execution duration" />
            </section>

            <section className="premium-card p-5">
              <div className="mb-4 flex items-center gap-2"><FileWarning className="h-5 w-5 text-primary" /><h2 className="text-xl font-semibold">Issue-Code Distribution</h2></div>
              {Object.keys(detail.issue_code_distribution).length ? <div className="grid gap-3 md:grid-cols-3">{Object.entries(detail.issue_code_distribution).map(([code, count]) => <div key={code} className="rounded-lg border border-border p-4"><p className="font-medium">{code}</p><p className="mt-1 text-sm text-muted-foreground">{count} occurrence(s)</p></div>)}</div> : <p className="text-sm text-muted-foreground">No record-level issues were recorded for this run.</p>}
            </section>

            <section className="premium-card p-5">
              <div className="mb-4 flex items-center gap-2"><Clock className="h-5 w-5 text-primary" /><h2 className="text-xl font-semibold">Retry Guidance</h2></div>
              {detail.retry_guidance.length ? <ul className="space-y-2 text-sm text-muted-foreground">{detail.retry_guidance.map((item) => <li key={item}>- {item}</li>)}</ul> : <p className="text-sm text-muted-foreground">No retry action is currently recommended.</p>}
            </section>

            <section className="premium-card p-5"><h2 className="mb-4 text-xl font-semibold">Safe Issue Details</h2>{issues.length ? <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-muted-foreground"><tr><th className="py-2">Severity</th><th>Code</th><th>Record</th><th>Field</th><th>Message</th></tr></thead><tbody>{issues.map((issue) => <tr key={issue.id} className="border-t border-border/60"><td className="py-3"><StatusBadge value={issue.severity} /></td><td>{issue.issue_code}</td><td>{issue.record_index ?? "-"}</td><td>{issue.field_name ?? "-"}</td><td className="max-w-xl">{issue.message}</td></tr>)}</tbody></table></div> : <p className="text-sm text-muted-foreground">No issues recorded.</p>}</section>
          </>
        ) : !detailQuery.isLoading ? <div className="premium-card p-8 text-center text-sm text-muted-foreground">Run not found or unavailable.</div> : null}
      </div>
    </AppShell>
  );
}

