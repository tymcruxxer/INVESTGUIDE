"use client";

import { useQuery } from "@tanstack/react-query";
import { KeyRound, LockKeyhole, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

export default function AdminSettingsPage() {
  const permissionsQuery = useQuery({ queryKey: ["admin", "permissions", "settings"], queryFn: () => adminService.permissions(), retry: false });

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><LockKeyhole size={14} /> Admin settings</p>
        <h1 className="text-3xl font-bold">Administration settings foundation</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          This page intentionally exposes read-only operating context for now. Role editing, user management, data-source controls, and feature flags belong to later admin sprints.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <article className="premium-card p-6">
          <div className="flex items-center gap-3">
            <span className="rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><ShieldCheck size={20} /></span>
            <div>
              <h2 className="text-xl font-semibold">Owner protections</h2>
              <p className="text-sm text-muted-foreground">Non-editable foundations for the platform Owner.</p>
            </div>
          </div>
          <ul className="mt-5 space-y-3 text-sm text-muted-foreground">
            <li>Owner cannot be deleted, suspended, or demoted through normal admin flows.</li>
            <li>Ownership transfer requires a dedicated future workflow.</li>
            <li>Owner bypasses permission checks while still being auditable.</li>
          </ul>
        </article>

        <article className="premium-card p-6">
          <div className="flex items-center gap-3">
            <span className="rounded-lg border border-primary/30 bg-primary/10 p-3 text-primary"><KeyRound size={20} /></span>
            <div>
              <h2 className="text-xl font-semibold">Sensitive actions</h2>
              <p className="text-sm text-muted-foreground">Future-ready hooks, not active MFA.</p>
            </div>
          </div>
          <div className="mt-5 space-y-3 text-sm text-muted-foreground">
            <p>Re-authentication hooks: supported by architecture.</p>
            <p>MFA compatibility: supported by architecture.</p>
            <p>Confirmation workflows: supported by architecture.</p>
          </div>
        </article>
      </section>

      <section className="premium-card p-6">
        <h2 className="text-xl font-semibold">Permission catalog</h2>
        {permissionsQuery.isLoading ? (
          <div className="mt-5 space-y-3">
            {[0, 1, 2].map((item) => <div key={item} className="h-12 animate-pulse rounded-lg bg-white/5" />)}
          </div>
        ) : permissionsQuery.data?.data ? (
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {Object.entries(permissionsQuery.data.data.grouped_permissions).map(([category, permissions]) => (
              <div key={category} className="rounded-lg border border-white/10 bg-background-secondary/70 p-4">
                <h3 className="font-semibold capitalize">{category}</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {permissions.map((permission) => (
                    <span key={permission.code} className="rounded-full border border-white/10 px-3 py-1 text-xs text-muted-foreground">
                      {permission.code}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-5 rounded-lg border border-amber-400/25 bg-amber-500/10 p-4 text-sm text-amber-100">
            Permission catalog unavailable.
          </p>
        )}
      </section>
    </div>
  );
}
