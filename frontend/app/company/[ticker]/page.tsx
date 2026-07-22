"use client";

import Link from "next/link";
import { useMemo } from "react";
import { AxiosError } from "axios";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Building2, FileText, GitCompare, Globe2, Newspaper, Star, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/layout";
import { AssetAssessmentPanel } from "@/features/assets/asset-assessment-panel";
import { ResearchPanel, ResearchPanelSkeleton, ResearchUnavailable } from "@/features/assets/research-panel";
import { BusinessDeepDive, BusinessDeepDiveSkeleton } from "@/features/company/business-deep-dive";
import { FinancialDashboard, FinancialDashboardSkeleton } from "@/features/company/financial-dashboard";
import { FinancialStatementIntelligencePanel, FinancialStatementIntelligenceSkeleton } from "@/features/company/financial-statement-intelligence";
import { DividendDashboard, DividendDashboardSkeleton } from "@/features/company/dividend-dashboard";
import { CardSkeleton } from "@/components/skeleton";
import { companyService, macroService, sectorService } from "@/services/api";
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
  { label: "Financial Statements", href: "#financial-statement-intelligence", icon: FileText, disabled: false },
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

  const researchQuery = useQuery({
    queryKey: ["company-research", ticker],
    queryFn: () => companyService.getCompanyResearch(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 5,
  });

  const businessQuery = useQuery({
    queryKey: ["company-business", ticker],
    queryFn: () => companyService.getCompanyBusiness(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
  });

  const financialQuery = useQuery({
    queryKey: ["company-financials", ticker],
    queryFn: () => companyService.getCompanyFinancials(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
  });

  const statementIntelligenceQuery = useQuery({
    queryKey: ["company-financial-statement-intelligence", ticker],
    queryFn: () => companyService.getCompanyFinancialStatementIntelligence(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
  });

  const dividendQuery = useQuery({
    queryKey: ["company-dividend-intelligence", ticker],
    queryFn: () => companyService.getCompanyDividendIntelligence(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
  });

  const relatedQuery = useQuery({
    queryKey: ["company-related", ticker],
    queryFn: () => companyService.getCompanyRelated(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
  });

  const macroImpactQuery = useQuery({
    queryKey: ["company-macro-impact", ticker],
    queryFn: () => macroService.getCompanyImpact(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 10,
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

  const sectorSlug = company?.sector ? company.sector.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") : "";

  const sectorResearchQuery = useQuery({
    queryKey: ["company-sector-intelligence", sectorSlug],
    queryFn: () => sectorService.getSectorResearch(sectorSlug),
    retry: 1,
    enabled: Boolean(sectorSlug),
    staleTime: 1000 * 60 * 10,
  });
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
          <div className="skeleton-card h-72" />
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
                      <h2 id="company-intelligence" className="text-xl font-semibold">Company Intelligence</h2>
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
                    <div className="skeleton-card" />
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


                <div id="business-deep-dive" className="space-y-4">
                  {businessQuery.isLoading ? (
                    <BusinessDeepDiveSkeleton />
                  ) : businessQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Business Intelligence is unavailable right now. Company profile and assessment sections remain available below.
                    </div>
                  ) : businessQuery.data?.data ? (
                    <BusinessDeepDive intelligence={businessQuery.data.data} />
                  ) : null}
                </div>
                <div id="financial-statement-intelligence" className="space-y-4">
                  {statementIntelligenceQuery.isLoading ? (
                    <FinancialStatementIntelligenceSkeleton />
                  ) : statementIntelligenceQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Financial Statement Intelligence is temporarily unavailable. The existing Financial Health dashboard remains available below.
                    </div>
                  ) : statementIntelligenceQuery.data?.data?.intelligence ? (
                    <FinancialStatementIntelligencePanel intelligence={statementIntelligenceQuery.data.data.intelligence} />
                  ) : null}
                </div>

                <div id="financial-dashboard" className="space-y-4">
                  {financialQuery.isLoading ? (
                    <FinancialDashboardSkeleton />
                  ) : financialQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Financial Intelligence is temporarily unavailable. Business intelligence and assessment sections remain available.
                    </div>
                  ) : financialQuery.data?.data &&
                    financialQuery.data.data.income_statements.length +
                      financialQuery.data.data.balance_sheets.length +
                      financialQuery.data.data.cash_flow_statements.length ===
                      0 ? (
                    <div className="premium-card p-6">
                      <h2 className="text-xl font-semibold">
                        Financial statements are not available for this company yet.
                      </h2>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        InvestGuide needs at least one persisted income statement, balance sheet, or cash flow statement before it can complete financial analysis. Business intelligence, assessments, related assets, and research remain available on this page.
                      </p>
                    </div>
                  ) : financialQuery.data?.data?.intelligence ? (
                    <FinancialDashboard intelligence={financialQuery.data.data.intelligence} />
                  ) : null}
                </div>

                <div id="dividend-intelligence" className="space-y-4">
                  {dividendQuery.isLoading ? (
                    <DividendDashboardSkeleton />
                  ) : dividendQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Dividend Intelligence is temporarily unavailable. Financial and business intelligence sections remain available.
                    </div>
                  ) : dividendQuery.data?.data?.intelligence && dividendQuery.data.data.dividends.length > 0 ? (
                    <DividendDashboard intelligence={dividendQuery.data.data.intelligence} />
                  ) : dividendQuery.data?.data ? (
                    <div className="premium-card p-6">
                      <h2 className="text-xl font-semibold">No verified dividend records are available for this company yet.</h2>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        The company may still have dividend history outside InvestGuide. Missing platform data is not proof that no dividend was paid. Business intelligence, financial health, assessments, and related research remain available.
                      </p>
                    </div>
                  ) : null}
                </div>
                <div id="macro-factors" className="space-y-4">
                  {macroImpactQuery.isLoading ? (
                    <div className="skeleton-card h-64" />
                  ) : macroImpactQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Macro Factors are temporarily unavailable. Company intelligence and financial sections remain available.
                    </div>
                  ) : macroImpactQuery.data?.data ? (
                    <MacroFactorsPanel impact={macroImpactQuery.data.data} />
                  ) : null}
                </div>

                <div id="sector-intelligence" className="space-y-4">
                  {sectorResearchQuery.isLoading ? (
                    <div className="skeleton-card h-64" />
                  ) : sectorResearchQuery.isError ? (
                    <div className="premium-card p-6 text-sm text-muted-foreground">
                      Sector Intelligence is temporarily unavailable. Macro Factors and company research remain available.
                    </div>
                  ) : sectorResearchQuery.data?.data ? (
                    <SectorIntelligencePanel research={sectorResearchQuery.data.data} />
                  ) : null}
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

                <div className="premium-card p-6">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h2 className="text-xl font-semibold">Related Research</h2>
                      <p className="mt-1 text-sm text-muted-foreground">Deterministic links that explain what to explore next.</p>
                    </div>
                    <span className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">Not advice</span>
                  </div>
                  {relatedQuery.isLoading ? (
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      <div className="skeleton-card" />
                      <div className="skeleton-card" />
                    </div>
                  ) : relatedQuery.data?.data ? (
                    <div className="mt-5 space-y-5">
                      <div>
                        <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">You may also want to research</h3>
                        <div className="mt-3 grid gap-3 sm:grid-cols-2">
                          {relatedQuery.data.data.related_companies.length > 0 ? relatedQuery.data.data.related_companies.map((item) => (
                            <Link key={item.ticker} href={item.href} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
                              <div className="flex items-center justify-between gap-3">
                                <p className="font-semibold">{item.ticker}</p>
                                <span className="text-xs text-muted-foreground">Score {item.relationship_score}</span>
                              </div>
                              <p className="mt-1 text-sm text-muted-foreground">{item.name}</p>
                              <p className="mt-3 text-xs text-muted-foreground">Related because: {item.reasons[0] ?? "It shares investable-market context."}</p>
                            </Link>
                          )) : <p className="text-sm text-muted-foreground">No related companies are available yet.</p>}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">Learn Next</h3>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {relatedQuery.data.data.educational_topics.map((topic) => (
                            <Link key={topic.topic} href={topic.path} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary transition hover:border-primary/70">
                              {topic.topic}
                            </Link>
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4 text-sm text-muted-foreground">
                        {relatedQuery.data.data.transparency.methodology}
                      </div>
                    </div>
                  ) : (
                    <p className="mt-4 text-sm text-muted-foreground">Related research is unavailable right now.</p>
                  )}
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

                <div className="space-y-4">
                  {researchQuery.isLoading ? (
                    <ResearchPanelSkeleton />
                  ) : researchQuery.isError ? (
                    <ResearchUnavailable subject="company" />
                  ) : researchQuery.data?.data ? (
                    <ResearchPanel research={researchQuery.data.data} title="Company AI Research" />
                  ) : null}
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









function MacroFactorsPanel({ impact }: { impact: { factors: Array<{ indicator_type: string; label: string; why_it_matters: string; relationship_chain: string[]; not_prediction: string }>; transparency: { methodology: string; not_advice: string; data_points_seen: number } } }) {
  const routeFor = (indicatorType: string) => ({
    inflation: "/macro/inflation",
    interest_rate: "/macro/interest-rates",
    exchange_rate: "/macro/exchange-rates",
    gdp: "/macro/gdp",
    commodity_price: "/macro/commodities",
  }[indicatorType] ?? "/macro/inflation");

  return (
    <div className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Globe2 className="text-primary" size={20} />
            <h2 className="text-xl font-semibold">Macro Factors</h2>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">How economic indicators typically connect to this company.</p>
        </div>
        <span className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">Deterministic</span>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {impact.factors.map((factor) => (
          <Link key={factor.indicator_type} href={routeFor(factor.indicator_type)} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:border-primary/60">
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold">{factor.label}</p>
              <span className="text-xs text-primary">Learn</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{factor.why_it_matters}</p>
            <p className="mt-3 text-xs text-muted-foreground">{factor.relationship_chain.slice(0, 4).join(" -> ")}</p>
          </Link>
        ))}
      </div>
      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/70 p-4 text-sm text-muted-foreground">
        {impact.transparency.methodology} {impact.transparency.not_advice}
      </div>
    </div>
  );
}




function SectorIntelligencePanel({ research }: { research: { sector: { name: string; slug: string; is_development_data: boolean }; overview: { what_it_is: string }; typical_risks: Array<{ label: string; why_it_matters: string }>; macro_relationships: Array<{ label: string; relationship: string; path: string }>; industries: Array<{ name: string; slug: string }>; companies: Array<{ ticker: string; name: string; href: string; reason: string }>; learn_next: Array<{ topic: string; path: string }>; transparency: { data_origin: string; not_advice: string } } }) {
  return (
    <div className="premium-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="text-primary" size={20} />
            <h2 className="text-xl font-semibold">Sector Intelligence</h2>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">How this company fits into its wider market sector.</p>
        </div>
        <Link href={`/sector/${research.sector.slug}`} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary transition hover:border-primary/70">
          View sector
        </Link>
      </div>
      {research.sector.is_development_data ? (
        <div className="mt-4 rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-sm text-blue-200">
          Development Preview: sector reference data is fixture-backed until verified taxonomy data is imported.
        </div>
      ) : null}
      <p className="mt-4 text-sm leading-6 text-muted-foreground">{research.overview.what_it_is}</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <p className="font-semibold">Macro relationships</p>
          <div className="mt-3 space-y-2">
            {research.macro_relationships.slice(0, 3).map((item) => (
              <Link key={item.label} href={item.path} className="block text-sm text-muted-foreground transition hover:text-primary">
                {item.label}: {item.relationship}
              </Link>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
          <p className="font-semibold">Typical risks</p>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            {research.typical_risks.slice(0, 3).map((item) => <li key={item.label}>{item.label}</li>)}
          </ul>
        </div>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">Industries</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {research.industries.slice(0, 5).map((industry) => (
              <Link key={industry.slug} href={`/industry/${industry.slug}`} className="rounded-lg border border-white/10 bg-background-primary/70 px-3 py-2 text-sm transition hover:border-primary/60">
                {industry.name}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-muted-foreground">Related companies</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {research.companies.slice(0, 5).map((company) => (
              <Link key={company.ticker} href={company.href} className="rounded-lg border border-white/10 bg-background-primary/70 px-3 py-2 text-sm transition hover:border-primary/60">
                {company.ticker}
              </Link>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        {research.learn_next.slice(0, 4).map((topic) => (
          <Link key={topic.topic} href={topic.path} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary transition hover:border-primary/70">
            {topic.topic}
          </Link>
        ))}
      </div>
      <div className="mt-4 rounded-lg border border-white/10 bg-background-primary/70 p-4 text-sm text-muted-foreground">
        Data origin: {research.transparency.data_origin}. {research.transparency.not_advice}
      </div>
    </div>
  );
}



