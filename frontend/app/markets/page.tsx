"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout";
import { DEMO_ASSETS } from "@/utils/demo-content";
import { motion } from "framer-motion";

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

const EXCHANGES = [
  { id: "zse", label: "ZSE", description: "Zimbabwe Stock Exchange" },
  { id: "vfex", label: "VFEX", description: "Victoria Falls Stock Exchange" },
  { id: "reits", label: "REITs", description: "Real Estate Investment Trusts" },
];

export default function MarketsPage() {
  const [activeExchange, setActiveExchange] = useState("zse");

  const visibleAssets = useMemo(() => {
    if (activeExchange === "vfex") {
      return DEMO_ASSETS.filter((asset) => asset.exchange === "VFEX");
    }
    if (activeExchange === "reits") {
      return DEMO_ASSETS.filter((asset) => asset.asset_type === "REIT");
    }
    return DEMO_ASSETS.filter((asset) => asset.exchange === "ZSE");
  }, [activeExchange]);

  return (
    <AppShell>
      <motion.div className="space-y-6" variants={container} initial="hidden" animate="show">
        <motion.div variants={item}>
          <h1 className="mb-2 text-4xl font-bold">Markets</h1>
          <p className="text-muted-foreground">Explore investment opportunities across Zimbabwean exchanges with a beginner-friendly market lens.</p>
        </motion.div>

        <motion.div variants={item} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            {EXCHANGES.map((exchange) => (
              <button
                key={exchange.id}
                onClick={() => setActiveExchange(exchange.id)}
                className={`rounded-lg border-2 p-4 text-left smooth-transition ${
                  activeExchange === exchange.id
                    ? "border-primary bg-primary/10"
                    : "border-border hover:border-primary/50"
                }`}
              >
                <h3 className="text-lg font-semibold">{exchange.label}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{exchange.description}</p>
              </button>
            ))}
          </div>
        </motion.div>

        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">{EXCHANGES.find((exchange) => exchange.id === activeExchange)?.label} assets</h2>
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
                <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                  <p>Type: {asset.asset_type}</p>
                  <p>Sector: {asset.sector}</p>
                  <p>Exchange: {asset.exchange}</p>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
