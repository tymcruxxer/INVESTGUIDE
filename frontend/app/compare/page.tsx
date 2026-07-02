"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout";
import { ANALYTICS_PLACEHOLDERS, DEMO_ASSETS } from "@/utils/demo-content";

export default function ComparePage() {
  const [leftTicker, setLeftTicker] = useState("DLTA");
  const [rightTicker, setRightTicker] = useState("TIGZ");

  const left = useMemo(() => DEMO_ASSETS.find((asset) => asset.ticker === leftTicker) ?? DEMO_ASSETS[0], [leftTicker]);
  const right = useMemo(() => DEMO_ASSETS.find((asset) => asset.ticker === rightTicker) ?? DEMO_ASSETS[3], [rightTicker]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold">Compare assets</h1>
          <p className="mt-2 text-muted-foreground">Choose two assets to compare their profile, analytics placeholders, and education framing.</p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <label className="rounded-lg border border-border bg-card p-4">
            <span className="mb-2 block text-sm font-medium">Asset one</span>
            <select value={leftTicker} onChange={(event) => setLeftTicker(event.target.value)} className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2">
              {DEMO_ASSETS.map((asset) => (
                <option key={asset.ticker} value={asset.ticker}>
                  {asset.ticker} · {asset.company_name}
                </option>
              ))}
            </select>
          </label>
          <label className="rounded-lg border border-border bg-card p-4">
            <span className="mb-2 block text-sm font-medium">Asset two</span>
            <select value={rightTicker} onChange={(event) => setRightTicker(event.target.value)} className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2">
              {DEMO_ASSETS.map((asset) => (
                <option key={asset.ticker} value={asset.ticker}>
                  {asset.ticker} · {asset.company_name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-lg border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Quick comparison</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Asset type</p>
                <p className="mt-1 font-semibold">{left.asset_type}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Asset type</p>
                <p className="mt-1 font-semibold">{right.asset_type}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Sector</p>
                <p className="mt-1 font-semibold">{left.sector}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Sector</p>
                <p className="mt-1 font-semibold">{right.sector}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Exchange</p>
                <p className="mt-1 font-semibold">{left.exchange}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Exchange</p>
                <p className="mt-1 font-semibold">{right.exchange}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Dividend availability</p>
                <p className="mt-1 font-semibold">{left.asset_type === "REIT" ? "Likely" : "Pending"}</p>
              </div>
              <div className="rounded-lg border border-border bg-background-secondary p-4">
                <p className="text-sm text-muted-foreground">Dividend availability</p>
                <p className="mt-1 font-semibold">{right.asset_type === "REIT" ? "Likely" : "Pending"}</p>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Analytics placeholders</h2>
              <div className="mt-4 space-y-3">
                {ANALYTICS_PLACEHOLDERS.map((metric) => (
                  <div key={metric.key} className="rounded-lg border border-border bg-background-secondary p-3">
                    <div className="flex items-center justify-between gap-3">
                      <span>{metric.label}</span>
                      <span className="text-sm text-muted-foreground">Calculation coming soon</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-lg border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">Educational summaries</h2>
              <div className="mt-4 space-y-3 text-sm text-muted-foreground">
                <p>{left.description}</p>
                <p>{right.description}</p>
              </div>
              <Link href="/dashboard" className="mt-4 inline-flex text-sm font-medium text-primary">Return to dashboard →</Link>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
