"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { AlertCircle, ArrowRight, Check, CheckCircle2, Eye, EyeOff, Loader2, ShieldCheck, UserPlus } from "lucide-react";
import { PublicLayout } from "@/components/layout";
import { useAuthStore } from "@/store";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const friendlySignupError = (message: string) => {
  const normalized = message.toLowerCase();
  if (normalized.includes("already") || normalized.includes("registered") || normalized.includes("exists")) {
    return "This account already exists.";
  }
  if (normalized.includes("backend is not reachable") || normalized.includes("network")) {
    return "Backend is not reachable. Please make sure the backend is running on http://127.0.0.1:8001.";
  }
  return message || "We could not create your account. Please check your details and try again.";
};

const passwordScore = (password: string) => {
  let score = 0;
  if (password.length >= 8) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  return score;
};

export default function SignupPage() {
  const router = useRouter();
  const { hydrated, isAuthenticated, onboardingComplete, loading, error, signup } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [accountExists, setAccountExists] = useState(false);
  const [signupComplete, setSignupComplete] = useState(false);

  const strength = useMemo(() => passwordScore(password), [password]);
  const strengthLabel = ["Too weak", "Basic", "Good", "Strong", "Excellent"][strength];

  useEffect(() => {
    if (!hydrated || !isAuthenticated || signupComplete) {
      return;
    }
    router.replace(onboardingComplete ? "/dashboard" : "/onboarding");
  }, [hydrated, isAuthenticated, onboardingComplete, router, signupComplete]);

  const validate = () => {
    if (!emailPattern.test(email)) {
      return "Enter a valid email address.";
    }
    if (password.length < 8 || strength < 2) {
      return "Use a stronger password with at least 8 characters, a number, and a capital letter.";
    }
    if (password !== confirmPassword) {
      return "Passwords do not match.";
    }
    return null;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    setAccountExists(false);

    const validationError = validate();
    if (validationError) {
      setFormError(validationError);
      return;
    }

    try {
      await signup(email, password);
      setSignupComplete(true);
    } catch (submitError) {
      const message = friendlySignupError(submitError instanceof Error ? submitError.message : "Signup failed");
      setAccountExists(message === "This account already exists.");
      setFormError(message);
    }
  };

  if (signupComplete) {
    return (
      <PublicLayout>
        <section className="premium-card w-full max-w-md p-7 text-center sm:p-8">
          <div className="mx-auto flex h-20 w-20 items-center justify-center success-ring">
            <CheckCircle2 size={44} />
          </div>
          <p className="mt-6 text-sm font-semibold uppercase tracking-[0.22em] text-emerald-300">Account created</p>
          <h1 className="mt-3 text-3xl font-bold">Welcome to InvestGuide.</h1>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Your account has been created successfully. Next, personalize your investor profile so InvestGuide can adapt explanations, dashboards, and learning paths to you.
          </p>
          <button onClick={() => router.replace("/onboarding")} className="premium-button-primary mt-7 w-full">
            Continue to onboarding <ArrowRight size={18} />
          </button>
          <button onClick={() => router.replace("/auth/login")} className="mt-3 text-sm font-medium text-muted-foreground hover:text-foreground">
            Continue to login instead
          </button>
        </section>
      </PublicLayout>
    );
  }

  return (
    <PublicLayout>
      <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="hidden rounded-lg border border-white/10 bg-background-secondary/50 p-7 shadow-2xl shadow-black/25 lg:block">
          <div className="premium-badge text-emerald-300"><ShieldCheck size={14} /> Secure onboarding</div>
          <h2 className="mt-8 text-4xl font-bold leading-tight">Start with a profile that makes investing feel clear.</h2>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            InvestGuide adapts language, education depth, and dashboard emphasis from your investor profile. No recommendations, no pressure, just clearer financial intelligence.
          </p>
          <div className="mt-8 grid gap-3">
            {["Beginner-friendly explanations", "Personalized investment horizon", "Secure JWT-backed session"].map((item) => (
              <div key={item} className="flex items-center gap-3 rounded-lg border border-white/10 bg-background-primary/60 p-3 text-sm text-muted-foreground">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-300"><Check size={15} /></span>
                {item}
              </div>
            ))}
          </div>
        </section>

        <form onSubmit={handleSubmit} className="premium-card w-full p-6 sm:p-8">
          <div className="mb-7">
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-lg border border-primary/30 bg-primary/10 text-primary">
              <UserPlus size={23} />
            </div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Create account</p>
            <h1 className="mt-2 text-3xl font-bold">Join InvestGuide</h1>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">Create your secure account and continue to personalized onboarding.</p>
          </div>

          {(formError || error) && (
            <div className="error-panel mb-5">
              <div className="flex items-start gap-3">
                <AlertCircle size={18} className="mt-0.5 shrink-0" />
                <div>
                  <p>{formError || friendlySignupError(error ?? "Signup failed")}</p>
                  {accountExists ? (
                    <Link href="/auth/login" className="mt-3 inline-flex font-semibold text-foreground hover:text-primary">
                      Go to Login
                    </Link>
                  ) : null}
                </div>
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
                <input value={password} onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} minLength={8} required autoComplete="new-password" placeholder="Create a strong password" className="premium-input pr-11" />
                <button type="button" onClick={() => setShowPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label={showPassword ? "Hide password" : "Show password"}>
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {password ? (
                <div className="mt-2">
                  <div className="grid grid-cols-4 gap-1">
                    {[0, 1, 2, 3].map((item) => <span key={item} className={`h-1.5 rounded-full ${item < strength ? "bg-emerald-400" : "bg-background-tertiary"}`} />)}
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">Password strength: {strengthLabel}</p>
                </div>
              ) : null}
            </label>

            <label className="block text-sm font-medium text-foreground">
              Confirm password
              <div className="relative mt-2">
                <input value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} type={showConfirmPassword ? "text" : "password"} minLength={8} required autoComplete="new-password" placeholder="Repeat your password" className="premium-input pr-11" />
                <button type="button" onClick={() => setShowConfirmPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" aria-label={showConfirmPassword ? "Hide password" : "Show password"}>
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </label>
          </div>

          <button type="submit" disabled={loading} className="premium-button-primary mt-6 w-full">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <ArrowRight size={18} />}
            Create account
          </button>

          <p className="mt-5 text-center text-sm text-muted-foreground">
            Already have an account? <Link href="/auth/login" className="font-semibold text-primary hover:text-blue-300">Sign in</Link>
          </p>
        </form>
      </div>
    </PublicLayout>
  );
}