"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BarChart3, BookOpen, Building2, GitBranch, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout";
import { macroService } from "@/services/api";

const macroLabels: Record<string, string> = {
  inflation: "Inflation",
  "interest-rates": "Interest Rates",
  "exchange-rates": "Exchange Rates",
  gdp: "GDP",
  commodities: "Commodity Prices",
};

const macroTypes = [
  { slug: "inflation", label: "Inflation" },
  { slug: "interest-rates", label: "Interest Rates" },
  { slug: "exchange-rates", label: "Exchange Rates" },
  { slug: "gdp", label: "GDP" },
  { slug: "commodities", label: "Commodity Prices" },
];

export default function MacroDetailPage() {
  const params = useParams<{ type: string }>();
  const type = params?.type ?? "inflation";
  const label = macroLabels[type] ?? "Macro Indicator";

  const researchQuery = useQuery({
    queryKey: ["macro-research", type],
    queryFn: () => macroService.getResearch(type),
    retry: 1,
    staleTime: 1000 * 60 * 10,
  });

  const research = researchQuery.data?.data;
  const current = research?.current_value;
  const graphEdges = research?.knowledge_graph.edges ?? [];

  const valueLabel = useMemo(() => {
    if (!current) return "Unavailable";
    return `${current.value} ${current.unit}`;
  }, [current]);

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="premium-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Macro Intelligence</p>
              <h1 className="mt-2 text-4xl font-bold">{label}</h1>
              <p className="mt-3 max-w-3xl text-muted-foreground">
                {research?.overview ?? "InvestGuide explains what this indicator means, why investors care, and which companies or sectors are typically affected."}
              </p>
            </div>
            <div className="rounded-lg border border-primary/30 bg-primary/10 px-5 py-4 text-primary">
              <p className="text-sm text-primary/80">Current Value</p>
              <p className="mt-1 text-3xl font-semibold">{valueLabel}</p>
              <p className="mt-1 text-xs text-primary/80">{current?.reporting_period ?? "No period available"}</p>
            </div>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            {macroTypes.map((item) => (
              <Link
                key={item.slug}
                href={`/macro/${item.slug}`}
                className={`rounded-lg border px-3 py-2 text-sm transition ${item.slug === type ? "border-primary bg-primary/10 text-primary" : "border-white/10 bg-background-primary/70 text-muted-foreground hover:border-primary/60"}`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </section>

        {researchQuery.isLoading ? (
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="skeleton-card h-64" />
            <div className="skeleton-card h-64" />
          </div>
        ) : researchQuery.isError ? (
          <div className="warning-panel">Macro Intelligence is unavailable right now. Check that the backend is running and macro migrations have been applied.</div>
        ) : research ? (
          <>
            <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="premium-card p-6">
                <div className="flex items-center gap-2">
                  <Activity className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Why It Matters</h2>
                </div>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.why_investors_care}</p>
                <div className="mt-5 rounded-lg border border-white/10 bg-background-primary/70 p-4">
                  <p className="text-sm font-semibold">Explain Like I am 18</p>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{research.explain_like_im_18}</p>
                </div>
              </div>

              <div className="premium-card p-6">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="text-emerald-300" size={20} />
                  <h2 className="text-xl font-semibold">Evidence & Provenance</h2>
                </div>
                <div className="mt-4 grid gap-3">
                  <Fact label="Confidence" value={research.evidence.confidence} />
                  <Fact label="Source quality" value={research.evidence.source_quality} />
                  <Fact label="Data completeness" value={`${research.evidence.data_completeness}%`} />
                  <Fact label="Data origin" value={research.transparency.data_origin} />
                  <Fact label="Source" value={current?.source_name ?? "Unavailable"} />
                  <Fact label="Last updated" value={current?.verified_at ?? current?.updated_at ?? "Unavailable"} />
                </div>
                {current?.is_development_data ? (
                  <div className="mt-4 rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-sm text-blue-200">
                    Development Preview: this value is fixture-backed until a verified macro import is available.
                  </div>
                ) : null}
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <ListCard icon={BarChart3} title="Typical Business Impacts" items={research.typical_business_impacts} />
              <ListCard icon={Building2} title="Typical Sector Impacts" items={research.typical_sector_impacts} />
            </section>

            <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Affected Sectors</h2>
                <div className="mt-4 space-y-3">
                  {research.affected_sectors.length > 0 ? research.affected_sectors.map((sector) => (
                    <Link key={sector.sector} href={`/sector/${sector.sector.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}`} className="block rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                      <p className="font-semibold">{sector.sector}</p>
                      <p className="mt-2 text-sm text-muted-foreground">{sector.reason}</p>
                    </Link>
                  )) : <p className="text-sm text-muted-foreground">No sector mapping is available yet.</p>}
                </div>
              </div>

              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Affected Companies</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {research.affected_companies.length > 0 ? research.affected_companies.map((company) => (
                    <Link key={company.ticker} href={company.href} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                      <p className="font-semibold">{company.ticker}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{company.name}</p>
                      <p className="mt-3 text-xs text-muted-foreground">{company.reason}</p>
                    </Link>
                  )) : <p className="text-sm text-muted-foreground">No related companies are available yet.</p>}
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <div className="premium-card p-6">
                <div className="flex items-center gap-2">
                  <GitBranch className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Knowledge Graph</h2>
                </div>
                <div className="mt-4 space-y-3">
                  {graphEdges.slice(0, 8).map((edge) => (
                    <div key={`${edge.from}-${edge.to}`} className="rounded-lg border border-white/10 bg-background-primary/70 p-3 text-sm">
                      <span className="font-semibold">{edge.from}</span> <span className="text-muted-foreground">to</span> <span className="font-semibold">{edge.to}</span>
                      <p className="mt-1 text-muted-foreground">{edge.reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="premium-card p-6">
                <div className="flex items-center gap-2">
                  <BookOpen className="text-emerald-300" size={20} />
                  <h2 className="text-xl font-semibold">Learn Next</h2>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {research.learn_next.map((topic) => (
                    <Link key={topic.topic} href={topic.path} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary transition hover:border-primary/70">
                      {topic.topic}
                    </Link>
                  ))}
                </div>
                <div className="mt-5 rounded-lg border border-amber-400/25 bg-amber-500/10 p-3 text-sm text-amber-100">
                  <div className="flex items-center gap-2 font-medium"><AlertTriangle size={16} /> Not financial advice</div>
                  <p className="mt-2 text-amber-100/80">{research.transparency.not_advice}</p>
                </div>
              </div>
            </section>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-3">
      <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">{label}</p>
      <p className="mt-1 break-words text-sm font-semibold">{value}</p>
    </div>
  );
}

function ListCard({ icon: Icon, title, items }: { icon: typeof BarChart3; title: string; items: string[] }) {
  return (
    <div className="premium-card p-6">
      <div className="flex items-center gap-2">
        <Icon className="text-primary" size={20} />
        <h2 className="text-xl font-semibold">{title}</h2>
      </div>
      <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

