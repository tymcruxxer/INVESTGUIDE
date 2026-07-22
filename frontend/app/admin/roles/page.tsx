"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { KeyRound, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

export default function AdminRolesPage() {
  const rolesQuery = useQuery({ queryKey: ["admin", "roles"], queryFn: () => adminService.roles(), retry: false });
  const roles = rolesQuery.data?.data ?? [];

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><KeyRound size={14} /> Role viewer</p>
        <h1 className="text-3xl font-bold">Roles and inherited permissions</h1>
        <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
          Inspect system roles and their permission inheritance. Permission editing is intentionally not available in this sprint.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        {rolesQuery.isLoading ? (
          Array.from({ length: 4 }).map((_, index) => <div key={index} className="premium-card h-44 animate-pulse p-5" />)
        ) : roles.length ? (
          roles.map((role) => (
            <Link key={role.id} href={`/admin/roles/${role.id}`} className="premium-card block p-5 smooth-transition hover:-translate-y-1 hover:border-primary/40">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">{role.name}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">{role.description ?? "No description provided."}</p>
                </div>
                {role.is_owner_role ? <span className="premium-badge"><ShieldCheck size={14} /> Owner</span> : null}
              </div>
              <div className="mt-5 grid gap-3 text-sm text-muted-foreground sm:grid-cols-3">
                <span>{role.permissions?.length ?? 0} permissions</span>
                <span>{role.assigned_user_count ?? 0} users</span>
                <span>{role.is_system_role ? "System role" : "Custom role"}</span>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(role.permissions ?? []).slice(0, 6).map((permission) => (
                  <span key={permission.code} className="rounded-full border border-white/10 px-3 py-1 text-xs text-muted-foreground">{permission.code}</span>
                ))}
              </div>
            </Link>
          ))
        ) : (
          <div className="premium-card p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold">No roles available</h2>
            <p className="mt-2 text-sm text-muted-foreground">Run the development seed command to bootstrap roles and permissions.</p>
          </div>
        )}
      </section>
    </div>
  );
}
