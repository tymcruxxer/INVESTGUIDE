"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, Database, FileWarning, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout";
import { internalOperationsService, handleApiError } from "@/services/api";
import type { EntityQualityPayload, IngestionRecordIssue } from "@/types";

function badgeClass(value: string): string {
  const normalized = value.toLowerCase();
  if (["healthy", "fresh", "excellent", "strong", "completed"].includes(normalized)) return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
  if (["degraded", "aging", "moderate", "good", "warning"].includes(normalized)) return "border-amber-400/30 bg-amber-400/10 text-amber-300";
  if (["failing", "stale", "critical", "weak", "failed", "rejected"].includes(normalized)) return "border-red-400/30 bg-red-400/10 text-red-300";
  return "border-slate-400/30 bg-slate-400/10 text-slate-300";
}

function StatusBadge({ value }: { value: string }) {
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${badgeClass(value)}`}>{value}</span>;
}

function MetricCard({ title, value, helper, icon: Icon }: { title: string; value: string | number; helper: string; icon: typeof Activity }) {
  return (
    <section className="premium-card p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-2 text-3xl font-semibold">{value}</p>
          <p className="mt-2 text-xs text-muted-foreground">{helper}</p>
        </div>
        <div className="rounded-lg border border-primary/20 bg-primary/10 p-3 text-primary"><Icon className="h-5 w-5" /></div>
      </div>
    </section>
  );
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="rounded-lg border border-dashed border-border p-6 text-sm text-muted-foreground"><p className="font-medium text-foreground">{title}</p><p className="mt-1">{detail}</p></div>;
}

export default function DataOperationsPage() {
  const [issueFilter, setIssueFilter] = useState("all");
  const summaryQuery = useQuery({ queryKey: ["internal-data-quality-summary"], queryFn: () => internalOperationsService.getDataQualitySummary(), retry: 1 });
  const runsQuery = useQuery({ queryKey: ["internal-ingestion-runs"], queryFn: () => internalOperationsService.getRuns({ limit: 10 }), retry: 1 });
  const sourcesQuery = useQuery({ queryKey: ["internal-source-health"], queryFn: () => internalOperationsService.getSources(), retry: 1 });
  const latestRunId = runsQuery.data?.data?.[0]?.id;
  const issuesQuery = useQuery({
    queryKey: ["internal-run-issues", latestRunId, issueFilter],
    queryFn: () => internalOperationsService.getRunIssues(Number(latestRunId), { limit: 20, severity: issueFilter === "all" ? undefined : issueFilter }),
    enabled: Boolean(latestRunId),
    retry: 1,
  });

  const summary = summaryQuery.data?.data;
  const runs = runsQuery.data?.data ?? [];
  const sources = sourcesQuery.data?.data ?? [];
  const issues = issuesQuery.data?.data ?? [];
  const errorMessage = [summaryQuery.error, runsQuery.error, sourcesQuery.error].find(Boolean);

  const entities = useMemo<EntityQualityPayload[]>(() => summary?.entities ?? [], [summary]);

  return (
    <AppShell>
      <div className="space-y-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-primary">Internal Operations</p>
            <h1 className="mt-2 text-3xl font-semibold">Data Operations</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">Source health, ingestion audit, rejection analysis, and data-quality diagnostics. This page is internal and read-only.</p>
          </div>
          {summary ? <StatusBadge value={summary.pipeline_health} /> : null}
        </header>

        {errorMessage ? <div className="warning-panel">{handleApiError(errorMessage)}</div> : null}

        {summaryQuery.isLoading ? (
          <div className="grid gap-4 md:grid-cols-4"><div className="skeleton-card h-28" /><div className="skeleton-card h-28" /><div className="skeleton-card h-28" /><div className="skeleton-card h-28" /></div>
        ) : summary ? (
          <div className="grid gap-4 md:grid-cols-4">
            <MetricCard title="Verified Records" value={summary.verified_record_count} helper="Rows with verified production provenance." icon={ShieldCheck} />
            <MetricCard title="Development Records" value={summary.development_record_count} helper="Fixture rows still visible to operators." icon={Database} />
            <MetricCard title="Stale Datasets" value={summary.stale_dataset_count} helper="Entities outside freshness targets or unknown." icon={AlertTriangle} />
            <MetricCard title="Rejected Issues" value={summary.rejected_record_count} helper="Persisted record-level rejection issues." icon={FileWarning} />
          </div>
        ) : <EmptyState title="No operations summary yet" detail="Run the ingestion diagnostics CLI or import fixtures to populate audit data." />}

        <section className="premium-card p-5">
          <div className="mb-4 flex items-center justify-between gap-4"><h2 className="text-xl font-semibold">Recent Runs</h2><span className="text-xs text-muted-foreground">Paginated by API</span></div>
          {runs.length ? <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-muted-foreground"><tr><th className="py-2">Run</th><th>Source</th><th>Entity</th><th>Mode</th><th>Status</th><th>Duration</th><th>Inserted</th><th>Updated</th><th>Rejected</th><th>Warnings</th></tr></thead><tbody>{runs.map((run) => <tr key={run.id} className="border-t border-border/60"><td className="py-3"><Link className="text-primary hover:underline" href={`/internal/data-operations/runs/${run.id}`}>#{run.id}</Link></td><td>{run.source_name}</td><td>{run.entity}</td><td>{run.mode}</td><td><StatusBadge value={run.status} /></td><td>{run.duration_ms ?? "-"} ms</td><td>{run.inserted_count}</td><td>{run.updated_count}</td><td>{run.rejected_count}</td><td>{run.warning_count}</td></tr>)}</tbody></table></div> : <EmptyState title="No ingestion runs" detail="Execute a dry-run or lenient import to create audit rows." />}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="premium-card p-5"><h2 className="mb-4 text-xl font-semibold">Source Health</h2>{sources.length ? <div className="space-y-3">{sources.map((source) => <div key={`${source.source_name}-${source.source_type}`} className="rounded-lg border border-border p-4"><div className="flex items-center justify-between gap-3"><div><p className="font-medium">{source.source_name}</p><p className="text-xs text-muted-foreground">{source.source_type} - success {source.success_rate}%</p></div><StatusBadge value={source.current_health} /></div><p className="mt-2 text-xs text-muted-foreground">Freshness: {source.freshness_status} - warnings {source.recent_warning_count} - rejected {source.recent_rejected_record_count}</p></div>)}</div> : <EmptyState title="No source history" detail="Sources appear after ingestion runs complete." />}</div>
          <div className="premium-card p-5"><h2 className="mb-4 text-xl font-semibold">Rejection Explorer</h2><label className="mb-3 block text-sm text-muted-foreground" htmlFor="severity-filter">Severity</label><select id="severity-filter" className="mb-4 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm" value={issueFilter} onChange={(event) => setIssueFilter(event.target.value)}><option value="all">All</option><option value="Rejected">Rejected</option><option value="Warning">Warning</option><option value="Error">Error</option></select>{issues.length ? <div className="space-y-3">{issues.map((issue: IngestionRecordIssue) => <div key={issue.id} className="rounded-lg border border-border p-4"><div className="flex items-center justify-between gap-3"><p className="font-medium">{issue.issue_code}</p><StatusBadge value={issue.severity} /></div><p className="mt-1 text-sm text-muted-foreground">{issue.message}</p><p className="mt-2 text-xs text-muted-foreground">record {issue.record_index ?? "-"} - field {issue.field_name ?? "-"}</p></div>)}</div> : <EmptyState title="No issues for current filter" detail="Warnings and rejections will appear here after validation runs." />}</div>
        </section>

        <section className="premium-card p-5"><h2 className="mb-4 text-xl font-semibold">Entity Quality</h2>{entities.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{entities.map((entity) => <article key={entity.entity_type} className="rounded-lg border border-border p-4"><div className="flex items-start justify-between gap-3"><div><h3 className="font-semibold">{entity.entity_type.replace(/_/g, " ")}</h3><p className="text-xs text-muted-foreground">{entity.total_records} records - {entity.source_count} source(s)</p></div><StatusBadge value={entity.quality_score.label} /></div><div className="mt-4 grid grid-cols-3 gap-2 text-xs text-muted-foreground"><span>Complete {entity.completeness.score}</span><span>Fresh {entity.freshness.score.score}</span><span>Prov {entity.provenance.score}</span></div><p className="mt-3 text-xs text-muted-foreground">Warnings {entity.open_warning_count} - Rejections {entity.open_rejection_count} - Dev {entity.development_records}</p></article>)}</div> : <EmptyState title="No entity summaries" detail="Entity quality appears after database records or ingestion audit rows exist." />}</section>
      </div>
    </AppShell>
  );
}




