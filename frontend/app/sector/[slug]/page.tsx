"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BarChart3, BookOpen, Building2, GitBranch, Layers3, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout";
import { sectorService } from "@/services/api";

export default function SectorPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug ?? "consumer-staples";
  const query = useQuery({
    queryKey: ["sector-research", slug],
    queryFn: () => sectorService.getSectorResearch(slug),
    retry: 1,
    staleTime: 1000 * 60 * 10,
  });
  const research = query.data?.data;

  return (
    <AppShell>
      <div className="space-y-6">
        {query.isLoading ? (
          <div className="skeleton-card h-72" />
        ) : query.isError ? (
          <div className="warning-panel">Sector Intelligence is unavailable. Check that backend sector migrations and seeds have run.</div>
        ) : research ? (
          <>
            <section className="premium-card p-6">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Sector Intelligence</p>
                  <h1 className="mt-2 text-4xl font-bold">{research.sector.name}</h1>
                  <p className="mt-3 max-w-3xl text-muted-foreground">{research.overview.what_it_is}</p>
                </div>
                <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
                  <p className="font-semibold">{research.transparency.data_origin}</p>
                  <p className="mt-1 text-primary/80">{research.sector.country}</p>
                </div>
              </div>
              {research.sector.is_development_data ? (
                <div className="mt-5 rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-sm text-blue-200">
                  Development Preview: this sector profile is fixture-backed until verified sector reference data is imported.
                </div>
              ) : null}
            </section>

            <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
              <InfoCard icon={Layers3} title="Why Investors Study It" items={[research.overview.why_investors_study_it, ...research.typical_characteristics]} />
              <div className="premium-card p-6">
                <div className="flex items-center gap-2">
                  <Building2 className="text-primary" size={20} />
                  <h2 className="text-xl font-semibold">Major Companies</h2>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {research.companies.length > 0 ? research.companies.map((company) => (
                    <Link key={company.ticker} href={company.href} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                      <p className="font-semibold">{company.ticker}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{company.name}</p>
                      <p className="mt-3 text-xs text-muted-foreground">{company.reason}</p>
                    </Link>
                  )) : <p className="text-sm text-muted-foreground">No listed companies are mapped to this sector yet.</p>}
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <InfoCard icon={BarChart3} title="Typical Opportunities" items={research.typical_opportunities.map((item) => `${item.label}: ${item.why_it_matters}`)} />
              <InfoCard icon={AlertTriangle} title="Typical Risks" items={research.typical_risks.map((item) => `${item.label}: ${item.why_it_matters}`)} />
            </section>

            <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Industries</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {research.industries.map((industry) => (
                    <Link key={industry.slug} href={`/industry/${industry.slug}`} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                      <p className="font-semibold">{industry.name}</p>
                      <p className="mt-2 text-sm text-muted-foreground">{industry.description ?? "Industry description pending."}</p>
                    </Link>
                  ))}
                </div>
              </div>
              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Macro Factors</h2>
                <div className="mt-4 space-y-3">
                  {research.macro_relationships.map((item) => (
                    <Link key={item.indicator_type} href={item.path} className="block rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                      <p className="font-semibold">{item.label}</p>
                      <p className="mt-2 text-sm text-muted-foreground">{item.relationship}</p>
                    </Link>
                  ))}
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <InfoCard icon={ShieldCheck} title="Financial Characteristics" items={research.financial_characteristics} />
              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Related Sectors</h2>
                <div className="mt-4 space-y-3">
                  {research.related_sectors.map((item) => (
                    <div key={item.name} className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                      <p className="font-semibold">{item.name}</p>
                      <p className="mt-2 text-sm text-muted-foreground">{item.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <GraphCard edges={research.knowledge_graph.edges} />
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
                <div className="mt-5 rounded-lg border border-white/10 bg-background-primary/70 p-4 text-sm text-muted-foreground">
                  {research.transparency.methodology} {research.transparency.not_advice}
                </div>
              </div>
            </section>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function InfoCard({ icon: Icon, title, items }: { icon: typeof Layers3; title: string; items: string[] }) {
  return (
    <div className="premium-card p-6">
      <div className="flex items-center gap-2">
        <Icon className="text-primary" size={20} />
        <h2 className="text-xl font-semibold">{title}</h2>
      </div>
      <ul className="mt-4 space-y-2 text-sm leading-6 text-muted-foreground">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

function GraphCard({ edges }: { edges: Array<{ from: string; to: string; reason: string }> }) {
  return (
    <div className="premium-card p-6">
      <div className="flex items-center gap-2">
        <GitBranch className="text-primary" size={20} />
        <h2 className="text-xl font-semibold">Knowledge Graph</h2>
      </div>
      <div className="mt-4 space-y-3">
        {edges.slice(0, 8).map((edge) => (
          <div key={`${edge.from}-${edge.to}`} className="rounded-lg border border-white/10 bg-background-primary/70 p-3 text-sm">
            <span className="font-semibold">{edge.from}</span> <span className="text-muted-foreground">to</span> <span className="font-semibold">{edge.to}</span>
            <p className="mt-1 text-muted-foreground">{edge.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
