/**
 * Markets Page
 * Browse and explore ZSE, VFEX, and REIT markets
 */

"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout";
import { CardSkeleton } from "@/components/skeleton";
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

  return (
    <AppShell>
      <motion.div
        className="space-y-6"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {/* Page Header */}
        <motion.div variants={item}>
          <h1 className="text-4xl font-bold mb-2">Markets</h1>
          <p className="text-muted-foreground">
            Explore investment opportunities across Zimbabwean exchanges
          </p>
        </motion.div>

        {/* Exchange Selector */}
        <motion.div variants={item} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {EXCHANGES.map((exchange) => (
              <button
                key={exchange.id}
                onClick={() => setActiveExchange(exchange.id)}
                className={`p-4 rounded-lg border-2 smooth-transition text-left ${
                  activeExchange === exchange.id
                    ? "border-primary bg-primary/10"
                    : "border-border hover:border-primary/50"
                }`}
              >
                <h3 className="font-semibold text-lg">{exchange.label}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {exchange.description}
                </p>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div variants={item} className="space-y-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <h2 className="font-semibold mb-4">Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Sector
                </label>
                <select className="w-full mt-2 px-3 py-2 bg-background-tertiary border border-border rounded-lg smooth-transition">
                  <option>All Sectors</option>
                  <option>Banking</option>
                  <option>Mining</option>
                  <option>Retail</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Risk Level
                </label>
                <select className="w-full mt-2 px-3 py-2 bg-background-tertiary border border-border rounded-lg smooth-transition">
                  <option>All Risk Levels</option>
                  <option>Low</option>
                  <option>Moderate</option>
                  <option>High</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Sort By
                </label>
                <select className="w-full mt-2 px-3 py-2 bg-background-tertiary border border-border rounded-lg smooth-transition">
                  <option>Market Cap</option>
                  <option>Price Change</option>
                  <option>Dividend Yield</option>
                  <option>Volatility</option>
                </select>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Assets Grid */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">
            {EXCHANGES.find((e) => e.id === activeExchange)?.label} Assets
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
