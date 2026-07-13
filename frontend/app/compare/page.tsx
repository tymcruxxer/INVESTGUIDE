"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout";
import { assetService, comparisonService } from "@/services/api";
import { mapAssets } from "@/lib/mappers/data-mappers";
import { ANALYTICS_PLACEHOLDERS, DEMO_ASSETS, getEducationSummary } from "@/utils/demo-content";

export default function ComparePage() {
  const [leftTicker, setLeftTicker] = useState("DLTA");
  const [rightTicker, setRightTicker] = useState("TIGZ");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const left = params.get("left");
    const right = params.get("right");
    if (left) setLeftTicker(left.toUpperCase());
    if (right) setRightTicker(right.toUpperCase());
  }, []);

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

  const comparisonQuery = useQuery({
    queryKey: ["asset-comparison", left?.ticker, right?.ticker],
    queryFn: () => comparisonService.compareAssets(left.ticker, right.ticker),
    retry: 1,
    enabled: Boolean(left?.ticker && right?.ticker && !usingFallback),
    staleTime: 1000 * 60 * 10,
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-muted-foreground">Research network</p>
          <h1 className="mt-2 text-4xl font-bold">Compare assets</h1>
          <p className="mt-2 max-w-3xl text-muted-foreground">Choose two backend catalog assets and compare their business profile, risk context, evidence quality, and next learning paths.</p>
        </div>

        {usingFallback ? (
          <div className="warning-panel">
            Backend unavailable. Showing development preview data.
          </div>
        ) : null}

        {assetsQuery.isLoading ? (
          <div className="skeleton-card h-56" />
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

            {comparisonQuery.isLoading ? (
              <section className="skeleton-card h-64" />
            ) : comparisonQuery.data?.data ? (
              <section className="premium-card p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.16em] text-muted-foreground">Deterministic comparison</p>
                    <h2 className="mt-2 text-2xl font-semibold">What changes between these two?</h2>
                    <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{comparisonQuery.data.data.summary}</p>
                  </div>
                  <span className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">Educational only</span>
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  <CompareSignal label="Opportunity" left={comparisonQuery.data.data.left.opportunity_label} right={comparisonQuery.data.data.right.opportunity_label} />
                  <CompareSignal label="Risk" left={comparisonQuery.data.data.left.risk_level} right={comparisonQuery.data.data.right.risk_level} />
                  <CompareSignal label="Evidence" left={comparisonQuery.data.data.left.evidence_strength} right={comparisonQuery.data.data.right.evidence_strength} />
                </div>

                <div className="mt-6 grid gap-4 lg:grid-cols-2">
                  <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                    <h3 className="font-semibold">Business comparison</h3>
                    <div className="mt-3 space-y-3">
                      {comparisonQuery.data.data.business_comparison.rows.map((row) => (
                        <div key={row.label} className="rounded-lg border border-white/10 p-3 text-sm">
                          <p className="font-medium">{row.label}</p>
                          <div className="mt-2 grid gap-2 sm:grid-cols-2 text-muted-foreground">
                            <p>{comparisonQuery.data.data.left.ticker}: {row.left}</p>
                            <p>{comparisonQuery.data.data.right.ticker}: {row.right}</p>
                          </div>
                          <p className="mt-2 text-xs text-muted-foreground">{row.insight}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                    <h3 className="font-semibold">Evidence and risk</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{comparisonQuery.data.data.evidence_comparison.why}</p>
                    <div className="mt-4 space-y-3 text-sm">
                      {comparisonQuery.data.data.risk_comparison.things_to_watch.map((item) => (
                        <div key={item} className="rounded-lg border border-white/10 p-3 text-muted-foreground">{item}</div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-6 rounded-lg border border-white/10 bg-background-primary/70 p-4">
                  <h3 className="font-semibold">Learn next</h3>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {comparisonQuery.data.data.suggested_follow_up_questions.map((question) => (
                      <span key={question} className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary">{question}</span>
                    ))}
                  </div>
                  <p className="mt-4 text-xs text-muted-foreground">{comparisonQuery.data.data.transparency.not_recommendation}</p>
                </div>
              </section>
            ) : comparisonQuery.isError ? (
              <div className="warning-panel">Structured comparison is unavailable. The basic asset cards are still shown below.</div>
            ) : null}

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

function CompareSignal({ label, left, right }: { label: string; left: string; right: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <div className="mt-3 grid gap-2 text-sm">
        <div className="flex items-center justify-between gap-3"><span>Left</span><span className="font-semibold">{left}</span></div>
        <div className="flex items-center justify-between gap-3"><span>Right</span><span className="font-semibold">{right}</span></div>
      </div>
    </div>
  );
}

