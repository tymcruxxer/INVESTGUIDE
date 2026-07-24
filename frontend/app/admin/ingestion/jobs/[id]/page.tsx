"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Clock, DatabaseZap, History, PauseCircle, PlayCircle, RefreshCcw, ShieldCheck, XCircle } from "lucide-react";
import { useState } from "react";
import { adminService } from "@/services/api";

function label(value?: string | null) {
  if (!value) return "Not configured";
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value?: string | null) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function badgeClass(value: string) {
  if (["completed", "queued", "fresh", "high", "critical"].includes(value)) return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (["failed", "expired", "cancelled"].includes(value)) return "border-rose-400/30 bg-rose-500/10 text-rose-100";
  if (["paused", "stale", "aging"].includes(value)) return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  return "border-white/10 bg-white/5 text-muted-foreground";
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre className="overflow-auto rounded-lg border border-white/10 bg-background-primary p-3 text-xs text-muted-foreground">{JSON.stringify(value ?? {}, null, 2)}</pre>;
}

export default function AdminIngestionJobDetailPage() {
  const params = useParams<{ id: string }>();
  const jobId = Number(params.id);
  const queryClient = useQueryClient();
  const [reason, setReason] = useState("Operator request recorded");
  const [message, setMessage] = useState<string | null>(null);

  const jobQuery = useQuery({ queryKey: ["admin", "ingestion", "job", jobId], queryFn: () => adminService.ingestionJob(jobId), enabled: Number.isFinite(jobId), retry: false });
  const job = jobQuery.data?.data;

  const operationMutation = useMutation({
    mutationFn: (operation: "run" | "retry" | "pause" | "resume" | "cancel") => adminService.ingestionJobOperation(jobId, operation, { reason }),
    onSuccess: async (_, operation) => {
      setMessage(`${label(operation)} request recorded. No live ingestion was executed.`);
      await queryClient.invalidateQueries({ queryKey: ["admin", "ingestion"] });
    },
    onError: () => setMessage("Unable to record the operation request."),
  });

  if (jobQuery.isLoading) return <div className="premium-card h-96 animate-pulse p-6" />;
  if (!job) return <div className="premium-card p-6"><h1 className="text-2xl font-bold">Job unavailable</h1><p className="mt-2 text-sm text-muted-foreground">The job may not exist or your account may not have ingestion permissions.</p><Link href="/admin/ingestion/jobs" className="premium-button mt-5 inline-flex"><ArrowLeft size={16} /> Back to jobs</Link></div>;

  const latestMetric = job.recent_executions[0]?.metric;

  return (
    <div className="space-y-6">
      <Link href="/admin/ingestion/jobs" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Jobs</Link>

      <section className="premium-card p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><DatabaseZap size={14} /> Ingestion job</p>
            <h1 className="text-3xl font-bold">{job.name}</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{job.description ?? "No description provided."}</p>
            <div className="mt-4 flex flex-wrap gap-2"><span className="premium-badge">{job.source_name}</span><span className="premium-badge">{label(job.job_type)}</span><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(job.status)}`}>{label(job.status)}</span></div>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(job.freshness_status)}`}>{label(job.freshness_status)}</span>
        </div>
        {message ? <p className="mt-5 rounded-lg border border-primary/25 bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={Clock} label="Timeout" value={`${job.timeout_seconds}s`} />
        <Metric icon={RefreshCcw} label="Retries" value={job.max_retries} />
        <Metric icon={ShieldCheck} label="Concurrency" value={job.concurrency_limit} />
        <Metric icon={History} label="Last Run" value={formatDate(job.last_run_at)} />
      </section>

      <section className="premium-card p-5">
        <h2 className="text-lg font-semibold">Manual operations</h2>
        <p className="mt-2 text-sm text-muted-foreground">These buttons record operator requests only. No connector, parser, worker, queue, or live ingestion runs in Sprint 055.</p>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto]">
          <input value={reason} onChange={(event) => setReason(event.target.value)} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          <div className="flex flex-wrap gap-2">
            <button onClick={() => operationMutation.mutate("run")} disabled={!reason.trim()} className="premium-button inline-flex items-center gap-2 disabled:opacity-50"><PlayCircle size={16} /> Run</button>
            <button onClick={() => operationMutation.mutate("retry")} disabled={!reason.trim()} className="premium-button-secondary inline-flex items-center gap-2 disabled:opacity-50"><RefreshCcw size={16} /> Retry</button>
            <button onClick={() => operationMutation.mutate("pause")} disabled={!reason.trim()} className="premium-button-secondary inline-flex items-center gap-2 disabled:opacity-50"><PauseCircle size={16} /> Pause</button>
            <button onClick={() => operationMutation.mutate("resume")} disabled={!reason.trim()} className="premium-button-secondary disabled:opacity-50">Resume</button>
            <button onClick={() => operationMutation.mutate("cancel")} disabled={!reason.trim()} className="inline-flex items-center gap-2 rounded-lg border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 disabled:opacity-50"><XCircle size={16} /> Cancel</button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Configuration</h2><dl className="mt-4 grid gap-3 text-sm text-muted-foreground md:grid-cols-2"><div><dt>Execution</dt><dd className="text-foreground">{label(job.execution_mode)}</dd></div><div><dt>Priority</dt><dd className="text-foreground">{label(job.priority)}</dd></div><div><dt>Manual only</dt><dd className="text-foreground">{job.manual_only ? "Yes" : "No"}</dd></div><div><dt>Queue</dt><dd className="text-foreground">{job.queue_name ?? "Future queue not set"}</dd></div></dl><div className="mt-4"><JsonBlock value={job.configuration} /></div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Latest metrics</h2>{latestMetric ? <dl className="mt-4 grid gap-3 text-sm text-muted-foreground md:grid-cols-2"><div><dt>Rows processed</dt><dd className="text-foreground">{latestMetric.rows_processed}</dd></div><div><dt>Inserted</dt><dd className="text-foreground">{latestMetric.records_inserted}</dd></div><div><dt>Updated</dt><dd className="text-foreground">{latestMetric.records_updated}</dd></div><div><dt>Rejected</dt><dd className="text-foreground">{latestMetric.records_rejected}</dd></div><div><dt>Duplicates</dt><dd className="text-foreground">{latestMetric.duplicates_detected}</dd></div><div><dt>Throughput</dt><dd className="text-foreground">{latestMetric.throughput_per_second ?? 0}/s</dd></div></dl> : <p className="mt-4 text-sm text-muted-foreground">No metrics recorded yet.</p>}</article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Execution history</h2><div className="mt-4 space-y-3">{job.recent_executions.length ? job.recent_executions.map((execution) => <Link key={execution.id} href={`/admin/ingestion/executions?job_id=${job.id}`} className="block rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm hover:border-primary/40"><div className="flex items-center justify-between"><span className="font-semibold">#{execution.id} • {label(execution.status)}</span><span className="text-muted-foreground">{formatDate(execution.created_at)}</span></div><p className="mt-1 text-muted-foreground">{execution.result_summary ?? "No summary recorded."}</p></Link>) : <p className="text-sm text-muted-foreground">No execution history yet.</p>}</div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Recent failures</h2><div className="mt-4 space-y-3">{job.recent_failures.length ? job.recent_failures.map((failure) => <div key={failure.id} className="rounded-lg border border-rose-400/20 bg-rose-500/10 p-3 text-sm"><div className="flex items-center justify-between"><span className="font-semibold text-rose-100">{label(failure.failure_category)}</span><span className="text-muted-foreground">{formatDate(failure.failed_at)}</span></div><p className="mt-1 text-rose-100/80">{failure.error_message}</p></div>) : <p className="text-sm text-muted-foreground">No failures recorded.</p>}</div></article>
      </section>
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Clock; label: string; value: string | number }) {
  return <article className="premium-card p-5"><span className="inline-flex rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><Icon size={20} /></span><p className="mt-4 text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p><p className="mt-2 text-lg font-semibold">{value}</p></article>;
}
