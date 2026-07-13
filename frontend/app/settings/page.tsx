/**
 * Settings Page
 * User preferences and account settings
 */

"use client";

import Link from "next/link";
import React from "react";
import { motion } from "framer-motion";
import { AlertCircle, Lock, ShieldCheck, UserCircle } from "lucide-react";
import { AppShell } from "@/components/layout";
import { useAuthStore } from "@/store";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

const labelValue = (value: string | null | undefined) => {
  if (!value) return "Not set yet";
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
};

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const profile = useAuthStore((state) => state.investorProfile);

  return (
    <AppShell>
      <motion.div className="mx-auto max-w-5xl space-y-6" variants={container} initial="hidden" animate="show">
        <motion.div variants={item} className="premium-card p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="premium-badge mb-3"><ShieldCheck size={14} /> Account center</p>
              <h1 className="text-4xl font-bold">Settings</h1>
              <p className="mt-2 max-w-2xl text-muted-foreground">
                Review your account, investor profile, and security status. Profile edits are intentionally handled through onboarding until a dedicated profile editor is built.
              </p>
            </div>
            <Link href="/dashboard" className="premium-button-secondary w-full md:w-auto">
              Back to dashboard
            </Link>
          </div>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <motion.section variants={item} className="premium-card p-6">
            <div className="flex items-center gap-3">
              <span className="rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><UserCircle size={22} /></span>
              <div>
                <h2 className="text-xl font-semibold">Account</h2>
                <p className="text-sm text-muted-foreground">Your current signed-in identity.</p>
              </div>
            </div>
            <div className="mt-5 space-y-3">
              <InfoRow label="Email" value={user?.email ?? "Unavailable"} />
              <InfoRow label="Username" value={user?.username ?? "Not set yet"} />
              <InfoRow label="Account status" value={user?.is_active ? "Active" : "Unavailable"} tone={user?.is_active ? "success" : "neutral"} />
              <InfoRow label="Verified" value={user?.is_verified ? "Verified" : "Not verified yet"} tone={user?.is_verified ? "success" : "neutral"} />
            </div>
          </motion.section>

          <motion.section variants={item} className="premium-card p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">Investor profile</h2>
                <p className="mt-1 text-sm text-muted-foreground">This is the personalization context used across InvestGuide.</p>
              </div>
              {profile ? <span className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-200">Saved</span> : <span className="rounded-full border border-amber-400/25 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-100">Incomplete</span>}
            </div>
            {profile ? (
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <InfoRow label="Experience" value={labelValue(profile.experience_level)} />
                <InfoRow label="Risk appetite" value={labelValue(profile.risk_appetite)} />
                <InfoRow label="Horizon" value={labelValue(profile.investment_horizon)} />
                <InfoRow label="Planned range" value={labelValue(profile.planned_investment_range)} />
                <InfoRow label="Preferred assets" value={profile.preferred_asset_types.length ? profile.preferred_asset_types.map(labelValue).join(", ") : "Not set yet"} />
                <InfoRow label="Goals" value={profile.investment_goals.length ? profile.investment_goals.map(labelValue).join(", ") : "Not set yet"} />
              </div>
            ) : (
              <div className="mt-5 rounded-lg border border-dashed border-border bg-background-primary/60 p-5">
                <h3 className="text-base font-semibold">No investor profile found</h3>
                <p className="mt-2 text-sm text-muted-foreground">Complete onboarding so the dashboard can adapt its explanations, roadmap, and asset discovery to you.</p>
                <Link href="/onboarding" className="premium-button-primary mt-4">Complete onboarding</Link>
              </div>
            )}
          </motion.section>
        </div>

        <motion.section variants={item} className="grid gap-6 md:grid-cols-2">
          <StatusCard
            icon={<Lock size={20} />}
            title="Security"
            description="Password changes, device management, and stronger session controls are planned for a future auth hardening sprint. Your current session uses the backend JWT foundation."
            status="Coming later"
          />
          <StatusCard
            icon={<AlertCircle size={20} />}
            title="Notifications"
            description="Email alerts, digests, watchlist alerts, and price notifications are not enabled yet. This page will expose them only after the backend notification system exists."
            status="Not started"
          />
        </motion.section>

        <motion.section variants={item} className="premium-card p-6">
          <h2 className="text-xl font-semibold">What should I do next?</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Link href="/dashboard" className="rounded-lg border border-white/10 bg-background-primary/70 p-4 smooth-transition hover:border-primary/50">
              <p className="font-semibold">Review dashboard</p>
              <p className="mt-1 text-sm text-muted-foreground">See your current profile and roadmap.</p>
            </Link>
            <Link href="/assets" className="rounded-lg border border-white/10 bg-background-primary/70 p-4 smooth-transition hover:border-primary/50">
              <p className="font-semibold">Browse assets</p>
              <p className="mt-1 text-sm text-muted-foreground">Explore persisted market data.</p>
            </Link>
            <Link href="/education" className="rounded-lg border border-white/10 bg-background-primary/70 p-4 smooth-transition hover:border-primary/50">
              <p className="font-semibold">Continue learning</p>
              <p className="mt-1 text-sm text-muted-foreground">Build confidence before decisions.</p>
            </Link>
          </div>
        </motion.section>
      </motion.div>
    </AppShell>
  );
}

function InfoRow({ label, value, tone = "neutral" }: { label: string; value: string; tone?: "neutral" | "success" }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={tone === "success" ? "mt-1 font-semibold text-emerald-200" : "mt-1 break-words font-semibold"}>{value}</p>
    </div>
  );
}

function StatusCard({ icon, title, description, status }: { icon: React.ReactNode; title: string; description: string; status: string }) {
  return (
    <div className="premium-card p-6">
      <div className="flex items-start gap-3">
        <span className="rounded-lg border border-white/10 bg-background-primary/70 p-3 text-primary">{icon}</span>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-xl font-semibold">{title}</h2>
            <span className="rounded-full border border-white/10 bg-background-primary/70 px-2 py-0.5 text-xs text-muted-foreground">{status}</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </div>
  );
}