"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle2, KeyRound, ShieldAlert, ShieldCheck, UserRound } from "lucide-react";
import { useMemo, useState } from "react";
import { adminService } from "@/services/api";

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function AdminUserDetailPage() {
  const params = useParams<{ id: string }>();
  const userId = Number(params.id);
  const queryClient = useQueryClient();
  const [roleId, setRoleId] = useState<number | "">("");
  const [roleReason, setRoleReason] = useState("");
  const [statusReason, setStatusReason] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const userQuery = useQuery({ queryKey: ["admin", "user", userId], queryFn: () => adminService.user(userId), retry: false, enabled: Number.isFinite(userId) });
  const rolesQuery = useQuery({ queryKey: ["admin", "roles"], queryFn: () => adminService.roles(), retry: false });
  const user = userQuery.data?.data;

  const availableRoles = useMemo(() => (rolesQuery.data?.data ?? []).filter((role) => !role.is_owner_role), [rolesQuery.data?.data]);

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin", "user", userId] });
    await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
  };

  const roleMutation = useMutation({
    mutationFn: (action: "assign" | "remove") => {
      if (!roleId) throw new Error("Select a role first.");
      return adminService.updateUserRoles(userId, { role_id: Number(roleId), action, reason: roleReason, confirmation: true });
    },
    onSuccess: async () => { setMessage("Role change recorded and audited."); setRoleReason(""); await refresh(); },
    onError: (error: Error) => setMessage(error.message),
  });

  const statusMutation = useMutation({
    mutationFn: (status: "active" | "suspended") => adminService.updateUserStatus(userId, { status, reason: statusReason, confirmation: true }),
    onSuccess: async () => { setMessage("Account status change recorded and audited."); setStatusReason(""); await refresh(); },
    onError: (error: Error) => setMessage(error.message),
  });

  if (userQuery.isLoading) {
    return <div className="premium-card h-80 animate-pulse p-6" />;
  }

  if (!user) {
    return (
      <div className="premium-card p-6">
        <h1 className="text-2xl font-bold">User unavailable</h1>
        <p className="mt-2 text-sm text-muted-foreground">The user may not exist, or your role may not allow inspection.</p>
        <Link href="/admin/users" className="premium-button mt-5 inline-flex"><ArrowLeft size={16} /> Back to users</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/admin/users" className="premium-button-secondary inline-flex items-center gap-2"><ArrowLeft size={16} /> Users</Link>

      <section className="premium-card p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="premium-badge mb-3"><UserRound size={14} /> User detail</p>
            <h1 className="text-3xl font-bold">{user.display_name ?? user.email}</h1>
            <p className="mt-2 text-sm text-muted-foreground">{user.email}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {user.roles.map((role) => <span key={role} className="premium-badge">{role}</span>)}
            </div>
          </div>
          <div className={`rounded-lg border px-4 py-3 text-sm ${user.status === "active" ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100" : "border-rose-400/30 bg-rose-500/10 text-rose-100"}`}>
            {user.status === "active" ? "Active account" : "Suspended account"}
          </div>
        </div>
        {message ? <p className="mt-5 rounded-lg border border-primary/25 bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <article className="premium-card p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold"><ShieldCheck size={18} /> Profile</h2>
          <dl className="mt-4 space-y-3 text-sm text-muted-foreground">
            <div><dt>Created</dt><dd className="text-foreground">{formatDate(user.created_at)}</dd></div>
            <div><dt>Last login</dt><dd className="text-foreground">{formatDate(user.last_login_at)}</dd></div>
            <div><dt>Verification</dt><dd className="text-foreground">{user.is_verified ? "Verified" : "Unverified"}</dd></div>
            <div><dt>Subscription</dt><dd className="text-foreground">{user.subscription_tier}</dd></div>
          </dl>
        </article>
        <article className="premium-card p-5 lg:col-span-2">
          <h2 className="flex items-center gap-2 text-lg font-semibold"><KeyRound size={18} /> Effective permissions</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {user.permissions.length ? user.permissions.map((permission) => <span key={permission} className="rounded-full border border-white/10 px-3 py-1 text-xs text-muted-foreground">{permission}</span>) : <span className="text-sm text-muted-foreground">No admin permissions inherited.</span>}
          </div>
        </article>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="premium-card p-5">
          <h2 className="text-lg font-semibold">Role assignment</h2>
          <p className="mt-1 text-sm text-muted-foreground">Owner role is intentionally excluded from normal assignment workflows.</p>
          <div className="mt-4 space-y-3">
            <select value={roleId} onChange={(event) => setRoleId(event.target.value ? Number(event.target.value) : "")} className="w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">
              <option value="">Select role</option>
              {availableRoles.map((role) => <option key={role.id} value={role.id}>{role.name}</option>)}
            </select>
            <textarea value={roleReason} onChange={(event) => setRoleReason(event.target.value)} placeholder="Reason for role change" className="min-h-24 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <div className="flex flex-wrap gap-2">
              <button disabled={roleMutation.isPending || !roleReason.trim()} onClick={() => roleMutation.mutate("assign")} className="premium-button disabled:cursor-not-allowed disabled:opacity-50"><CheckCircle2 size={16} /> Assign</button>
              <button disabled={roleMutation.isPending || !roleReason.trim()} onClick={() => roleMutation.mutate("remove")} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Remove</button>
            </div>
          </div>
        </article>
        <article className="premium-card p-5">
          <h2 className="flex items-center gap-2 text-lg font-semibold"><ShieldAlert size={18} /> Account status</h2>
          <p className="mt-1 text-sm text-muted-foreground">Suspension and restoration require a reason and are audited.</p>
          <div className="mt-4 space-y-3">
            <textarea value={statusReason} onChange={(event) => setStatusReason(event.target.value)} placeholder="Reason for status change" className="min-h-24 w-full rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2" />
            <div className="flex flex-wrap gap-2">
              <button disabled={statusMutation.isPending || !statusReason.trim() || user.status === "suspended"} onClick={() => statusMutation.mutate("suspended")} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Suspend</button>
              <button disabled={statusMutation.isPending || !statusReason.trim() || user.status === "active"} onClick={() => statusMutation.mutate("active")} className="premium-button disabled:cursor-not-allowed disabled:opacity-50">Restore</button>
            </div>
            {user.suspension_reason ? <p className="rounded-lg border border-rose-400/20 bg-rose-500/10 p-3 text-sm text-rose-100">Suspension reason: {user.suspension_reason}</p> : null}
          </div>
        </article>
      </section>

      <section className="premium-card p-5">
        <h2 className="text-lg font-semibold">Audit summary</h2>
        <div className="mt-4 space-y-3">
          {user.audit_summary.length ? user.audit_summary.map((event, index) => (
            <div key={`${event.action}-${index}`} className="rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold">{event.action}</span>
                <span className="text-muted-foreground">{formatDate(event.created_at)}</span>
              </div>
              <p className="mt-1 text-muted-foreground">{event.reason ?? event.result}</p>
            </div>
          )) : <p className="text-sm text-muted-foreground">No recent audit events for this user yet.</p>}
        </div>
      </section>
    </div>
  );
}
