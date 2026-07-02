import type { AssetAssessment } from "@/types";

interface AssetAssessmentPanelProps {
  assessment: AssetAssessment;
}

const labelClass = "text-sm font-medium text-muted-foreground";
const valueClass = "mt-1 text-base font-semibold text-foreground";

export function AssetAssessmentPanel({ assessment }: AssetAssessmentPanelProps) {
  return (
    <div className="space-y-4 rounded-lg border border-border bg-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Investment assessment</p>
          <h2 className="mt-2 text-2xl font-semibold text-foreground">{assessment.overall_assessment}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            This assessment is based on currently available structured asset profile information.
          </p>
        </div>
        <div className="rounded-2xl border border-border bg-background-secondary px-4 py-3 text-sm text-foreground">
          <p className="font-semibold">Version {assessment.assessment_version}</p>
          <p className="mt-1 text-muted-foreground">Generated {new Date(assessment.generated_at).toLocaleDateString("en", { month: "short", day: "numeric", year: "numeric" })}</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Evidence strength</p>
          <p className={valueClass}>{assessment.evidence_strength}</p>
        </div>
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Current outlook</p>
          <p className={valueClass}>{assessment.investment_horizon}</p>
        </div>
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Ticker</p>
          <p className={valueClass}>{assessment.ticker}</p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Key strengths</p>
          {assessment.key_strengths.length > 0 ? (
            <ul className="mt-3 space-y-2 text-sm text-foreground">
              {assessment.key_strengths.map((strength) => (
                <li key={strength} className="flex gap-2">
                  <span className="mt-1 inline-flex h-2 w-2 rounded-full bg-primary" />
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">No strengths available from current profile data.</p>
          )}
        </div>

        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Things to watch</p>
          {assessment.things_to_watch.length > 0 ? (
            <ul className="mt-3 space-y-2 text-sm text-foreground">
              {assessment.things_to_watch.map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="mt-1 inline-flex h-2 w-2 rounded-full bg-amber-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-muted-foreground">No watch items are currently highlighted.</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Educational summary</p>
          <p className="mt-3 text-sm leading-6 text-foreground">{assessment.educational_summary}</p>
        </div>
        <div className="rounded-xl border border-border bg-background-secondary p-4">
          <p className={labelClass}>Explain like I’m 18</p>
          <p className="mt-3 text-sm leading-6 text-foreground">{assessment.explain_like_im_18}</p>
        </div>
      </div>
    </div>
  );
}
