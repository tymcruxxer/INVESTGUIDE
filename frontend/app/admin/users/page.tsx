"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, ShieldCheck, UserCheck, UserX } from "lucide-react";
import { adminService } from "@/services/api";

function formatDate(value?: string | null) {
  if (!value) return "Never";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

export default function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [verified, setVerified] = useState("all");
  const [page, setPage] = useState(1);

  const params = useMemo(
    () => ({
      page,
      limit: 12,
      search: search.trim() || undefined,
      status: status === "all" ? undefined : status,
      verified: verified === "all" ? undefined : verified === "verified",
    }),
    [page, search, status, verified]
  );

  const usersQuery = useQuery({
    queryKey: ["admin", "users", params],
    queryFn: () => adminService.users(params),
    retry: false,
  });

  const payload = usersQuery.data?.data;
  const totalPages = payload ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;

  return (
    <div className="space-y-6">
      <section className="premium-card p-6">
        <p className="premium-badge mb-3"><ShieldCheck size={14} /> User directory</p>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Users, roles, and account status</h1>
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
              Inspect authenticated users, their inherited roles, verification state, and administrative account status without exposing sensitive credentials.
            </p>
          </div>
          <div className="rounded-lg border border-white/10 bg-background-secondary/70 px-4 py-3 text-sm text-muted-foreground">
            {payload?.total ?? 0} users visible
          </div>
        </div>
      </section>

      <section className="premium-card p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_180px_180px]">
          <label className="relative block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
            <input
              value={search}
              onChange={(event) => { setSearch(event.target.value); setPage(1); }}
              placeholder="Search by email or username"
              className="w-full rounded-lg border border-white/10 bg-background-secondary py-3 pl-10 pr-3 text-sm outline-none ring-primary/40 focus:ring-2"
            />
          </label>
          <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
          </select>
          <select value={verified} onChange={(event) => { setVerified(event.target.value); setPage(1); }} className="rounded-lg border border-white/10 bg-background-secondary px-3 py-3 text-sm outline-none ring-primary/40 focus:ring-2">
            <option value="all">All verification</option>
            <option value="verified">Verified</option>
            <option value="unverified">Unverified</option>
          </select>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        {usersQuery.isLoading ? (
          Array.from({ length: 6 }).map((_, index) => <div key={index} className="premium-card h-36 animate-pulse p-5" />)
        ) : payload && payload.users.length > 0 ? (
          payload.users.map((user) => (
            <Link key={user.id} href={`/admin/users/${user.id}`} className="premium-card block p-5 smooth-transition hover:-translate-y-1 hover:border-primary/40">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-lg font-semibold">{user.display_name ?? user.email}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{user.email}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {user.roles.length ? user.roles.map((role) => <span key={role} className="premium-badge">{role}</span>) : <span className="premium-badge">no role</span>}
                  </div>
                </div>
                <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${user.status === "active" ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100" : "border-rose-400/30 bg-rose-500/10 text-rose-100"}`}>
                  {user.status === "active" ? <UserCheck size={14} /> : <UserX size={14} />}
                  {user.status}
                </span>
              </div>
              <div className="mt-5 grid gap-3 text-sm text-muted-foreground sm:grid-cols-3">
                <span>Joined: {formatDate(user.created_at)}</span>
                <span>Last login: {formatDate(user.last_login_at)}</span>
                <span>{user.is_verified ? "Verified" : "Unverified"}</span>
              </div>
            </Link>
          ))
        ) : (
          <div className="premium-card p-6 xl:col-span-2">
            <h2 className="text-xl font-semibold">No users found</h2>
            <p className="mt-2 text-sm text-muted-foreground">Try another search, remove filters, or confirm the development seed command has run.</p>
          </div>
        )}
      </section>

      {payload ? (
        <div className="flex items-center justify-between rounded-lg border border-white/10 bg-background-secondary/70 p-3 text-sm">
          <button disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Previous</button>
          <span className="text-muted-foreground">Page {page} of {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="premium-button-secondary disabled:cursor-not-allowed disabled:opacity-50">Next</button>
        </div>
      ) : null}
    </div>
  );
}
