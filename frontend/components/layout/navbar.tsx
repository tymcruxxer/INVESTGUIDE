/**
 * Top Navigation Bar Component
 * Header with global search, theme toggle, and notifications
 */

"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, Briefcase, Building2, Moon, Newspaper, Search, Sun, UserCircle, X } from "lucide-react";
import { useAuthStore, useThemeStore } from "@/store";
import { DEMO_ASSETS, DEMO_COMPANIES, DEMO_NEWS } from "@/utils/demo-content";
import { normalizeTickerForApi, tickerToRoute } from "@/utils/tickers";
import { cn } from "@/utils";

type SearchResult = {
  label: string;
  detail: string;
  href: string;
  type: "Company" | "Asset" | "News";
};

const typeIcon = {
  Company: Building2,
  Asset: Briefcase,
  News: Newspaper,
};

export function Navbar() {
  const { theme, toggleTheme } = useThemeStore();
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const results = useMemo(() => {
    const query = search.trim().toLowerCase();
    const canonicalQuery = normalizeTickerForApi(search).toLowerCase();
    if (query.length < 2) return [];

    const matches = (values: Array<string | null | undefined>) =>
      values
        .filter(Boolean)
        .some((value) => {
          const normalized = String(value).toLowerCase();
          return normalized.includes(query) || normalized.includes(canonicalQuery);
        });

    const companies: SearchResult[] = DEMO_COMPANIES.filter((company) =>
      matches([company.name, company.ticker, normalizeTickerForApi(company.ticker), company.sector, company.industry])
    ).map((company) => ({
      label: company.name,
      detail: `${company.ticker} / ${company.exchange}`,
      href: `/company/${tickerToRoute(company.ticker)}`,
      type: "Company",
    }));

    const assets: SearchResult[] = DEMO_ASSETS.filter((asset) =>
      matches([asset.ticker, normalizeTickerForApi(asset.ticker), asset.company_name, asset.asset_type, asset.sector, asset.industry])
    ).map((asset) => ({
      label: asset.company_name,
      detail: `${asset.ticker} / ${asset.asset_type}`,
      href: `/assets/${tickerToRoute(asset.ticker)}`,
      type: "Asset",
    }));

    const news: SearchResult[] = DEMO_NEWS.filter((article) =>
      matches([article.title, article.summary, article.source, ...article.asset_tickers])
    ).map((article) => ({
      label: article.title,
      detail: article.source,
      href: "/dashboard#latest-news",
      type: "News",
    }));

    const deduped = [...companies, ...assets, ...news].filter(
      (result, index, all) => all.findIndex((item) => item.type === result.type && item.href === result.href) === index
    );
    return deduped.slice(0, 6);
  }, [search]);

  const hasSearchQuery = search.trim().length >= 2;

  useEffect(() => {
    setActiveIndex(0);
  }, [search]);

  const openResult = (href: string) => {
    setSearch("");
    router.push(href);
  };

  return (
    <nav className="sticky top-0 z-20 h-16 border-b border-white/10 bg-background-secondary/90 backdrop-blur-xl">
      <div className="flex h-full items-center justify-between gap-3 px-4 lg:px-6">
        <div className="relative w-full max-w-md">
          <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "ArrowDown") {
                event.preventDefault();
                setActiveIndex((index) => Math.min(index + 1, Math.max(results.length - 1, 0)));
              }
              if (event.key === "ArrowUp") {
                event.preventDefault();
                setActiveIndex((index) => Math.max(index - 1, 0));
              }
              if (event.key === "Enter" && results[activeIndex]) {
                event.preventDefault();
                openResult(results[activeIndex].href);
              }
              if (event.key === "Escape") {
                setSearch("");
              }
            }}
            className="h-10 w-full rounded-lg border border-white/10 bg-background-primary/80 px-10 text-sm outline-none transition placeholder:text-muted-foreground focus:border-primary focus:ring-4 focus:ring-primary/20"
            placeholder="Search companies, assets, news"
            aria-label="Search companies, assets, and news"
            aria-expanded={hasSearchQuery}
            aria-controls="global-search-results"
            role="combobox"
          />
          {results.length > 0 ? (
            <div id="global-search-results" role="listbox" className="absolute left-0 right-0 top-12 z-30 overflow-hidden rounded-lg border border-white/10 bg-card shadow-2xl shadow-black/30">
              {results.map((result, index) => {
                const Icon = typeIcon[result.type];
                const isActive = index === activeIndex;
                return (
                  <button
                    key={`${result.type}-${result.href}-${result.label}`}
                    onMouseEnter={() => setActiveIndex(index)}
                    onClick={() => openResult(result.href)}
                    role="option"
                    aria-selected={isActive}
                    className={cn(
                      "flex w-full items-center gap-3 border-b border-white/10 px-3 py-3 text-left text-sm last:border-b-0 smooth-transition",
                      isActive ? "bg-primary/10 text-foreground" : "hover:bg-background-secondary"
                    )}
                  >
                    <span className="rounded-lg bg-primary/10 p-2 text-primary"><Icon size={16} /></span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate font-medium">{result.label}</span>
                      <span className="block truncate text-xs text-muted-foreground">{result.type} / {result.detail}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          ) : hasSearchQuery ? (
            <div id="global-search-results" role="status" className="absolute left-0 right-0 top-12 z-30 rounded-lg border border-white/10 bg-card p-4 text-sm shadow-2xl shadow-black/30">
              <p className="font-medium">No matching results yet</p>
              <p className="mt-1 text-muted-foreground">Try a ticker such as DLTA, a theme such as REIT, or browse the asset catalog.</p>
              <button type="button" onClick={() => openResult("/assets")} className="mt-3 text-sm font-medium text-primary hover:text-blue-300">
                Browse assets
              </button>
            </div>
          ) : null}
        </div>
        <div className="flex shrink-0 items-center gap-3">
          {search ? (
            <button
              onClick={() => setSearch("")}
              className="hidden rounded-lg border border-white/10 bg-background-primary/50 p-2 smooth-transition hover:bg-background-tertiary sm:inline-flex"
              aria-label="Clear search"
            >
              <X size={20} className="text-muted-foreground" />
            </button>
          ) : null}
          <button
            className="relative rounded-lg border border-white/10 bg-background-primary/50 p-2 smooth-transition hover:bg-background-tertiary active:scale-[0.98]"
            aria-label="Notifications"
          >
            <Bell size={20} className="text-muted-foreground" />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-destructive" />
          </button>
          <button
            onClick={toggleTheme}
            className="rounded-lg border border-white/10 bg-background-primary/50 p-2 smooth-transition hover:bg-background-tertiary active:scale-[0.98]"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            aria-label="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun size={20} className="text-muted-foreground" />
            ) : (
              <Moon size={20} className="text-muted-foreground" />
            )}
          </button>
          <div className="ml-1 hidden items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-3 py-2 text-sm font-medium text-primary sm:flex">
            <UserCircle size={18} />
            <span className="max-w-[180px] truncate">{user?.email ?? "Investor"}</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
