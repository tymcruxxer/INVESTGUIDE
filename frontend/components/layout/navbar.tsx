/**
 * Top Navigation Bar Component
 * Header with user profile, theme toggle, and notifications
 */

"use client";

import React from "react";
import { Bell, Moon, Sun, UserCircle } from "lucide-react";
import { useAuthStore, useThemeStore } from "@/store";

export function Navbar() {
  const { theme, toggleTheme } = useThemeStore();
  const user = useAuthStore((state) => state.user);

  return (
    <nav className="sticky top-0 z-20 h-16 border-b border-border bg-background-secondary">
      <div className="flex h-full items-center justify-between px-4 lg:px-6">
        <div className="flex-1" />
        <div className="flex items-center gap-3">
          <button
            className="relative rounded-lg p-2 smooth-transition hover:bg-background-tertiary"
            aria-label="Notifications"
          >
            <Bell size={20} className="text-muted-foreground" />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-destructive" />
          </button>
          <button
            onClick={toggleTheme}
            className="rounded-lg p-2 smooth-transition hover:bg-background-tertiary"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            aria-label="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun size={20} className="text-muted-foreground" />
            ) : (
              <Moon size={20} className="text-muted-foreground" />
            )}
          </button>
          <div className="ml-1 flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-2 text-sm font-medium text-primary">
            <UserCircle size={18} />
            <span className="max-w-[180px] truncate">{user?.email ?? "Investor"}</span>
          </div>
        </div>
      </div>
    </nav>
  );
}
