"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DatabaseZap, Plus, Search, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

const CATEGORIES = ["all", "market", "government", "regulator", "company", "research", "news", "international", "commodity", "currency", "weather", "alternative_intelligence", "esg", "corporate_registry"];
const TIERS = ["all", "tier_1", "tier_2", "tier_3"];
const STATUSES = ["all", "enabled", "disabled", "maintenance"];
const CONNECTORS = ["all", "rest_api", "rss", "website", "html_scraper", "pdf", "csv", "json", "xml", "manual_upload", "database", "future_connector"];

function label(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter: string) => letter.toUpperCase());
}

function tierClass(tier: string) {
  if (tier === "tier_1") return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (tier === "tier_2") return "border-sky-400/30 bg-sky-500/10 text-sky-100";
  return "border-amber-400/30 bg-amber-500/10 text-amber-100";
}

function statusClass(status: string) {
  if (status === "enabled") return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (status === "maintenance") return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  return "border-white/10 bg-white/5 text-muted-foreground";
}

export default function AdminSourcesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [tier, setTier] = useState("all");
  const [status, setStatus] = useState("all");
  const [connector, setConnector] = useState("all");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", display_name: "", category: "market", tier: "tier_1", connector_type: "website", base_url: "", reason: "Initial registry setup" });

  const params = useMemo(() => ({
    page,
    limit: 12,
    search: search.trim() || undefined,
    category: category === "all" ? undefined : category,
    tier: tier === "all" ? undefined : tier,
    status: status === "all" ? undefined : status,
    connector_type: connector === "all" ? undefined : connector,
  }), [page, search, category, tier, status, connector]);

  const sourcesQuery = useQuery({ queryKey: ["admin", "sources", params], queryFn: () => adminService.sources(params), retry: false });
  const payload = sourcesQuery.data?.data;
  const totalPages = payload ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;

  const createMutation = useMutation({
    mutationFn: () => adminService.createSource({
      name: form.name,
      display_name: form.display_name,
      category: form.category,
      tier: form.tier,
      connector_type: form.connector_type,
      authentication_type: "none",
      status: "disabled",
      configuration: { base_url: form.base_url || null, refresh_policy: "manual", parser: {}, connector_config: {}, timeout_seconds: 30, retry_count: 3 },
      credentials: [],
      reason: form.reason,
    }),
    onSuccess: async () => {
      setShowCreate(false);
      setForm({ name: "", display_name: "", category: "market", tier: "tier_1", connector_type: "website", base_url: "", reason: "Initial registry setup" });
      await queryClient.invalidateQueries({ queryKey: ["admin", "sources"] });
    },
  });

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><DatabaseZap size={14} /> Data Source Registry</p>
            <h1 className="text-3xl font-bold">Configurable source operating system</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
              Manage trust tiers, connector settings, refresh policy, provenance rules, and credential metadata before live ingestion is enabled.
            </p>
          </div>
          <button onClick={() => setShowCreate((value) => !value)} className="premium-button inline-flex items-center gap-2"><Plus size={16} /> Add Source</button>
        </div>
      </section>

      {showCreate ? (
        <section className="premium-card p-5">
          <h2 className="text-xl font-semibold">Create source</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="source_name" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} placeholder="Display name" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <input value={form.base_url} onChange={(event) => setForm({ ...form, base_url: event.target.value })} placeholder="Base URL" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CATEGORIES.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
            <select value={form.tier} onChange={(event) => setForm({ ...form, tier: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{TIERS.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
            <select value={form.connector_type} onChange={(event) => setForm({ ...form, connector_type: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CONNECTORS.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          </div>
          <textarea value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} className="mt-3 min-h-20 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          {createMutation.isError ? <p className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">Unable to create source. Check unique name and required fields.</p> : null}
          <button disabled={createMutation.isPending || !form.name.trim() || !form.display_name.trim() || !form.reason.trim()} onClick={() => createMutation.mutate()} className="premium-button mt-4 disabled:cursor-not-allowed disabled:opacity-50">Create source</button>
        </section>
      ) : null}

      <section className="premium-card p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_repeat(4,170px)]">
          <label className="relative block"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} /><input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder="Search sources" className="w-full rounded-lg border border-white/10 bg-background-secondary py-3 pl-10 pr-3 text-sm outline-none ring-primary/40 focus:ring-2" /></label>
          <select value={tier} onChange={(event) => { setTier(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{TIERS.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CATEGORIES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{STATUSES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={connector} onChange={(event) => { setConnector(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CONNECTORS.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {sourcesQuery.isLoading ? Array.from({ length: 6 }).map((_, index) => <div key={index} className="premium-card h-40 animate-pulse p-5" />) : payload && payload.sources.length ? payload.sources.map((source) => (
          <Link key={source.id} href={`/admin/sources/${source.id}`} className="premium-card block p-5 smooth-transition hover:-translate-y-1 hover:border-primary/40">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">{source.display_name}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{source.name} • {label(source.category)} • {label(source.connector_type)}</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs ${statusClass(source.status)}`}>{label(source.status)}</span>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              <span className={`rounded-full border px-3 py-1 text-xs ${tierClass(source.tier)}`}>{label(source.tier)}</span>
              <span className="premium-badge"><ShieldCheck size={14} /> {Math.round(source.confidence_weight * 100)}% confidence</span>
              <span className="premium-badge">{label(source.refresh_policy)}</span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {source.supported_capabilities.length ? source.supported_capabilities.slice(0, 5).map((capability) => (
                <span key={capability} className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-100">{label(capability)}</span>
              )) : <span className="text-xs text-muted-foreground">No capabilities declared yet</span>}
              {source.supported_capabilities.length > 5 ? <span className="text-xs text-muted-foreground">+{source.supported_capabilities.length - 5} more</span> : null}
            </div>
          </Link>
        )) : (
          <div className="premium-card p-6 xl:col-span-2"><h2 className="text-xl font-semibold">No sources found</h2><p className="mt-2 text-sm text-muted-foreground">Adjust filters, create a source, or run the development seed command.</p></div>
        )}
      </section>

      {payload ? <div className="flex items-center justify-between rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Previous</button><span className="text-muted-foreground">Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Next</button></div> : null}
    </div>
  );
}


