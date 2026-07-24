"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, ArrowLeft, Clock, Search } from "lucide-react";
import { adminService } from "@/services/api";

const STATUSES = ["all", "pending", "queued", "running", "completed", "failed", "cancelled", "paused"];
const TRIGGERS = ["all", "manual", "scheduled", "event", "retry", "system"];

function label(value?: string | null) {
  if (!value) return "Not recorded";
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value?: string | null) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function badgeClass(value: string) {
  if (["completed", "queued", "manual"].includes(value)) return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (["failed", "cancelled"].includes(value)) return "border-rose-400/30 bg-rose-500/10 text-rose-100";
  if (["paused", "retry"].includes(value)) return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  return "border-white/10 bg-white/5 text-muted-foreground";
}

export default function AdminIngestionExecutionsPage() {
  const searchParams = useSearchParams();
  const initialJobId = searchParams.get("job_id") ?? "";
  const [jobId, setJobId] = useState(initialJobId);
  const [status, setStatus] = useState("all");
  const [trigger, setTrigger] = useState("all");
  const [page, setPage] = useState(1);

  const params = useMemo(() => ({
    page,
    limit: 15,
    job_id: jobId ? Number(jobId) : undefined,
    status: status === "all" ? undefined : status,
    trigger_type: trigger === "all" ? undefined : trigger,
  }), [jobId, page, status, trigger]);

  const executionsQuery = useQuery({ queryKey: ["admin", "ingestion", "executions", params], queryFn: () => adminService.ingestionExecutions(params), retry: false });
  const payload = executionsQuery.data?.data;
  const totalPages = payload ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;

  return (
    <div className="space-y-6">
      <Link href="/admin/ingestion/jobs" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Jobs</Link>

      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><Activity size={14} /> Execution history</p>
        <h1 className="text-3xl font-bold">Immutable ingestion execution trail</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">Review operator-triggered and simulated execution history, metrics, failures, and outcomes. This page does not run ingestion.</p>
      </section>

      <section className="premium-card p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_180px_180px]">
          <label className="relative block"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} /><input value={jobId} onChange={(event) => { setJobId(event.target.value); setPage(1); }} placeholder="Filter by job ID" className="w-full rounded-lg border border-white/10 bg-background-secondary py-3 pl-10 pr-3 text-sm outline-none ring-primary/40 focus:ring-2" /></label>
          <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{STATUSES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={trigger} onChange={(event) => { setTrigger(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{TRIGGERS.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
        </div>
      </section>

      <section className="space-y-3">
        {executionsQuery.isLoading ? Array.from({ length: 6 }).map((_, index) => <div key={index} className="premium-card h-32 animate-pulse" />) : payload && payload.executions.length ? payload.executions.map((execution) => (
          <article key={execution.id} className="premium-card p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h2 className="text-xl font-semibold">#{execution.id} • {execution.job_name ?? `Job ${execution.job_id}`}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{execution.source_name ?? "Unknown source"} • {execution.operator_email ?? "System"}</p>
              </div>
              <div className="flex flex-wrap gap-2"><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(execution.status)}`}>{label(execution.status)}</span><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(execution.trigger_type)}`}>{label(execution.trigger_type)}</span></div>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">{execution.result_summary ?? "No result summary recorded."}</p>
            <div className="mt-4 grid gap-3 text-sm md:grid-cols-4">
              <Metric icon={Clock} label="Started" value={formatDate(execution.started_at)} />
              <Metric icon={Clock} label="Finished" value={formatDate(execution.finished_at)} />
              <Metric icon={Activity} label="Rows" value={execution.metric?.rows_processed ?? 0} />
              <Metric icon={AlertTriangle} label="Errors" value={execution.metric?.error_count ?? execution.failures.length} />
            </div>
          </article>
        )) : <div className="premium-card p-6"><h2 className="text-xl font-semibold">No executions found</h2><p className="mt-2 text-sm text-muted-foreground">Adjust filters or seed development operations data. Execution history is immutable once recorded.</p></div>}
      </section>

      {payload ? <div className="flex items-center justify-between rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="premium-button-secondary disabled:opacity-50">Previous</button><span className="text-muted-foreground">Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="premium-button-secondary disabled:opacity-50">Next</button></div> : null}
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Clock; label: string; value: string | number }) {
  return <div className="rounded-lg border border-white/10 bg-background-secondary/70 p-3"><p className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground"><Icon size={14} /> {label}</p><p className="mt-2 font-semibold text-foreground">{value}</p></div>;
}
