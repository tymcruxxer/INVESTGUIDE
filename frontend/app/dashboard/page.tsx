/**
 * Dashboard Page
 * Main dashboard displaying market overview and AI insights
 */

"use client";

import React from "react";
import { AppShell } from "@/components/layout";
import { CardSkeleton, ChartSkeleton } from "@/components/skeleton";
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

export default function DashboardPage() {
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
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            AI-powered market intelligence and investment insights
          </p>
        </motion.div>

        {/* Market Overview Section */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Market Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </motion.div>

        {/* Charts Section */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Performance Analytics</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ChartSkeleton />
            <ChartSkeleton />
          </div>
        </motion.div>

        {/* AI Insights Section */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">AI Insights</h2>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </motion.div>

        {/* Top Movers Section */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Top Movers</h2>
          <div className="bg-card rounded-lg border border-border p-6">
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-muted rounded animate-pulse" />
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
