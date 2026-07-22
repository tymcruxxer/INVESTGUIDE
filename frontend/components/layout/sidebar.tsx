/**
 * Navigation Sidebar Component
 * Left sidebar with navigation links and branding
 */

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/utils";
import { useAuthStore, useUIStore } from "@/store";
import { adminService } from "@/services/api";
import {
  BarChart3,
  BookOpen,
  Briefcase,
  GitCompare,
  LogOut,
  Menu,
  Settings,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3, helper: "Your control center" },
  { href: "/markets", label: "Markets", icon: TrendingUp, helper: "Browse the market" },
  { href: "/assets", label: "Assets", icon: Briefcase, helper: "Research instruments" },
  { href: "/compare", label: "Compare", icon: GitCompare, helper: "Compare tradeoffs" },
  { href: "/ai-assistant", label: "AI Preview", icon: Sparkles, helper: "Coming intelligence layer" },
  { href: "/education", label: "Education", icon: BookOpen, helper: "Build confidence" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore();
  const logout = useAuthStore((state) => state.logout);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [hasAdminAccess, setHasAdminAccess] = useState(false);


  useEffect(() => {
    let cancelled = false;
    if (!isAuthenticated) {
      setHasAdminAccess(false);
      return;
    }
    adminService
      .me()
      .then(() => {
        if (!cancelled) setHasAdminAccess(true);
      })
      .catch(() => {
        if (!cancelled) setHasAdminAccess(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);
  const handleLogout = () => {
    logout();
    router.replace("/auth/login");
  };

  return (
    <>
      <button
        onClick={toggleSidebar}
        className="fixed left-4 top-4 z-40 rounded-lg border border-white/10 bg-primary p-2 text-primary-foreground shadow-lg shadow-blue-950/30 lg:hidden"
        aria-label={sidebarOpen ? "Close navigation" : "Open navigation"}
        aria-expanded={sidebarOpen}
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen w-64 border-r border-white/10 bg-background-secondary/95 shadow-2xl shadow-black/30 backdrop-blur-xl smooth-transition",
          "lg:relative lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
        aria-label="Primary navigation"
      >
        <div className="border-b border-white/10 p-6">
          <h1 className="text-2xl font-bold text-gradient">InvestGuide</h1>
          <p className="mt-1 text-sm text-muted-foreground">Investment Intelligence</p>
        </div>

        <nav className="space-y-1.5 p-4">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-4 py-3 text-sm smooth-transition",
                  isActive
                    ? "bg-primary font-semibold text-primary-foreground shadow-lg shadow-blue-950/20"
                    : "text-muted-foreground hover:bg-background-tertiary hover:text-foreground"
                )}
              >
                {isActive ? <span className="absolute left-1 top-1/2 h-7 w-1 -translate-y-1/2 rounded-full bg-blue-100" aria-hidden="true" /> : null}
                <Icon size={20} className="shrink-0" />
                <span className="min-w-0">
                  <span className="block leading-tight">{item.label}</span>
                  <span className={cn("mt-0.5 block text-[11px] leading-tight", isActive ? "text-blue-100" : "text-muted-foreground group-hover:text-slate-300")}>{item.helper}</span>
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 space-y-2 border-t border-white/10 p-4">
          {hasAdminAccess ? (
            <Link
              href="/admin/dashboard"
              onClick={() => setSidebarOpen(false)}
              className="flex items-center gap-3 rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm font-semibold text-primary smooth-transition hover:bg-primary/20"
            >
              <ShieldCheck size={20} />
              <span>Admin Dashboard</span>
            </Link>
          ) : null}
          <Link
            href="/settings"
            aria-current={pathname === "/settings" ? "page" : undefined}
            onClick={() => setSidebarOpen(false)}
            className={cn(
              "flex items-center gap-3 rounded-lg px-4 py-3 text-sm smooth-transition",
              pathname === "/settings"
                ? "bg-primary text-primary-foreground shadow-lg shadow-blue-950/20"
                : "text-muted-foreground hover:bg-background-tertiary"
            )}
          >
            <Settings size={20} />
            <span>Settings</span>
          </Link>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-muted-foreground smooth-transition hover:bg-background-tertiary hover:text-foreground active:scale-[0.99]"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="fixed inset-0 z-30 animate-fade-in bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={toggleSidebar}
          aria-label="Close navigation"
        />
      )}
    </>
  );
}



