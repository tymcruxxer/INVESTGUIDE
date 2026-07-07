"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout";
import { assetService } from "@/services/api";
import { mapAssets } from "@/lib/mappers/data-mappers";
import { ANALYTICS_PLACEHOLDERS, DEMO_ASSETS, getEducationSummary } from "@/utils/demo-content";

export default function ComparePage() {
  const [leftTicker, setLeftTicker] = useState("DLTA");
  const [rightTicker, setRightTicker] = useState("TIGZ");

  const assetsQuery = useQuery({
    queryKey: ["assets", "compare"],
    queryFn: () => assetService.getAssets({ limit: 100, status: "active" }),
    retry: 1,
  });

  const backendAssets = useMemo(() => mapAssets(assetsQuery.data?.data), [assetsQuery.data]);
  const usingFallback = assetsQuery.isError || (!assetsQuery.isLoading && backendAssets.length === 0);
  const assets = usingFallback ? DEMO_ASSETS : backendAssets;

  useEffect(() => {
    if (assets.length === 0) return;
    if (!assets.some((asset) => asset.ticker === leftTicker)) setLeftTicker(assets[0].ticker);
    if (!assets.some((asset) => asset.ticker === rightTicker)) setRightTicker(assets[1]?.ticker ?? assets[0].ticker);
  }, [assets, leftTicker, rightTicker]);

  const left = assets.find((asset) => asset.ticker === leftTicker) ?? assets[0];
  const right = assets.find((asset) => asset.ticker === rightTicker) ?? assets[1] ?? assets[0];

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold">Compare assets</h1>
          <p className="mt-2 text-muted-foreground">Choose two backend catalog assets and compare their profile, education framing, and analytics placeholders.</p>
        </div>

        {usingFallback ? (
          <div className="warning-panel">
            Backend unavailable. Showing demo data for preview only.
          </div>
        ) : null}

        {assetsQuery.isLoading ? (
          <div className="h-56 animate-pulse premium-card" />
        ) : assets.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center">
            <h2 className="text-xl font-semibold">No assets available</h2>
            <p className="mt-2 text-sm text-muted-foreground">The backend asset catalog returned no records.</p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 lg:grid-cols-2">
              <label className="premium-card p-4">
                <span className="mb-2 block text-sm font-medium">Asset one</span>
                <select value={leftTicker} onChange={(event) => setLeftTicker(event.target.value)} className="w-full rounded-lg border border-white/10 bg-background-primary/70 px-3 py-2">
                  {assets.map((asset) => <option key={asset.ticker} value={asset.ticker}>{asset.ticker} - {asset.company_name}</option>)}
                </select>
              </label>
              <label className="premium-card p-4">
                <span className="mb-2 block text-sm font-medium">Asset two</span>
                <select value={rightTicker} onChange={(event) => setRightTicker(event.target.value)} className="w-full rounded-lg border border-white/10 bg-background-primary/70 px-3 py-2">
                  {assets.map((asset) => <option key={asset.ticker} value={asset.ticker}>{asset.ticker} - {asset.company_name}</option>)}
                </select>
              </label>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              {[left, right].map((asset) => (
                <section key={asset.ticker} className="premium-card p-6">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm uppercase tracking-[0.16em] text-muted-foreground">{asset.exchange}</p>
                      <h2 className="mt-2 text-2xl font-semibold">{asset.ticker}</h2>
                      <p className="mt-1 text-sm text-muted-foreground">{asset.company_name}</p>
                    </div>
                    <Link href={`/assets/${asset.ticker.toLowerCase()}`} className="text-sm font-medium text-primary">Open</Link>
                  </div>

                  <div className="mt-5 grid gap-3 text-sm">
                    <div className="flex justify-between gap-4 rounded-lg border border-white/10 bg-background-primary/70 p-3"><span className="text-muted-foreground">Asset type</span><span>{asset.asset_type}</span></div>
                    <div className="flex justify-between gap-4 rounded-lg border border-white/10 bg-background-primary/70 p-3"><span className="text-muted-foreground">Sector</span><span>{asset.sector}</span></div>
                    <div className="flex justify-between gap-4 rounded-lg border border-white/10 bg-background-primary/70 p-3"><span className="text-muted-foreground">Exchange</span><span>{asset.exchange}</span></div>
                    <div className="flex justify-between gap-4 rounded-lg border border-white/10 bg-background-primary/70 p-3"><span className="text-muted-foreground">Currency</span><span>{asset.currency}</span></div>
                    <div className="flex justify-between gap-4 rounded-lg border border-white/10 bg-background-primary/70 p-3"><span className="text-muted-foreground">Risk placeholder</span><span>Methodology coming soon</span></div>
                  </div>

                  <div className="mt-5 rounded-lg border border-white/10 bg-background-primary/70 p-4">
                    <h3 className="font-semibold">Educational summary</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{getEducationSummary(asset)}</p>
                  </div>
                </section>
              ))}
            </div>

            <section className="premium-card p-6">
              <h2 className="text-xl font-semibold">Analytics placeholders</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                {ANALYTICS_PLACEHOLDERS.map((metric) => (
                  <div key={metric.key} className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                    <p className="font-medium">{metric.label}</p>
                    <p className="mt-2 text-sm text-muted-foreground">Calculation coming soon</p>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}
