/**
 * Landing Page
 * Public landing page for unauthenticated users
 */

"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BarChart3, BookOpen, Building2, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";

const features = [
  { icon: TrendingUp, title: "Market intelligence", description: "Track ZSE, VFEX, REITs, macro signals, and company context in one clean workspace." },
  { icon: Building2, title: "Company research", description: "Move beyond ticker lists with issuer-level profiles, related assets, and news context." },
  { icon: BarChart3, title: "Assessment framework", description: "Structured, deterministic investment assessments without pretending to predict the future." },
  { icon: BookOpen, title: "Adaptive education", description: "Beginner-friendly explanations that grow in depth as your confidence improves." },
];

const metrics = [
  ["9", "seeded assets"],
  ["9", "company profiles"],
  ["14", "app routes"],
  ["DRY", "safe ingestion"],
];

const companies = ["Delta", "Econet", "CBZ", "Innscor", "Tigere REIT", "Seed Co"];

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.12 } } };
const item = { hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0 } };

export default function Home() {
  return (
    <div className="min-h-screen bg-background-primary text-foreground">
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-background-secondary/95 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-6">
          <Link href="/" className="text-2xl font-bold text-gradient">InvestGuide</Link>
          <div className="flex items-center gap-2 sm:gap-3">
            <Link href="/auth/login" className="rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-background-tertiary hover:text-foreground smooth-transition">Login</Link>
            <Link href="/auth/signup" className="premium-button-primary py-2 text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      <motion.section className="px-5 py-16 sm:px-6 lg:py-24" initial="hidden" animate="show" variants={container}>
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <motion.div variants={item} className="premium-badge text-emerald-300"><ShieldCheck size={14} /> Financial intelligence for serious investors</motion.div>
            <motion.h1 variants={item} className="mt-6 max-w-4xl text-5xl font-bold leading-[1.02] tracking-tight sm:text-6xl lg:text-7xl">
              Invest smarter. <span className="text-gradient">Understand faster.</span>
            </motion.h1>
            <motion.p variants={item} className="mt-6 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
              A premium Zimbabwe-focused investment intelligence platform that makes company research, market context, and investor education feel clear, calm, and actionable.
            </motion.p>
            <motion.div variants={item} className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/auth/signup" className="premium-button-primary px-6">Create free account <ArrowRight size={18} /></Link>
              <Link href="#features" className="premium-button-secondary px-6">Explore the platform</Link>
            </motion.div>
            <motion.div variants={item} className="mt-8 flex flex-wrap gap-2">
              {companies.map((company) => <span key={company} className="premium-badge">{company}</span>)}
            </motion.div>
          </div>

          <motion.div variants={item} className="premium-card p-4 sm:p-5">
            <div className="rounded-lg border border-white/10 bg-background-primary/70 p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Portfolio-style preview</p>
                  <p className="mt-1 text-3xl font-bold">$24,230.50</p>
                  <p className="mt-1 text-sm text-emerald-300">+12.3% simulated growth</p>
                </div>
                <span className="rounded-lg bg-emerald-500/10 p-3 text-emerald-300"><TrendingUp size={24} /></span>
              </div>
              <div className="mt-6 h-40 rounded-lg border border-emerald-400/20 bg-[linear-gradient(180deg,rgba(20,184,166,0.16),rgba(15,23,42,0.1))] p-4">
                <svg viewBox="0 0 360 120" className="h-full w-full" aria-hidden="true">
                  <path d="M0 92 C40 86 48 70 78 76 C106 82 113 48 145 55 C174 61 182 34 214 44 C250 55 256 26 288 30 C321 34 330 18 360 20" fill="none" stroke="#14B8A6" strokeWidth="4" strokeLinecap="round" />
                  <path d="M0 112 C40 106 48 90 78 96 C106 102 113 68 145 75 C174 81 182 54 214 64 C250 75 256 46 288 50 C321 54 330 38 360 40 L360 120 L0 120 Z" fill="rgba(20,184,166,0.12)" />
                </svg>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                {["ZSE", "VFEX", "REITs"].map((label, index) => (
                  <div key={label} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3">
                    <p className="text-xs text-muted-foreground">{label}</p>
                    <p className="mt-1 font-semibold text-emerald-300">+{(index + 1) * 1.4}%</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </motion.section>

      <section className="border-y border-white/10 bg-background-secondary/50 px-5 py-8 sm:px-6">
        <div className="mx-auto grid max-w-7xl gap-3 sm:grid-cols-4">
          {metrics.map(([value, label]) => <div key={label} className="rounded-lg border border-white/10 bg-background-primary/60 p-4"><p className="text-2xl font-bold text-foreground">{value}</p><p className="text-sm text-muted-foreground">{label}</p></div>)}
        </div>
      </section>

      <motion.section id="features" className="px-5 py-16 sm:px-6 lg:py-20" initial="hidden" whileInView="show" variants={container} viewport={{ once: true }}>
        <div className="mx-auto max-w-7xl">
          <motion.div variants={item} className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary">Why InvestGuide</p>
            <h2 className="mt-3 text-4xl font-bold">Research, learn, and decide with more confidence.</h2>
          </motion.div>
          <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => {
              const Icon = feature.icon;
              return <motion.div key={feature.title} variants={item} className="premium-card premium-card-hover p-6"><Icon size={30} className="text-primary" /><h3 className="mt-5 text-lg font-semibold">{feature.title}</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.description}</p></motion.div>;
            })}
          </div>
        </div>
      </motion.section>

      <section className="px-5 pb-16 sm:px-6 lg:pb-24">
        <div className="mx-auto grid max-w-7xl gap-4 lg:grid-cols-3">
          {["Create your investor profile", "Explore companies and assets", "Learn with clear explanations"].map((step, index) => (
            <div key={step} className="premium-card p-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">{index + 1}</div>
              <h3 className="mt-5 text-xl font-semibold">{step}</h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">InvestGuide keeps the experience structured, beginner-friendly, and transparent at every step.</p>
            </div>
          ))}
        </div>
      </section>

      <section className="px-5 pb-20 sm:px-6">
        <div className="premium-card mx-auto max-w-4xl p-8 text-center sm:p-10">
          <Sparkles className="mx-auto text-teal-300" size={32} />
          <h2 className="mt-5 text-3xl font-bold">Ready to make investing feel less intimidating?</h2>
          <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">Start with secure signup, complete onboarding, and enter a dashboard shaped around your investor profile.</p>
          <Link href="/auth/signup" className="premium-button-primary mt-7 px-7">Get Started Free <ArrowRight size={18} /></Link>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-background-secondary/70 px-5 py-10 sm:px-6">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <p>(c) 2024 InvestGuide. Educational investment intelligence, not financial advice.</p>
          <div className="flex gap-4"><span>Trust</span><span>Clarity</span><span>Education</span></div>
        </div>
      </footer>
    </div>
  );
}