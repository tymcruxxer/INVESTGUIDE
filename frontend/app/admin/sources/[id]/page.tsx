"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, DatabaseZap, KeyRound, ShieldCheck, Trash2 } from "lucide-react";
import { useState } from "react";
import { adminService } from "@/services/api";

function label(value?: string | null) {
  if (!value) return "Not configured";
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter: string) => letter.toUpperCase());
}

function formatDate(value?: string | null) {
  if (!value) return "Not recorded";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre className="overflow-auto rounded-lg border border-white/10 bg-background-primary p-3 text-xs text-muted-foreground">{JSON.stringify(value ?? {}, null, 2)}</pre>;
}

export default function AdminSourceDetailPage() {
  const params = useParams<{ id: string }>();
  const sourceId = Number(params.id);
  const queryClient = useQueryClient();
  const [statusReason, setStatusReason] = useState("Operational update");
  const [deleteReason, setDeleteReason] = useState("Source retired");
  const [message, setMessage] = useState<string | null>(null);

  const sourceQuery = useQuery({ queryKey: ["admin", "source", sourceId], queryFn: () => adminService.source(sourceId), retry: false, enabled: Number.isFinite(sourceId) });
  const source = sourceQuery.data?.data;

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin", "source", sourceId] });
    await queryClient.invalidateQueries({ queryKey: ["admin", "sources"] });
  };

  const statusMutation = useMutation({
    mutationFn: (status: "enabled" | "disabled" | "maintenance") => adminService.updateSourceStatus(sourceId, { status, reason: statusReason }),
    onSuccess: async () => { setMessage("Source status updated and audited."); await refresh(); },
    onError: () => setMessage("Unable to update source status."),
  });

  const deleteMutation = useMutation({
    mutationFn: () => adminService.deleteSource(sourceId, deleteReason),
    onSuccess: async () => { setMessage("Source soft-deleted and removed from active registry lists."); await refresh(); },
    onError: () => setMessage("Unable to soft-delete source."),
  });

  if (sourceQuery.isLoading) return <div className="premium-card h-96 animate-pulse p-6" />;

  if (!source) {
    return <div className="premium-card p-6"><h1 className="text-2xl font-bold">Source unavailable</h1><p className="mt-2 text-sm text-muted-foreground">The source may not exist, may be deleted, or your permissions may not allow inspection.</p><Link href="/admin/sources" className="premium-button mt-5 inline-flex"><ArrowLeft size={16} /> Back to sources</Link></div>;
  }

  const configuration = source.configuration;

  return (
    <div className="space-y-6">
      <Link href="/admin/sources" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Sources</Link>

      <section className="premium-card p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><DatabaseZap size={14} /> Source detail</p>
            <h1 className="text-3xl font-bold">{source.display_name}</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{source.description ?? "No description provided."}</p>
            <div className="mt-4 flex flex-wrap gap-2"><span className="premium-badge">{label(source.category)}</span><span className="premium-badge">{label(source.tier)}</span><span className="premium-badge">{label(source.connector_type)}</span></div>
          </div>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted-foreground">{label(source.status)}</span>
        </div>
        {message ? <p className="mt-5 rounded-lg border border-primary/25 bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Overview</h2><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Name</dt><dd className="text-foreground">{source.name}</dd></div><div><dt>Organization</dt><dd className="text-foreground">{source.organization ?? "Not recorded"}</dd></div><div><dt>Classification</dt><dd className="text-foreground">{source.classification ?? "Not recorded"}</dd></div><div><dt>Last updated</dt><dd className="text-foreground">{formatDate(source.updated_at)}</dd></div></dl></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Trust</h2><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Confidence weight</dt><dd className="text-foreground">{Math.round(source.confidence_weight * 100)}%</dd></div><div><dt>Trust level</dt><dd className="text-foreground">{configuration?.trust_level ?? "standard"}</dd></div><div><dt>Verification required</dt><dd className="text-foreground">{configuration?.verification_required ? "Yes" : "No"}</dd></div><div><dt>Last verified</dt><dd className="text-foreground">{formatDate(configuration?.last_verified_at)}</dd></div></dl></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Operational settings</h2><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Refresh</dt><dd className="text-foreground">{label(source.refresh_policy)}</dd></div><div><dt>Timeout</dt><dd className="text-foreground">{configuration?.timeout_seconds ?? 30}s</dd></div><div><dt>Retries</dt><dd className="text-foreground">{configuration?.retry_count ?? 0}</dd></div><div><dt>Rate limit</dt><dd className="text-foreground">{configuration?.rate_limit_per_minute ?? "Not set"}</dd></div></dl></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Capabilities</h2><p className="mt-2 text-sm text-muted-foreground">Future ingestion jobs use these declarations to discover what this source can provide.</p><div className="mt-4 flex flex-wrap gap-2">{source.supported_capabilities.length ? source.supported_capabilities.map((capability) => <span key={capability} className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-100">{label(capability)}</span>) : <span className="text-sm text-muted-foreground">No capabilities declared yet.</span>}</div></article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Connector configuration</h2><p className="mt-2 text-sm text-muted-foreground">Base URL: {configuration?.base_url ?? "Not configured"}</p><div className="mt-4 space-y-3"><JsonBlock value={configuration?.connector_config} /><JsonBlock value={configuration?.parser} /></div></article>
        <article className="premium-card p-5"><h2 className="flex items-center gap-2 text-lg font-semibold"><KeyRound size={18} /> Credentials</h2><p className="mt-2 text-sm text-muted-foreground">Secret values are never displayed after creation.</p><div className="mt-4 space-y-3">{source.credentials.length ? source.credentials.map((credential) => <div key={credential.id} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex items-center justify-between gap-3"><span className="font-semibold">{credential.label}</span><span className="text-muted-foreground">{credential.masked_value}</span></div><p className="mt-1 text-xs text-muted-foreground">{credential.key} • {label(credential.secret_type)} • {credential.is_configured ? "configured" : "not configured"}</p></div>) : <p className="text-sm text-muted-foreground">No credentials configured.</p>}</div></article>
      </section>

      <section className="premium-card p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold"><ShieldCheck size={18} /> Source operations</h2>
        <p className="mt-2 text-sm text-muted-foreground">Status changes and soft deletion are audited. Live ingestion remains disabled until future sprints.</p>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto]">
          <input value={statusReason} onChange={(event) => setStatusReason(event.target.value)} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          <div className="flex flex-wrap gap-2"><button onClick={() => statusMutation.mutate("enabled")} disabled={!statusReason.trim()} className="premium-button disabled:opacity-50">Enable</button><button onClick={() => statusMutation.mutate("maintenance")} disabled={!statusReason.trim()} className="premium-button-secondary disabled:opacity-50">Maintenance</button><button onClick={() => statusMutation.mutate("disabled")} disabled={!statusReason.trim()} className="premium-button-secondary disabled:opacity-50">Disable</button></div>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto]"><input value={deleteReason} onChange={(event) => setDeleteReason(event.target.value)} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" /><button onClick={() => deleteMutation.mutate()} disabled={!deleteReason.trim()} className="inline-flex items-center gap-2 rounded-lg border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 disabled:opacity-50"><Trash2 size={16} /> Soft delete</button></div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Version history</h2><div className="mt-4 space-y-3">{source.version_history.length ? source.version_history.map((version) => <div key={version.id} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex items-center justify-between"><span className="font-semibold">v{version.version} • {label(version.change_type)}</span><span className="text-muted-foreground">{formatDate(version.created_at)}</span></div><p className="mt-1 text-muted-foreground">{version.reason ?? "No reason recorded."}</p></div>) : <p className="text-sm text-muted-foreground">No version history yet.</p>}</div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Recent activity</h2><div className="mt-4 space-y-3">{source.recent_activity.length ? source.recent_activity.map((activity, index) => <div key={index} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex items-center justify-between"><span className="font-semibold">{String(activity.action ?? "activity")}</span><span className="text-muted-foreground">{formatDate(String(activity.created_at ?? ""))}</span></div><p className="mt-1 text-muted-foreground">{String(activity.reason ?? activity.result ?? "No detail recorded.")}</p></div>) : <p className="text-sm text-muted-foreground">No recent activity yet.</p>}</div></article>
      </section>
    </div>
  );
}


