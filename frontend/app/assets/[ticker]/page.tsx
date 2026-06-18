/**
 * Assets Page - Asset Detail
 * Display detailed information about a specific asset
 */

"use client";

import React from "react";
import { AppShell } from "@/components/layout";
import { ChartSkeleton, CardSkeleton, Skeleton } from "@/components/skeleton";
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

interface AssetDetailPageProps {
  params: {
    ticker: string;
  };
}

export default function AssetDetailPage({ params: _params }: AssetDetailPageProps) {
  return (
    <AppShell>
      <motion.div
        className="space-y-6"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {/* Asset Header */}
        <motion.div variants={item} className="bg-card border border-border rounded-lg p-6">
          <div className="space-y-4">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-6 w-48" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i}>
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-6 w-32" />
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Price Chart */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Price Chart</h2>
          <ChartSkeleton />
        </motion.div>

        {/* Main Grid */}
        <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI Summary */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">AI Summary</h2>
              <CardSkeleton />
            </div>

            {/* Key Metrics */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Key Metrics</h2>
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="grid grid-cols-2 gap-6">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i}>
                      <Skeleton className="h-4 w-24 mb-2" />
                      <Skeleton className="h-6 w-32" />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Sentiment Analysis */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Sentiment Analysis</h2>
              <CardSkeleton />
            </div>

            {/* News */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Latest News</h2>
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <CardSkeleton key={i} />
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Add to Watchlist */}
            <button className="w-full px-4 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 smooth-transition">
              Add to Watchlist
            </button>

            {/* Risk Indicator */}
            <CardSkeleton />

            {/* Macroeconomic Exposure */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Macro Exposure</h2>
              <CardSkeleton />
            </div>

            {/* Comparison */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Similar Assets</h2>
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
