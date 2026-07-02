"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout";
import { DEMO_ASSETS } from "@/utils/demo-content";

export default function AssetsPage() {
  const [search, setSearch] = useState("");

  const filteredAssets = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return DEMO_ASSETS;
    return DEMO_ASSETS.filter((asset) => {
      const haystack = [asset.ticker, asset.company_name, asset.sector, asset.exchange, asset.asset_type].join(" ").toLowerCase();
      return haystack.includes(query);
    });
  }, [search]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold">Asset explorer</h1>
          <p className="mt-2 text-muted-foreground">Search across equities, REITs, and fixed-income ideas using the same categories you will later see in the real data layer.</p>
        </div>

        <label className="block rounded-lg border border-border bg-card p-4">
          <span className="mb-2 block text-sm font-medium">Search assets</span>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Try delta, reit, treasury..." className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2" />
        </label>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredAssets.map((asset) => (
            <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="rounded-lg border border-border bg-card p-5 transition hover:border-primary/60">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold">{asset.ticker}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{asset.company_name}</p>
                </div>
                <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">{asset.exchange}</span>
              </div>
              <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                <p>Type: {asset.asset_type}</p>
                <p>Sector: {asset.sector}</p>
                <p>Exchange: {asset.exchange}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
