/**
 * Top Navigation Bar Component
 * Header with user profile, theme toggle, and notifications
 */

"use client";

import React from "react";
import { useThemeStore } from "@/store";
import { Moon, Sun, Bell } from "lucide-react";

export function Navbar() {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <nav className="sticky top-0 h-16 bg-background-secondary border-b border-border z-20">
      <div className="h-full px-4 lg:px-6 flex items-center justify-between">
        {/* Left section - breadcrumb (future) */}
        <div className="flex-1" />

        {/* Right section - actions */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 hover:bg-background-tertiary rounded-lg smooth-transition">
            <Bell size={20} className="text-muted-foreground" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 hover:bg-background-tertiary rounded-lg smooth-transition"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          >
            {theme === "dark" ? (
              <Sun size={20} className="text-muted-foreground" />
            ) : (
              <Moon size={20} className="text-muted-foreground" />
            )}
          </button>

          {/* User Profile (placeholder) */}
          <button className="ml-2 px-3 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 smooth-transition text-sm font-medium">
            Profile
          </button>
        </div>
      </div>
    </nav>
  );
}
