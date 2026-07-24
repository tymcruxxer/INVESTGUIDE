"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Cable, CheckCircle2, ShieldCheck } from "lucide-react";
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

function statusClass(value: string) {
  if (value === "passed" || value === "active") return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (value === "warning" || value === "deprecated") return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  if (value === "failed") return "border-rose-400/30 bg-rose-500/10 text-rose-100";
  return "border-white/10 bg-white/5 text-muted-foreground";
}

export default function AdminConnectorDetailPage() {
  const params = useParams<{ id: string }>();
  const connectorId = Number(params.id);
  const queryClient = useQueryClient();
  const [statusReason, setStatusReason] = useState("Connector lifecycle update");
  const [validationReason, setValidationReason] = useState("Metadata contract validation");
  const [message, setMessage] = useState<string | null>(null);

  const connectorQuery = useQuery({ queryKey: ["admin", "connector", connectorId], queryFn: () => adminService.connector(connectorId), retry: false, enabled: Number.isFinite(connectorId) });
  const connector = connectorQuery.data?.data;

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin", "connector", connectorId] });
    await queryClient.invalidateQueries({ queryKey: ["admin", "connectors"] });
  };

  const statusMutation = useMutation({
    mutationFn: (lifecycle: "draft" | "active" | "deprecated" | "disabled" | "archived") => adminService.updateConnectorStatus(connectorId, { lifecycle, reason: statusReason }),
    onSuccess: async () => { setMessage("Connector lifecycle updated and audited."); await refresh(); },
    onError: () => setMessage("Unable to update connector lifecycle."),
  });

  const validationMutation = useMutation({
    mutationFn: () => adminService.validateConnector(connectorId, { configuration: {}, reason: validationReason }),
    onSuccess: async (response) => { setMessage(`Validation completed: ${label(response.data.status)}.`); await refresh(); },
    onError: () => setMessage("Unable to validate connector metadata."),
  });

  if (connectorQuery.isLoading) return <div className="premium-card h-96 animate-pulse p-6" />;

  if (!connector) {
    return <div className="premium-card p-6"><h1 className="text-2xl font-bold">Connector unavailable</h1><p className="mt-2 text-sm text-muted-foreground">The connector may not exist, may be archived, or your permissions may not allow inspection.</p><Link href="/admin/connectors" className="premium-button mt-5 inline-flex"><ArrowLeft size={16} /> Back to connectors</Link></div>;
  }

  const contract = connector.configuration_contract;

  return (
    <div className="space-y-6">
      <Link href="/admin/connectors" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Connectors</Link>

      <section className="premium-card p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><Cable size={14} /> Connector detail</p>
            <h1 className="text-3xl font-bold">{connector.display_name}</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{connector.description ?? "No description provided."}</p>
            <div className="mt-4 flex flex-wrap gap-2"><span className="premium-badge">v{connector.version}</span><span className="premium-badge">{label(connector.connector_type)}</span><span className="premium-badge">{label(connector.authentication_strategy)}</span></div>
          </div>
          <span className={`rounded-full border px-3 py-1 text-xs ${statusClass(connector.lifecycle)}`}>{label(connector.lifecycle)}</span>
        </div>
        {message ? <p className="mt-5 rounded-lg border border-primary/25 bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Overview</h2><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Name</dt><dd className="text-foreground">{connector.name}</dd></div><div><dt>Vendor</dt><dd className="text-foreground">{connector.vendor ?? "Not recorded"}</dd></div><div><dt>Author</dt><dd className="text-foreground">{connector.author ?? "Not recorded"}</dd></div><div><dt>Classification</dt><dd className="text-foreground">{label(connector.classification)}</dd></div></dl></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Contract</h2><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Parser</dt><dd className="text-foreground">{contract?.parser_identifier ?? "Not configured"}</dd></div><div><dt>Method</dt><dd className="text-foreground">{contract?.request_method ?? "GET"}</dd></div><div><dt>Timeout</dt><dd className="text-foreground">{contract?.default_timeout_seconds ?? 30}s</dd></div><div><dt>Retries</dt><dd className="text-foreground">{contract?.default_retry_count ?? 3}</dd></div></dl></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Source binding</h2><p className="mt-2 text-sm text-muted-foreground">{connector.compatible_source_count} source{connector.compatible_source_count === 1 ? "" : "s"} currently reference this connector.</p><div className="mt-4 flex flex-wrap gap-2">{connector.supported_source_categories.length ? connector.supported_source_categories.map((item) => <span key={item} className="premium-badge">{label(item)}</span>) : <span className="text-sm text-muted-foreground">No category limits set.</span>}</div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Capabilities</h2><div className="mt-4 flex flex-wrap gap-2">{connector.capabilities.length ? connector.capabilities.map((capability) => <span key={capability} className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-100">{label(capability)}</span>) : <span className="text-sm text-muted-foreground">No capabilities declared yet.</span>}</div></article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Configuration schema</h2><p className="mt-2 text-sm text-muted-foreground">Schemas store field metadata only. Secret values belong in future secure credential references.</p><div className="mt-4 space-y-3"><JsonBlock value={connector.configuration_schema} /><JsonBlock value={contract?.endpoint_templates} /></div></article>
        <article className="premium-card p-5"><h2 className="flex items-center gap-2 text-lg font-semibold"><ShieldCheck size={18} /> Authentication contract</h2><p className="mt-2 text-sm text-muted-foreground">No real auth flow is implemented here. This defines the strategy future connector workers must satisfy.</p><dl className="mt-4 space-y-3 text-sm text-muted-foreground"><div><dt>Strategy</dt><dd className="text-foreground">{label(connector.authentication_strategy)}</dd></div><div><dt>Headers schema</dt><dd><JsonBlock value={contract?.headers_schema} /></dd></div><div><dt>Rate limit</dt><dd><JsonBlock value={contract?.rate_limit_policy} /></dd></div></dl></article>
      </section>

      <section className="premium-card p-5">
        <h2 className="flex items-center gap-2 text-lg font-semibold"><CheckCircle2 size={18} /> Metadata validation</h2>
        <p className="mt-2 text-sm text-muted-foreground">Validation checks lifecycle, config schema, required fields, auth compatibility, and source category compatibility. It never performs network requests.</p>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto]">
          <input value={validationReason} onChange={(event) => setValidationReason(event.target.value)} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          <button onClick={() => validationMutation.mutate()} disabled={!validationReason.trim() || validationMutation.isPending} className="premium-button disabled:opacity-50">Validate contract</button>
        </div>
        <div className="mt-4 space-y-3">{connector.validation_history.length ? connector.validation_history.map((validation) => <div key={validation.id} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex flex-wrap items-center justify-between gap-3"><span className={`rounded-full border px-3 py-1 text-xs ${statusClass(validation.status)}`}>{label(validation.status)}</span><span className="text-muted-foreground">{formatDate(validation.created_at)}</span></div><p className="mt-2 text-muted-foreground">{validation.summary}</p>{validation.errors.length ? <p className="mt-2 text-rose-100">Errors: {validation.errors.join("; ")}</p> : null}{validation.warnings.length ? <p className="mt-2 text-amber-100">Warnings: {validation.warnings.join("; ")}</p> : null}</div>) : <p className="text-sm text-muted-foreground">No validation runs recorded yet.</p>}</div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Compatible sources</h2><div className="mt-4 space-y-3">{connector.compatible_sources.length ? connector.compatible_sources.map((source) => <Link key={source.id} href={`/admin/sources/${source.id}`} className="block rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm smooth-transition hover:border-primary/40"><div className="flex items-center justify-between gap-3"><span className="font-semibold">{source.display_name}</span><span className="text-muted-foreground">{label(source.status)}</span></div><p className="mt-1 text-muted-foreground">{label(source.category)} • {label(source.connector_type)}</p></Link>) : <p className="text-sm text-muted-foreground">No sources are bound to this connector yet.</p>}</div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Lifecycle controls</h2><p className="mt-2 text-sm text-muted-foreground">Archiving is a soft-delete. Existing version and validation records remain available for audit.</p><input value={statusReason} onChange={(event) => setStatusReason(event.target.value)} className="mt-4 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" /><div className="mt-3 flex flex-wrap gap-2"><button onClick={() => statusMutation.mutate("active")} disabled={!statusReason.trim()} className="premium-button disabled:opacity-50">Activate</button><button onClick={() => statusMutation.mutate("deprecated")} disabled={!statusReason.trim()} className="premium-button-secondary disabled:opacity-50">Deprecate</button><button onClick={() => statusMutation.mutate("disabled")} disabled={!statusReason.trim()} className="premium-button-secondary disabled:opacity-50">Disable</button><button onClick={() => statusMutation.mutate("archived")} disabled={!statusReason.trim()} className="premium-button-secondary disabled:opacity-50">Archive</button></div></article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Version history</h2><div className="mt-4 space-y-3">{connector.version_history.length ? connector.version_history.map((version) => <div key={version.id} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex items-center justify-between"><span className="font-semibold">v{version.version} • {label(version.change_type)}</span><span className="text-muted-foreground">{formatDate(version.created_at)}</span></div><p className="mt-1 text-muted-foreground">{version.change_summary ?? "No change summary recorded."}</p></div>) : <p className="text-sm text-muted-foreground">No version history yet.</p>}</div></article>
        <article className="premium-card p-5"><h2 className="text-lg font-semibold">Recent activity</h2><div className="mt-4 space-y-3">{connector.recent_activity.length ? connector.recent_activity.map((activity, index) => <div key={index} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><div className="flex items-center justify-between"><span className="font-semibold">{String(activity.action ?? "activity")}</span><span className="text-muted-foreground">{formatDate(String(activity.created_at ?? ""))}</span></div><p className="mt-1 text-muted-foreground">{String(activity.reason ?? activity.result ?? "No detail recorded.")}</p></div>) : <p className="text-sm text-muted-foreground">No recent activity yet.</p>}</div></article>
      </section>
    </div>
  );
}
