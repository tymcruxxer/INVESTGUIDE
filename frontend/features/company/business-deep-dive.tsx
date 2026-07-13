import Link from "next/link";
import {
  AlertTriangle,
  BadgeCheck,
  BookOpen,
  Building2,
  Globe2,
  Network,
  Route,
  TrendingUp,
} from "lucide-react";
import type { BusinessDriver, BusinessIntelligence } from "@/types";

interface BusinessDeepDiveProps {
  intelligence: BusinessIntelligence;
}

export function BusinessDeepDiveSkeleton() {
  return (
    <section className="premium-card p-6" aria-label="Loading business intelligence">
      <div className="skeleton-card h-5 w-56" />
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
        <div className="skeleton-card" />
      </div>
    </section>
  );
}

export function BusinessDeepDive({ intelligence }: BusinessDeepDiveProps) {
  const competitors = [
    ...intelligence.competitors.direct_competitors,
    ...intelligence.competitors.similar_businesses,
    ...intelligence.competitors.related_businesses,
  ].slice(0, 6);

  return (
    <section id="business-deep-dive" className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <Building2 size={15} /> Business intelligence
          </p>
          <h2 className="mt-2 text-2xl font-semibold">Company Deep Dive</h2>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            {intelligence.business_summary.summary}
          </p>
        </div>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
          Deterministic
        </span>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <InfoCard
          icon={Route}
          title="Business model"
          body={intelligence.business_model.how_it_makes_money}
          footer={intelligence.business_model.why_investguide_thinks_this[0]}
        />
        <InfoCard
          icon={BadgeCheck}
          title="Competitive position"
          body={`${intelligence.competitive_position.label} (${intelligence.competitive_position.confidence} confidence)`}
          footer={intelligence.competitive_position.reasons[0]}
        />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <DriverPanel
          icon={TrendingUp}
          title="Revenue drivers"
          drivers={intelligence.revenue_drivers}
        />
        <DriverPanel
          icon={AlertTriangle}
          title="Operational risks"
          drivers={intelligence.operational_risks}
        />
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Globe2 size={16} className="text-primary" /> Geographic exposure
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            {intelligence.geographic_exposure.summary}
          </p>
          <div className="mt-3 grid gap-2 text-sm">
            <span className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
              Country: {intelligence.geographic_exposure.primary_country}
            </span>
            <span className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2">
              HQ: {intelligence.geographic_exposure.headquarters}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Network size={16} className="text-blue-300" /> Industry intelligence
          </div>
          <h3 className="mt-3 text-lg font-semibold">
            {intelligence.industry_intelligence.industry}
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            {intelligence.industry_intelligence.description}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs">
              {intelligence.industry_intelligence.cycle_profile}
            </span>
            <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs">
              {intelligence.industry_intelligence.economic_sensitivity}
            </span>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Building2 size={16} className="text-emerald-300" /> Competitors
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {competitors.length > 0 ? (
              competitors.map((company) => (
                <Link
                  key={`${company.relationship_type}-${company.ticker}`}
                  href={company.href}
                  className="rounded-lg border border-white/10 bg-white/[0.03] p-3 transition hover:border-primary/50 hover:bg-primary/10"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold">{company.ticker}</span>
                    <span className="text-xs text-muted-foreground">
                      {company.relationship_type}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {company.reasons[0]}
                  </p>
                </Link>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No competitors are available from the current company catalog.
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/70 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <BookOpen size={16} className="text-purple-300" /> Learn next
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          {intelligence.educational_notes.map((note) => (
            <div key={note.title} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <p className="text-sm font-semibold">{note.title}</p>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">{note.note}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/50 p-3 text-xs leading-5 text-muted-foreground">
        <span className="font-semibold text-foreground">Transparency: </span>
        {intelligence.transparency.methodology} {intelligence.transparency.data_boundary}{" "}
        {intelligence.transparency.not_advice}
      </div>
    </section>
  );
}

function InfoCard({
  icon: Icon,
  title,
  body,
  footer,
}: {
  icon: typeof Building2;
  title: string;
  body: string;
  footer?: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Icon size={16} className="text-primary" /> {title}
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{body}</p>
      {footer ? <p className="mt-3 text-xs text-muted-foreground">Why: {footer}</p> : null}
    </div>
  );
}

function DriverPanel({
  icon: Icon,
  title,
  drivers,
}: {
  icon: typeof TrendingUp;
  title: string;
  drivers: BusinessDriver[];
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Icon size={16} className="text-emerald-300" /> {title}
      </div>
      <div className="mt-3 space-y-3">
        {drivers.map((driver) => (
          <div key={driver.name} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
            <p className="text-sm font-semibold">{driver.name}</p>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">
              {driver.why_it_matters}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
