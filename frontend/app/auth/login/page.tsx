"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { AlertCircle, ArrowRight, Eye, EyeOff, Loader2, LogIn, ShieldCheck } from "lucide-react";
import { PublicLayout } from "@/components/layout";
import { useAuthStore } from "@/store";

const friendlyLoginError = (message: string) => {
  const normalized = message.toLowerCase();
  if (normalized.includes("backend is not reachable") || normalized.includes("network")) {
    return "Backend is not reachable. Please make sure the backend is running on http://127.0.0.1:8001.";
  }
  if (normalized.includes("invalid") || normalized.includes("credential") || normalized.includes("password")) {
    return "Email or password is incorrect.";
  }
  return message || "We could not sign you in. Please try again.";
};

export default function LoginPage() {
  const router = useRouter();
  const { hydrated, isAuthenticated, onboardingComplete, loading, error, login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
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
      setFormError(friendlyLoginError(submitError instanceof Error ? submitError.message : "Login failed"));
    }
  };

  return (
    <PublicLayout>
      <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="hidden rounded-lg border border-white/10 bg-background-secondary/50 p-7 shadow-2xl shadow-black/25 lg:block">
          <div className="premium-badge text-emerald-300"><ShieldCheck size={14} /> Secure session</div>
          <h2 className="mt-8 text-4xl font-bold leading-tight">Return to your financial intelligence workspace.</h2>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            Continue researching Zimbabwean assets, reviewing company intelligence, and progressing through your investor roadmap.
          </p>
          <div className="mt-8 rounded-lg border border-white/10 bg-background-primary/70 p-5">
            <p className="text-sm font-semibold text-foreground">Today&apos;s focus</p>
            <div className="mt-4 grid gap-3 text-sm text-muted-foreground">
              <div className="flex justify-between"><span>Market clarity</span><span className="text-emerald-300">Online</span></div>
              <div className="flex justify-between"><span>Company profiles</span><span className="text-blue-300">Ready</span></div>
              <div className="flex justify-between"><span>Education mode</span><span className="text-teal-300">Adaptive</span></div>
            </div>
          </div>
        </section>

        <form onSubmit={handleSubmit} className="premium-card w-full p-6 sm:p-8">
          <div className="mb-7">
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-lg border border-primary/30 bg-primary/10 text-primary">
              <LogIn size={23} />
            </div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Welcome back</p>
            <h1 className="mt-2 text-3xl font-bold">Sign in securely</h1>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">Access your dashboard, onboarding profile, company intelligence, and saved session.</p>
          </div>

          {(formError || error) && (
            <div className="error-panel mb-5">
              <div className="flex items-start gap-3">
                <AlertCircle size={18} className="mt-0.5 shrink-0" />
                <p>{formError || friendlyLoginError(error ?? "Login failed")}</p>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <label className="block text-sm font-medium text-foreground">
              Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required autoComplete="email" placeholder="you@example.com" className="premium-input mt-2" />
            </label>
            <label className="block text-sm font-medium text-foreground">
              Password
              <div className="relative mt-2">
                <input value={password} onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} required autoComplete="current-password" placeholder="Your password" className="premium-input pr-11" />
                <button type="button" onClick={() => setShowPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label={showPassword ? "Hide password" : "Show password"}>
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </label>
          </div>

          <button type="submit" disabled={loading} className="premium-button-primary mt-6 w-full">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <ArrowRight size={18} />}
            Sign in
          </button>

          <div className="mt-5 flex flex-col gap-2 text-center text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:text-left">
            <Link href="/auth/signup" className="font-semibold text-primary hover:text-blue-300">Create an account</Link>
            <span>Forgot password coming later</span>
          </div>
        </form>
      </div>
    </PublicLayout>
  );
}