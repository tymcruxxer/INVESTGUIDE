"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout";
import { ANALYTICS_PLACEHOLDERS, DEMO_ASSETS, DEMO_NEWS, getEducationSummary, getExplainLikeIm18 } from "@/utils/demo-content";

export default function AssetDetailPage() {
  const params = useParams<{ ticker: string }>();
  const ticker = (params?.ticker ?? "DLTA").toUpperCase();

  const asset = useMemo(() => DEMO_ASSETS.find((item) => item.ticker === ticker) ?? DEMO_ASSETS[0], [ticker]);
  const assetNews = useMemo(() => DEMO_NEWS.filter((item) => item.asset_ticker === ticker), [ticker]);
  const education = useMemo(() => getExplainLikeIm18(asset), [asset]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">{asset.exchange}</p>
              <h1 className="mt-2 text-4xl font-bold">{asset.company_name}</h1>
              <p className="mt-3 max-w-2xl text-muted-foreground">{asset.description}</p>
            </div>
            <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
              <p className="font-semibold">{asset.ticker}</p>
              <p className="mt-1 text-primary/80">{asset.asset_type}</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Asset type</p>
              <p className="mt-1 font-semibold">{asset.asset_type}</p>
            </div>
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Sector</p>
              <p className="mt-1 font-semibold">{asset.sector}</p>
            </div>
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Exchange</p>
              <p className="mt-1 font-semibold">{asset.exchange}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Company overview</h2>
              <p className="mt-3 text-sm text-muted-foreground">{asset.description}</p>
            </div>

            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Analytics section</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {ANALYTICS_PLACEHOLDERS.map((metric) => (
                  <div key={metric.key} className="rounded-lg border border-border bg-background-secondary p-4">
                    <p className="font-medium">{metric.label}</p>
                    <p className="mt-2 text-sm text-muted-foreground">Calculation coming soon</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">News</h2>
              <div className="mt-4 space-y-3">
                {assetNews.length > 0 ? assetNews.map((item) => (
                  <div key={item.id} className="rounded-lg border border-border bg-background-secondary p-4">
                    <p className="font-medium">{item.title}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{item.source} · {item.published_at}</p>
                    <p className="mt-2 text-sm">{item.summary}</p>
                  </div>
                )) : <p className="text-sm text-muted-foreground">No linked news available yet.</p>}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Educational section</h2>
              <p className="mt-3 text-sm text-muted-foreground">{getEducationSummary(asset)}</p>
              <div className="mt-4 rounded-lg border border-border bg-background-secondary p-4">
                <h3 className="font-semibold">Explain Like I&apos;m 18</h3>
                <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                  {education.map((line) => (
                    <li key={line} className="leading-6">{line}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Quick actions</h2>
              <div className="mt-4 flex flex-col gap-3">
                <Link href="/compare" className="rounded-lg bg-primary px-4 py-3 text-center font-medium text-primary-foreground">Compare this asset</Link>
                <Link href="/assets" className="rounded-lg border border-border px-4 py-3 text-center font-medium">Back to explorer</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
