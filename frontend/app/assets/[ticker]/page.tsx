"use client";

import Link from "next/link";
import { useMemo } from "react";
import { AxiosError } from "axios";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout";
import { assetService, newsService } from "@/services/api";
import { formatDisplayDate, mapAsset, mapNewsArticles } from "@/lib/mappers/data-mappers";
import {
  ANALYTICS_PLACEHOLDERS,
  DEMO_ASSETS,
  DEMO_NEWS,
  getEducationSummary,
  getExplainLikeIm18,
} from "@/utils/demo-content";
import { AssetAssessmentPanel } from "@/features/assets/asset-assessment-panel";
import { CardSkeleton } from "@/components/skeleton";

function formatMoney(value: number | undefined, currency: string) {
  if (typeof value !== "number") return "Unavailable";
  return `${currency} ${new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(value)}`;
}

export default function AssetDetailPage() {
  const params = useParams<{ ticker: string }>();
  const ticker = (params?.ticker ?? "").toUpperCase();

  const assetQuery = useQuery({
    queryKey: ["asset-detail", ticker],
    queryFn: () => assetService.getAssetByTicker(ticker),
    retry: 1,
    enabled: Boolean(ticker),
  });

  const newsQuery = useQuery({
    queryKey: ["asset-news", ticker],
    queryFn: () => newsService.getNewsFeed({ asset: ticker, limit: 4, sort: "desc" }),
    retry: 1,
    enabled: Boolean(ticker),
  });

  const assessmentQuery = useQuery({
    queryKey: ["asset-assessment", ticker],
    queryFn: () => assetService.getAssetAssessment(ticker),
    retry: 1,
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 5,
  });

  const backendAsset = mapAsset(assetQuery.data?.data);
  const fallbackAsset = DEMO_ASSETS.find((asset) => asset.ticker === ticker) ?? null;
  const isNotFound = assetQuery.isError && (assetQuery.error as AxiosError)?.response?.status === 404 && !fallbackAsset;
  const usingFallback = assetQuery.isError && Boolean(fallbackAsset);
  const asset = backendAsset ?? fallbackAsset;

  const news = useMemo(() => {
    const backendNews = mapNewsArticles(newsQuery.data?.data);
    if (backendNews.length > 0) return backendNews;
    return DEMO_NEWS.filter((article) => article.asset_tickers.includes(ticker));
  }, [newsQuery.data, ticker]);

  const education = useMemo(() => (asset ? getExplainLikeIm18(asset) : []), [asset]);

  return (
    <AppShell>
      <div className="space-y-6">
        {usingFallback || newsQuery.isError ? (
          <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-sm text-yellow-200">
            Backend unavailable. Showing demo data for preview only.
          </div>
        ) : null}

        {assetQuery.isLoading ? (
          <div className="h-72 animate-pulse rounded-lg border border-border bg-card" />
        ) : isNotFound || !asset ? (
          <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center">
            <h1 className="text-2xl font-semibold">Asset not found</h1>
            <p className="mt-2 text-sm text-muted-foreground">We could not find an asset matching {ticker || "that ticker"}.</p>
            <div className="mt-5 flex justify-center gap-3">
              <Link href="/assets" className="rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground">Browse assets</Link>
              <Link href="/dashboard" className="rounded-lg border border-border px-4 py-3 text-sm font-medium">Back to dashboard</Link>
            </div>
          </div>
        ) : (
          <>
            <section className="rounded-lg border border-border bg-card p-6">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">{asset.exchange} / {asset.asset_type}</p>
                  <h1 className="mt-2 text-4xl font-bold">{asset.company_name}</h1>
                  <p className="mt-3 max-w-3xl text-muted-foreground">{asset.description}</p>
                </div>
                <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
                  <p className="text-2xl font-semibold">{asset.ticker}</p>
                  <p className="mt-1 text-primary/80">{asset.currency}</p>
                </div>
              </div>
              <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <div className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="text-sm text-muted-foreground">Sector</p>
                  <p className="mt-1 font-semibold">{asset.sector}</p>
                </div>
                <div className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="text-sm text-muted-foreground">Industry</p>
                  <p className="mt-1 font-semibold">{asset.industry}</p>
                </div>
                <div className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="text-sm text-muted-foreground">Exchange</p>
                  <p className="mt-1 font-semibold">{asset.exchange}</p>
                </div>
                <div className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="text-sm text-muted-foreground">Market cap</p>
                  <p className="mt-1 font-semibold">{formatMoney(asset.market_cap, asset.currency)}</p>
                </div>
                <div className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="text-sm text-muted-foreground">Listing date</p>
                  <p className="mt-1 font-semibold">{asset.listing_date ?? "Unavailable"}</p>
                </div>
              </div>
            </section>

            <section className="space-y-6">
              <div>
                {assessmentQuery.isLoading ? (
                  <CardSkeleton />
                ) : assessmentQuery.isError ? (
                  <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
                    Assessment currently unavailable.
                  </div>
                ) : assessmentQuery.data?.data ? (
                  <AssetAssessmentPanel assessment={assessmentQuery.data.data} />
                ) : (
                  <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">
                    Assessment currently unavailable.
                  </div>
                )}
              </div>

              <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
                <div className="space-y-6">
                  <div className="rounded-lg border border-border bg-card p-6">
                    <h2 className="text-xl font-semibold">Analytics section</h2>
                    <p className="mt-1 text-sm text-muted-foreground">Connected to the Analytics Engine foundation. Real calculations are intentionally not implemented yet.</p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {ANALYTICS_PLACEHOLDERS.map((metric) => (
                        <div key={metric.key} className="rounded-lg border border-border bg-background-secondary p-4">
                          <p className="font-medium">{metric.label}</p>
                          <p className="mt-2 text-sm text-muted-foreground">Calculation coming soon</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-card p-6">
                  <h2 className="text-xl font-semibold">Related news</h2>
                  <div className="mt-4 space-y-3">
                    {newsQuery.isLoading ? [1, 2].map((item) => <div key={item} className="h-24 animate-pulse rounded-lg border border-border bg-background-secondary" />) : news.length > 0 ? news.map((article) => (
                      <article key={article.id} className="rounded-lg border border-border bg-background-secondary p-4">
                        <p className="text-xs text-muted-foreground">{article.source} / {formatDisplayDate(article.published_at)}</p>
                        <h3 className="mt-2 text-base font-semibold">{article.title}</h3>
                        <p className="mt-2 text-sm text-muted-foreground">{article.summary}</p>
                      </article>
                    )) : <p className="text-sm text-muted-foreground">No linked news available for this asset yet.</p>}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-lg border border-border bg-card p-6">
                  <h2 className="text-xl font-semibold">Educational section</h2>
                  <p className="mt-3 text-sm text-muted-foreground">{getEducationSummary(asset)}</p>
                  <div className="mt-4 rounded-lg border border-border bg-background-secondary p-4">
                    <h3 className="font-semibold">Explain Like I am 18</h3>
                    <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                      {education.map((line) => <li key={line}>{line}</li>)}
                    </ul>
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-card p-6">
                  <h2 className="text-xl font-semibold">Compare</h2>
                  <p className="mt-2 text-sm text-muted-foreground">Compare this asset with another backend catalog asset.</p>
                  <Link href={`/compare?left=${asset.ticker}`} className="mt-4 inline-flex rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground">Open comparison</Link>
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}