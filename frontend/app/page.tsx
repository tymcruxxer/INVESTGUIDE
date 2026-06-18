/**
 * Landing Page
 * Public landing page for unauthenticated users
 */

"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  TrendingUp,
  BarChart3,
  Brain,
  Globe,
  ArrowRight,
} from "lucide-react";

const features = [
  {
    icon: TrendingUp,
    title: "Market Intelligence",
    description: "Real-time analytics on ZSE, VFEX, and REIT markets",
  },
  {
    icon: Brain,
    title: "AI-Powered Insights",
    description: "Get intelligent investment recommendations powered by AI",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Professional-grade financial analysis tools",
  },
  {
    icon: Globe,
    title: "Zimbabwe-Focused",
    description: "Built specifically for Zimbabwean investment markets",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function Home() {
  return (
    <div className="min-h-screen bg-background-primary">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border bg-background-secondary/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-gradient">
            InvestGuide
          </Link>
          <div className="flex gap-4">
            <Link
              href="/auth/login"
              className="px-4 py-2 text-foreground hover:text-primary smooth-transition"
            >
              Login
            </Link>
            <Link
              href="/auth/register"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 smooth-transition font-medium"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <motion.section
        className="py-20 px-6"
        initial="hidden"
        whileInView="show"
        variants={container}
        viewport={{ once: true }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <motion.h1
            className="text-5xl lg:text-6xl font-bold mb-6 text-gradient"
            variants={item}
          >
            AI-Powered Investment Intelligence for Zimbabwe
          </motion.h1>
          <motion.p
            className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto"
            variants={item}
          >
            Make smarter investment decisions with institutional-grade analytics,
            real-time market intelligence, and AI-powered insights tailored for
            Zimbabwean markets.
          </motion.p>
          <motion.div
            className="flex gap-4 justify-center flex-wrap"
            variants={item}
          >
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 font-medium smooth-transition flex items-center gap-2"
            >
              Start Free Trial <ArrowRight size={20} />
            </Link>
            <Link
              href="#features"
              className="px-8 py-3 border border-border rounded-lg hover:bg-background-secondary smooth-transition font-medium"
            >
              Learn More
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        id="features"
        className="py-20 px-6 bg-background-secondary"
        initial="hidden"
        whileInView="show"
        variants={container}
        viewport={{ once: true }}
      >
        <div className="max-w-6xl mx-auto">
          <motion.h2
            className="text-4xl font-bold text-center mb-12"
            variants={item}
          >
            Powerful Features
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={i}
                  className="p-6 bg-card rounded-lg border border-border hover:border-primary/50 smooth-transition"
                  variants={item}
                >
                  <Icon size={32} className="text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        className="py-20 px-6"
        initial="hidden"
        whileInView="show"
        variants={container}
        viewport={{ once: true }}
      >
        <div className="max-w-2xl mx-auto text-center bg-card border border-border rounded-lg p-12">
          <motion.h2
            className="text-3xl font-bold mb-6"
            variants={item}
          >
            Ready to Start Investing Smarter?
          </motion.h2>
          <motion.p
            className="text-muted-foreground mb-8 text-lg"
            variants={item}
          >
            Join thousands of Zimbabwean investors using InvestGuide to make
            data-driven investment decisions.
          </motion.p>
          <motion.div variants={item}>
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 font-medium smooth-transition inline-flex items-center gap-2"
            >
              Get Started Free <ArrowRight size={20} />
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-6 bg-background-secondary">
        <div className="max-w-6xl mx-auto text-center text-muted-foreground text-sm">
          <p>© 2024 InvestGuide. All rights reserved.</p>
          <p className="mt-2">
            InvestGuide is an educational investment intelligence platform, not a
            licensed financial advisor.
          </p>
        </div>
      </footer>
    </div>
  );
}
