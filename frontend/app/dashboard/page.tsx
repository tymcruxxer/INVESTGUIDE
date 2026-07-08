"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout";
import { assetService, investorProfileService, newsService } from "@/services/api";
import { mapAssets, mapNewsArticles, formatDisplayDate } from "@/lib/mappers/data-mappers";
import {
  buildRecommendedAssets,
  buildRoadmap,
  DEMO_ASSETS,
  DEMO_NEWS,
  getPersonalizationCopy,
  getRecommendationReason,
} from "@/utils/demo-content";
import { useAuthStore } from "@/store";
import { motion } from "framer-motion";
import { CheckCircle2, Circle, Sparkles } from "lucide-react";

const profileLabel = (value: string | null | undefined) => {
  if (!value) return "Not set";
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
};

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const storeProfile = useAuthStore((state) => state.investorProfile);

  const profileQuery = useQuery({
    queryKey: ["investor-profile", "dashboard"],
    queryFn: () => investorProfileService.getProfile(),
    retry: 1,
  });

  const assetsQuery = useQuery({
    queryKey: ["assets", "dashboard"],
    queryFn: () => assetService.getAssets({ limit: 100, status: "active" }),
    retry: 1,
  });

  const newsQuery = useQuery({
    queryKey: ["news", "dashboard"],
    queryFn: () => newsService.getNewsFeed({ limit: 5, sort: "desc" }),
    retry: 1,
  });

  const profile = profileQuery.data?.data ?? storeProfile ?? null;
  const backendAssets = useMemo(() => mapAssets(assetsQuery.data?.data), [assetsQuery.data]);
  const backendNews = useMemo(() => mapNewsArticles(newsQuery.data?.data), [newsQuery.data]);
  const assetsFallback = assetsQuery.isError || (!assetsQuery.isLoading && backendAssets.length === 0);
  const newsFallback = newsQuery.isError || (!newsQuery.isLoading && backendNews.length === 0);
  const profileFallback = profileQuery.isError && !storeProfile;
  const assets = assetsFallback ? DEMO_ASSETS : backendAssets;
  const news = newsFallback ? DEMO_NEWS : backendNews;
  const roadmap = buildRoadmap(profile);
  const recommendedAssets = buildRecommendedAssets(profile, assets);
  const personalization = getPersonalizationCopy(profile);

  return (
    <AppShell>
      <motion.div className="space-y-6" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        {assetsFallback || newsFallback || profileFallback ? (
          <div className="warning-panel">
            Backend unavailable. Showing development preview data.
          </div>
        ) : null}

        <section className="premium-card p-6">
          <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
            <div>
              <p className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-primary"><Sparkles size={15} /> Your intelligence hub</p>
              <h1 className="mt-2 text-4xl font-bold">Good day {user?.username || user?.email?.split("@")[0] || "investor"}.</h1>
              <p className="mt-3 max-w-3xl text-muted-foreground">
                Based on your profile, you are a {profileLabel(profile?.risk_appetite).toLowerCase()} risk {profileLabel(profile?.investment_horizon).toLowerCase()} investor with {profileLabel(profile?.experience_level).toLowerCase()} experience.
              </p>
              <p className="mt-3 text-sm text-muted-foreground">{personalization.intro}</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                <p className="text-sm text-muted-foreground">Preferred assets</p>
                <p className="mt-1 font-semibold">{profile?.preferred_asset_types?.length ? profile.preferred_asset_types.map(profileLabel).join(", ") : "ZSE, REITs"}</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                <p className="text-sm text-muted-foreground">Experience mode</p>
                <p className="mt-1 font-semibold">{profileLabel(profile?.experience_level)} ({personalization.tone})</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          <div className="premium-card premium-card-hover p-4">
            <p className="text-sm text-muted-foreground">Risk appetite</p>
            <p className="mt-1 text-xl font-semibold">{profileLabel(profile?.risk_appetite)}</p>
          </div>
          <div className="premium-card premium-card-hover p-4">
            <p className="text-sm text-muted-foreground">Horizon</p>
            <p className="mt-1 text-xl font-semibold">{profileLabel(profile?.investment_horizon)}</p>
          </div>
          <div className="premium-card premium-card-hover p-4">
            <p className="text-sm text-muted-foreground">Planned amount</p>
            <p className="mt-1 text-xl font-semibold">{profileLabel(profile?.planned_investment_range)}</p>
          </div>
          <div className="premium-card premium-card-hover p-4">
            <p className="text-sm text-muted-foreground">Catalog assets</p>
            <p className="mt-1 text-xl font-semibold">{assets.length}</p>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="premium-card p-6">
            <h2 className="text-xl font-semibold">Financial roadmap</h2>
            <div className="mt-4 space-y-3">
              {roadmap.map((step, index) => (
                <div key={step} className="flex gap-3 rounded-lg border border-white/10 bg-background-primary/70 p-3">
                  <span className={index < 2 ? "text-emerald-300" : "text-muted-foreground"}>{index < 2 ? <CheckCircle2 size={18} /> : <Circle size={18} />}</span>
                  <p className="text-sm text-muted-foreground">{step}</p>
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm text-muted-foreground">{personalization.helper}</p>
          </div>

          <div className="premium-card p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">Recommended assets</h2>
                <p className="mt-1 text-sm text-muted-foreground">Rule-based matches from the backend asset catalog.</p>
              </div>
              <Link href="/assets" className="text-sm font-medium text-primary">Explore all</Link>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {assetsQuery.isLoading ? [1, 2, 3, 4].map((item) => <div key={item} className="h-32 animate-pulse rounded-lg border border-white/10 bg-background-primary/70" />) : recommendedAssets.map((asset) => (
                <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 transition hover:-translate-y-0.5 hover:border-primary/60 hover:shadow-glow">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{asset.ticker}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{asset.company_name}</p>
                    </div>
                    <span className="rounded-full border border-primary/30 px-2 py-1 text-xs text-primary">{asset.asset_type}</span>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">{getRecommendationReason(asset, profile)}</p>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section id="latest-news" className="premium-card p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold">Latest investment news</h2>
              <p className="mt-1 text-sm text-muted-foreground">Connected to the backend news API when available.</p>
            </div>
          </div>
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {newsQuery.isLoading ? [1, 2, 3, 4].map((item) => <div key={item} className="h-28 animate-pulse rounded-lg border border-white/10 bg-background-primary/70" />) : news.map((article) => (
              <article key={article.id} className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  <span>{article.source}</span>
                  <span>/</span>
                  <span>{formatDisplayDate(article.published_at)}</span>
                  {article.asset_tickers.length > 0 ? <span className="rounded-full border border-primary/30 px-2 py-0.5 text-primary">{article.asset_tickers[0]}</span> : null}
                </div>
                <h3 className="mt-2 text-base font-semibold">{article.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{article.summary}</p>
              </article>
            ))}
          </div>
        </section>
      </motion.div>
    </AppShell>
  );
}