"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Cable, Plus, Search, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

const CONNECTOR_TYPES = ["all", "rest_api", "graphql", "rss", "html_scraper", "pdf_extractor", "csv_importer", "json_feed", "xml_feed", "database", "file_upload", "manual", "future_custom_connector"];
const LIFECYCLES = ["all", "draft", "active", "deprecated", "disabled", "archived"];
const CAPABILITIES = ["all", "market_prices", "company_filings", "annual_reports", "interim_reports", "trading_updates", "corporate_actions", "dividends", "news", "macroeconomic_indicators", "currency_rates", "commodity_prices", "weather", "research_reports", "esg_data"];

function label(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter: string) => letter.toUpperCase());
}

function lifecycleClass(value: string) {
  if (value === "active") return "border-emerald-400/30 bg-emerald-500/10 text-emerald-100";
  if (value === "deprecated") return "border-amber-400/30 bg-amber-500/10 text-amber-100";
  if (value === "archived" || value === "disabled") return "border-white/10 bg-white/5 text-muted-foreground";
  return "border-sky-400/30 bg-sky-500/10 text-sky-100";
}

export default function AdminConnectorsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [connectorType, setConnectorType] = useState("all");
  const [lifecycle, setLifecycle] = useState("all");
  const [capability, setCapability] = useState("all");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", display_name: "", connector_type: "rest_api", authentication_strategy: "none", capability: "market_prices", reason: "Initial connector registry setup" });

  const params = useMemo(() => ({
    page,
    limit: 12,
    search: search.trim() || undefined,
    connector_type: connectorType === "all" ? undefined : connectorType,
    lifecycle: lifecycle === "all" ? undefined : lifecycle,
    capability: capability === "all" ? undefined : capability,
  }), [page, search, connectorType, lifecycle, capability]);

  const connectorsQuery = useQuery({ queryKey: ["admin", "connectors", params], queryFn: () => adminService.connectors(params), retry: false });
  const payload = connectorsQuery.data?.data;
  const totalPages = payload ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;

  const createMutation = useMutation({
    mutationFn: () => adminService.createConnector({
      name: form.name,
      display_name: form.display_name,
      description: "Operator-created connector contract. Metadata only; no execution is enabled.",
      version: "1.0.0",
      vendor: "InvestGuide",
      author: "InvestGuide Platform",
      classification: "operator_defined",
      connector_type: form.connector_type,
      lifecycle: "draft",
      authentication_strategy: form.authentication_strategy,
      configuration_schema: { base_url: "string", endpoint_templates: "object" },
      required_fields: [],
      supported_source_categories: [],
      compatibility_notes: "Connector definition only. Future workers will consume this contract.",
      capabilities: [{ capability: form.capability, description: `Supports ${form.capability} payload contracts.` }],
      configuration_contract: {
        schema: { base_url: "string", endpoint_templates: "object" },
        required_fields: [],
        endpoint_templates: {},
        headers_schema: {},
        pagination_strategy: "contract_defined",
        parser_identifier: `${form.connector_type}.operator.v1`,
        rate_limit_policy: { requests_per_minute: 30 },
        default_timeout_seconds: 30,
        default_retry_count: 3,
        request_method: "GET",
        user_agent: "InvestGuideConnector/1.0",
      },
      reason: form.reason,
    }),
    onSuccess: async () => {
      setShowCreate(false);
      setForm({ name: "", display_name: "", connector_type: "rest_api", authentication_strategy: "none", capability: "market_prices", reason: "Initial connector registry setup" });
      await queryClient.invalidateQueries({ queryKey: ["admin", "connectors"] });
    },
  });

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><Cable size={14} /> Connector Registry</p>
            <h1 className="text-3xl font-bold">Reusable connector framework</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
              Define how InvestGuide will communicate with external sources later: capabilities, configuration contracts, validation rules, auth strategy, and version history.
            </p>
          </div>
          <button onClick={() => setShowCreate((value) => !value)} className="premium-button inline-flex items-center gap-2"><Plus size={16} /> Add Connector</button>
        </div>
      </section>

      {showCreate ? (
        <section className="premium-card p-5">
          <h2 className="text-xl font-semibold">Create connector</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="generic_connector" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} placeholder="Display name" className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <select value={form.connector_type} onChange={(event) => setForm({ ...form, connector_type: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CONNECTOR_TYPES.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
            <select value={form.authentication_strategy} onChange={(event) => setForm({ ...form, authentication_strategy: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{["none", "api_key", "bearer_token", "oauth2", "username_password", "cookie", "custom"].map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
            <select value={form.capability} onChange={(event) => setForm({ ...form, capability: event.target.value })} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CAPABILITIES.filter((item) => item !== "all").map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          </div>
          <textarea value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} className="mt-3 min-h-20 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
          {createMutation.isError ? <p className="mt-3 rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">Unable to create connector. Check unique name, safe schema fields, and required values.</p> : null}
          <button disabled={createMutation.isPending || !form.name.trim() || !form.display_name.trim() || !form.reason.trim()} onClick={() => createMutation.mutate()} className="premium-button mt-4 disabled:cursor-not-allowed disabled:opacity-50">Create connector</button>
        </section>
      ) : null}

      <section className="premium-card p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_repeat(3,210px)]">
          <label className="relative block"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} /><input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder="Search connectors" className="w-full rounded-lg border border-white/10 bg-background-secondary py-3 pl-10 pr-3 text-sm outline-none ring-primary/40 focus:ring-2" /></label>
          <select value={connectorType} onChange={(event) => { setConnectorType(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CONNECTOR_TYPES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={lifecycle} onChange={(event) => { setLifecycle(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{LIFECYCLES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
          <select value={capability} onChange={(event) => { setCapability(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">{CAPABILITIES.map((item) => <option key={item} value={item}>{label(item)}</option>)}</select>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {connectorsQuery.isLoading ? Array.from({ length: 6 }).map((_, index) => <div key={index} className="premium-card h-40 animate-pulse p-5" />) : payload && payload.connectors.length ? payload.connectors.map((connector) => (
          <Link key={connector.id} href={`/admin/connectors/${connector.id}`} className="premium-card block p-5 smooth-transition hover:-translate-y-1 hover:border-primary/40">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">{connector.display_name}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{connector.name} • v{connector.version} • {label(connector.connector_type)}</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs ${lifecycleClass(connector.lifecycle)}`}>{label(connector.lifecycle)}</span>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              <span className="premium-badge"><ShieldCheck size={14} /> {label(connector.authentication_strategy)}</span>
              <span className="premium-badge">{connector.compatible_source_count} source{connector.compatible_source_count === 1 ? "" : "s"}</span>
              {connector.classification ? <span className="premium-badge">{label(connector.classification)}</span> : null}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {connector.capabilities.length ? connector.capabilities.slice(0, 6).map((item) => <span key={item} className="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-100">{label(item)}</span>) : <span className="text-xs text-muted-foreground">No capabilities declared yet</span>}
              {connector.capabilities.length > 6 ? <span className="text-xs text-muted-foreground">+{connector.capabilities.length - 6} more</span> : null}
            </div>
          </Link>
        )) : (
          <div className="premium-card p-6 xl:col-span-2"><h2 className="text-xl font-semibold">No connectors found</h2><p className="mt-2 text-sm text-muted-foreground">Run the development seed command, clear filters, or create a connector contract.</p></div>
        )}
      </section>

      {payload ? <div className="flex items-center justify-between rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm"><button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Previous</button><span className="text-muted-foreground">Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Next</button></div> : null}
    </div>
  );
}
