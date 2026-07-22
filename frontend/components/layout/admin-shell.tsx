"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, KeyRound, LayoutDashboard, Settings, ShieldCheck, Users } from "lucide-react";
import { adminService } from "@/services/api";
import { useAuthStore } from "@/store";
import { cn } from "@/utils";

const ADMIN_NAV = [
  { href: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/roles", label: "Roles", icon: KeyRound },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { hydrated, isAuthenticated, user } = useAuthStore();
  const adminQuery = useQuery({
    queryKey: ["admin", "me"],
    queryFn: () => adminService.me(),
    retry: false,
    enabled: hydrated && isAuthenticated,
  });

  if (!hydrated || (isAuthenticated && adminQuery.isLoading)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background-primary px-4 text-foreground">
        <div className="premium-card w-full max-w-sm p-6 text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-pulse rounded-full bg-primary/30" />
          <p className="text-sm text-muted-foreground">Checking administration access</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    router.replace("/auth/login");
    return null;
  }

  if (adminQuery.isError || !adminQuery.data?.data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background-primary px-4 text-foreground">
        <div className="premium-card max-w-lg p-6 text-center">
          <p className="premium-badge mx-auto mb-4 w-fit"><ShieldCheck size={14} /> Admin mode</p>
          <h1 className="text-2xl font-bold">Administration access required</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            This area is separate from the investor experience and requires server-side administrative permissions.
          </p>
          <Link href="/dashboard" className="premium-button mt-6 inline-flex">
            Return to user dashboard
          </Link>
        </div>
      </div>
    );
  }

  const context = adminQuery.data.data;
  const primaryRole = context.primary_role?.name ?? (context.is_owner ? "Owner" : "Administrator");

  return (
    <div className="flex min-h-screen bg-background-primary text-foreground">
      <aside className="hidden w-72 border-r border-white/10 bg-background-secondary/95 p-5 lg:block">
        <div className="rounded-lg border border-primary/20 bg-primary/10 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-primary"><ShieldCheck size={16} /> Admin Mode</p>
          <h1 className="mt-2 text-2xl font-bold">InvestGuide OS</h1>
          <p className="mt-1 text-xs text-muted-foreground">Secure operating layer</p>
        </div>
        <nav className="mt-6 space-y-2">
          {ADMIN_NAV.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-4 py-3 text-sm smooth-transition",
                  isActive ? "bg-primary font-semibold text-primary-foreground" : "text-muted-foreground hover:bg-background-tertiary hover:text-foreground"
                )}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-background-secondary/90 px-4 py-4 backdrop-blur-xl lg:px-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-primary">Administration</p>
              <h2 className="text-xl font-semibold">{primaryRole}</h2>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <span className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-3 py-1 text-emerald-100">{process.env.NODE_ENV}</span>
              <span className="max-w-[240px] truncate text-muted-foreground">{context.user.email ?? user?.email}</span>
              <Link href="/dashboard" className="premium-button-secondary inline-flex items-center gap-2">
                <ArrowLeft size={16} />
                User View
              </Link>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <div className="mx-auto max-w-7xl space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}


