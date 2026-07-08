"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { assetService } from "@/services/api";
import { mapAssets } from "@/lib/mappers/data-mappers";
import { DEMO_ASSETS } from "@/utils/demo-content";
import type { Asset } from "@/types";

const ASSET_TYPE_OPTIONS = [
  { value: "", label: "All types" },
  { value: "equity", label: "Equities" },
  { value: "REIT", label: "REITs" },
  { value: "bond", label: "Bonds" },
  { value: "money_market", label: "Money market" },
  { value: "alternative", label: "Alternatives" },
];

const EXCHANGE_OPTIONS = [
  { value: "", label: "All exchanges" },
  { value: "ZSE", label: "ZSE" },
  { value: "VFEX", label: "VFEX" },
];

function matchesSearch(asset: Asset, search: string) {
  const normalized = search.trim().toLowerCase();
  if (!normalized) return true;
  return [asset.ticker, asset.company_name, asset.asset_type, asset.sector, asset.exchange, asset.industry]
    .join(" ")
    .toLowerCase()
    .includes(normalized);
}

export function AssetExplorer() {
  const [search, setSearch] = useState("");
  const [exchange, setExchange] = useState("");
  const [assetType, setAssetType] = useState("");
  const [sector, setSector] = useState("");

  const assetsQuery = useQuery({
    queryKey: ["assets", "explorer"],
    queryFn: () => assetService.getAssets({ limit: 100, status: "active" }),
    retry: 1,
  });

  const backendAssets = useMemo(() => mapAssets(assetsQuery.data?.data), [assetsQuery.data]);
  const usingFallback = assetsQuery.isError || (!assetsQuery.isLoading && backendAssets.length === 0);
  const sourceAssets = usingFallback ? DEMO_ASSETS : backendAssets;

  const sectors = useMemo(() => {
    return Array.from(new Set(sourceAssets.map((asset) => asset.sector).filter(Boolean))).sort();
  }, [sourceAssets]);

  const visibleAssets = useMemo(() => {
    return sourceAssets.filter((asset) => {
      if (!matchesSearch(asset, search)) return false;
      if (exchange && asset.exchange !== exchange) return false;
      if (assetType && asset.asset_type !== assetType) return false;
      if (sector && asset.sector !== sector) return false;
      return true;
    });
  }, [assetType, exchange, search, sector, sourceAssets]);

  return (
    <div className="space-y-6">
      {usingFallback ? (
        <div className="warning-panel">
          Backend unavailable. Showing development preview data.
        </div>
      ) : null}

      <div className="grid gap-3 rounded-lg border border-border bg-card p-4 lg:grid-cols-[1.3fr_0.7fr_0.7fr_0.7fr]">
        <label className="space-y-2">
          <span className="text-sm font-medium">Search</span>
          <div className="flex items-center gap-2 rounded-lg border border-border bg-background-secondary px-3 py-2">
            <Search size={16} className="text-muted-foreground" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search delta, REIT, treasury..."
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium">Exchange</span>
          <select value={exchange} onChange={(event) => setExchange(event.target.value)} className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2 text-sm">
            {EXCHANGE_OPTIONS.map((option) => (
              <option key={option.value || "all"} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium">Type</span>
          <select value={assetType} onChange={(event) => setAssetType(event.target.value)} className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2 text-sm">
            {ASSET_TYPE_OPTIONS.map((option) => (
              <option key={option.value || "all"} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium">Sector</span>
          <select value={sector} onChange={(event) => setSector(event.target.value)} className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2 text-sm">
            <option value="">All sectors</option>
            {sectors.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>
      </div>

      {assetsQuery.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="h-44 animate-pulse rounded-lg border border-border bg-card" />
          ))}
        </div>
      ) : visibleAssets.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center">
          <h2 className="text-xl font-semibold">No assets found</h2>
          <p className="mt-2 text-sm text-muted-foreground">Try a broader search or clear one of the filters.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {visibleAssets.map((asset) => (
            <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="rounded-lg border border-border bg-card p-5 transition hover:border-primary/60">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold">{asset.ticker}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{asset.company_name}</p>
                </div>
                <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">{asset.exchange}</span>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                <p>Type</p>
                <p className="text-right text-foreground">{asset.asset_type}</p>
                <p>Sector</p>
                <p className="text-right text-foreground">{asset.sector}</p>
                <p>Currency</p>
                <p className="text-right text-foreground">{asset.currency}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}