/**
 * App Shell / Layout Wrapper
 * Main layout structure with sidebar and navbar
 */

import React from "react";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen bg-background-primary">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <Navbar />

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 lg:p-6 max-w-[1920px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

/**
 * Public Layout (for auth pages)
 */
interface PublicLayoutProps {
  children: React.ReactNode;
}

export function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="min-h-screen bg-background-primary flex flex-col">
      {/* Minimal Header */}
      <header className="h-16 bg-background-secondary border-b border-border flex items-center px-6">
        <h1 className="text-2xl font-bold text-gradient">InvestGuide</h1>
      </header>

      {/* Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        {children}
      </main>
    </div>
  );
}
