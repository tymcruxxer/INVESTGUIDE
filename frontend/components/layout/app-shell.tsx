/**
 * App Shell / Layout Wrapper
 * Main layout structure with sidebar and navbar
 */

"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { useAuthStore } from "@/store";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { hydrated, isAuthenticated, onboardingComplete } = useAuthStore();

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    if (!isAuthenticated) {
      router.replace("/auth/login");
      return;
    }
    if (!onboardingComplete && pathname !== "/onboarding") {
      router.replace("/onboarding");
    }
  }, [hydrated, isAuthenticated, onboardingComplete, pathname, router]);

  if (!hydrated || !isAuthenticated || (!onboardingComplete && pathname !== "/onboarding")) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background-primary px-4">
        <div className="w-full max-w-sm rounded-lg border border-border bg-background-secondary p-6 text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-pulse rounded-full bg-primary/30" />
          <p className="text-sm text-muted-foreground">Preparing your InvestGuide workspace</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background-primary">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-auto">
          <div className="mx-auto max-w-[1920px] p-4 lg:p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}

interface PublicLayoutProps {
  children: React.ReactNode;
}

export function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-background-primary">
      <header className="flex h-16 items-center border-b border-border bg-background-secondary px-6">
        <h1 className="text-2xl font-bold text-gradient">InvestGuide</h1>
      </header>
      <main className="flex flex-1 items-center justify-center p-4">{children}</main>
    </div>
  );
}
