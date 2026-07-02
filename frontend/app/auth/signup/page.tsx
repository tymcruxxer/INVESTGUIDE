"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ArrowRight, Loader2, UserPlus } from "lucide-react";
import { PublicLayout } from "@/components/layout";
import { useAuthStore } from "@/store";

export default function SignupPage() {
  const router = useRouter();
  const { hydrated, isAuthenticated, onboardingComplete, loading, error, signup } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
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
    if (password !== confirmPassword) {
      setFormError("Passwords do not match");
      return;
    }
    try {
      await signup(email, password);
      router.replace("/onboarding");
    } catch (submitError) {
      setFormError(submitError instanceof Error ? submitError.message : "Signup failed");
    }
  };

  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-lg border border-border bg-background-secondary p-6 shadow-xl">
        <div className="mb-6">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <UserPlus size={22} />
          </div>
          <h1 className="mb-2 text-3xl font-bold">Create your account</h1>
          <p className="text-sm text-muted-foreground">Start with a profile that helps InvestGuide adapt explanations to you.</p>
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
              minLength={8}
              required
              autoComplete="new-password"
              className="mt-2 w-full rounded-lg border border-input bg-background-primary px-3 py-2 text-foreground outline-none ring-primary/30 smooth-transition focus:ring-4"
            />
          </label>
          <label className="block text-sm font-medium">
            Confirm password
            <input
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              type="password"
              minLength={8}
              required
              autoComplete="new-password"
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
          Sign up
        </button>

        <p className="mt-5 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/auth/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </PublicLayout>
  );
}
