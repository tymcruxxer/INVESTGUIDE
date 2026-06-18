/**
 * Navigation Sidebar Component
 * Left sidebar with navigation links and branding
 */

"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/utils";
import { useUIStore } from "@/store";
import {
  BarChart3,
  TrendingUp,
  Briefcase,
  BookOpen,
  Settings,
  LogOut,
  Menu,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: BarChart3,
  },
  {
    href: "/markets",
    label: "Markets",
    icon: TrendingUp,
  },
  {
    href: "/assets",
    label: "Assets",
    icon: Briefcase,
  },
  {
    href: "/ai-assistant",
    label: "AI Assistant",
    icon: BarChart3,
  },
  {
    href: "/education",
    label: "Education",
    icon: BookOpen,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <>
      {/* Mobile Sidebar Toggle */}
      <button
        onClick={toggleSidebar}
        className="lg:hidden fixed top-4 left-4 z-40 p-2 bg-primary text-primary-foreground rounded-lg"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen w-64 bg-background-secondary border-r border-border smooth-transition z-40",
          "lg:translate-x-0 lg:relative",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold text-gradient">InvestGuide</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Investment Intelligence
          </p>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg smooth-transition",
                  isActive
                    ? "bg-primary text-primary-foreground font-medium"
                    : "text-muted-foreground hover:bg-background-tertiary hover:text-foreground"
                )}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer Navigation */}
        <div className="absolute bottom-0 left-0 right-0 p-4 space-y-2 border-t border-border">
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg smooth-transition",
              pathname === "/settings"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-background-tertiary"
            )}
          >
            <Settings size={20} />
            <span>Settings</span>
          </Link>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-muted-foreground hover:bg-background-tertiary rounded-lg smooth-transition">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={toggleSidebar}
        />
      )}
    </>
  );
}
