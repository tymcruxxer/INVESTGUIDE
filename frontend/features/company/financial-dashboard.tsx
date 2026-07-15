import {
  Activity,
  BadgeDollarSign,
  BarChart3,
  BookOpen,
  Landmark,
  LineChart,
  Scale,
  ShieldCheck,
  TrendingUp,
  WalletCards,
} from "lucide-react";
import type { FinancialIntelligence, FinancialRatio, FinancialTrend } from "@/types";

interface FinancialDashboardProps {
  intelligence: FinancialIntelligence;
}

export function FinancialDashboardSkeleton() {
  return (
    <section className="premium-card p-6" aria-label="Loading financial intelligence">
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

export function FinancialDashboard({ intelligence }: FinancialDashboardProps) {
  return (
    <section id="financial-health" className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <BadgeDollarSign size={15} /> Financial intelligence
          </p>
          <h2 className="mt-2 text-2xl font-semibold">Financial Health</h2>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            {intelligence.educational_summary}
          </p>
        </div>
        <span className="rounded-full border border-blue-400/30 bg-blue-400/10 px-3 py-1 text-xs font-medium text-blue-200">
          {intelligence.transparency.development_data ? "Development Data" : "Persisted Data"}
        </span>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <FinancialHealthCard intelligence={intelligence} />
        <RevenuePanel intelligence={intelligence} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <ProfitabilityPanel intelligence={intelligence} />
        <CashFlowPanel intelligence={intelligence} />
        <BalanceSheetPanel intelligence={intelligence} />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <FinancialRatioTable ratios={intelligence.ratios} />
        <TrendChart trends={intelligence.trend_analysis} />
      </div>

      <div className="mt-4">
        <FinancialEducationPanel intelligence={intelligence} />
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/50 p-3 text-xs leading-5 text-muted-foreground">
        <span className="font-semibold text-foreground">Transparency: </span>
        {intelligence.transparency.methodology} Sources:{" "}
        {intelligence.transparency.data_sources.join(", ")}. Available periods:{" "}
        {intelligence.transparency.available_periods.join(", ") || "Unavailable"}.{" "}
        {intelligence.transparency.not_advice}
      </div>
    </section>
  );
}

export function FinancialHealthCard({ intelligence }: FinancialDashboardProps) {
  const health = intelligence.financial_health;
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <ShieldCheck size={16} className="text-emerald-300" /> Health assessment
        </div>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">
          {health.label}
        </span>
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{health.why}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <MiniList title="Evidence" items={health.evidence} />
        <MiniList title="Watch" items={health.cautions} />
      </div>
      {health.missing_data.length > 0 ? (
        <p className="mt-3 text-xs text-amber-200">
          Missing: {health.missing_data.join(", ")}
        </p>
      ) : null}
    </div>
  );
}

export function RevenuePanel({ intelligence }: FinancialDashboardProps) {
  return (
    <Panel
      icon={TrendingUp}
      title="Revenue"
      value={formatMoney(intelligence.revenue_analysis.current_revenue)}
      label={intelligence.revenue_analysis.trend}
      body={intelligence.revenue_analysis.explanation}
      footer={intelligence.revenue_quality.educational_explanation}
    />
  );
}

export function ProfitabilityPanel({ intelligence }: FinancialDashboardProps) {
  return (
    <Panel
      icon={BarChart3}
      title="Profitability"
      value={formatPercent(intelligence.profitability_analysis.net_margin.value)}
      label={intelligence.profitability_analysis.net_profit_trend.direction}
      body={intelligence.profitability_analysis.explanation}
      footer={intelligence.profitability_analysis.net_margin.educational_explanation}
    />
  );
}

export function CashFlowPanel({ intelligence }: FinancialDashboardProps) {
  return (
    <Panel
      icon={WalletCards}
      title="Cash Flow"
      value={formatMoney(intelligence.cash_flow_analysis.operating_cash_flow)}
      label={intelligence.cash_flow_analysis.trend.direction}
      body={intelligence.cash_flow_analysis.explanation}
      footer="Cash flow matters because the business pays bills, reinvests, and funds dividends with cash."
    />
  );
}

export function BalanceSheetPanel({ intelligence }: FinancialDashboardProps) {
  return (
    <Panel
      icon={Landmark}
      title="Balance Sheet"
      value={formatMoney(intelligence.balance_sheet_intelligence.assets)}
      label={intelligence.balance_sheet_intelligence.liquidity}
      body={intelligence.balance_sheet_intelligence.financial_flexibility}
      footer={`Equity: ${formatMoney(intelligence.balance_sheet_intelligence.equity)}. Debt: ${intelligence.balance_sheet_intelligence.debt}`}
    />
  );
}

export function FinancialRatioTable({ ratios }: { ratios: FinancialRatio[] }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Scale size={16} className="text-primary" /> Financial Ratios
      </div>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="text-xs uppercase text-muted-foreground">
            <tr>
              <th className="py-2 pr-4">Ratio</th>
              <th className="py-2 pr-4">Value</th>
              <th className="py-2 pr-4">Interpretation</th>
              <th className="py-2">Why it matters</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {ratios.map((ratio) => (
              <tr key={ratio.name}>
                <td className="py-3 pr-4 font-medium">{ratio.name}</td>
                <td className="py-3 pr-4 text-muted-foreground">{formatRatio(ratio)}</td>
                <td className="py-3 pr-4 text-muted-foreground">{ratio.interpretation}</td>
                <td className="py-3 text-muted-foreground">{ratio.why_it_matters}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function TrendChart({ trends }: { trends: FinancialTrend[] }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <LineChart size={16} className="text-blue-300" /> Trend Analysis
      </div>
      <div className="mt-3 space-y-3">
        {trends.map((trend) => (
          <div key={trend.metric} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold">{trend.metric}</p>
              <span className="rounded-full border border-white/10 px-2 py-1 text-xs text-muted-foreground">
                {trend.direction}
              </span>
            </div>
            <p className="mt-2 text-xs leading-5 text-muted-foreground">{trend.explanation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function FinancialEducationPanel({ intelligence }: FinancialDashboardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <BookOpen size={16} className="text-purple-300" /> Educational Notes
      </div>
      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
          <p className="text-sm font-semibold">Explain Like I am 18</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {intelligence.explain_like_im_18}
          </p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
          <p className="text-sm font-semibold">Learn Next</p>
          <ul className="mt-2 space-y-2 text-sm text-muted-foreground">
            <li>Revenue quality</li>
            <li>Profit margins</li>
            <li>Cash conversion</li>
            <li>Debt and liquidity</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function Panel({
  icon: Icon,
  title,
  value,
  label,
  body,
  footer,
}: {
  icon: typeof Activity;
  title: string;
  value: string;
  label: string;
  body: string;
  footer: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Icon size={16} className="text-primary" /> {title}
      </div>
      <p className="mt-3 text-2xl font-semibold">{value}</p>
      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-muted-foreground">{label}</p>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{body}</p>
      <p className="mt-3 text-xs leading-5 text-muted-foreground">Why: {footer}</p>
    </div>
  );
}

function MiniList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{title}</p>
      <ul className="mt-2 space-y-1 text-xs leading-5 text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function formatMoney(value: number | null): string {
  if (value === null) return "Unavailable";
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatPercent(value: number | null): string {
  if (value === null) return "Unavailable";
  return `${(value * 100).toFixed(1)}%`;
}

function formatRatio(ratio: FinancialRatio): string {
  if (ratio.value === null) return "Unavailable";
  if (ratio.name.includes("Margin") || ratio.name.includes("Return")) {
    return formatPercent(ratio.value);
  }
  return ratio.value.toFixed(2);
}
