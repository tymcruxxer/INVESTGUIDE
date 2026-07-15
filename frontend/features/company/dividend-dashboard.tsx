import {
  AlertTriangle,
  BadgeDollarSign,
  BookOpen,
  CalendarDays,
  Database,
  Percent,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import type { DividendIntelligence } from "@/types";

interface DividendDashboardProps {
  intelligence: DividendIntelligence;
}

export function DividendDashboardSkeleton() {
  return (
    <section className="premium-card p-6" aria-label="Loading dividend intelligence">
      <div className="skeleton-card h-5 w-64" />
      <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    </section>
  );
}

export function DividendDashboard({ intelligence }: DividendDashboardProps) {
  const transparency = intelligence.data_transparency;
  return (
    <section id="dividend-intelligence" className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <BadgeDollarSign size={15} /> Dividend intelligence
          </p>
          <h2 className="mt-2 text-2xl font-semibold">Dividend History & Coverage</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            {intelligence.educational_summary}
          </p>
        </div>
        <span className="rounded-full border border-blue-400/30 bg-blue-400/10 px-3 py-1 text-xs font-medium text-blue-200">
          {transparency.development_data ? "Development Preview" : "Persisted Backend"}
        </span>
      </div>

      {transparency.development_data ? (
        <div className="mt-4 rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-sm text-blue-100">
          Development Preview: these dividend values are sample data for product testing. They are not verified ZSE or VFEX dividend records.
        </div>
      ) : null}

      <div className="mt-5 grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={ShieldCheck}
          title="Dividend status"
          value={intelligence.dividend_status.label}
          body={intelligence.dividend_status.explanation}
        />
        <MetricCard
          icon={Percent}
          title="Dividend yield"
          value={formatPercent(intelligence.dividend_yield.value)}
          body={intelligence.dividend_yield.interpretation}
        />
        <MetricCard
          icon={TrendingUp}
          title="Growth"
          value={intelligence.dividend_growth.trend_label}
          body={intelligence.dividend_growth.explanation}
        />
        <MetricCard
          icon={Database}
          title="Sustainability"
          value={intelligence.sustainability_assessment.label}
          body={intelligence.sustainability_assessment.methodology}
        />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <DividendHistoryTable intelligence={intelligence} />
        <DividendCoveragePanel intelligence={intelligence} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <DividendRiskPanel intelligence={intelligence} />
        <DividendEducationPanel intelligence={intelligence} />
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/50 p-3 text-xs leading-5 text-muted-foreground">
        <span className="font-semibold text-foreground">Transparency: </span>
        {transparency.methodology} Sources: {transparency.data_sources.join(", ")}. Available periods: {transparency.available_periods.join(", ") || "Unavailable"}. {transparency.not_advice}
      </div>
    </section>
  );
}

function DividendHistoryTable({ intelligence }: DividendDashboardProps) {
  const periods = intelligence.dividend_history.periods;
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <CalendarDays size={16} className="text-primary" /> Dividend history
      </div>
      {periods.length === 0 ? (
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          No verified dividend records are available for this company yet. Missing platform data is not proof that the company has never paid dividends.
        </p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-2 pr-4">Year</th>
                <th className="py-2 pr-4">Type</th>
                <th className="py-2 pr-4">DPS</th>
                <th className="py-2 pr-4">Payment</th>
                <th className="py-2">Currency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {periods.map((period, index) => (
                <tr key={`${period.fiscal_year}-${period.dividend_type}-${index}`}>
                  <td className="py-3 pr-4 font-medium">{period.fiscal_year ?? "Unavailable"}</td>
                  <td className="py-3 pr-4 text-muted-foreground">{period.dividend_type ?? "Other"}</td>
                  <td className="py-3 pr-4 text-muted-foreground">{formatAmount(period.dividend_per_share)}</td>
                  <td className="py-3 pr-4 text-muted-foreground">{formatDate(period.payment_date)}</td>
                  <td className="py-3 text-muted-foreground">{period.currency ?? "Unavailable"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="mt-3 text-xs leading-5 text-muted-foreground">{intelligence.dividend_history.methodology}</p>
    </div>
  );
}

function DividendCoveragePanel({ intelligence }: DividendDashboardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <ShieldCheck size={16} className="text-emerald-300" /> Coverage
      </div>
      <div className="mt-3 space-y-3">
        <CoverageItem title="Payout ratio" metric={intelligence.payout_ratio} />
        <CoverageItem title="Cash payout ratio" metric={intelligence.cash_payout_ratio} />
      </div>
      <p className="mt-3 text-xs leading-5 text-muted-foreground">{intelligence.dividend_coverage.summary}</p>
    </div>
  );
}

function DividendRiskPanel({ intelligence }: DividendDashboardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <AlertTriangle size={16} className="text-amber-300" /> Things to watch
      </div>
      <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
        {intelligence.key_risks.length > 0 ? intelligence.key_risks.map((risk) => (
          <li key={risk.risk} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
            <span className="font-medium text-foreground">{risk.risk}: </span>{risk.why_it_matters}
          </li>
        )) : <li>No deterministic dividend risk factors were identified from available records.</li>}
      </ul>
    </div>
  );
}

function DividendEducationPanel({ intelligence }: DividendDashboardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <BookOpen size={16} className="text-purple-300" /> Learn dividend concepts
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{intelligence.explain_like_im_18}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {intelligence.suggested_learning_topics.map((topic) => (
          <span key={topic} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-1 text-sm text-primary">
            {topic}
          </span>
        ))}
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, title, value, body }: { icon: typeof ShieldCheck; title: string; value: string; body: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold"><Icon size={16} className="text-primary" /> {title}</div>
      <p className="mt-3 text-xl font-semibold">{value}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{body}</p>
    </div>
  );
}

function CoverageItem({ title, metric }: { title: string; metric: { value: number | null; status: string; interpretation: string } }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-medium">{title}</p>
        <span className="text-sm text-muted-foreground">{formatPercent(metric.value)}</span>
      </div>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{metric.interpretation}</p>
    </div>
  );
}

function formatPercent(value: number | null): string {
  if (value === null) return "Unavailable";
  return `${(value * 100).toFixed(1)}%`;
}

function formatAmount(value: number | null): string {
  if (value === null) return "Unavailable";
  return value.toFixed(4);
}

function formatDate(value?: string | null): string {
  if (!value) return "Unavailable";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}
