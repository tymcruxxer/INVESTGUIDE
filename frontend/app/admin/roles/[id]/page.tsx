"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, KeyRound, ShieldCheck } from "lucide-react";
import { adminService } from "@/services/api";

export default function AdminRoleDetailPage() {
  const params = useParams<{ id: string }>();
  const roleId = Number(params.id);
  const roleQuery = useQuery({ queryKey: ["admin", "role", roleId], queryFn: () => adminService.role(roleId), retry: false, enabled: Number.isFinite(roleId) });
  const role = roleQuery.data?.data;

  if (roleQuery.isLoading) {
    return <div className="premium-card h-72 animate-pulse p-6" />;
  }

  if (!role) {
    return (
      <div className="premium-card p-6">
        <h1 className="text-2xl font-bold">Role unavailable</h1>
        <p className="mt-2 text-sm text-muted-foreground">The role may not exist, or your permissions may not allow inspection.</p>
        <Link href="/admin/roles" className="premium-button mt-5 inline-flex"><ArrowLeft size={16} /> Back to roles</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/admin/roles" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Roles</Link>
      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><KeyRound size={14} /> Permission inheritance</p>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-3xl font-bold">{role.name}</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{role.description ?? "No description provided."}</p>
          </div>
          {role.is_owner_role ? <span className="premium-badge"><ShieldCheck size={14} /> Protected Owner role</span> : null}
        </div>
      </section>
      <section className="premium-card p-5">
        <h2 className="text-xl font-semibold">Inherited permissions</h2>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {(role.permissions ?? []).length ? (role.permissions ?? []).map((permission) => (
            <div key={permission.code} className="rounded-lg border border-white/10 bg-background-secondary/70 p-4">
              <p className="font-semibold">{permission.name}</p>
              <p className="mt-1 text-xs text-primary">{permission.code}</p>
              <p className="mt-2 text-sm text-muted-foreground">{permission.description ?? "No description provided."}</p>
            </div>
          )) : <p className="text-sm text-muted-foreground">This role does not grant administrative permissions.</p>}
        </div>
      </section>
    </div>
  );
}
