"use client";

import Link from "next/link";
import { useMemo } from "react";
import { AxiosError } from "axios";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Building2, FileText, GitCompare, Newspaper, Star, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/layout";
import { AssetAssessmentPanel } from "@/features/assets/asset-assessment-panel";
import { CardSkeleton } from "@/components/skeleton";
import { companyService } from "@/services/api";
import {
  formatDisplayDate,
  mapAssets,
  mapCompany,
  mapCompanyProfile,
  mapCompanyProfileVerification,
  mapNewsArticles,
} from "@/lib/mappers/data-mappers";
import {
  DEMO_ASSETS,
  DEMO_COMPANIES,
  DEMO_COMPANY_PROFILES,
  DEMO_NEWS,
  getExplainLikeIm18,
  resolveCompanyTicker,
} from "@/utils/demo-content";
import type { ResearchStatus } from "@/types";

const quickActions = [
  { label: "View Assets", href: "#related-assets", icon: TrendingUp, disabled: false },
  { label: "Compare", href: "/compare", icon: GitCompare, disabled: false },
  { label: "Latest News", href: "#latest-news", icon: Newspaper, disabled: false },
  { label: "Assessment", href: "#assessment", icon: Star, disabled: false },
  { label: "Financial Statements", href: "#", icon: FileText, disabled: true },
  { label: "Watchlist", href: "#", icon: Building2, disabled: true },
];

const statusLabels: Record<ResearchStatus, string> = {
  development: "Development",
  verified: "Verified",
  needs_review: "Needs Review",
  unavailable: "Unavailable",
};

export default function CompanyDetailPage() {
  const params = useParams<{ ticker: string }>();
  const routeTicker = params?.ticker ?? "";
  const ticker = resolveCompanyTicker(routeTicker);

  const companyQuery = useQuery({
    queryKey: ["company-detail", ticker],
    queryFn: () => companyService.getCompanyByTicker(ticker),
    retry: 1,
    enabled: Boolean(ticker),
  });

  const profileQuery = useQuery({
    queryKey: ["company-profile", ticker],
    queryFn: () => companyService.getCompanyProfile(ticker),
    retry: 1,
    enabled: Boolean(ticker),
  });

  const assessmentQuery = useQuery({
    queryKey: ["company-assessment", ticker],
    queryFn: () => companyService.getCompanyAssessment(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 5,
  });

  const backendDetail = companyQuery.data?.data;
  const backendCompany = mapCompany(backendDetail?.company);
  const fallbackCompany = DEMO_COMPANIES.find((company) => company.ticker === ticker) ?? null;
  const company = backendCompany ?? fallbackCompany;
  const relatedAssets = useMemo(() => {
    const backendAssets = mapAssets(backendDetail?.related_assets);
    if (!companyQuery.isError) return backendAssets;
    return DEMO_ASSETS.filter((asset) => asset.ticker === ticker);
  }, [backendDetail, companyQuery.isError, ticker]);

  const profileData = profileQuery.data?.data;
  const backendProfile = mapCompanyProfile(profileData?.profile);
  const fallbackProfile = DEMO_COMPANY_PROFILES[ticker] ?? null;
  const profile = backendProfile ?? fallbackProfile;
  const profileDataOrigin = backendProfile?.id ? "Persisted Backend" : profile ? "Development Preview" : "Unavailable";
  const usingProfilePreview = profileDataOrigin === "Development Preview";
  const profileLoadError = profileQuery.isError && !backendProfile;
  const verification = profileData?.verification && backendProfile
    ? mapCompanyProfileVerification(profileData.verification)
    : mapCompanyProfileVerification(profile);

  const news = useMemo(() => {
    const backendNews = mapNewsArticles(backendDetail?.latest_news);
    if (!companyQuery.isError) return backendNews;
    return DEMO_NEWS.filter((article) => article.asset_tickers.includes(ticker));
  }, [backendDetail, companyQuery.isError, ticker]);

  const primaryAsset = relatedAssets[0] ?? DEMO_ASSETS.find((asset) => asset.ticker === ticker) ?? null;
  const education = primaryAsset ? getExplainLikeIm18(primaryAsset) : [];
  const isNotFound = companyQuery.isError && (companyQuery.error as AxiosError)?.response?.status === 404 && !fallbackCompany;
  const usingFallback = companyQuery.isError && Boolean(fallbackCompany);

  return (
    <AppShell>
      <div className="space-y-6">
        {usingFallback ? (
          <div className="warning-panel">
            Backend unavailable. Showing development preview data.
          </div>
        ) : null}

        {companyQuery.isLoading ? (
          <div className="h-72 animate-pulse premium-card" />
        ) : isNotFound || !company ? (
          <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center">
            <h1 className="text-2xl font-semibold">Company not found</h1>
            <p className="mt-2 text-sm text-muted-foreground">We could not find a company matching {ticker || "that ticker"}.</p>
            <div className="mt-5 flex justify-center gap-3">
              <Link href="/assets" className="rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground">Browse assets</Link>
              <Link href="/dashboard" className="rounded-lg border border-border px-4 py-3 text-sm font-medium">Back to dashboard</Link>
            </div>
          </div>
        ) : (
          <>
            <section className="premium-card p-6">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Company / {company.exchange}</p>
                  <h1 className="mt-2 text-4xl font-bold">{company.name}</h1>
                  <p className="mt-3 max-w-3xl text-muted-foreground">{company.description}</p>
                </div>
                <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
                  <p className="text-2xl font-semibold">{company.ticker}</p>
                  <p className="mt-1 text-primary/80">{company.market ?? company.exchange}</p>
                </div>
              </div>
              <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <QuickFact label="Sector" value={company.sector ?? "Unavailable"} />
                <QuickFact label="Industry" value={company.industry ?? "Unavailable"} />
                <QuickFact label="Country" value={company.country ?? "Unavailable"} />
                <QuickFact label="Status" value={company.status} />
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-6">
                <div className="premium-card p-6">
                  <h2 className="text-xl font-semibold">Company Profile</h2>
                  <p className="mt-3 text-sm text-muted-foreground">{company.description}</p>
                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    <QuickFact label="Legal name" value={company.legal_name ?? company.name} />
                    <QuickFact label="Headquarters" value={company.headquarters ?? "Unavailable"} />
                    <QuickFact label="Founded" value={company.founded_year ? String(company.founded_year) : "Unavailable"} />
                    <QuickFact label="Website" value={company.website ?? "Unavailable"} href={company.website ?? undefined} />
                  </div>
                </div>

                <div className="premium-card p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-xl font-semibold">Company Intelligence</h2>
                      <p className="mt-1 text-sm text-muted-foreground">Structured facts with source transparency.</p>
                    </div>
                    <ResearchStatusBadge status={verification.research_status} />
                  </div>
                  {usingProfilePreview ? (
                    <div className="mt-4 rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-sm text-blue-200">
                      Development Preview: this company profile is fixture-backed until a persisted backend profile is seeded or verified.
                    </div>
                  ) : null}
                  {profileLoadError ? (
                    <div className="mt-4 rounded-lg border border-amber-400/25 bg-amber-500/10 p-3 text-sm text-amber-100">
                      Company profile data could not be reached. Preview data is shown only when available.
                    </div>
                  ) : null}
                  {profileQuery.isLoading ? (
                    <div className="mt-4 h-40 animate-pulse rounded-lg border border-white/10 bg-background-primary/70" />
                  ) : profile ? (
                    <div className="mt-4 space-y-4">
                      <p className="text-sm text-muted-foreground">{profile.business_summary ?? "No business summary is available yet."}</p>
                      <div className="grid gap-3 sm:grid-cols-2">
                        <QuickFact label="Primary business" value={profile.primary_business ?? "Unavailable"} />
                        <QuickFact label="Industry" value={profile.industry ?? "Unavailable"} />
                        <QuickFact label="Headquarters" value={profile.headquarters ?? "Unavailable"} />
                        <QuickFact label="Founded" value={profile.founded_year ? String(profile.founded_year) : "Unavailable"} />
                        <QuickFact label="Website" value={profile.website ?? "Unavailable"} href={profile.website ?? undefined} />
                        <QuickFact label="Source" value={verification.source_name ?? "Unavailable"} href={verification.source_url ?? undefined} />
                      </div>
                      <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                        <p className="text-sm text-muted-foreground">Products & Services</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {profile.products_services.length > 0 ? profile.products_services.map((item) => (
                            <span key={item} className="rounded-lg border border-border px-3 py-1 text-sm">{item}</span>
                          )) : <span className="text-sm text-muted-foreground">Unavailable</span>}
                        </div>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-2">
                        <QuickFact label="Research status" value={statusLabels[verification.research_status]} />
                        <QuickFact label="Last verified" value={formatDisplayDate(verification.last_verified)} />
                        <QuickFact label="Data origin" value={profileDataOrigin} />
                      </div>
                    </div>
                  ) : (
                    <p className="mt-4 text-sm text-muted-foreground">Company intelligence profile is unavailable right now. Please try again once backend profile data is reachable.</p>
                  )}
                </div>

                <div id="related-assets" className="premium-card p-6">
                  <h2 className="text-xl font-semibold">Related Investments</h2>
                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    {relatedAssets.length > 0 ? relatedAssets.map((asset) => (
                      <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                        <p className="text-lg font-semibold">{asset.ticker}</p>
                        <p className="mt-1 text-sm text-muted-foreground">{asset.company_name}</p>
                        <p className="mt-3 text-xs uppercase text-muted-foreground">{asset.asset_type} / {asset.exchange}</p>
                      </Link>
                    )) : <p className="text-sm text-muted-foreground">No related listed assets are connected yet.</p>}
                  </div>
                </div>

                <div id="assessment" className="space-y-4">
                  {assessmentQuery.isLoading ? (
                    <CardSkeleton />
                  ) : assessmentQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Company assessment is not available yet.
                    </div>
                  ) : assessmentQuery.data?.data ? (
                    <AssetAssessmentPanel assessment={assessmentQuery.data.data} />
                  ) : (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Company assessment is not available yet.
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-6">
                <div className="premium-card p-6">
                  <h2 className="text-xl font-semibold">Quick Facts</h2>
                  <div className="mt-4 space-y-3">
                    <QuickFact label="Exchange" value={company.exchange} />
                    <QuickFact label="Currency" value={company.currency ?? "Unavailable"} />
                    <QuickFact label="Market" value={company.market ?? company.exchange} />
                    <QuickFact label="Employees" value={company.employee_count ? String(company.employee_count) : "Unavailable"} />
                  </div>
                </div>

                <div className="premium-card p-6">
                  <h2 className="text-xl font-semibold">Quick Actions</h2>
                  <div className="mt-4 grid gap-2">
                    {quickActions.map((action) => {
                      const Icon = action.icon;
                      const href = action.label === "Compare" && primaryAsset ? `/compare?left=${primaryAsset.ticker}` : action.href;
                      return action.disabled ? (
                        <div key={action.label} className="flex items-center justify-between rounded-lg border border-white/10 bg-background-primary/70 p-3 text-sm text-muted-foreground">
                          <span className="flex items-center gap-2"><Icon size={16} />{action.label}</span>
                          <span>Coming Soon</span>
                        </div>
                      ) : (
                        <Link key={action.label} href={href} className="flex items-center gap-2 rounded-lg border border-white/10 bg-background-primary/70 p-3 text-sm font-medium transition hover:border-primary/60">
                          <Icon size={16} />{action.label}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="premium-card p-6">
                <h2 className="text-xl font-semibold">Explain Like I am 18</h2>
                <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
                  {education.length > 0 ? education.map((line) => <li key={line}>{line}</li>) : <li>Company education content will appear once a related investment is connected.</li>}
                </ul>
              </div>

              <div id="latest-news" className="premium-card p-6">
                <h2 className="text-xl font-semibold">Latest News</h2>
                <div className="mt-4 space-y-3">
                  {news.length > 0 ? news.map((article) => (
                    <article key={article.id} className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                      <p className="text-xs text-muted-foreground">{article.source} / {formatDisplayDate(article.published_at)}</p>
                      <h3 className="mt-2 text-base font-semibold">{article.title}</h3>
                      <p className="mt-2 text-sm text-muted-foreground">{article.summary}</p>
                    </article>
                  )) : <p className="text-sm text-muted-foreground">No company news is linked yet.</p>}
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

function QuickFact({ label, value, href }: { label: string; value: string; href?: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      {href ? (
        <a href={href} target="_blank" rel="noreferrer" className="mt-1 block truncate font-semibold text-primary">
          {value}
        </a>
      ) : (
        <p className="mt-1 break-words font-semibold capitalize">{value}</p>
      )}
    </div>
  );
}

function ResearchStatusBadge({ status }: { status: ResearchStatus }) {
  const style = {
    development: "border-blue-500/30 bg-blue-500/10 text-blue-300",
    verified: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    needs_review: "border-amber-400/25 bg-amber-500/10 text-amber-200",
    unavailable: "border-border bg-background-secondary text-muted-foreground",
  }[status];

  return (
    <span className={`rounded-lg border px-3 py-1 text-sm font-medium ${style}`}>
      {statusLabels[status]}
    </span>
  );
}
