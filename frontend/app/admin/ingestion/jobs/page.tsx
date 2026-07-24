"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, AlertTriangle, Clock, DatabaseZap, PauseCircle, PlayCircle, Plus, Search } from "lucide-react";
import { adminService } from "@/services/api";

const STATUSES = ["all", "pending", "queued", "running", "completed", "failed", "cancelled", "paused", "disabled"];
const PRIORITIES = ["all", "low", "normal", "high", "critical"];
const JOB_TYPES = ["all", "market_prices", "corporate_actions", "dividends", "annual_reports", "interim_reports", "trading_updates", "news", "economic_indicators", "exchange_rates", "commodity_prices", "weather", "research_reports"];
const FRESHNESS = ["all", "fresh", "aging", "stale", "expired", "unknown"];

function label(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function badgeClass(value: string) {
  if (["running", "queued", "fresh", "high", "critical"].includes(value)) return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (["failed", "expired"].includes(value)) return "border-rose-400/30 bg-rose-500/10 text-rose-100";
  if (["paused", "stale", "aging"].includes(value)) return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  return "border-white/10 bg-white/5 text-muted-foreground";
}

export default function AdminIngestionJobsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [priority, setPriority] = useState("all");
  const [jobType, setJobType] = useState("all");
  const [freshness, setFreshness] = useState("all");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ source_id: "", name: "", job_type: "news", priority: "normal", reason: "Initial operations setup" });

  const params = useMemo(() => ({
    page,
    limit: 12,
    search: search.trim() || undefined,
    status: status === "all" ? undefined : status,
    priority: priority === "all" ? undefined : priority,
    job_type: jobType === "all" ? undefined : jobType,
    freshness_status: freshness === "all" ? undefined : freshness,
  }), [freshness, jobType, page, priority, search, status]);

  const jobsQuery = useQuery({ queryKey: ["admin", "ingestion", "jobs", params], queryFn: () => adminService.ingestionJobs(params), retry: false });
  const payload = jobsQuery.data?.data;
  const totalPages = payload ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;

  const createMutation = useMutation({
    mutationFn: () => adminService.createIngestionJob({
      source_id: Number(form.source_id),
      name: form.name,
      job_type: form.job_type,
      priority: form.priority,
      execution_mode: "manual",
      status: "pending",
      is_enabled: false,
      manual_only: true,
      freshness_status: "unknown",
      configuration: { executes_live_ingestion: false },
      reason: form.reason,
    }),
    onSuccess: async () => {
      setShowCreate(false);
      setForm({ source_id: "", name: "", job_type: "news", priority: "normal", reason: "Initial operations setup" });
      await queryClient.invalidateQueries({ queryKey: ["admin", "ingestion", "jobs"] });
    },
  });

  const summary = payload?.summary ?? {};

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><DatabaseZap size={14} /> Ingestion Operations Centre</p>
            <h1 className="text-3xl font-bold">Observable job control plane</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">Define ingestion jobs, inspect execution history, and record operator requests without running live connectors or background workers.</p>
          </div>
          <button onClick={() => setShowCreate((value) => !value)} className="premium-button inline-flex items-center gap-2"><Plus size={16} /> Add Job</button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={Activity} label="Registered Jobs" value={summary.registered_jobs ?? 0} />
        <Metric icon={PlayCircle} label="Running Jobs" value={summary.running_jobs ?? 0} />
        <Metric icon={AlertTriangle} label="Failed Jobs" value={summary.failed_jobs ?? 0} />
        <Metric icon={PauseCircle} label="Paused Jobs" value={summary.paused_jobs ?? 0} />
        <Metric icon={DatabaseZap} label="Fresh Sources" value={summary.fresh_sources ?? 0} />
        <Metric icon={AlertTriangle} label="Stale Sources" value={summary.stale_sources ?? 0} />
        <Metric icon={Clock} label="Avg Duration" value={`${summary.average_duration_ms ?? 0} ms`} />
        <Metric icon={Activity} label="Executions" value={summary.todays_executions ?? 0} />
      </section>

      {showCreate ? (
        <section className="premium-card p-5">
          <h2 className="text-xl font-semibold">Create job definition</h2>
          <p className="mt-1 text-sm text-muted-foreground">This records configuration only. It will not run ingestion.</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <input value={form.source_id} onChange={(event) => setForm({ ...form, source_id: event.target.value })} placeholder="Source ID" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Job name" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <select value={form.job_type} onChange={(event) => setForm({ ...form, job_type: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{JOB_TYPES.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
            <select value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{PRIORITIES.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          </div>
          <textarea value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} className="mt-3 min-h-20 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          {createMutation.isError ? <p className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">Unable to create job. Confirm source ID exists and the job name is unique for that source.</p> : null}
          <button disabled={createMutation.isPending || !Number(form.source_id) || !form.name.trim() || !form.reason.trim()} onClick={() => createMutation.mutate()} className="premium-button mt-4 disabled:cursor-not-allowed disabled:opacity-50">Create job</button>
        </section>
      ) : null}

      <section className="premium-card p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_repeat(4,170px)]">
          <label className="relative block"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} /><input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder="Search jobs or sources" className="w-full rounded-lg border border-white/10 bg-background-secondary py-3 pl-10 pr-3 text-sm outline-none ring-primary/40 focus:ring-2" /></label>
          {[status, priority, jobType, freshness].map((value, index) => {
            const lists = [STATUSES, PRIORITIES, JOB_TYPES, FRESHNESS];
            const setters = [setStatus, setPriority, setJobType, setFreshness];
            return <select key={index} value={value} onChange={(event) => { setters[index](event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{lists[index].map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>;
          })}
        </div>
      </section>

      <section className="space-y-3">
        {jobsQuery.isLoading ? Array.from({ length: 6 }).map((_, index) => <div key={index} className="premium-card h-28 animate-pulse" />) : payload && payload.jobs.length ? payload.jobs.map((job) => (
          <Link key={job.id} href={`/admin/ingestion/jobs/${job.id}`} className="premium-card block p-5 smooth-transition hover:-translate-y-1 hover:border-primary/40">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-xl font-semibold">{job.name}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{job.source_name} • {label(job.job_type)} • {job.execution_mode}</p>
              </div>
              <div className="flex flex-wrap gap-2"><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(job.status)}`}>{label(job.status)}</span><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(job.priority)}`}>{label(job.priority)}</span><span className={`rounded-full border px-3 py-1 text-xs ${badgeClass(job.freshness_status)}`}>{label(job.freshness_status)}</span></div>
            </div>
          </Link>
        )) : <div className="premium-card p-6"><h2 className="text-xl font-semibold">No ingestion jobs found</h2><p className="mt-2 text-sm text-muted-foreground">Create a job definition or run the development seed. Jobs do not execute live ingestion in this sprint.</p></div>}
      </section>

      {payload ? <div className="flex items-center justify-between rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="premium-button-secondary disabled:opacity-50">Previous</button><span className="text-muted-foreground">Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="premium-button-secondary disabled:opacity-50">Next</button></div> : null}
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Activity; label: string; value: string | number }) {
  return <article className="premium-card p-5"><span className="inline-flex rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><Icon size={20} /></span><p className="mt-4 text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-semibold">{value}</p></article>;
}
