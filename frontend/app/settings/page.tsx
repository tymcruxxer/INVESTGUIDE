/**
 * Settings Page
 * User preferences and account settings
 */

"use client";

import React from "react";
import { AppShell } from "@/components/layout";
import { Skeleton } from "@/components/skeleton";
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

export default function SettingsPage() {
  return (
    <AppShell>
      <motion.div
        className="space-y-6 max-w-3xl"
        variants={container}
        initial="hidden"
        animate="show"
      >
        {/* Page Header */}
        <motion.div variants={item}>
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account preferences and settings
          </p>
        </motion.div>

        {/* Profile Section */}
        <motion.div
          variants={item}
          className="bg-card border border-border rounded-lg p-6 space-y-6"
        >
          <div>
            <h2 className="text-2xl font-semibold mb-6">Profile Settings</h2>

            <div className="space-y-6">
              {/* Name */}
              <div>
                <label className="text-sm font-medium">Full Name</label>
                <Skeleton className="mt-2 h-10" />
              </div>

              {/* Email */}
              <div>
                <label className="text-sm font-medium">Email Address</label>
                <Skeleton className="mt-2 h-10" />
              </div>

              {/* Risk Profile */}
              <div>
                <label className="text-sm font-medium">Risk Profile</label>
                <div className="mt-4 space-y-3">
                  {["Conservative", "Moderate", "Aggressive"].map((risk) => (
                    <label
                      key={risk}
                      className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-background-tertiary smooth-transition"
                    >
                      <input
                        type="radio"
                        name="risk"
                        value={risk}
                        className="mr-3"
                      />
                      <span>{risk}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Experience Level */}
              <div>
                <label className="text-sm font-medium">Experience Level</label>
                <div className="mt-4 space-y-3">
                  {["Beginner", "Intermediate", "Advanced"].map((level) => (
                    <label
                      key={level}
                      className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-background-tertiary smooth-transition"
                    >
                      <input
                        type="radio"
                        name="level"
                        value={level}
                        className="mr-3"
                      />
                      <span>{level}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 smooth-transition">
                Save Changes
              </button>
            </div>
          </div>
        </motion.div>

        {/* Preferences Section */}
        <motion.div
          variants={item}
          className="bg-card border border-border rounded-lg p-6 space-y-6"
        >
          <h2 className="text-2xl font-semibold">Preferences</h2>

          <div className="space-y-4">
            {/* Notifications */}
            <div className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="font-medium">Email Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive alerts and updates via email
                </p>
              </div>
              <input type="checkbox" className="w-5 h-5" defaultChecked />
            </div>

            {/* News Digest */}
            <div className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="font-medium">Daily News Digest</p>
                <p className="text-sm text-muted-foreground">
                  Receive curated market news daily
                </p>
              </div>
              <input type="checkbox" className="w-5 h-5" defaultChecked />
            </div>

            {/* Analytics Reports */}
            <div className="flex items-center justify-between p-3 border border-border rounded-lg">
              <div>
                <p className="font-medium">Weekly Analytics Reports</p>
                <p className="text-sm text-muted-foreground">
                  Get personalized market analysis weekly
                </p>
              </div>
              <input type="checkbox" className="w-5 h-5" />
            </div>
          </div>
        </motion.div>

        {/* Security Section */}
        <motion.div
          variants={item}
          className="bg-card border border-border rounded-lg p-6 space-y-6"
        >
          <h2 className="text-2xl font-semibold">Security</h2>

          <div className="space-y-4">
            <button className="w-full px-6 py-3 border border-border rounded-lg hover:bg-background-tertiary smooth-transition text-left">
              Change Password
            </button>
            <button className="w-full px-6 py-3 border border-border rounded-lg hover:bg-background-tertiary smooth-transition text-left">
              Two-Factor Authentication
            </button>
          </div>
        </motion.div>

        {/* Danger Zone */}
        <motion.div
          variants={item}
          className="bg-destructive/10 border border-destructive/20 rounded-lg p-6"
        >
          <h2 className="text-2xl font-semibold text-destructive mb-4">
            Danger Zone
          </h2>
          <button className="px-6 py-2 bg-destructive text-destructive-foreground rounded-lg font-medium hover:bg-destructive/90 smooth-transition">
            Delete Account
          </button>
        </motion.div>
      </motion.div>
    </AppShell>
  );
}
