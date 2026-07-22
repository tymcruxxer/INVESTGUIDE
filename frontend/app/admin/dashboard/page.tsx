"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, Database, LockKeyhole, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

const cards = [
  { title: "RBAC foundation", description: "Roles and permissions are enforced server-side before admin data is returned.", icon: ShieldCheck },
  { title: "Audit ready", description: "Privileged reads can record actor, action, target, result, IP address, and request ID.", icon: Activity },
  { title: "Sensitive actions", description: "Future re-authentication, MFA, and confirmation workflows have a dedicated contract.", icon: LockKeyhole },
  { title: "Operational data", description: "Future data source, ingestion, and analytics modules can plug into this shell.", icon: Database },
];

export default function AdminDashboardPage() {
  const meQuery = useQuery({ queryKey: ["admin", "me", "dashboard"], queryFn: () => adminService.me(), retry: false });
  const permissionsQuery = useQuery({ queryKey: ["admin", "permissions", "dashboard"], queryFn: () => adminService.permissions(), retry: false });

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><ShieldCheck size={14} /> Admin dashboard</p>
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">InvestGuide operating system</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
              This protected workspace is the foundation for future user management, data operations, analytics administration, and platform configuration.
            </p>
          </div>
          <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            {meQuery.data?.data.primary_role?.name ?? "Admin"}
          </span>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <article key={card.title} className="premium-card p-5">
              <span className="inline-flex rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><Icon size={20} /></span>
              <h2 className="mt-4 text-lg font-semibold">{card.title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{card.description}</p>
            </article>
          );
        })}
      </section>

      <section className="premium-card p-6">
        <h2 className="text-xl font-semibold">Permission snapshot</h2>
        <p className="mt-1 text-sm text-muted-foreground">A quick read-only view of the current administrator permission model.</p>
        {permissionsQuery.isLoading ? (
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {[0, 1, 2].map((item) => <div key={item} className="h-20 animate-pulse rounded-lg bg-white/5" />)}
          </div>
        ) : permissionsQuery.data?.data ? (
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <Metric label="Roles" value={permissionsQuery.data.data.roles.length} />
            <Metric label="Permissions" value={permissionsQuery.data.data.permissions.length} />
            <Metric label="Owner bypass" value={permissionsQuery.data.data.owner_bypass ? "Enabled" : "No"} />
          </div>
        ) : (
          <p className="mt-5 rounded-lg border border-amber-400/25 bg-amber-500/10 p-4 text-sm text-amber-100">
            Permission metadata is unavailable. Confirm the backend is running and your account has admin access.
          </p>
        )}
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-secondary/70 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}
