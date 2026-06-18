/**
 * Education Hub Page
 * Educational content about investing and financial concepts
 */

"use client";

import React from "react";
import { AppShell } from "@/components/layout";
import { CardSkeleton } from "@/components/skeleton";
import { motion } from "framer-motion";
import { BookOpen, Video, FileText } from "lucide-react";

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

const EDUCATION_CATEGORIES = [
  {
    id: "basics",
    title: "Investing Basics",
    description: "Learn the fundamentals of stock investing",
    icon: BookOpen,
  },
  {
    id: "markets",
    title: "Zimbabwean Markets",
    description: "Understanding ZSE, VFEX, and local investing",
    icon: FileText,
  },
  {
    id: "analysis",
    title: "Financial Analysis",
    description: "How to read and interpret financial statements",
    icon: Video,
  },
];

export default function EducationPage() {
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
          <h1 className="text-4xl font-bold mb-2">Education Hub</h1>
          <p className="text-muted-foreground">
            Learn about investing, financial analysis, and Zimbabwean markets
          </p>
        </motion.div>

        {/* Category Grid */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Learning Paths</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {EDUCATION_CATEGORIES.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  className="text-left p-6 bg-card border border-border rounded-lg hover:border-primary/50 smooth-transition group"
                >
                  <Icon size={32} className="mb-4 text-primary group-hover:scale-110 smooth-transition" />
                  <h3 className="text-lg font-semibold mb-2">{category.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {category.description}
                  </p>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Featured Content */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Featured Content</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </motion.div>

        {/* Latest Articles */}
        <motion.div variants={item} className="space-y-4">
          <h2 className="text-2xl font-semibold">Latest Articles</h2>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
