import Link from "next/link";
import {
  BookOpen,
  Building2,
  GraduationCap,
  Network,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { NewsResearch } from "@/types";

interface NewsIntelligencePanelProps {
  research: NewsResearch;
}

const importanceTone: Record<NewsResearch["importance"]["label"], string> = {
  High: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  Medium: "border-blue-400/40 bg-blue-400/10 text-blue-200",
  Low: "border-slate-400/30 bg-slate-400/10 text-slate-200",
};

export function NewsIntelligenceSkeleton() {
  return (
    <section
      className="rounded-xl border border-white/10 bg-background-primary/70 p-5"
      aria-label="Loading news intelligence"
    >
      <div className="skeleton-card h-5 w-52" />
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    </section>
  );
}

export function NewsIntelligencePanel({ research }: NewsIntelligencePanelProps) {
  return (
    <section className="rounded-xl border border-primary/20 bg-gradient-to-br from-primary/10 via-background-primary/80 to-emerald-400/10 p-5 shadow-card">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <Sparkles size={15} /> News intelligence
          </p>
          <h3 className="mt-2 text-xl font-semibold">What happened?</h3>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            {research.title}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-foreground">
            {research.event_category.label}
          </span>
          <span
            className={`rounded-full border px-3 py-1 text-xs font-medium ${
              importanceTone[research.importance.label]
            }`}
          >
            {research.importance.label} importance
          </span>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <ShieldCheck size={16} className="text-emerald-300" /> Why it matters
          </div>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            {research.why_it_matters}
          </p>
          <div className="mt-4 rounded-lg border border-emerald-400/20 bg-emerald-400/10 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200">
              Explain like I am 18
            </p>
            <p className="mt-2 text-sm text-emerald-50/90">
              {research.explain_like_im_18}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Network size={16} className="text-primary" /> Evidence
          </div>
          <div className="mt-3 grid gap-3 text-sm">
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Confidence</span>
              <span className="font-semibold text-foreground">
                {research.evidence.confidence}
              </span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Completeness</span>
              <span className="font-semibold text-foreground">
                {research.evidence.data_completeness}%
              </span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-muted-foreground">Source tier</span>
              <span className="max-w-[12rem] text-right font-semibold text-foreground">
                {research.evidence.source_quality.tier}
              </span>
            </div>
          </div>
          <p className="mt-3 text-xs leading-5 text-muted-foreground">
            {research.evidence.why_confidence[0]}
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Building2 size={16} className="text-emerald-300" /> Related companies
          </div>
          <div className="mt-3 space-y-3">
            {research.related_companies.length > 0 ? (
              research.related_companies.slice(0, 4).map((company) => (
                <Link
                  key={company.ticker}
                  href={`/company/${company.ticker.toLowerCase()}`}
                  className="block rounded-lg border border-white/10 bg-white/[0.03] p-3 transition hover:border-primary/50 hover:bg-primary/10"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold text-foreground">
                      {company.ticker}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {company.sector}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {company.reason}
                  </p>
                </Link>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No listed company relationship was detected from the available article fields.
              </p>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <GraduationCap size={16} className="text-blue-300" /> Learn next
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {research.learn_next.slice(0, 6).map((topic) => (
              <Link
                key={topic.topic}
                href={topic.path}
                className="rounded-full border border-blue-400/30 bg-blue-400/10 px-3 py-1 text-xs font-medium text-blue-100 transition hover:border-blue-300 hover:bg-blue-400/20"
              >
                {topic.topic}
              </Link>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <BookOpen size={16} className="text-purple-300" /> Related concepts
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {research.related_topics.slice(0, 7).map((topic) => (
              <span
                key={topic}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-muted-foreground"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/50 p-3 text-xs leading-5 text-muted-foreground">
        <span className="font-semibold text-foreground">Transparency: </span>
        {research.transparency.methodology} {research.transparency.not_advice}
      </div>
    </section>
  );
}
