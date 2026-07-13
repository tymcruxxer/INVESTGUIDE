import type { ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  BookOpen,
  CheckCircle2,
  Clock3,
  Database,
  HelpCircle,
  Info,
  Lightbulb,
  Search,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ResearchAssessment } from "@/types";

interface ResearchPanelProps {
  research: ResearchAssessment;
  title?: string;
}

interface ResearchUnavailableProps {
  subject: "asset" | "company";
}

const dateFormatter = new Intl.DateTimeFormat("en", {
  month: "short",
  day: "numeric",
  year: "numeric",
});

function formatDate(value?: string | null) {
  if (!value) return "Unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unavailable";
  return dateFormatter.format(date);
}

export function ResearchPanel({ research, title = "AI Research" }: ResearchPanelProps) {
  const evidenceTone = getEvidenceTone(research.evidence.strength);
  const riskTone = getRiskTone(research.risk.risk_level);
  const availableDataCount = research.evidence.data_used.length;
  const missingDataCount = research.evidence.missing_data.length;

  return (
    <section className="premium-card overflow-hidden p-0" aria-labelledby="research-panel-title">
      <div className="border-b border-white/10 bg-gradient-to-br from-primary/15 via-background-primary/80 to-emerald-500/10 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-lg border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-primary">
              <Sparkles size={14} aria-hidden="true" />
              Deterministic research
            </div>
            <h2 id="research-panel-title" className="mt-3 text-3xl font-semibold tracking-tight text-foreground">
              {title}
            </h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              Evidence-based research generated from structured backend data. It explains what the evidence suggests, why it suggests that, how confident it is, and what to learn next.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-background-primary/80 px-4 py-3 text-sm shadow-lg shadow-black/10">
            <p className="font-semibold text-foreground">Engine {research.engine_version}</p>
            <p className="mt-1 text-muted-foreground">Generated {formatDate(research.generated_at)}</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-xl border border-primary/20 bg-background-primary/75 p-5">
            <p className="flex items-center gap-2 text-sm font-medium text-primary">
              <BadgeCheck size={16} aria-hidden="true" />
              What the evidence suggests
            </p>
            <h3 className="mt-2 text-2xl font-semibold text-foreground">{research.overall_assessment.label}</h3>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.overall_assessment.summary}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <MetricPill icon={Lightbulb} label="Opportunity" value={`${research.opportunity.score}/100`} tone="primary" />
            <MetricPill icon={ShieldAlert} label="Risk" value={research.risk.risk_level} tone={riskTone} />
            <MetricPill icon={Database} label="Evidence" value={research.evidence.strength} tone={evidenceTone} />
          </div>
        </div>
      </div>

      <div className="space-y-6 p-6">
        <div className="grid gap-4 xl:grid-cols-3">
          <OpportunitySection research={research} />
          <RiskSection research={research} />
          <EvidenceSection research={research} availableDataCount={availableDataCount} missingDataCount={missingDataCount} />
        </div>

        <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
          <EducationSection research={research} />
          <Eli18Section research={research} />
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
          <QuestionChips questions={research.suggested_questions} />
          <TransparencyPanel research={research} />
        </div>
      </div>
    </section>
  );
}

export function ResearchPanelSkeleton() {
  return (
    <section className="premium-card overflow-hidden p-0" aria-label="Loading AI Research">
      <div className="border-b border-white/10 bg-background-primary/70 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="w-full max-w-3xl space-y-3">
            <SkeletonBlock className="h-7 w-48" />
            <SkeletonBlock className="h-9 w-72" />
            <SkeletonBlock className="h-4 w-full" />
            <SkeletonBlock className="h-4 w-2/3" />
          </div>
          <SkeletonBlock className="h-16 w-44" />
        </div>
        <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <SkeletonBlock className="h-36 w-full" />
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <SkeletonBlock className="h-16 w-full" />
            <SkeletonBlock className="h-16 w-full" />
            <SkeletonBlock className="h-16 w-full" />
          </div>
        </div>
      </div>
      <div className="grid gap-4 p-6 xl:grid-cols-3">
        <SkeletonBlock className="h-60 w-full" />
        <SkeletonBlock className="h-60 w-full" />
        <SkeletonBlock className="h-60 w-full" />
      </div>
    </section>
  );
}

export function ResearchUnavailable({ subject }: ResearchUnavailableProps) {
  return (
    <section className="premium-card p-6" role="status" aria-live="polite">
      <div className="flex flex-wrap items-start gap-4">
        <div className="rounded-xl border border-amber-400/25 bg-amber-500/10 p-3 text-amber-200">
          <AlertTriangle size={22} aria-hidden="true" />
        </div>
        <div className="max-w-3xl">
          <p className="text-sm uppercase tracking-[0.18em] text-amber-200">Research unavailable</p>
          <h2 className="mt-2 text-2xl font-semibold text-foreground">AI Research could not be generated right now.</h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            The {subject} page is still usable, but the research card needs reachable backend data and the research endpoint to respond successfully. No raw technical error is shown to users.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <StatusFact label="Available" value="Profile data if loaded" />
            <StatusFact label="Unavailable" value="Research payload" />
            <StatusFact label="Next step" value="Retry or browse assets" />
          </div>
        </div>
      </div>
    </section>
  );
}

function OpportunitySection({ research }: { research: ResearchAssessment }) {
  return (
    <ResearchSection icon={Lightbulb} title="Opportunity" subtitle="What looks interesting" accent="primary">
      <ScoreHeader label={research.opportunity.label} score={research.opportunity.score} tone="primary" />
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.opportunity.summary}</p>
      <MiniFacts
        items={[
          { title: "Current outlook", value: research.overall_assessment.label },
          { title: "Evidence", value: research.evidence.strength },
          { title: "Coverage", value: `${research.evidence.data_used.length} fields used` },
        ]}
      />
      <DetailDisclosure title="Key drivers" items={research.opportunity.reasons} icon={CheckCircle2} />
      <DetailDisclosure title="Supporting evidence" items={research.opportunity.supporting_evidence} icon={Database} />
    </ResearchSection>
  );
}

function RiskSection({ research }: { research: ResearchAssessment }) {
  const tone = getRiskTone(research.risk.risk_level);
  const reducers = research.risk.supporting_evidence.length > 0
    ? research.risk.supporting_evidence
    : ["More complete issuer data would reduce uncertainty."];

  return (
    <ResearchSection icon={ShieldAlert} title="Risk" subtitle="What could change the view" accent={tone}>
      <ScoreHeader label={research.risk.risk_level} score={research.risk.risk_score} tone={tone} />
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.risk.summary}</p>
      <MiniFacts
        items={[
          { title: "Overall risk", value: research.risk.overall_risk },
          { title: "Main watch item", value: research.risk.things_to_watch[0] ?? "Unavailable" },
          { title: "Certainty", value: "Not implied" },
        ]}
      />
      <DetailDisclosure title="What increases this risk?" items={research.risk.reasons} icon={AlertTriangle} />
      <DetailDisclosure title="What may reduce uncertainty?" items={reducers} icon={CheckCircle2} />
      <DetailDisclosure title="Things to watch" items={research.risk.things_to_watch} icon={Activity} />
    </ResearchSection>
  );
}

function EvidenceSection({ research, availableDataCount, missingDataCount }: { research: ResearchAssessment; availableDataCount: number; missingDataCount: number }) {
  const tone = getEvidenceTone(research.evidence.strength);
  const completeness = availableDataCount + missingDataCount === 0
    ? 0
    : Math.round((availableDataCount / (availableDataCount + missingDataCount)) * 100);

  return (
    <ResearchSection icon={Database} title="Evidence strength" subtitle="How reliable the inputs are" accent={tone}>
      <ScoreHeader label={research.evidence.strength} score={research.evidence.score} tone={tone} />
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.evidence.summary}</p>
      <MiniFacts
        items={[
          { title: "Data completeness", value: `${completeness}%` },
          { title: "Available data", value: `${availableDataCount} fields` },
          { title: "Freshness", value: formatDate(research.transparency.last_updated) },
        ]}
      />
      <DetailDisclosure title="Why?" items={research.evidence.reasons} icon={Info} defaultOpen />
      <DetailDisclosure title="Available data" items={research.evidence.data_used} icon={Database} />
      <DetailDisclosure title="Unavailable data" items={research.evidence.missing_data} icon={AlertTriangle} />
    </ResearchSection>
  );
}

function EducationSection({ research }: { research: ResearchAssessment }) {
  return (
    <div className="rounded-xl border border-emerald-400/20 bg-emerald-500/10 p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-emerald-200">
        <BookOpen size={18} aria-hidden="true" />
        Learn before you invest
      </div>
      <p className="mt-3 text-base leading-7 text-foreground">{research.education.summary}</p>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{research.education.why_it_matters}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {research.education.key_concepts.map((concept) => (
          <span key={concept} className="rounded-lg border border-emerald-300/20 bg-background-primary/60 px-3 py-1 text-xs text-emerald-100">
            {concept}
          </span>
        ))}
      </div>
    </div>
  );
}

function Eli18Section({ research }: { research: ResearchAssessment }) {
  return (
    <div className="rounded-xl border border-primary/20 bg-primary/10 p-5">
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-primary/30 bg-background-primary/70 text-primary">
          <HelpCircle size={24} aria-hidden="true" />
        </div>
        <div>
          <p className="text-sm font-medium text-primary">Explain Like I am 18</p>
          <p className="mt-2 text-base leading-7 text-foreground">{research.eli18.summary}</p>
          <p className="mt-3 rounded-lg border border-white/10 bg-background-primary/60 p-3 text-sm leading-6 text-muted-foreground">
            Zimbabwe example: {research.eli18.example}
          </p>
        </div>
      </div>
    </div>
  );
}

function QuestionChips({ questions }: { questions: string[] }) {
  const defaults = ["Compare with another asset", "Show company profile", "Why is evidence limited?", "Show latest news"];
  const items = questions.length > 0 ? questions : defaults;

  return (
    <div className="rounded-xl border border-white/10 bg-background-primary/70 p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Search size={18} aria-hidden="true" />
        What should I learn next?
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {items.map((question) => (
          <a
            key={question}
            href={questionHref(question)}
            className="rounded-lg border border-white/10 bg-background-secondary px-3 py-2 text-sm text-foreground transition hover:border-primary/50 hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-primary/60"
          >
            {question}
          </a>
        ))}
      </div>
    </div>
  );
}

function TransparencyPanel({ research }: { research: ResearchAssessment }) {
  return (
    <div className="rounded-xl border border-white/10 bg-background-primary/70 p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Clock3 size={18} aria-hidden="true" />
        Research transparency
      </div>
      <dl className="mt-4 space-y-2 text-sm">
        <TransparencyRow label="Research status" value={research.transparency.research_status} />
        <TransparencyRow label="Last updated" value={formatDate(research.transparency.last_updated)} />
        <TransparencyRow label="Assessment version" value={research.assessment_version} />
        <TransparencyRow label="Subject" value={`${research.subject_type.toUpperCase()} ${research.ticker}`} />
      </dl>
      <p className="mt-4 text-xs leading-5 text-muted-foreground">
        This section shows the data coverage behind the research. Missing data lowers confidence; it does not mean the investment is good or bad.
      </p>
    </div>
  );
}

function ResearchSection({ icon: Icon, title, subtitle, accent, children }: { icon: LucideIcon; title: string; subtitle: string; accent: Tone; children: ReactNode }) {
  return (
    <div className={`rounded-xl border ${toneBorder(accent)} bg-background-primary/70 p-5 transition hover:-translate-y-0.5 hover:shadow-xl hover:shadow-black/10`}>
      <div className="flex items-start gap-3">
        <div className={`rounded-lg border p-2 ${toneSurface(accent)}`}>
          <Icon size={18} aria-hidden="true" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
        </div>
      </div>
      {children}
    </div>
  );
}

function ScoreHeader({ label, score, tone }: { label: string; score: number; tone: Tone }) {
  return (
    <div className="mt-4">
      <div className="flex items-end justify-between gap-3">
        <p className="text-base font-semibold text-foreground">{label}</p>
        <p className={`text-2xl font-semibold ${toneText(tone)}`}>{score}</p>
      </div>
      <ScoreBar value={score} tone={tone} />
    </div>
  );
}

function ScoreBar({ value, tone }: { value: number; tone: Tone }) {
  return (
    <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-white/10" aria-hidden="true">
      <div className={`h-full rounded-full ${toneFill(tone)}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

function DetailDisclosure({ title, items, icon: Icon, defaultOpen = false }: { title: string; items: string[]; icon: LucideIcon; defaultOpen?: boolean }) {
  return (
    <details className="group mt-4 rounded-lg border border-white/10 bg-background-secondary/70 p-3" open={defaultOpen}>
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium text-foreground focus:outline-none focus:ring-2 focus:ring-primary/60">
        <span className="flex items-center gap-2">
          <Icon size={16} aria-hidden="true" />
          {title}
        </span>
        <span className="text-muted-foreground transition group-open:rotate-45">+</span>
      </summary>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
          {items.map((item) => (
            <li key={item} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-muted-foreground">No items available from current data.</p>
      )}
    </details>
  );
}

function MiniFacts({ items }: { items: Array<{ title: string; value: string }> }) {
  return (
    <div className="mt-4 grid gap-2 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
      {items.map((item) => (
        <StatusFact key={item.title} label={item.title} value={item.value} />
      ))}
    </div>
  );
}

function MetricPill({ icon: Icon, label, value, tone }: { icon: LucideIcon; label: string; value: string; tone: Tone }) {
  return (
    <div className={`rounded-xl border ${toneBorder(tone)} bg-background-primary/75 p-4`}>
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Icon size={16} aria-hidden="true" />
        {label}
      </div>
      <p className={`mt-2 text-lg font-semibold ${toneText(tone)}`}>{value}</p>
    </div>
  );
}

function StatusFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-background-secondary/80 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-medium text-foreground">{value}</p>
    </div>
  );
}

function TransparencyRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium text-foreground">{value}</dd>
    </div>
  );
}

function SkeletonBlock({ className }: { className: string }) {
  return <div className={`animate-pulse rounded-lg bg-white/10 ${className}`} />;
}

type Tone = "primary" | "emerald" | "amber" | "red" | "teal";

function getEvidenceTone(strength: ResearchAssessment["evidence"]["strength"]): Tone {
  if (strength === "Strong") return "emerald";
  if (strength === "Moderate") return "teal";
  if (strength === "Limited") return "amber";
  return "red";
}

function getRiskTone(level: ResearchAssessment["risk"]["risk_level"]): Tone {
  if (level === "Low") return "emerald";
  if (level === "Moderate") return "amber";
  return "red";
}

function toneText(tone: Tone) {
  return {
    primary: "text-primary",
    emerald: "text-emerald-300",
    amber: "text-amber-300",
    red: "text-red-300",
    teal: "text-teal-300",
  }[tone];
}

function toneFill(tone: Tone) {
  return {
    primary: "bg-primary",
    emerald: "bg-emerald-300",
    amber: "bg-amber-300",
    red: "bg-red-300",
    teal: "bg-teal-300",
  }[tone];
}

function toneBorder(tone: Tone) {
  return {
    primary: "border-primary/25",
    emerald: "border-emerald-400/25",
    amber: "border-amber-400/25",
    red: "border-red-400/25",
    teal: "border-teal-400/25",
  }[tone];
}

function toneSurface(tone: Tone) {
  return {
    primary: "border-primary/30 bg-primary/10 text-primary",
    emerald: "border-emerald-400/30 bg-emerald-500/10 text-emerald-300",
    amber: "border-amber-400/30 bg-amber-500/10 text-amber-300",
    red: "border-red-400/30 bg-red-500/10 text-red-300",
    teal: "border-teal-400/30 bg-teal-500/10 text-teal-300",
  }[tone];
}

function questionHref(question: string) {
  const normalized = question.toLowerCase();
  if (normalized.includes("compare")) return "/compare";
  if (normalized.includes("news")) return "#latest-news";
  if (normalized.includes("profile") || normalized.includes("revenue")) return "#company-intelligence";
  if (normalized.includes("risk")) return "#research-panel-title";
  if (normalized.includes("evidence")) return "#research-panel-title";
  if (normalized.includes("reit")) return "/education";
  return "#research-panel-title";
}