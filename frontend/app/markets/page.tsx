"use client";

import { AppShell } from "@/components/layout";
import { AssetExplorer } from "@/features/assets/asset-explorer";
import { motion } from "framer-motion";

export default function MarketsPage() {
  return (
    <AppShell>
      <motion.div className="space-y-6" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="mb-2 text-4xl font-bold">Markets</h1>
          <p className="text-muted-foreground">Explore backend-connected investment opportunities across Zimbabwean exchanges with a beginner-friendly market lens.</p>
        </div>
        <AssetExplorer />
      </motion.div>
    </AppShell>
  );
}