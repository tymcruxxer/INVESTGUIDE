"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ArrowRight, Loader2, LogIn } from "lucide-react";
import { PublicLayout } from "@/components/layout";
import { useAuthStore } from "@/store";

export default function LoginPage() {
  const router = useRouter();
  const { hydrated, isAuthenticated, onboardingComplete, loading, error, login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!hydrated || !isAuthenticated) {
      return;
    }
    router.replace(onboardingComplete ? "/dashboard" : "/onboarding");
  }, [hydrated, isAuthenticated, onboardingComplete, router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    try {
      await login(email, password);
      const nextComplete = useAuthStore.getState().onboardingComplete;
      router.replace(nextComplete ? "/dashboard" : "/onboarding");
    } catch (submitError) {
      setFormError(submitError instanceof Error ? submitError.message : "Login failed");
    }
  };

  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-lg border border-border bg-background-secondary p-6 shadow-xl">
        <div className="mb-6">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <LogIn size={22} />
          </div>
          <h1 className="mb-2 text-3xl font-bold">Welcome back</h1>
          <p className="text-sm text-muted-foreground">Continue to your investment intelligence workspace.</p>
        </div>

        {(formError || error) && (
          <div className="mb-4 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {formError || error}
          </div>
        )}

        <div className="space-y-4">
          <label className="block text-sm font-medium">
            Email
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              required
              autoComplete="email"
              className="mt-2 w-full rounded-lg border border-input bg-background-primary px-3 py-2 text-foreground outline-none ring-primary/30 smooth-transition focus:ring-4"
            />
          </label>
          <label className="block text-sm font-medium">
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              required
              autoComplete="current-password"
              className="mt-2 w-full rounded-lg border border-input bg-background-primary px-3 py-2 text-foreground outline-none ring-primary/30 smooth-transition focus:ring-4"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 font-semibold text-primary-foreground smooth-transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <ArrowRight size={18} />}
          Sign in
        </button>

        <p className="mt-5 text-center text-sm text-muted-foreground">
          New to InvestGuide?{" "}
          <Link href="/auth/signup" className="font-medium text-primary hover:underline">
            Create an account
          </Link>
        </p>
      </form>
    </PublicLayout>
  );
}
