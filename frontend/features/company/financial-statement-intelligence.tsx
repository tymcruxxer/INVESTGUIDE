"use client";

import { BookOpen, ClipboardCheck, FileBarChart, ShieldCheck } from "lucide-react";
import type { FinancialStatementIntelligence } from "@/types";

interface FinancialStatementIntelligencePanelProps {
  intelligence: FinancialStatementIntelligence;
}

const sectionLabels: Record<string, string> = {
  revenue: "Revenue",
  profitability: "Profitability",
  liquidity: "Liquidity",
  leverage: "Leverage",
  cash_flow: "Cash Flow",
  earnings_quality: "Earnings Quality",
};

export function FinancialStatementIntelligenceSkeleton() {
  return (
    <section className="premium-card p-6" aria-label="Loading financial statement intelligence">
      <div className="skeleton-card h-5 w-72" />
      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    </section>
  );
}

export function FinancialStatementIntelligencePanel({ intelligence }: FinancialStatementIntelligencePanelProps) {
  const sections = Object.entries(intelligence.sections);

  return (
    <section id="financial-intelligence" className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <FileBarChart size={15} /> Statement Intelligence
          </p>
          <h2 className="mt-2 text-2xl font-semibold">Financial Statement Intelligence</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Translates persisted income statement, balance sheet, and cash flow rows into explainable evidence. No forecasts, recommendations, or AI opinions are used.
          </p>
        </div>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
          Confidence: {intelligence.evidence.confidence}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {sections.map(([key, section]) => (
          <article key={key} className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-semibold">{sectionLabels[key] ?? key}</h3>
              <span className="rounded-full border border-white/10 px-2 py-1 text-xs text-muted-foreground">
                {section.confidence}
              </span>
            </div>
            <p className="mt-3 text-sm font-medium text-foreground">{section.headline}</p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{section.explanation}</p>
            <div className="mt-3 rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Evidence</p>
              <ul className="mt-2 space-y-1 text-xs leading-5 text-muted-foreground">
                {section.evidence.slice(0, 3).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <p className="mt-3 text-xs leading-5 text-muted-foreground">
              <span className="font-semibold text-foreground">Why it matters: </span>
              {section.why_it_matters}
            </p>
          </article>
        ))}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_0.9fr]">
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <ShieldCheck size={16} className="text-emerald-300" /> Evidence and provenance
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <Fact label="Source" value={intelligence.transparency.source} />
            <Fact label="Reporting period" value={intelligence.transparency.reporting_period} />
            <Fact label="Verification" value={intelligence.transparency.verification_status} />
            <Fact label="Last updated" value={intelligence.transparency.last_updated ?? "Unavailable"} />
          </div>
          {intelligence.evidence.missing_data.length > 0 ? (
            <p className="mt-3 text-xs leading-5 text-amber-200">
              Missing: {intelligence.evidence.missing_data.join(", ")}
            </p>
          ) : null}
        </div>

        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <BookOpen size={16} className="text-primary" /> Learn Next
          </div>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            {intelligence.educational_layer.explain_like_im_18}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {intelligence.educational_layer.learn_next.map((topic) => (
              <span key={topic} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-xs text-primary">
                {topic}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/50 p-3 text-xs leading-5 text-muted-foreground">
        <ClipboardCheck className="mr-2 inline text-primary" size={14} />
        {intelligence.transparency.methodology} {intelligence.transparency.not_advice}
      </div>
    </section>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">{label}</p>
      <p className="mt-1 break-words text-sm font-medium">{value}</p>
    </div>
  );
}
