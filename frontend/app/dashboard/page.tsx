"use client";

import Link from "next/link";
import { AppShell } from "@/components/layout";
import { useAuthStore } from "@/store";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { buildRecommendedAssets, buildRoadmap, DEMO_ASSETS, DEMO_NEWS, getPersonalizationCopy } from "@/utils/demo-content";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function DashboardPage() {
  const investorProfile = useAuthStore((state) => state.investorProfile);
  const personalization = getPersonalizationCopy(investorProfile);
  const roadmap = buildRoadmap(investorProfile);
  const recommendations = buildRecommendedAssets(investorProfile);

  return (
    <AppShell>
      <motion.div className="space-y-6" variants={container} initial="hidden" animate="show">
        <motion.div variants={item} className="rounded-lg border border-border bg-card p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Welcome back</p>
              <h1 className="mt-2 text-4xl font-bold">Good morning, {investorProfile ? "investor" : "friend"}.</h1>
              <p className="mt-3 max-w-2xl text-muted-foreground">{personalization.intro}</p>
            </div>
            <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
              <div className="flex items-center gap-2 font-semibold">
                <Sparkles size={16} />
                {investorProfile?.risk_appetite ?? "moderate"} risk profile
              </div>
              <p className="mt-1 text-primary/80">{personalization.helper}</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Investment horizon</p>
              <p className="mt-2 font-semibold">{investorProfile?.investment_horizon ?? "long_term"}</p>
            </div>
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Risk appetite</p>
              <p className="mt-2 font-semibold">{investorProfile?.risk_appetite ?? "moderate"}</p>
            </div>
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Preferred types</p>
              <p className="mt-2 font-semibold">{investorProfile?.preferred_asset_types?.join(", ") ?? "zse, reits"}</p>
            </div>
            <div className="rounded-lg border border-border bg-background-secondary p-4">
              <p className="text-sm text-muted-foreground">Experience</p>
              <p className="mt-2 font-semibold">{investorProfile?.experience_level ?? "beginner"}</p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={item} className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-2xl font-semibold">Financial roadmap</h2>
              <span className="rounded-full border border-border px-3 py-1 text-sm text-muted-foreground">Rule-based</span>
            </div>
            <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
              {roadmap.map((step) => (
                <li key={step} className="rounded-lg border border-border bg-background-secondary p-3">{step}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-2xl font-semibold">Recommended assets</h2>
              <Link href="/assets" className="text-sm font-medium text-primary">Explore all</Link>
            </div>
            <div className="mt-4 space-y-3">
              {recommendations.map((asset) => (
                <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="flex items-center justify-between rounded-lg border border-border bg-background-secondary p-3">
                  <div>
                    <p className="font-medium">{asset.company_name}</p>
                    <p className="text-sm text-muted-foreground">{asset.ticker} · {asset.sector}</p>
                  </div>
                  <ArrowRight size={16} className="text-primary" />
                </Link>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div variants={item} className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
          <div className="rounded-lg border border-border bg-card p-6">
            <h2 className="text-2xl font-semibold">Featured news</h2>
            <div className="mt-4 space-y-3">
              {DEMO_NEWS.map((item) => (
                <div key={item.id} className="rounded-lg border border-border bg-background-secondary p-4">
                  <p className="font-medium">{item.title}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{item.source} · {item.published_at}</p>
                  <p className="mt-2 text-sm">{item.summary}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <h2 className="text-2xl font-semibold">Asset explorer</h2>
            <div className="mt-4 space-y-3">
              {DEMO_ASSETS.slice(0, 4).map((asset) => (
                <Link key={asset.ticker} href={`/assets/${asset.ticker.toLowerCase()}`} className="flex items-center justify-between rounded-lg border border-border bg-background-secondary p-3">
                  <div>
                    <p className="font-medium">{asset.ticker}</p>
                    <p className="text-sm text-muted-foreground">{asset.company_name}</p>
                  </div>
                  <span className="text-sm text-muted-foreground">{asset.exchange}</span>
                </Link>
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
