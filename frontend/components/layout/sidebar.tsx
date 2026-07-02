/**
 * Navigation Sidebar Component
 * Left sidebar with navigation links and branding
 */

"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/utils";
import { useAuthStore, useUIStore } from "@/store";
import {
  BarChart3,
  BookOpen,
  Briefcase,
  LogOut,
  Menu,
  Settings,
  TrendingUp,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/markets", label: "Markets", icon: TrendingUp },
  { href: "/assets", label: "Assets", icon: Briefcase },
  { href: "/ai-assistant", label: "AI Assistant", icon: BarChart3 },
  { href: "/education", label: "Education", icon: BookOpen },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    router.replace("/auth/login");
  };

  return (
    <>
      <button
        onClick={toggleSidebar}
        className="fixed left-4 top-4 z-40 rounded-lg bg-primary p-2 text-primary-foreground lg:hidden"
        aria-label="Toggle navigation"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-background-secondary smooth-transition",
          "lg:relative lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="border-b border-border p-6">
          <h1 className="text-2xl font-bold text-gradient">InvestGuide</h1>
          <p className="mt-1 text-sm text-muted-foreground">Investment Intelligence</p>
        </div>

        <nav className="space-y-2 p-4">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-4 py-3 smooth-transition",
                  isActive
                    ? "bg-primary font-medium text-primary-foreground"
                    : "text-muted-foreground hover:bg-background-tertiary hover:text-foreground"
                )}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 space-y-2 border-t border-border p-4">
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 rounded-lg px-4 py-3 smooth-transition",
              pathname === "/settings"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-background-tertiary"
            )}
          >
            <Settings size={20} />
            <span>Settings</span>
          </Link>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-muted-foreground smooth-transition hover:bg-background-tertiary"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={toggleSidebar}
          aria-label="Close navigation"
        />
      )}
    </>
  );
}
