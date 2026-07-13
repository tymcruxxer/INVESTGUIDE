/**
 * Education Hub Page
 * Educational content about investing and financial concepts
 */

"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BookOpen, FileText, GraduationCap, Video } from "lucide-react";
import { AppShell } from "@/components/layout";

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

const EDUCATION_CATEGORIES = [
  {
    id: "basics",
    title: "Investing Basics",
    description: "Understand shares, REITs, bonds, risk, and why time horizon matters.",
    icon: BookOpen,
    next: "Start with what owning a share actually means.",
  },
  {
    id: "markets",
    title: "Zimbabwean Markets",
    description: "Learn how ZSE, VFEX, currency, inflation, and liquidity affect research.",
    icon: FileText,
    next: "Compare ZSE and VFEX exposure before choosing assets.",
  },
  {
    id: "analysis",
    title: "Company Analysis",
    description: "Read company pages with a better sense of sector, quality, and risks.",
    icon: Video,
    next: "Open an asset page and read the Explain Like I am 18 section.",
  },
];

const FEATURED_TOPICS = [
  {
    title: "What is a ticker?",
    purpose: "Tickers are short market codes, but the real job is understanding the company behind the code.",
    action: "Try searching DLTA or Delta from the top navigation.",
    href: "/company/delta",
  },
  {
    title: "Why liquidity matters",
    purpose: "If few people are buying and selling, it can be harder to exit when you need cash.",
    action: "Use asset pages to watch for liquidity context as data improves.",
    href: "/assets",
  },
  {
    title: "REITs in plain English",
    purpose: "REITs expose investors to property income themes, but occupancy and property quality still matter.",
    action: "Search REIT in the asset explorer.",
    href: "/assets",
  },
  {
    title: "Assessment versus advice",
    purpose: "InvestGuide assessments are educational context. They should help you ask better questions, not replace judgment.",
    action: "Open an assessment and review the evidence strength.",
    href: "/assets/delta",
  },
];

export default function EducationPage() {
  return (
    <AppShell>
      <motion.div className="space-y-6" variants={container} initial="hidden" animate="show">
        <motion.section variants={item} className="premium-card p-6">
          <p className="premium-badge mb-3"><GraduationCap size={14} /> Learning foundation</p>
          <h1 className="text-4xl font-bold">Education Hub</h1>
          <p className="mt-2 max-w-3xl text-muted-foreground">
            Build enough financial confidence to understand what you are looking at, why it matters, and what to research next. Structured lessons are coming later; for now, these guides point you toward the best current product surfaces.
          </p>
        </motion.section>

        <motion.section variants={item} className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Learning paths</h2>
              <p className="mt-1 text-sm text-muted-foreground">Choose a starting point based on the question you are trying to answer.</p>
            </div>
            <Link href="/assets" className="text-sm font-medium text-primary hover:text-blue-300">Apply learning in Asset Explorer</Link>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {EDUCATION_CATEGORIES.map((category) => {
              const Icon = category.icon;
              return (
                <div key={category.id} className="premium-card premium-card-hover p-6">
                  <Icon size={32} className="mb-4 text-primary" />
                  <h3 className="mb-2 text-lg font-semibold">{category.title}</h3>
                  <p className="text-sm text-muted-foreground">{category.description}</p>
                  <p className="mt-4 rounded-lg border border-white/10 bg-background-primary/70 p-3 text-sm text-slate-200">{category.next}</p>
                </div>
              );
            })}
          </div>
        </motion.section>

        <motion.section variants={item} className="premium-card p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-semibold">Featured topics</h2>
              <p className="mt-1 text-sm text-muted-foreground">Short, practical explanations linked to places you can explore right now.</p>
            </div>
            <span className="rounded-full border border-amber-400/25 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-100">Curriculum coming soon</span>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {FEATURED_TOPICS.map((topic) => (
              <Link key={topic.title} href={topic.href} className="rounded-lg border border-white/10 bg-background-primary/70 p-4 smooth-transition hover:-translate-y-0.5 hover:border-primary/50">
                <h3 className="text-base font-semibold">{topic.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{topic.purpose}</p>
                <p className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-primary">{topic.action} <ArrowRight size={15} /></p>
              </Link>
            ))}
          </div>
        </motion.section>

        <motion.section variants={item} className="rounded-lg border border-dashed border-border bg-card/80 p-6">
          <h2 className="text-xl font-semibold">No formal lessons yet</h2>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            The learning platform, quizzes, progress tracking, and adaptive lessons are intentionally not implemented yet. Use this page as a guided map into the current dashboard, assets, company pages, assessments, and comparison tools.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link href="/dashboard" className="premium-button-secondary">Go to dashboard</Link>
            <Link href="/compare" className="premium-button-secondary">Compare assets</Link>
          </div>
        </motion.section>
      </motion.div>
    </AppShell>
  );
}