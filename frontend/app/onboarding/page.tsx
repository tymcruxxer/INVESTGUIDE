"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Check, Loader2 } from "lucide-react";
import { PublicLayout } from "@/components/layout";
import { useAuthStore } from "@/store";
import { ExperienceLevel, InvestorProfilePayload, PreferredLanguageLevel, RiskProfile } from "@/types";

type StepId =
  | "experience"
  | "goals"
  | "assets"
  | "risk"
  | "horizon"
  | "range"
  | "language";

interface Choice<T extends string = string> {
  label: string;
  value: T;
  description?: string;
}

const steps: { id: StepId; title: string; subtitle: string }[] = [
  {
    id: "experience",
    title: "Experience level",
    subtitle: "This sets the language and depth of explanations.",
  },
  {
    id: "goals",
    title: "Investment goals",
    subtitle: "Choose what you want InvestGuide to emphasize.",
  },
  {
    id: "assets",
    title: "Preferred investment types",
    subtitle: "These preferences guide discovery without hiding the rest of the market.",
  },
  {
    id: "risk",
    title: "Risk appetite",
    subtitle: "Risk framing helps InvestGuide explain tradeoffs clearly.",
  },
  {
    id: "horizon",
    title: "Investment horizon",
    subtitle: "Time horizon changes how volatility, income, and compounding are explained.",
  },
  {
    id: "range",
    title: "Planned investment range",
    subtitle: "A range is enough. InvestGuide uses it for education, not advice.",
  },
  {
    id: "language",
    title: "Language preference",
    subtitle: "You can change this later as your confidence grows.",
  },
];

const experienceOptions: Choice<ExperienceLevel>[] = [
  { label: "Beginner", value: "beginner", description: "Clear definitions and examples" },
  { label: "Intermediate", value: "intermediate", description: "Balanced context and tradeoffs" },
  { label: "Advanced", value: "advanced", description: "Technical metrics and methodology" },
];

const goalOptions: Choice[] = [
  { label: "Long-term wealth", value: "long_term_wealth" },
  { label: "Dividend income", value: "passive_income" },
  { label: "Capital appreciation", value: "wealth_building" },
  { label: "Passive income", value: "passive_income" },
  { label: "Learning how to invest", value: "learning" },
  { label: "Property/REIT exposure", value: "passive_income" },
  { label: "Portfolio diversification", value: "diversification" },
];

const assetOptions: Choice[] = [
  { label: "ZSE", value: "zse" },
  { label: "VFEX", value: "vfex" },
  { label: "REITs", value: "reits" },
  { label: "Money Market", value: "money_market" },
  { label: "Bonds", value: "bonds" },
  { label: "Alternative Investments", value: "alternatives" },
];

const riskOptions: Choice<RiskProfile>[] = [
  { label: "Conservative", value: "conservative", description: "Capital preservation first" },
  { label: "Moderate", value: "moderate", description: "Balanced risk and opportunity" },
  { label: "Aggressive", value: "aggressive", description: "Higher volatility tolerance" },
];

const horizonOptions: Choice[] = [
  { label: "Less than 6 months", value: "short_term" },
  { label: "6-12 months", value: "short_term" },
  { label: "1-3 years", value: "medium_term" },
  { label: "3-5 years", value: "long_term" },
  { label: "More than 5 years", value: "long_term" },
];

const rangeOptions: Choice[] = [
  { label: "Under $100", value: "under_100_usd" },
  { label: "$100-500", value: "100_to_500_usd" },
  { label: "$500-1,000", value: "500_to_1000_usd" },
  { label: "$1,000-5,000", value: "1000_to_5000_usd" },
  { label: "Above $5,000", value: "above_5000_usd" },
];

const languageOptions: Choice<PreferredLanguageLevel>[] = [
  { label: "Simple English", value: "simple", description: "Plain-language guidance" },
  { label: "Balanced", value: "balanced", description: "Context with selected metrics" },
  { label: "Technical", value: "technical", description: "Concise, data-rich explanations" },
];

const unique = (values: string[]) => Array.from(new Set(values));

export default function OnboardingPage() {
  const router = useRouter();
  const { hydrated, isAuthenticated, onboardingComplete, loading, error, completeOnboarding } = useAuthStore();
  const [stepIndex, setStepIndex] = useState(0);
  const [formError, setFormError] = useState<string | null>(null);
  const [experience, setExperience] = useState<ExperienceLevel>("beginner");
  const [goals, setGoals] = useState<string[]>([]);
  const [assets, setAssets] = useState<string[]>([]);
  const [risk, setRisk] = useState<RiskProfile>("moderate");
  const [horizon, setHorizon] = useState("long_term");
  const [range, setRange] = useState("100_to_500_usd");
  const [language, setLanguage] = useState<PreferredLanguageLevel>("simple");

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    if (!isAuthenticated) {
      router.replace("/auth/login");
      return;
    }
    if (onboardingComplete) {
      router.replace("/dashboard");
    }
  }, [hydrated, isAuthenticated, onboardingComplete, router]);

  const activeStep = steps[stepIndex];
  const progress = useMemo(() => Math.round(((stepIndex + 1) / steps.length) * 100), [stepIndex]);

  const toggleValue = (value: string, setter: (next: string[]) => void, current: string[]) => {
    setter(current.includes(value) ? current.filter((item) => item !== value) : [...current, value]);
  };

  const canContinue = () => {
    if (activeStep.id === "goals") {
      return goals.length > 0;
    }
    if (activeStep.id === "assets") {
      return assets.length > 0;
    }
    return true;
  };

  const next = () => {
    setFormError(null);
    if (!canContinue()) {
      setFormError("Select at least one option to continue.");
      return;
    }
    setStepIndex((current) => Math.min(current + 1, steps.length - 1));
  };

  const back = () => {
    setFormError(null);
    setStepIndex((current) => Math.max(current - 1, 0));
  };

  const submit = async () => {
    setFormError(null);
    if (!goals.length || !assets.length) {
      setFormError("Choose at least one goal and investment type.");
      return;
    }

    const payload: InvestorProfilePayload = {
      experience_level: experience,
      risk_appetite: risk,
      investment_horizon: horizon,
      planned_investment_range: range,
      preferred_asset_types: unique(assets),
      investment_goals: unique(goals),
      preferred_language_level: language,
      education_focus: ["investing_basics", ...unique(assets), ...unique(goals)].slice(0, 8),
    };

    try {
      await completeOnboarding(payload);
      router.replace("/dashboard");
    } catch (submitError) {
      setFormError(submitError instanceof Error ? submitError.message : "Onboarding failed");
    }
  };

  if (!hydrated || !isAuthenticated || onboardingComplete) {
    return (
      <PublicLayout>
        <div className="rounded-lg border border-border bg-background-secondary p-6 text-sm text-muted-foreground">
          Preparing onboarding
        </div>
      </PublicLayout>
    );
  }

  return (
    <PublicLayout>
      <div className="w-full max-w-3xl rounded-lg border border-border bg-background-secondary p-5 shadow-xl sm:p-6">
        <div className="mb-6">
          <div className="mb-3 flex items-center justify-between gap-4 text-sm text-muted-foreground">
            <span>Step {stepIndex + 1} of {steps.length}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-background-tertiary">
            <div className="h-full bg-primary smooth-transition" style={{ width: `${progress}%` }} />
          </div>
        </div>

        <div className="mb-6">
          <h1 className="mb-2 text-3xl font-bold">{activeStep.title}</h1>
          <p className="text-sm text-muted-foreground">{activeStep.subtitle}</p>
        </div>

        {(formError || error) && (
          <div className="mb-5 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {formError || error}
          </div>
        )}

        {activeStep.id === "experience" && (
          <SingleChoice options={experienceOptions} value={experience} onChange={setExperience} />
        )}
        {activeStep.id === "goals" && (
          <MultiChoice options={goalOptions} values={goals} onToggle={(value) => toggleValue(value, setGoals, goals)} />
        )}
        {activeStep.id === "assets" && (
          <MultiChoice options={assetOptions} values={assets} onToggle={(value) => toggleValue(value, setAssets, assets)} />
        )}
        {activeStep.id === "risk" && (
          <SingleChoice options={riskOptions} value={risk} onChange={setRisk} />
        )}
        {activeStep.id === "horizon" && (
          <SingleChoice options={horizonOptions} value={horizon} onChange={setHorizon} />
        )}
        {activeStep.id === "range" && (
          <SingleChoice options={rangeOptions} value={range} onChange={setRange} />
        )}
        {activeStep.id === "language" && (
          <SingleChoice options={languageOptions} value={language} onChange={setLanguage} />
        )}

        <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
          <button
            type="button"
            onClick={back}
            disabled={stepIndex === 0 || loading}
            className="flex items-center justify-center gap-2 rounded-lg border border-border px-4 py-3 text-sm font-medium smooth-transition hover:bg-background-tertiary disabled:cursor-not-allowed disabled:opacity-50"
          >
            <ArrowLeft size={18} />
            Back
          </button>
          {stepIndex === steps.length - 1 ? (
            <button
              type="button"
              onClick={submit}
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground smooth-transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Check size={18} />}
              Finish onboarding
            </button>
          ) : (
            <button
              type="button"
              onClick={next}
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground smooth-transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
            >
              Continue
              <ArrowRight size={18} />
            </button>
          )}
        </div>
      </div>
    </PublicLayout>
  );
}

function SingleChoice<T extends string>({
  options,
  value,
  onChange,
}: {
  options: Choice<T>[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {options.map((option) => {
        const selected = value === option.value;
        return (
          <button
            key={`${option.label}-${option.value}`}
            type="button"
            onClick={() => onChange(option.value)}
            className={`min-h-24 rounded-lg border p-4 text-left smooth-transition ${
              selected
                ? "border-primary bg-primary/10 text-foreground"
                : "border-border bg-background-primary text-muted-foreground hover:border-primary/60"
            }`}
          >
            <span className="block font-semibold text-foreground">{option.label}</span>
            {option.description && <span className="mt-2 block text-sm">{option.description}</span>}
          </button>
        );
      })}
    </div>
  );
}

function MultiChoice({
  options,
  values,
  onToggle,
}: {
  options: Choice[];
  values: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {options.map((option) => {
        const selected = values.includes(option.value);
        return (
          <button
            key={`${option.label}-${option.value}`}
            type="button"
            onClick={() => onToggle(option.value)}
            className={`flex min-h-16 items-center justify-between gap-3 rounded-lg border p-4 text-left smooth-transition ${
              selected
                ? "border-primary bg-primary/10 text-foreground"
                : "border-border bg-background-primary text-muted-foreground hover:border-primary/60"
            }`}
          >
            <span className="font-semibold text-foreground">{option.label}</span>
            {selected && <Check size={18} className="shrink-0 text-primary" />}
          </button>
        );
      })}
    </div>
  );
}
